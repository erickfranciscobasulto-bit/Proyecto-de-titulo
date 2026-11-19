# Registro de implementación – Telefonía IP

Proyecto Agroprodel Ltda. · Fase 2 (implementación)

## Arquitectura

- **Central:** Issabel (Asterisk) en VM VirtualBox, servidor centralizado en Temuco (requerimiento del enunciado).
- **IP del servidor:** 192.168.40.226/28 · gateway 192.168.40.225 (VLAN 80 Servidores) · conectado a SW-FISICO-TEM Fa0/3.
- **Plan de numeración:** 1xxx Temuco · 2xxx Talca · 3xxx Concepción · 4xxx Los Ángeles.
- **IVR previsto:** 1 → 1001 (asistente Temuco) · 2 → 2001 (Talca) · 3 → 3001 (Concepción) · 4 → 4001 (Los Ángeles).

## Terminales

> **Softphones en el laboratorio vs. teléfonos en la empresa real.** El equipo contaba con un solo teléfono IP físico
> (Cisco CP-8861), por lo que las pruebas entre sedes se realizaron con softphones (MicroSIP). Un softphone usa el mismo
> protocolo SIP y recorre la misma ruta de red que un teléfono físico (VLAN de la sede → router → túnel GRE/IPsec →
> Issabel), de modo que valida el enrutamiento, los túneles, la QoS, las ACL y el IVR. La implementación real considera
> **10 teléfonos Cisco CP-7841 (firmware 3PCC, SIP) por sede**, alimentados por PoE en la VLAN de voz 50, con el PC
> conectado detrás del teléfono. Los softphones quedan como complemento para teletrabajo o usuarios móviles.

| Extensión | Sede | Terminal | Tecnología | Red / puerto |
|---|---|---|---|---|
| 1001 | Temuco | MicroSIP (PC con Issabel) | PJSIP | Host 192.168.40.232 (VLAN 80), Issabel 192.168.40.226 |
| 2001 (prueba inicial) | Talca | Teléfono físico Cisco CP-8861 (MAC 7802.B142.A521, SEP7802B142A521) | PJSIP | SW-FISICO-TEM Fa0/5, VLAN de voz 50 (192.168.40.178–.190) |
| 3001 | Concepción | MicroSIP (segundo PC) | PJSIP | SW-FISICO-TEM Fa0/2, VLAN 210 → VLAN 10 de Concepción (DHCP R-CONCEPCION, 192.168.20.2). Registra en Issabel a través del túnel GRE/IPsec; llamadas Temuco ↔ Concepción verificadas |
| 2001 | Talca | MicroSIP (tercer PC) | PJSIP | SW-FISICO-TEM Fa0/6, VLAN 220 → VLAN 10 de Talca por SW-PUENTE e0/3 ↔ DIST-TALCA e2/2 (DHCP R-TALCA, 192.168.10.66). Llamada Talca ↔ Concepción verificada (pasa por Temuco); captura Wireshark en R-TEMUCO e0/0: ESP 282 bytes con DSCP EF |
| 4001 | Los Ángeles | MicroSIP (cuarto PC) | PJSIP | SW-FISICO-TEM Fa0/7, VLAN 230 → VLAN 10 de Los Ángeles por SW-PUENTE e1/1 ↔ DIST-LOS-ANGELES e2/2 (DHCP R-LOS-ANGELES, 192.168.30.34–.46). Llamadas entre las 4 sedes verificadas |

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

### Paso 7 – Cierre del CP-8861
El CP-8861 se utilizó para validar el aprovisionamiento de un teléfono físico Cisco por TFTP (pasos 1 a 6). No queda en
la configuración final: compartía la extensión 2001 con el softphone de Talca y, tras el aprovisionamiento, operaba en la
VLAN 10 (T-04). Las pruebas de la plataforma se realizan con los softphones MicroSIP de las 4 sedes.

## Prueba del IVR y de las ACL entre VLAN (16-11-2026)

Llamada: **3001 (Concepción) → IVR → opción 1 → 1001 (Temuco)**, contestada. Se mide en R-CONCEPCION porque el PC de
Concepción está en su VLAN 10 (ACL `DEPTOS-IN`); el softphone de Temuco está en la VLAN 80, la misma red de Issabel, por
lo que su tráfico no cruza ninguna ACL del router.

**Hallazgo previo:** R-CONCEPCION no tenía cargadas las ACL IPv4 `DEPTOS-IN`, `VOZ-IN` e `IOT-IN` (ver P-11). Se
reaplicaron desde `R-CONCEPCION.txt` y se guardaron; `show ip interface ethernet 0/1.10 | include access list` →
*Inbound access list is DEPTOS-IN*.

### Prueba positiva (la voz pasa con la segmentación activa)
```
clear ip access-list counters DEPTOS-IN
show access-lists DEPTOS-IN        ! antes
! llamada 3001 -> IVR -> 1 -> 1001
show access-lists DEPTOS-IN        ! despues
```

| Línea de DEPTOS-IN | Antes | Después | Interpretación |
|---|---|---|---|
| 20 `permit ip any 192.168.40.224 0.0.0.15` (Issabel, VLAN 80) | 1 | **1978** | Señalización SIP y audio RTP de la llamada (G.711 ≈ 50 paquetes/s) |
| 30 `deny ip any 192.168.0.0 0.0.255.255 log` | 0 | **0** | No se bloqueó ningún paquete de la llamada |
| 60 `permit ip any any` | 83 | 579 | Tráfico del PC hacia Internet y la nube, ajeno a la llamada |

En Issabel (`asterisk -rvvv`) se observa el paso por el IVR, el dígito 1 y el `Dial(PJSIP/1001...)` contestado; al
colgar se ejecuta `macro-hangupcall` (los avisos `exited non-zero` al cortar son normales).

**Conclusión:** la voz entre sedes funciona con la política de mínimo privilegio activa. `DEPTOS-IN` impide que la
VLAN 10 de Concepción alcance otras redes internas, pero el audio se ancla en Issabel, el único destino interno
permitido.

### Prueba negativa (la ACL bloquea lo que debe bloquear)
Ping desde el PC de Concepción a `192.168.10.65` (gateway de la VLAN 10 de Talca): **falla**. La línea 30 de
`DEPTOS-IN` registra el bloqueo (`%SEC-6-IPACCESSLOGDP ... denied icmp`).

### Registros observados en R-CONCEPCION
`%SEC-6-IPACCESSLOGP: list DEPTOS-IN denied udp 192.168.20.2(137) -> 192.168.20.31(137)`, cada ~5 minutos.
Corresponde a NetBIOS (UDP 137) del PC hacia el *broadcast* de su propia VLAN (192.168.20.0/27). El broadcast llega a
los demás equipos de la VLAN por capa 2; solo se descarta la copia que recibe el router. Es tráfico esperado (ruido
conocido): IOS registra el primer paquete y luego un resumen cada 5 minutos.

## Punto único de falla
La telefonía está centralizada en la matriz (requisito del enunciado), por lo que Issabel es un punto único de falla: si
el servidor pierde la red se cortan las llamadas en curso (el audio pasa por la central), no se pueden realizar llamadas
nuevas ni usar el IVR, y los softphones pierden su registro. Datos, Internet, túneles, VPN y monitoreo no se ven
afectados. Mitigación en producción: servidor físico con UPS, enlace redundante al switch y, en un diseño mayor,
central de respaldo o supervivencia local en las sucursales.

## Equipo físico de integración
El Catalyst 2960 (SW-FISICO-TEM) se utilizó durante la implementación para integrar los equipos físicos (Issabel,
teléfono CP-8861 y PC con softphones) al laboratorio EVE-NG. Cumplida su función, se restableció a fábrica
(`write erase` + `delete flash:vlan.dat`); su última configuración se conserva en
`configuraciones/SW-FISICO-2960.txt`. Las pruebas de telefonía quedaron registradas en video y capturas.
