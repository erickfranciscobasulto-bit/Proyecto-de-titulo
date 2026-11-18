#!/usr/bin/env python3
# Integracion Wazuh -> Telegram (SOC Agroprodel)
# Wazuh la ejecuta con: <archivo de alerta> <api_key = chat id> <hook_url = https://api.telegram.org/bot<TOKEN>/sendMessage>
# El token y el chat id quedan solo en /var/ossec/etc/ossec.conf (no se documentan).
import sys, json, requests

alert_file, chat_id, hook_url = sys.argv[1], sys.argv[2], sys.argv[3]
with open(alert_file) as f:
    a = json.load(f)

r = a.get('rule', {})
d = a.get('data', {})
equipo = a.get('predecoder', {}).get('hostname') or a.get('agent', {}).get('name', '-')
origen = d.get('srcip') or d.get('src_ip') or '-'
destino = d.get('dstip') or d.get('dest_ip') or '-'
nivel = r.get('level', 0)
gravedad = 'CRITICA' if nivel >= 12 else 'ALTA'

texto = (f"[SOC Agroprodel] Alerta {gravedad} (nivel {nivel})\n"
         f"{r.get('description', '')}\n"
         f"Regla: {r.get('id', '-')} | Equipo: {equipo}\n"
         f"Origen: {origen} -> Destino: {destino}\n")
firma = d.get('alert', {}).get('signature') if isinstance(d.get('alert'), dict) else None
if firma:
    texto += f"Suricata: {firma}\n"
texto += f"Hora: {a.get('timestamp', '-')}"

requests.post(hook_url, json={'chat_id': chat_id, 'text': texto}, timeout=10)
