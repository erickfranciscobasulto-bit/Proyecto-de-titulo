# SRV-NOC – Comandos aplicados

Servidor: EC2 t3.small, Ubuntu Server 24.04 LTS · IP privada 10.40.1.30 · IP elástica 98.83.92.138.
Funciones: Zabbix, Grafana y concentrador VPN (strongSwan). Acceso: PuTTY con la llave LLAVE-NOC (no se documenta).

## 1. Preparación del sistema
```bash
sudo hostnamectl set-hostname srv-noc
sudo timedatectl set-timezone America/Santiago
sudo apt update && sudo apt -y upgrade
```

## 2. VPN IPsec (strongSwan) y reenvío de paquetes
```bash
sudo apt install -y strongswan strongswan-swanctl charon-systemd
echo "net.ipv4.ip_forward=1" | sudo tee /etc/sysctl.d/99-vpn-soc.conf
sudo sysctl -p /etc/sysctl.d/99-vpn-soc.conf
systemctl is-active strongswan
swanctl --version
```

Se instaló también `strongswan-starter` (servicio heredado `ipsec`) como dependencia; se deshabilita para que un
solo demonio (charon-systemd, administrado con `swanctl`) use los puertos UDP 500/4500. Se reinicia para cargar el
kernel actualizado (7.0.0-1017-aws):
```bash
sudo systemctl disable --now strongswan-starter
sudo sysctl -p /etc/sysctl.d/99-vpn-soc.conf
sudo reboot
```
Verificación: `uname -r` → 7.0.0-1017-aws · `net.ipv4.ip_forward = 1` · strongswan **active** · strongswan-starter **disabled**.

## 3. Túnel IKEv2 hacia R-TEMUCO (`/etc/swanctl/conf.d/agroprodel.conf`, permiso 600)
La clave compartida se genera aleatoriamente en el servidor (32 caracteres) y no se documenta.
```
connections {
  temuco {
    version = 2
    local_addrs = 10.40.1.30
    remote_addrs = %any
    proposals = aes256-sha256-modp2048
    dpd_delay = 30s
    local {
      auth = psk
      id = 98.83.92.138
    }
    remote {
      auth = psk
      id = r-temuco.agroprodel.cl
    }
    children {
      sedes {
        local_ts = 10.40.0.0/16
        remote_ts = 192.168.0.0/16
        esp_proposals = aes256-sha256-modp2048
        dpd_action = clear
      }
    }
  }
}
secrets {
  ike-temuco {
    id = r-temuco.agroprodel.cl
    secret = "<clave no documentada>"
  }
}
```
```bash
sudo chmod 600 /etc/swanctl/conf.d/agroprodel.conf
sudo swanctl --load-all
sudo swanctl --list-conns
```
Resultado: `loaded ike secret 'ike-temuco'`, `loaded connection 'temuco'`; sedes 10.40.0.0/16 === 192.168.0.0/16.

## 5. Memoria swap (2 GB)
La instancia t3.small tiene 2 GB de RAM para Zabbix, MySQL y Grafana; el swap evita que el kernel termine
procesos por falta de memoria.
```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
free -h
```
Resultado: `Mem: 1.9Gi` · `Swap: 2.0Gi`.

## 6. Zabbix 7.0 LTS – repositorio oficial
```bash
wget https://repo.zabbix.com/zabbix/7.0/ubuntu/pool/main/z/zabbix-release/zabbix-release_latest_7.0+ubuntu24.04_all.deb
sudo dpkg -i zabbix-release_latest_7.0+ubuntu24.04_all.deb
sudo apt update
```
Resultado: paquete `zabbix-release 1:7.0-5+ubuntu24.04`; `apt update` lee `repo.zabbix.com/zabbix/7.0/ubuntu noble`.
El aviso *New release '26.04.1 LTS' available* se ignora: el servidor se mantiene en 24.04 LTS, versión soportada
por Zabbix 7.0.

## 7. Zabbix 7.0 – paquetes
```bash
sudo apt -y install mysql-server zabbix-server-mysql zabbix-frontend-php zabbix-nginx-conf zabbix-sql-scripts zabbix-agent2
systemctl is-active mysql
zabbix_server --version | head -1
```
Resultado: `active` · `zabbix_server (Zabbix) 7.0.32` · MySQL 8.0.46.

## 8. Base de datos de Zabbix
Usuario `zabbix` exclusivo con permisos solo sobre la base `zabbix` (mínimo privilegio). Clave no documentada.
```sql
-- sudo mysql
CREATE DATABASE zabbix CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;
CREATE USER 'zabbix'@'localhost' IDENTIFIED BY '<clave no documentada>';
GRANT ALL PRIVILEGES ON zabbix.* TO 'zabbix'@'localhost';
SET GLOBAL log_bin_trust_function_creators = 1;
QUIT;
```
```bash
zcat /usr/share/zabbix-sql-scripts/mysql/server.sql.gz | mysql --default-character-set=utf8mb4 -uzabbix -p zabbix
sudo mysql -e "SET GLOBAL log_bin_trust_function_creators = 0;"
sudo mysql -e "SELECT COUNT(*) AS tablas FROM information_schema.tables WHERE table_schema='zabbix';"
```
Resultado: 203 tablas. `log_bin_trust_function_creators` se activa solo durante la carga del esquema (crea
triggers con el binlog habilitado) y se desactiva enseguida.

## 9. Conexión de Zabbix a la base de datos y panel web
```bash
sudo nano /etc/zabbix/zabbix_server.conf
#   bajo "# DBPassword=" se agrega:  DBPassword=<clave no documentada>   (DBUser=zabbix ya viene definido)
sudo sed -i 's/^#\s*listen\s*8080;/        listen          80;/; s/^#\s*server_name\s*example.com;/        server_name     _;/' /etc/zabbix/nginx.conf
sudo rm /etc/nginx/sites-enabled/default
grep -E "^\s*(listen|server_name)" /etc/zabbix/nginx.conf
sudo nginx -t
sudo systemctl restart zabbix-server zabbix-agent2 nginx php8.3-fpm
sudo systemctl enable zabbix-server zabbix-agent2 nginx php8.3-fpm
systemctl is-active zabbix-server zabbix-agent2 nginx php8.3-fpm
sudo tail -5 /var/log/zabbix/zabbix_server.log
```
La clave se edita con nano (no con `sed`) para que no quede en el historial de la shell.
Se elimina el sitio por defecto de Nginx para que el puerto 80 sirva directamente el panel de Zabbix.

Resultado: `listen 80;` · `server_name _;` · `syntax is ok` · 4 servicios `active` · log sin errores de acceso a la
base (`server #47 started [snmp poller #1]`, `configuration syncer`, `internal poller`, `proxy group manager`).

## 10. Panel web de Zabbix (asistente de instalación)
Idioma español: los idiomas aparecían deshabilitados porque el sistema solo tenía la configuración regional en inglés.
```bash
sudo locale-gen es_ES.UTF-8
sudo systemctl restart php8.3-fpm
```
Asistente en `http://98.83.92.138/` (puerto 80 permitido solo desde la IP del administrador en SG_SOC_NOC):

| Pantalla | Valor |
|---|---|
| Idioma | Español (es_ES) |
| Requisitos previos | Todos OK (PHP 8.3.6, MySQL, bcmath, mbstring, sockets…) |
| Conexión BD | MySQL · localhost · puerto por defecto · base `zabbix` · usuario `zabbix` · clave no documentada · sin TLS (conexión por socket local) |
| Nombre del servidor | SOC-AGROPRODEL |

Resultado: tablero *Global view* operativo; "El servidor Zabbix se está ejecutando: Sí (localhost:10051)", versión 7.0.32,
1 equipo (Zabbix server) monitoreado por el agente 2.
La clave de fábrica del usuario `Admin` se cambió al primer ingreso (no documentada).

## 11. Ajustes del panel (Administración → General → Interfaz de usuario)
| Parámetro | Valor | Motivo |
|---|---|---|
| Zona horaria por defecto | (UTC-03:00) America/Santiago | El tablero mostraba UTC ("Reykjavik"); se alinean alertas y gráficos con la hora de las sedes |
| Idioma | Español (es_ES) | — |
| Jornada laboral | `1-5,08:00-17:00` | Lunes a viernes, 8 h + 1 h de colación = 40 h semanales (bajo el máximo de 42 h de la Ley 21.561). Los gráficos sombrean el horario laboral para distinguir eventos con impacto en usuarios de los que ocurren fuera de horario |

## 12. Prueba SNMPv3 hacia los equipos de red (por la VPN)
```bash
sudo apt -y install snmp
# con un espacio inicial para que la línea (con claves) no quede en el historial
 snmpget -v3 -l authPriv -u zabbix -a SHA -A '<clave no documentada>' -x AES -X '<clave no documentada>' 192.168.40.241 1.3.6.1.2.1.1.5.0 1.3.6.1.2.1.1.6.0
```
Primer intento: *Timeout* (error S-06, túnel cerrado por inactividad; corregido con IP SLA en R-TEMUCO).
Resultado tras la corrección:
```
iso.3.6.1.2.1.1.5.0 = STRING: "R-TEMUCO.agroprodel.cl"
iso.3.6.1.2.1.1.6.0 = STRING: "Temuco - Casa Matriz"
```

## 13. Grafana (repositorio oficial) y plugin de Zabbix
```bash
sudo apt-get install -y apt-transport-https wget gnupg
sudo mkdir -p /etc/apt/keyrings
wget -q -O - https://apt.grafana.com/gpg.key | gpg --dearmor | sudo tee /etc/apt/keyrings/grafana.gpg > /dev/null
echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main" | sudo tee /etc/apt/sources.list.d/grafana.list
sudo apt-get update
sudo apt-get install -y grafana
sudo systemctl enable --now grafana-server
# el comando antiguo grafana-cli falla (ver S-08); se usa "grafana cli" con --homepath
sudo grafana cli --homepath /usr/share/grafana plugins install alexanderzobnin-zabbix-app
sudo systemctl restart grafana-server
systemctl is-active grafana-server
sudo ss -tlnp | grep 3000
sudo ls /var/lib/grafana/plugins
```
Resultado: Grafana 13.3.1 · plugin `alexanderzobnin-zabbix-app` v6.10.3 · servicio `active` · escucha en `*:3000`.
Memoria tras la instalación: 928 MiB disponibles, swap en uso (328 MiB) como respaldo.

## 14. VPN: red de tránsito del firewall (203.0.113.0/30)
Permite que el SOC alcance FW-TEMUCO (203.0.113.1) por el túnel.
```bash
sudo sed -i 's|remote_ts = 192.168.0.0/16$|remote_ts = 192.168.0.0/16,203.0.113.0/30|' /etc/swanctl/conf.d/agroprodel.conf
sudo grep remote_ts /etc/swanctl/conf.d/agroprodel.conf
sudo swanctl --load-all
sudo swanctl --terminate --ike temuco
```
Resultado: `remote_ts = 192.168.0.0/16,203.0.113.0/30` · `loaded connection 'temuco'`.
En R-TEMUCO: línea 20 en `VPN-AWS` y `clear crypto session`; túnel restablecido (ping 9/10).
