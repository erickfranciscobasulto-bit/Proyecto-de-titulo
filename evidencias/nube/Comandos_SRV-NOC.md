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
