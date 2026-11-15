# Servicio FTPS en la nube (AWS) – Registro de implementación

| Dato | Valor |
|---|---|
| Servidor | SRV-AGROPRODEL (EC2, Ubuntu 24.04), IP elástica 54.236.126.16 |
| Software | vsftpd 3.0.5 |
| Modalidad | **FTPS implícito** (TLS desde el primer byte) en el puerto **990** |
| Certificado | Let's Encrypt de `agroprodel-ltda.duckdns.org` (el mismo de la web HTTPS) |
| Modo de datos | Pasivo, puertos 30000-30100, `pasv_address=54.236.126.16` |
| Usuario | `ftpagro` (dedicado, sin uso de la cuenta `ubuntu`); contraseña no documentada |
| Jaula | `/home/ftpagro/ftp` (de root, solo lectura) y `/home/ftpagro/ftp/archivos` (escritura) |
| Cliente probado | WinSCP: protocolo FTP, cifrado TLS/SSL implícito, puerto 990, host por nombre de dominio |

## Configuración aplicada (`/etc/vsftpd.conf`)
```
listen=YES
listen_ipv6=NO
anonymous_enable=NO
local_enable=YES
write_enable=YES
local_umask=022
chroot_local_user=YES
user_sub_token=$USER
local_root=/home/$USER/ftp
userlist_enable=YES
userlist_file=/etc/vsftpd.userlist
userlist_deny=NO
pasv_enable=YES
pasv_min_port=30000
pasv_max_port=30100
pasv_address=54.236.126.16
ssl_enable=YES
rsa_cert_file=/etc/letsencrypt/live/agroprodel-ltda.duckdns.org/fullchain.pem
rsa_private_key_file=/etc/letsencrypt/live/agroprodel-ltda.duckdns.org/privkey.pem
force_local_logins_ssl=YES
force_local_data_ssl=YES
ssl_tlsv1=YES
ssl_sslv2=NO
ssl_sslv3=NO
require_ssl_reuse=NO
ssl_ciphers=HIGH
xferlog_enable=YES
xferlog_std_format=YES
ftpd_banner=Agroprodel Ltda. - Servicio FTP seguro. Acceso solo autorizado.
pam_service_name=vsftpd
listen_port=990
implicit_ssl=YES
```
Durante el diagnóstico se agregaron temporalmente `log_ftp_protocol=YES`, `dual_log_enable=YES` y
`vsftpd_log_file=/var/log/vsftpd.log` (registro de comandos FTP); se retiran al finalizar las pruebas.

## Grupo de seguridad (SG_SERVICIOS_AGROPRODEL)
| Puerto | Origen | Uso |
|---|---|---|
| TCP 990 | IP de cada administrador (/32) | Control FTPS |
| TCP 30000-30100 | IP de cada administrador (/32) | Datos en modo pasivo |

## Verificaciones
- `openssl s_client -connect localhost:990 -brief`: **TLSv1.3**, `TLS_AES_256_GCM_SHA384`, CN `agroprodel-ltda.duckdns.org`, *Verification: OK*, banner 220.
- WinSCP: *Conexión TLS establecida*; candado en la barra de estado; el panel remoto muestra solo `/archivos` (jaula efectiva).
- Subida a la raíz `/`: **"Could not create file"** (la raíz de la jaula es de solo lectura) – comportamiento esperado.

## Problemas encontrados

### P-07 · El router doméstico intercepta FTP explícito en el puerto 21
| Campo | Detalle |
|---|---|
| Síntoma | WinSCP (TLS explícito, puerto 21): *"Command not implemented for that parameter"* (504). |
| Diagnóstico | El servidor negocia TLS 1.3 correctamente (`openssl s_client -starttls ftp`). Con `log_ftp_protocol` el registro solo muestra la conexión y el banner 220: **el comando `AUTH TLS` nunca llegó al servidor**, pero el cliente recibió una respuesta. |
| Causa | Un equipo intermedio (función **FTP ALG** del router doméstico) inspecciona el puerto 21 en texto plano, no reconoce `AUTH TLS` y responde por su cuenta. No había antivirus en el equipo. |
| Solución | Cambiar a **FTPS implícito en el puerto 990** (`listen_port=990`, `implicit_ssl=YES`): el canal va cifrado desde el primer byte y el ALG no puede intervenir. Reglas del grupo de seguridad 21 → 990. |
| Beneficio adicional | Funcionará igual en redes que no se controlan (por ejemplo, la de Duoc el día de la demostración). |

### P-08 · Archivos subidos con 0 bytes (OneDrive "solo en la nube")
| Campo | Detalle |
|---|---|
| Síntoma | Los archivos subidos desde `C:\Users\<usuario>\OneDrive\Documentos` aparecen en `/archivos` con **0 KB**. El listado de directorios funciona. |
| Diagnóstico | Registro de vsftpd: `STOR ...` → `FAIL UPLOAD ... 0.00Kbyte/sec` y luego `OK UPLOAD ... 0.00Kbyte/sec`: la sesión TLS y el canal pasivo funcionan, pero no llegan datos. |
| Hipótesis descartada | Incompatibilidad de vsftpd 3.0.5 con TLS 1.3: limitar el cliente a TLS 1.2 no cambió el resultado mientras el origen seguía en OneDrive. |
| Prueba concluyente | El mismo procedimiento con archivos de `C:\Users\<usuario>\Downloads` (almacenamiento local) sube con su **tamaño completo** (`index.html`, 36 KB). |
| Causa | **OneDrive Archivos a petición**: los archivos marcados "solo en la nube" muestran su tamaño en el explorador, pero el contenido no está en el disco; el cliente FTP lee 0 bytes. No es una falla del servidor ni de TLS. |
| Solución | Subir desde una carpeta local, o en OneDrive marcar la carpeta como **"Mantener siempre en este dispositivo"** antes de transferir. El cliente puede volver a TLS 1.3 (máxima versión) sin problemas. |
| Aprendizaje | Ante un síntoma en la red, comprobar también el origen de los datos: el registro del servidor (OK UPLOAD con 0 KB/s) indicaba que la sesión era correcta y que el cliente no entregaba contenido. |

## Cierre
- Registro detallado de comandos retirado (`log_ftp_protocol`, `dual_log_enable`, `vsftpd_log_file`); `systemctl is-active vsftpd` → **active**.
- Prueba final con TLS 1.3 (cliente: mínima 1.2, máxima 1.3): `Informe_Implementacion_Red_Agroprodel.docx` subido desde almacenamiento local con su tamaño completo (1 571 KB).
