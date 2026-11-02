# Registro de implementación – Telefonía IP

Proyecto Agroprodel Ltda. · Fase 2 (implementación)

## Arquitectura

- **Central:** Issabel (Asterisk) en VM VirtualBox, servidor centralizado en Temuco (requerimiento del enunciado).
- **IP del servidor:** 192.168.40.226/28 · gateway 192.168.40.225 (VLAN 80 Servidores) · conectado a SW-FISICO-TEM Fa0/3.
- **Plan de numeración:** 1xxx Temuco · 2xxx Talca · 3xxx Concepción · 4xxx Los Ángeles.
- **IVR previsto:** 1 → 1001 (asistente Temuco) · 2 → 2001 (Talca) · 3 → 3001 (Concepción) · 4 → 4001 (Los Ángeles).

## Terminales

| Extensión | Sede | Terminal | Tecnología | Red / puerto |
|---|---|---|---|---|
| 1001 | Temuco | MicroSIP (PC con Issabel) | PJSIP | 192.168.40.230 (VLAN 80) |
| 2001 | Talca | Teléfono físico Cisco CP-8861 (MAC 7802.B142.A521, SEP7802B142A521) | PJSIP | SW-FISICO-TEM Fa0/5, VLAN de voz 50 (192.168.40.178–.190) |

## Conexión física del teléfono CP-8861

1. Inyector PoE 3Com conectado a la corriente (LED POWER verde).
2. Switch Fa0/5 → puerto **"To Hub/Switch"** del inyector (solo datos).
3. Puerto **"To Network Jack"** del inyector → puerto de **red** del teléfono (datos + PoE).
4. Puerto de **PC** del teléfono disponible para un equipo detrás del teléfono (VLAN 10).

### Verificación realizada

- Fa0/5 up/up (el puerto baja y sube una vez durante el arranque del teléfono: normal).
- `show cdp neighbors` → **SEP7802B142A521** en Fa0/5, plataforma IP Phone.
- `show mac address-table interface fa0/5` → MAC del teléfono en **VLAN 50** (también en VLAN 10 por el primer paquete antes de aprender la VLAN de voz por CDP).
- El teléfono obtuvo IP por DHCP de R-TEMUCO (pool V50-VOZ-TEM) y responde ping.

## Registro del CP-8861 en Issabel (firmware Enterprise → aprovisionamiento por TFTP)

El CP-8861-K9 no se configura desde pantalla ni web: al arrancar descarga `SEP<MAC>.cnf.xml` desde el servidor TFTP indicado por la **opción DHCP 150**.

### Paso 1 – Extensión 2001 en Issabel ✅
- PBX → PBX Configuration → Extensions → 2001 · tecnología **PJSIP** · secret anotado.

### Paso 2 – Servidor TFTP en Issabel (en curso)

**T-01 · `yum install` falla con error 403.** El repositorio `mirror.issabel.org` rechaza la descarga (Status code 403). No es un problema de red (la VM tiene salida a Internet). Se verificó que no hacía falta instalar nada:

```
rpm -q tftp-server xinetd    # tftp-server-5.2-26.el8 y xinetd-2.3.15-25.el8 ya instalados
ls -ld /tftpboot             # drwxrwxrwx root root /tftpboot (existe)
head -2 /etc/os-release      # Rocky Linux 8.8 (Issabel 5)
```

Comandos previstos originalmente (no necesarios en esta instalación):
```
yum install -y tftp-server xinetd
sed -i 's/disable.*= yes/disable = no/' /etc/xinetd.d/tftp
mkdir -p /tftpboot
systemctl enable xinetd
systemctl restart xinetd
systemctl status xinetd      # active (running)
```

`cat /etc/xinetd.d/tftp` → `server = /usr/sbin/in.tftpd`, `server_args = -s -vv /tftpboot`, `disable = no`: el TFTP de Issabel ya viene habilitado y sirve la carpeta /tftpboot.

```
systemctl enable --now xinetd
ss -ulnp | grep :69          # UNCONN 0.0.0.0:69 users:(("xinetd",pid=775,fd=5))
```
✅ Paso 2 completado: TFTP escuchando en UDP 69.

### Paso 3 – Archivo de configuración del teléfono (SEP7802B142A521.cnf.xml)
Extensión 2001 (Talca) · servidor de registro 192.168.40.226 · DSCP de audio 184 (EF) · la clave se reemplaza por el secret de la extensión (no se documenta).
```
cat > /tftpboot/SEP7802B142A521.cnf.xml <<'XML'
<device>
<fullConfig>true</fullConfig>
<deviceProtocol>SIP</deviceProtocol>
<devicePool>
<dateTimeSetting>
<dateTemplate>D/M/Ya</dateTemplate>
<timeZone>Pacific SA Standard/Daylight Time</timeZone>
</dateTimeSetting>
<callManagerGroup>
<members>
<member priority="0">
<callManager>
<ports>
<ethernetPhonePort>2000</ethernetPhonePort>
<sipPort>5060</sipPort>
</ports>
<processNodeName>192.168.40.226</processNodeName>
</callManager>
</member>
</members>
</callManagerGroup>
</devicePool>
<sipProfile>
<sipProxies>
<registerWithProxy>true</registerWithProxy>
</sipProxies>
<preferredCodec>g711ulaw</preferredCodec>
<phoneLabel>TALCA</phoneLabel>
<sipLines>
<line button="1">
<featureID>9</featureID>
<featureLabel>2001</featureLabel>
<proxy>USECALLMANAGER</proxy>
<port>5060</port>
<name>2001</name>
<displayName>Asistente Talca</displayName>
<authName>2001</authName>
<authPassword>********</authPassword>
<contact>2001</contact>
</line>
</sipLines>
<voipControlPort>5060</voipControlPort>
<dscpForAudio>184</dscpForAudio>
</sipProfile>
<transportLayerProtocol>2</transportLayerProtocol>
</device>
XML
chmod 644 /tftpboot/SEP7802B142A521.cnf.xml
```

Acceso al servidor para pegar el archivo: `ssh root@192.168.40.226` desde el PC anfitrión (el usuario "issabel" no existe → *Permission denied*; no era el firewall).
Verificación: `grep authPassword /tftpboot/SEP7802B142A521.cnf.xml` coincide con el secret de la extensión 2001 en Issabel. ✅ Paso 3 completado.

### Paso 4 – Opción DHCP 150 en R-TEMUCO (servidor TFTP para teléfonos Cisco)
```
configure terminal
ip dhcp pool V50-VOZ-TEM
 option 150 ip 192.168.40.226
 exit
end
write memory
```
