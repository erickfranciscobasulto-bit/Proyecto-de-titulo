# SRV-AGROPRODEL – Comandos aplicados

Servidor: EC2 t3.micro, Ubuntu Server 24.04 LTS · IP privada 10.40.1.10 · IP elástica 54.236.126.16.
Acceso: PuTTY/WinSCP con la llave LLAVE_AGROPRODEL (no se documenta). Comandos en el orden en que se aplicaron.

## 1. Preparación del sistema
```bash
sudo hostnamectl set-hostname srv-agroprodel
sudo timedatectl set-timezone America/Santiago
sudo apt update && sudo apt -y upgrade
```

## 2. Servidor WEB (Nginx)
```bash
sudo apt -y install nginx
sudo systemctl enable --now nginx
systemctl status nginx --no-pager
```
Página inicial de prueba (luego reemplazada por la página definitiva):
```bash
sudo tee /var/www/html/index.html > /dev/null <<'EOF'
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Agroprodel Ltda.</title>
<style>
 body{margin:0;font-family:Arial,sans-serif;background:#f4f6f8;color:#1f2937}
 header{background:#1f3864;color:#fff;padding:24px 16px;text-align:center}
 header h1{margin:0;font-size:28px} header p{margin:6px 0 0;opacity:.85}
 main{max-width:900px;margin:24px auto;padding:0 16px}
 .card{background:#fff;border-radius:8px;padding:18px 20px;margin-bottom:16px;box-shadow:0 1px 3px rgba(0,0,0,.08)}
 h2{color:#1f3864;margin-top:0;font-size:20px}
 table{width:100%;border-collapse:collapse} td,th{border:1px solid #d1d5db;padding:8px;text-align:left}
 th{background:#e5eaf2} footer{text-align:center;color:#6b7280;font-size:13px;padding:20px}
</style>
</head>
<body>
<header>
 <h1>Agroprodel Ltda.</h1>
 <p>Producción de trigo y harinas · Temuco · Talca · Concepción · Los Ángeles</p>
</header>
<main>
 <div class="card">
  <h2>Quiénes somos</h2>
  <p>Empresa dedicada a la siembra de trigo, cosecha y producción de harina, con presencia en cuatro ciudades del país y proyección exportadora.</p>
 </div>
 <div class="card">
  <h2>Productos</h2>
  <table>
   <tr><th>Producto</th><th>Formato</th></tr>
   <tr><td>Harina de trigo panadera</td><td>25 kg / 50 kg</td></tr>
   <tr><td>Harina de trigo especial</td><td>1 kg / 25 kg</td></tr>
   <tr><td>Trigo en grano</td><td>A granel</td></tr>
  </table>
 </div>
 <div class="card">
  <h2>Contacto</h2>
  <p>Mesa central con IVR: opción 1 Temuco · 2 Talca · 3 Concepción · 4 Los Ángeles</p>
 </div>
</main>
<footer>Servicio WEB alojado en la nube (AWS) · Servidor srv-agroprodel</footer>
</body>
</html>
EOF
```
Publicación de la página definitiva (subida con WinSCP a /home/ubuntu):
```bash
sudo cp /home/ubuntu/index.html /var/www/html/index.html
```

## 3. DNS (BIND9)
```bash
sudo apt update
sudo apt -y install bind9 bind9utils dnsutils
sudo systemctl enable --now named
systemctl status named --no-pager
```
Solo IPv4 y recursión restringida:
```bash
sudo sed -i 's/^OPTIONS=.*/OPTIONS="-u bind -4"/' /etc/default/named

sudo tee /etc/bind/named.conf.options > /dev/null <<'EOF'
acl "red-agroprodel" {
    127.0.0.1;
    10.40.0.0/16;        // VPC en la nube
    192.168.0.0/16;      // sedes (VLSM 192.168.10/20/30/40)
    186.189.96.148;      // IP publica de salida del laboratorio
};

options {
    directory "/var/cache/bind";
    listen-on { any; };
    listen-on-v6 { none; };

    allow-query { any; };                 // la zona agroprodel.cl se responde a todos
    recursion yes;
    allow-recursion { red-agroprodel; };  // solo la empresa resuelve otros dominios
    forwarders { 1.1.1.1; 8.8.8.8; };

    dnssec-validation auto;
    version "no disponible";
};
EOF

sudo named-checkconf && echo "CONFIGURACION OK"
```
Zona `agroprodel.cl`:
```bash
sudo tee -a /etc/bind/named.conf.local > /dev/null <<'EOF'

zone "agroprodel.cl" {
    type master;
    file "/etc/bind/db.agroprodel.cl";
    allow-transfer { none; };
};
EOF

sudo tee /etc/bind/db.agroprodel.cl > /dev/null <<'EOF'
$TTL 3600
@       IN  SOA ns1.agroprodel.cl. admin.agroprodel.cl. (
                2026111401  ; serial (AAAAMMDDnn)
                3600        ; refresh
                900         ; retry
                1209600     ; expire
                300 )       ; TTL negativo
        IN  NS  ns1.agroprodel.cl.

; ---- Servidor en la nube (AWS, IP elastica) ----
@       IN  A     54.236.126.16
ns1     IN  A     54.236.126.16
www     IN  CNAME agroprodel.cl.
ftp     IN  A     54.236.126.16

; ---- IP privada del servidor en la VPC (para la VPN futura) ----
srv-nube IN A     10.40.1.10
EOF

sudo named-checkzone agroprodel.cl /etc/bind/db.agroprodel.cl
sudo systemctl restart named && systemctl is-active named
```
Script para autorizar la recursión desde una IP pública (casa, Duoc):
```bash
sudo tee /usr/local/bin/permitir-mi-ip > /dev/null <<'EOF'
#!/bin/bash
# Uso: sudo permitir-mi-ip <IP>   (agrega la IP a la lista red-agroprodel del DNS)
IP="$1"
[[ "$IP" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]] || { echo "Uso: sudo permitir-mi-ip <IP>"; exit 1; }
F=/etc/bind/named.conf.options
grep -q "    $IP;" "$F" && { echo "La IP $IP ya estaba permitida"; exit 0; }
cp "$F" "$F.bak"
sed -i "0,/^};/s||    $IP;   // agregada $(date +%F)\n};|" "$F"
if named-checkconf && rndc reload >/dev/null; then echo "IP $IP permitida en el DNS"; else cp "$F.bak" "$F"; echo "Error: se restauro la configuracion"; fi
EOF
sudo chmod +x /usr/local/bin/permitir-mi-ip
sudo permitir-mi-ip $(echo $SSH_CLIENT | cut -d' ' -f1)
```
Uso posterior:
```bash
sudo permitir-mi-ip 181.42.142.12
```

## 4. HTTPS (Let's Encrypt)
```bash
sudo apt update
sudo apt install -y certbot python3-certbot-nginx
sudo sed -i 's/server_name _;/server_name agroprodel-ltda.duckdns.org;/' /etc/nginx/sites-available/default
sudo nginx -t
sudo systemctl reload nginx
grep server_name /etc/nginx/sites-available/default
sudo certbot --nginx -d agroprodel-ltda.duckdns.org --redirect
sudo certbot renew --dry-run
```

## 5. FTPS (vsftpd)
```bash
sudo apt install -y vsftpd
sudo adduser ftpagro
sudo mkdir -p /home/ftpagro/ftp/archivos
sudo chown root:root /home/ftpagro/ftp
sudo chmod 755 /home/ftpagro/ftp
sudo chown ftpagro:ftpagro /home/ftpagro/ftp/archivos
echo "ftpagro" | sudo tee /etc/vsftpd.userlist
sudo cp /etc/vsftpd.conf /etc/vsftpd.conf.original
```
Configuración:
```bash
sudo tee /etc/vsftpd.conf > /dev/null <<'EOF'
# --- vsftpd Agroprodel: FTPS (FTP sobre TLS) ---
listen=YES
listen_ipv6=NO
anonymous_enable=NO
local_enable=YES
write_enable=YES
local_umask=022
# Jaula: cada usuario queda encerrado en /home/USUARIO/ftp
chroot_local_user=YES
user_sub_token=$USER
local_root=/home/$USER/ftp
# Solo los usuarios de la lista blanca
userlist_enable=YES
userlist_file=/etc/vsftpd.userlist
userlist_deny=NO
# Modo pasivo (NAT de AWS y del cliente)
pasv_enable=YES
pasv_min_port=30000
pasv_max_port=30100
pasv_address=54.236.126.16
# Cifrado TLS obligatorio con el certificado de Let's Encrypt
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
# Registro de transferencias y mensajes
xferlog_enable=YES
xferlog_std_format=YES
ftpd_banner=Agroprodel Ltda. - Servicio FTP seguro. Acceso solo autorizado.
pam_service_name=vsftpd
EOF
```
```bash
sudo systemctl restart vsftpd
sudo systemctl status vsftpd --no-pager | head -5
sudo ss -tlnp | grep :21
```
Cambio a FTPS implícito en el puerto 990 (P-07):
```bash
echo -e "listen_port=990\nimplicit_ssl=YES" | sudo tee -a /etc/vsftpd.conf
sudo systemctl restart vsftpd
sudo ss -tlnp | grep vsftpd
openssl s_client -connect localhost:990 -brief </dev/null
```
Diagnóstico temporal (registro de comandos FTP) y su retiro (P-08):
```bash
echo -e "log_ftp_protocol=YES\ndual_log_enable=YES\nvsftpd_log_file=/var/log/vsftpd.log" | sudo tee -a /etc/vsftpd.conf
sudo systemctl restart vsftpd
sudo grep -E "STOR|UPLOAD" /var/log/vsftpd.log | tail -6
sudo sed -i '/^log_ftp_protocol=YES/d;/^dual_log_enable=YES/d;/^vsftpd_log_file=/d' /etc/vsftpd.conf
sudo systemctl restart vsftpd
sudo systemctl is-active vsftpd
tail -4 /etc/vsftpd.conf
```
