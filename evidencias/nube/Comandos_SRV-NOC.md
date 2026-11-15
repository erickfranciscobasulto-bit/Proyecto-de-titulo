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
