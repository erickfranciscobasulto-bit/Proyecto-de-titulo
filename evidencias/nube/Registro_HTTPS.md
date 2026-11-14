# HTTPS del servidor web (AWS) – Registro de implementación

| Dato | Valor |
|---|---|
| Servidor | SRV-AGROPRODEL (EC2 t3.micro, Ubuntu 24.04), IP elástica 54.236.126.16 |
| Dominio público | **agroprodel-ltda.duckdns.org** (DuckDNS, registro A → 54.236.126.16) |
| Autoridad certificadora | Let's Encrypt (validación HTTP-01 por el puerto 80) |
| Cliente | Certbot 2.9.0 con el conector de Nginx |
| Certificado | `/etc/letsencrypt/live/agroprodel-ltda.duckdns.org/fullchain.pem` |
| Clave privada | `/etc/letsencrypt/live/agroprodel-ltda.duckdns.org/privkey.pem` (no sale del servidor) |
| Emitido / vence | 14-11-2026 / 12-02-2027 (90 días, renovación automática) |
| Redirección | HTTP → HTTPS (`--redirect`) |

## Por qué DuckDNS y no agroprodel.cl
`agroprodel.cl` es una zona interna servida por el BIND del propio servidor: no está delegada en el DNS público,
por lo que Let's Encrypt no puede validarla. Se usó un subdominio público gratuito de DuckDNS
(`agroprodel` ya estaba ocupado por otro usuario).

## Pasos aplicados
1. Grupo de seguridad SG_SERVICIOS_AGROPRODEL: regla SSH (22) desde la IP pública del administrador (/32).
2. DuckDNS: subdominio `agroprodel-ltda` con current ip 54.236.126.16. Verificación: `dig +short agroprodel-ltda.duckdns.org` → 54.236.126.16.
3. `sudo apt install -y certbot python3-certbot-nginx`
4. `server_name agroprodel-ltda.duckdns.org;` en `/etc/nginx/sites-available/default`; `nginx -t` correcto; `systemctl reload nginx`.
5. `sudo certbot --nginx -d agroprodel-ltda.duckdns.org --redirect` → *Successfully deployed certificate*.

## Seguridad
- El token de DuckDNS y la clave privada del certificado **no se documentan**.
- Puertos 80/443 abiertos a Internet (necesarios para la web y la renovación); SSH y FTP solo desde IP autorizadas.

## Lista de verificación antes de una demostración
- Iniciar el Learner Lab y comprobar la instancia en *Running*.
- `sudo certbot renew` (la renovación automática solo corre con la instancia encendida).
- Desde la red de la demostración: agregar su IP pública al grupo de seguridad (SSH/ICMP) y ejecutar `permitir-mi-ip` para el DNS; retirar la regla al terminar.
