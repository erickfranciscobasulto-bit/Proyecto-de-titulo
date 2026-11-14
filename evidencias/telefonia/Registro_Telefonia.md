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
| 3001 | Concepción | MicroSIP (segundo PC) | PJSIP | SW-FISICO-TEM Fa0/2, VLAN 210 → VLAN 10 de Concepción (DHCP R-CONCEPCION, 192.168.20.2). Registra en Issabel a través del túnel GRE/IPsec; llamadas Temuco ↔ Concepción verificadas |

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

### Paso 5 – Arranque del teléfono y descarga por TFTP

**T-02 · El teléfono no consultaba al TFTP de Issabel.** En el teléfono, *Servidor TFTP 1* estaba vacío (la option 150 no se aplicaba porque se había agregado a un pool nuevo y vacío, ver P-04). Se configuró manualmente **Servidor TFTP 1 = 192.168.40.226** (además de la option 150 en VLAN50-VOZ-TEM).

Resultado en `tail -f /var/log/messages | grep -i tftp`: el teléfono (192.168.40.178) ya consulta al TFTP y pide `ITLFile.tlv`, `SEP7802B142A521.cnf.xml.sgn`, `XMLDefault.cnf.xml.sgn`, `CTLSEP…tlv`, `ITLSEP…tlv`, `AppDialRules.xml` (todos *File not found*).

**T-03 · El teléfono solo pide archivos firmados (.sgn).** Pide la versión firmada `SEP…cnf.xml.sgn` y no la versión `.cnf.xml`: conserva una lista de confianza (ITL/CTL) de la central Cisco del laboratorio y está en modo seguro, por lo que rechaza configuraciones sin firma. Solución: restablecer la configuración de seguridad del teléfono (borrar la lista de confianza) para que acepte el archivo XML sin firma.

**Resultado tras restablecer la seguridad del teléfono (Admin Settings → Reset Settings → Security settings):**
```
RRQ from 192.168.40.178 filename SEP7802B142A521.cnf.xml
Client 192.168.40.178 finished SEP7802B142A521.cnf.xml      <- descarga exitosa
```
✅ El teléfono descargó su configuración sin firma. Los demás archivos (`ITLFile.tlv`, `CTLSEP…tlv`, `/sl-be-sip.jar`, `/g3-tones.xml`, `AppDialRules.xml`, `defaultheadsetconfig.json`) son opcionales; su *File not found* no impide el registro.

**T-04 · Tras aplicar la configuración el teléfono pasa a la IP 192.168.40.130 (VLAN 10).** Después de la descarga, las siguientes solicitudes provienen de 192.168.40.130, del pool de datos (VLAN 10) y no del de voz (VLAN 50). El teléfono dejó de usar la VLAN de voz, por lo que su tráfico se mezcla con los datos y no recibe la prioridad prevista. Pendiente: forzar la VLAN de voz en el teléfono (Admin VLAN ID = 50) o verificar que mantenga CDP activo.

### Paso 6 – Registro verificado ✅
```
asterisk -rx "pjsip show contacts"
Contact: 2001/sip:2001@192.168.40.130:5060;transport=udp   Avail   6.393 ms
```
El CP-8861 quedó registrado en Issabel como extensión **2001 (Talca)**; la pantalla muestra el menú de reposo (New call, Forward all, Redial).

### Paso 7 – Prueba de llamada 2001 ↔ 1001 (en curso)
