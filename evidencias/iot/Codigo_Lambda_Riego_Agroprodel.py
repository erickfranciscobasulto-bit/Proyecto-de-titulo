# Función AWS Lambda del módulo IoT de riego (Agroprodel Ltda.)
# Intermediario entre el ESP32 y la API de bots de Telegram.
# Variables de entorno requeridas: DEVICE_API_KEY, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID (no se documentan sus valores).
import json, os, hmac
import urllib.request, urllib.parse, urllib.error

COMANDOS_VALIDOS = {"/parar", "/stop", "/regar", "/auto", "/estado", "/ayuda", "/start"}


def respuesta(codigo, datos):
    return {"statusCode": codigo,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(datos, ensure_ascii=False, separators=(",", ":"))}


def telegram(metodo, params):
    """Llama a la API de Telegram. El token solo existe en la Lambda."""
    token = os.environ["TELEGRAM_TOKEN"].strip()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/{metodo}",
        data=urllib.parse.urlencode(params).encode("utf-8"),
        headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"ok": False, "error_code": e.code,
                "description": e.read().decode("utf-8", "replace")}


def enviar_mensaje(event, ip):
    raw_body = event.get("body") or "{}"
    try:
        body = json.loads(raw_body) if isinstance(raw_body, str) else raw_body
    except json.JSONDecodeError:
        print(f"RECHAZADO 400 JSON invalido | ip={ip}")
        return respuesta(400, {"error": "JSON invalido"})
    mensaje = body.get("mensaje")
    if not mensaje:
        print(f"RECHAZADO 400 sin mensaje | ip={ip}")
        return respuesta(400, {"error": "Falta el mensaje"})
    r = telegram("sendMessage", {"chat_id": os.environ["TELEGRAM_CHAT_ID"].strip(),
                                 "text": str(mensaje)})
    if not r.get("ok"):
        print(f"ERROR TELEGRAM sendMessage | {r}")
        return respuesta(502, {"error": "Telegram rechazo el mensaje"})
    msg_id = r["result"]["message_id"]
    print(f"ENVIADO OK | ip={ip} | message_id={msg_id} | texto={str(mensaje)[:60]!r}")
    return respuesta(200, {"estado": "enviado", "message_id": msg_id})


def obtener_comandos(qs, ip):
    try:
        offset = int(qs.get("offset", "0"))
    except ValueError:
        return respuesta(400, {"error": "offset invalido"})
    r = telegram("getUpdates", {"offset": offset, "timeout": 0, "limit": 10,
                                "allowed_updates": json.dumps(["message"])})
    if not r.get("ok"):
        print(f"ERROR TELEGRAM getUpdates | {r}")
        return respuesta(502, {"error": "Telegram no respondio"})
    chat_autorizado = os.environ["TELEGRAM_CHAT_ID"].strip()
    siguiente, comandos = max(offset, 0), []
    for u in r.get("result", []):
        siguiente = max(siguiente, u["update_id"] + 1)
        msg = u.get("message") or {}
        chat_id = str((msg.get("chat") or {}).get("id", ""))
        texto = (msg.get("text") or "").strip().lower()
        if chat_id != chat_autorizado:
            print(f"IGNORADO chat no autorizado | chat_id={chat_id}")
            continue
        if not texto:
            continue
        cmd = texto.split()[0].split("@")[0]
        comandos.append(cmd if cmd in COMANDOS_VALIDOS else "/desconocido")
    if comandos:
        print(f"COMANDOS | ip={ip} | {comandos}")
    return respuesta(200, {"siguiente": siguiente, "comandos": comandos})


def lambda_handler(event, context):
    http = (event.get("requestContext") or {}).get("http", {})
    ip, metodo = http.get("sourceIp", "?"), http.get("method", "POST")
    try:
        headers = {str(k).lower(): str(v).strip()
                   for k, v in (event.get("headers") or {}).items()}
        api_key = headers.get("x-api-key", "")
        expected = os.environ.get("DEVICE_API_KEY", "").strip()
        if not expected or not hmac.compare_digest(api_key, expected):
            print(f"RECHAZADO 401 | ip={ip} | metodo={metodo}")
            return respuesta(401, {"error": "No autorizado"})
        if metodo == "GET":
            qs = event.get("queryStringParameters") or {}
            if qs.get("accion") == "comandos":
                return obtener_comandos(qs, ip)
            return respuesta(400, {"error": "accion desconocida"})
        return enviar_mensaje(event, ip)
    except Exception as e:
        print(f"ERROR INTERNO | {type(e).__name__}: {e}")
        return respuesta(500, {"error": "Error procesando la solicitud"})
