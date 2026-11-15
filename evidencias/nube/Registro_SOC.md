# SOC en la nube (AWS) – Registro de implementación

## Arquitectura
| Servidor | Función | Herramientas | Instancia | IP privada |
|---|---|---|---|---|
| SRV-AGROPRODEL (existente) | Servicios | Nginx (HTTPS), BIND, vsftpd (FTPS) | t3.micro | 10.40.1.10 |
| SRV-NOC | Disponibilidad, visualización y concentrador VPN | Zabbix, Grafana, strongSwan | t3.small | 10.40.1.30 |
| SRV-SIEM | Seguridad | Wazuh (manager, indexer, dashboard) | t3.large | 10.40.1.20 |

Suricata (IDS) se habilita en OPNsense (FW-TEMUCO), que ya inspecciona el tráfico hacia Internet.

**Por qué en la nube:** el monitoreo queda fuera de la infraestructura que supervisa; si una sede (incluida la
casa matriz) falla, el SOC sigue operando y alerta la caída.

**Por qué VPN propia (strongSwan) y no Site-to-Site VPN administrada de AWS:** el laboratorio sale a Internet con
IP dinámica (red doméstica y red de Duoc). La VPN administrada exige registrar una IP pública fija del cliente
(Customer Gateway); con strongSwan, R-TEMUCO inicia el túnel IPsec (NAT-T) desde cualquier red y se autentica
con clave compartida.

## Grupos de seguridad
### SG_SOC_NOC (SRV-NOC) – sg-009f0cbc448d25185
| Tipo | Puerto | Origen | Descripción |
|---|---|---|---|
| UDP | 500 | 0.0.0.0/0 | VPN IKE |
| UDP | 4500 | 0.0.0.0/0 | VPN IPsec NAT-T |
| SSH | 22 | IP pública de cada administrador /32 | Administración |
| HTTP | 80 | IP del administrador /32 | Zabbix web |
| TCP | 3000 | IP del administrador /32 | Grafana |
| Todo | Todos | 10.40.0.0/16 | Tráfico interno de la VPC |

UDP 500/4500 se abren a cualquier origen porque el extremo del laboratorio cambia de IP; el túnel exige clave
compartida y cifrado, sin los cuales la negociación se rechaza.

### SG_SOC_SIEM (SRV-SIEM) – sg-04301cb151e77d101
| Tipo | Puerto | Origen | Descripción |
|---|---|---|---|
| UDP | 514 | 192.168.0.0/16 | Syslog de routers y switches (por la VPN) |
| TCP | 1514-1515 | 192.168.0.0/16 | Agentes Wazuh de las sedes |
| HTTPS | 443 | IP del administrador /32 | Panel de Wazuh |
| HTTPS | 443 | 192.168.40.224/27 | Panel de Wazuh desde VLAN 80/99 de Temuco (por la VPN) |
| SSH | 22 | IP pública de cada administrador /32 | Administración |
| Todo | Todos | 10.40.0.0/16 | Tráfico interno de la VPC |

El SIEM no expone ningún puerto a Internet.

## Instancias
### SRV-NOC
| Dato | Valor |
|---|---|
| ID | i-0149582ee2a3b6e88 |
| Tipo / SO | t3.small (2 vCPU, 2 GiB) · Ubuntu Server 24.04 LTS |
| Red | VPC_AGROPRODEL-vpc · subnet-03f4cc1647d14719c (pública 10.40.1.0/24) · IP privada 10.40.1.30 |
| Grupo de seguridad | SG_SOC_NOC |
| Disco | 20 GiB gp3 |
| Perfil IAM / créditos | LabInstanceProfile · standard |
| Llave | LLAVE-NOC (exclusiva del servidor; no se documenta) |
| IP elástica | 98.83.92.138 (eipalloc-0a80a0ba5323a9f9a): extremo fijo de la VPN para R-TEMUCO |

## Enrutamiento en la VPC
- SRV-NOC: *source/destination check* desactivado (reenvía tráfico entre la VPN y la VPC).
- Tabla `VPC_AGROPRODEL-rtb-public` (rtb-009819cc49bbdfa36), asociada a subnet-03f4cc1647d14719c:

| Destino | Destino siguiente | Uso |
|---|---|---|
| 10.40.0.0/16 | local | Tráfico interno de la VPC |
| 0.0.0.0/0 | igw-0038a87052752e964 | Internet |
| 192.168.0.0/16 | eni-0d88fe11da28b32a8 (SRV-NOC) | Redes de las 4 sedes, a través de la VPN |

## VPN sitio a sitio R-TEMUCO ↔ SRV-NOC
| Parámetro | Valor |
|---|---|
| Protocolo | IKEv2 + IPsec ESP modo túnel, NAT-T (UDP 4500) |
| IKE | AES-CBC-256 / SHA-256 / DH grupo 14 (MODP 2048) |
| ESP | AES-256 / SHA-256, PFS grupo 14 |
| Autenticación | Clave compartida (no se documenta) |
| Identidades | R-TEMUCO: FQDN `r-temuco.agroprodel.cl` · SRV-NOC: `98.83.92.138` |
| Extremo AWS | strongSwan (swanctl) en SRV-NOC, acepta el par desde `%any` (IP del laboratorio dinámica) |
| Extremo sede | Crypto map `CM-AWS` en Ethernet0/0 de R-TEMUCO, ACL `VPN-AWS` |
| Tráfico protegido | 192.168.0.0/16 (sedes) ↔ 10.40.0.0/16 (VPC) |
| Exención de NAT | ACL `NAT-TEMUCO-EXT` (deny hacia 10.40.0.0/16 antes del permit) |
| DPD | 30 s (ambos extremos) |

Ambos extremos están detrás de NAT (R-TEMUCO tras el router del laboratorio, SRV-NOC tras el NAT 1:1 de la
IP elástica), por lo que la negociación pasa automáticamente a UDP 4500.

### Prueba
`ping 10.40.1.30 source 192.168.40.241 repeat 10` desde R-TEMUCO: 9/10 (el primer paquete se pierde mientras
se negocia el túnel), RTT 138/190/207 ms.

Captura en SRV-NOC (`tcpdump -ni any 'udp port 500 or udp port 4500'`): los ICMP viajan como
`UDP-encap: ESP` con un SPI por sentido; se observan `isakmp-nat-keep-alive` (~20 s) e intercambios
INFORMATIONAL de DPD (30 s). No aparece tráfico ICMP en claro.

### Acceso de las otras sedes
R-TEMUCO tiene una ruta estática 10.40.0.0/16 hacia su salida a Internet y la redistribuye en OSPF
(route-map `RM-AWS` con prefix-list `PL-AWS`, solo esa red). Las sedes la reciben como `O E2` por su túnel
GRE/IPsec hacia Temuco, y desde ahí el tráfico entra a la VPN de AWS (la ACL `VPN-AWS` cubre 192.168.0.0/16).
Las redes de usuarios no alcanzan la VPC: `DEPTOS-IN` e `IOT-IN` bloquean 10.0.0.0/8 (solo equipos de red
y gestión llegan al SOC).

| Origen | Prueba | Resultado |
|---|---|---|
| R-TALCA (VLAN 99, 192.168.10.193) | ping 10.40.1.30 ×100 | 100/100, RTT 138/197/229 ms |
| R-CONCEPCION (VLAN 99, 192.168.20.161) | ping 10.40.1.30 ×10 | Exitoso |
| R-LOS-ANGELES (VLAN 99, 192.168.30.129) | ping 10.40.1.30 ×10 | Exitoso |

### Errores encontrados
| N° | Síntoma | Causa | Solución |
|---|---|---|---|
| S-01 | Al instalar strongSwan quedaron activos `strongswan-starter` y `charon-systemd` | El paquete habilita los dos servicios; compiten por UDP 500/4500 | `systemctl disable --now strongswan-starter`; se verificó con `ss -ulnp` que solo charon escucha |
| S-02 | `swanctl` sin sudo muestra *Permission denied* y avisos `plugin ... failed to load` | El socket VICI requiere root; los plugins listados no están instalados y no se usan | Ejecutar con `sudo`; los avisos de plugins son informativos |
| S-03 | Clave compartida expuesta durante la configuración | Se mostró en pantalla al revisar el archivo | Se generó una clave nueva, se cargó con `swanctl --load-creds` y se guardó fuera del repositorio |
| S-04 | Ping 0/10, `show crypto ikev2 sa` vacío; en SRV-NOC: `tried 1 shared key ... but MAC mismatched` → `AUTH_FAILED` | IKE_SA_INIT correcto (propuesta y NAT-T aceptados) pero la clave del keyring `KR-AWS` en R-TEMUCO no coincidía con la de strongSwan tras la rotación | Se reingresó la clave en `crypto ikev2 keyring KR-AWS / peer SRV-NOC`; túnel arriba, ping 9/10 |
| S-05 | Conteo de tablas de la base `zabbix` = 0; `ls /usr/share/zabbix/sql-scripts/mysql/server.sql.gz`: *No such file* | Se usó la ruta del esquema de otra versión de la documentación; en el paquete instalado el archivo está en `/usr/share/zabbix-sql-scripts/mysql/` | Se ubicó con `dpkg -L zabbix-sql-scripts \| grep server.sql`, se reactivó `log_bin_trust_function_creators` y se cargó el esquema: 203 tablas |
| S-06 | `snmpget` desde SRV-NOC a 192.168.40.241: *Timeout*; `ping` desde SRV-NOC: 100 % pérdida; `show snmp`: 0 paquetes de entrada; `swanctl --list-sas` vacío | strongSwan acepta al par desde `%any` (IP del laboratorio dinámica), por lo que AWS no puede iniciar el túnel; tras un periodo sin tráfico desde Temuco las SA se cerraron y SRV-NOC quedó sin camino hacia las sedes | Se confirmó levantando el túnel con un ping desde R-TEMUCO (luego SRV-NOC respondió 4/4). Solución permanente: sonda IP SLA en R-TEMUCO que envía un ICMP a SRV-NOC cada 30 s desde la VLAN 99 y mantiene la VPN activa |

## Zabbix – equipos monitoreados
| Equipo | Interfaz | Plantilla | Grupo | Resultado |
|---|---|---|---|---|
| Zabbix server (SRV-NOC) | Agente 127.0.0.1:10050 | Linux by Zabbix agent, Zabbix server health | Zabbix servers | ZBX verde |
| R-TEMUCO (Casa Matriz) | SNMPv3 authPriv (SHA1/AES128, usuario `zabbix`) 192.168.40.241:161 por la VPN | Cisco IOS by SNMP | Routers Agroprodel | SNMP verde · 180 métricas · 78 iniciadores · 19 gráficos (descubrimiento de interfaces y túneles) |
| R-TALCA (Sucursal) | SNMPv3 authPriv 192.168.10.193:161 (túnel Talca–Temuco + VPN AWS) | Cisco IOS by SNMP | Routers Agroprodel | SNMP verde · 153 métricas · 66 iniciadores · 16 gráficos. Creado clonando R-TEMUCO |
| R-CONCEPCION (Sucursal) | SNMPv3 authPriv 192.168.20.161:161 (túnel Concepción–Temuco + VPN AWS) | Cisco IOS by SNMP | Routers Agroprodel | SNMP verde. Creado clonando R-TALCA |
| R-LOS-ANGELES (Sucursal) | SNMPv3 authPriv 192.168.30.129:161 (túnel Los Ángeles–Temuco + VPN AWS) | Cisco IOS by SNMP | Routers Agroprodel | SNMP verde. Creado clonando R-TALCA |

Se monitorea por la IP de la VLAN 99 (gestión): pertenece a 192.168.0.0/16, por lo que el tráfico viaja cifrado
en la VPN, y la ACL `SNMP-NOC` del router solo acepta consultas de 10.40.1.30. Los 4 routers quedaron en verde: todo el
monitoreo de las sucursales recorre su túnel GRE/IPsec hasta Temuco y luego la VPN hacia AWS. Se mantiene marcada la opción de
solicitudes combinadas (varias OID por paquete) para reducir tráfico por la VPN.
| S-07 | R-TALCA: `% Invalid input detected` en `snmp-server user ...` y `show snmp user` vacío | Al reemplazar las claves en la plantilla del comando se borró el espacio entre la clave de autenticación y la palabra `priv`; IOS no reconoce la línea y el usuario no se crea (el resto del bloque sí se aplica) | Se reingresó la línea con los espacios correctos; `show snmp user` muestra `zabbix` (SHA/AES128, GRP-NOC) |

### Calibración de alertas
| Alerta | Situación | Ajuste |
|---|---|---|
| *Cisco IOS: High ICMP ping response time* (4 routers) | La plantilla alerta sobre 150 ms (`{$ICMP_RESPONSE_TIME_WARN}` = 0.15), valor pensado para una LAN. El SOC está en us-east-1 y consulta por la VPN: la línea base medida es ~140–290 ms (ping, IP SLA). Generaba falsos positivos permanentes | Macro a nivel de equipo `{$ICMP_RESPONSE_TIME_WARN}` = `0.4` en los 4 routers (modificación masiva). Se calibra sobre la línea base, sin desactivar la alerta, que sigue detectando degradación real de la VPN o de los túneles. Las 4 alertas pasaron a RESUELTO (16:04–16:07) |
| *Linux: Number of installed packages has been changed* (SRV-NOC) | Aviso informativo por la instalación del paquete `snmp` | Cambio esperado; se cierra manualmente |

## Switches monitoreados (importación masiva)
Credenciales SNMPv3 centralizadas en macros globales de Zabbix (Administración → Macros): `{$SNMPV3_USER}` (texto),
`{$SNMPV3_AUTH}` y `{$SNMPV3_PRIV}` (texto secreto: no se pueden leer desde la interfaz). Las interfaces SNMP de los
equipos referencian las macros, por lo que el archivo de importación no contiene claves y la rotación de credenciales
se hace en un solo lugar.

Archivo: `zabbix/switches_agroprodel.yaml` (Recopilación de datos → Equipos → Importar; reglas: crear nuevo y
modificar existentes, sin *eliminar faltante*). Grupo `Switches Agroprodel`, plantilla *Cisco IOS by SNMP*,
macro `{$ICMP_RESPONSE_TIME_WARN}` = 0.4.

| Sede | Distribución | Acceso 1 | Acceso 2 |
|---|---|---|---|
| Temuco | DIST-TEMUCO 192.168.40.242 | ACC1-TEMUCO .243 | ACC2-TEMUCO .244 |
| Talca | DIST-TALCA 192.168.10.194 | ACC1-TALCA .195 | ACC2-TALCA .196 |
| Concepción | DIST-CONCEPCION 192.168.20.162 | ACC1-CONCEPCION .163 | ACC2-CONCEPCION .164 |
| Los Ángeles | DIST-LOS-ANGELES 192.168.30.130 | ACC1-LOS-ANGELES .131 | ACC2-LOS-ANGELES .132 |

Resultado: 12 switches con SNMP verde (158 métricas y 68 iniciadores cada uno tras el descubrimiento de interfaces).
Total monitoreado: 17 equipos (4 routers, 12 switches, SRV-NOC). Pendientes: SW-FISICO-TEM (192.168.40.245, cuando
esté encendido), servidores, FW-TEMUCO e ISP (requieren ampliar el dominio de la VPN).

## Servidores monitoreados
| Equipo | Interfaz | Plantilla | Grupo | Resultado |
|---|---|---|---|---|
| SRV-AGROPRODEL (Web · DNS · FTPS) | Agente 2 en modo activo (`ServerActive=10.40.1.30`); interfaz de agente 10.40.1.10:10050 registrada | Linux by Zabbix agent active | Servidores Agroprodel | ZBX verde · 43 métricas · 15 iniciadores |

En modo activo el agente abre la conexión hacia SRV-NOC dentro de la VPC, por lo que no se agregan reglas de entrada en
el grupo de seguridad del servidor. Error de alta: el equipo se creó primero sin plantilla (sin métricas); se corrigió
editándolo y vinculando *Linux by Zabbix agent active*. El grupo `Servidores Agroprodel` se agregó con permiso de lectura
a `Grafana Lectura`.

## Acceso de Grafana a Zabbix (mínimo privilegio)
| Elemento | Configuración |
|---|---|
| Grupo de usuarios | `Grafana Lectura` · acceso a la interfaz web **deshabilitado** · permisos de equipo: `Routers Agroprodel` y `Zabbix servers` en **Lectura** (el resto: Ninguno) |
| Usuario | `grafana` (Grafana SOC) · rol **User role** (tipo Usuario, el más bajo) · acceso a la API activado · clave no documentada |
| Autenticación de Grafana | Token de API del usuario `grafana`, con fecha de expiración; revocable sin cambiar la clave del usuario. Token no documentado |

Grafana solo puede consultar métricas y problemas de los 5 equipos; no puede modificar configuración ni ver otros grupos.
Primer intento de crear el grupo: se guardó sin permisos de equipo (Grafana no habría visto ningún equipo); se corrigió
agregando los dos grupos en Lectura.

### Alertas de seguridad generadas por la instalación de Grafana
| Alerta (SRV-NOC) | Causa | Cierre |
|---|---|---|
| *Linux: /etc/passwd has been changed* | El paquete grafana crea el usuario de sistema `grafana` | Reconocida y cerrada: "Usuario de sistema creado por instalacion de Grafana" |
| *Linux: Number of installed packages has been changed* | Instalación del paquete grafana | Reconocida y cerrada: "Cambio esperado: instalacion de Grafana" |

La misma alerta de `/etc/passwd` se generaría si un atacante creara una cuenta en el servidor; por eso cada evento se
revisa y se cierra con su justificación (trazabilidad del operador).

### Fuente de datos en Grafana
| Parámetro | Valor |
|---|---|
| Plugin | Zabbix (alexanderzobnin) 6.10.3 – aplicación habilitada; la fuente de datos viene incluida |
| Nombre | Zabbix SOC-AGROPRODEL |
| URL | `http://localhost/api_jsonrpc.php` (Grafana y Zabbix en el mismo servidor: la consulta no sale a la red; Zabbix se publica en la raíz del sitio Nginx, sin `/zabbix/`) |
| Autenticación | Tipo API token (usuario `grafana`, solo lectura) · HTTP: sin autenticación |
| Conexión directa a la BD | Desactivada (solo API) |
| Prueba | *Save & test*: **Zabbix API version 7.0.32** |

Nota: la página del plugin muestra dos tarjetas "Zabbix" (aplicación y fuente de datos); la fuente de datos se crea desde
Connections → Add new connection → Data Sources → Zabbix → *Add new data source*.

## Dashboard del SOC en Grafana (implementado)
Archivo importable: `grafana/SOC_Agroprodel_dashboard.json` (UID `agroprodel-soc`, versión 4). Se importa en
Dashboards → New → Import, seleccionando la fuente *Zabbix SOC-AGROPRODEL*.

| Sección | Panel | Consulta Zabbix |
|---|---|---|
| Indicadores | Sedes operativas (x / 4) | `ICMP ping` de los 4 routers con `sumSeries()` |
| Indicadores | VPN Temuco ↔ AWS (ACTIVA / CAÍDA) | `ICMP ping` de R-TEMUCO (si el SOC alcanza la VLAN 99 de Temuco, el túnel está arriba) |
| Indicadores | Disponibilidad por sede (periodo) | Promedio de `ICMP ping` (1/0) en el rango seleccionado |
| Disponibilidad | Línea de tiempo de estado | `ICMP ping` de los 4 routers |
| Rendimiento | Latencia SOC → sedes (umbral 400 ms) | `ICMP response time` |
| Rendimiento | CPU de los routers | `CPU utilization` (descubrimiento) |
| Rendimiento | Tráfico WAN R-TEMUCO | `Interface Et0/0: Bits received/sent` |
| Rendimiento | Tráfico por túnel | `Interface Tu1-3: Bits received` en R-TEMUCO |
| Eventos | Problemas actuales | Panel *Zabbix Problems* |

Primera lectura (últimas 6 h): 4/4 sedes, VPN activa, latencia media 132–170 ms (máx. 389 ms, bajo el umbral),
disponibilidad 89,8–92,5 %. La disponibilidad refleja las pausas del host EVE-NG (P-09): la línea de tiempo muestra
en rojo, en las 4 sedes a la vez, la detención de R-TEMUCO de 17:19 a 17:27 (las sucursales se monitorean a través
del hub de Temuco, por lo que su caída deja sin visibilidad al resto). CPU de los routers IOL ≈ 0 %.

## Diseño del dashboard (Grafana)
Maqueta aprobada: `Diseno_Dashboard_SOC.html` (valores simulados a partir de las mediciones del laboratorio).
Secciones: indicadores de servicio (disponibilidad 30 d vs SLA 99,5 %, sedes operativas, VPN, latencia media,
problemas abiertos, MTTR) · topología lógica en vivo (AWS → VPN → Temuco → túneles) · mapa de sedes ·
línea de tiempo de estado · latencia, uso de enlaces, voz EF, CPU/RAM, servidores en la nube · registro de eventos.
Pestañas previstas: Resumen ejecutivo, Red WAN, Sedes, Seguridad (Wazuh), IDS (Suricata).
| S-08 | `grafana-cli plugins install ...`: *Grafana-server Init Failed: Could not find config defaults, make sure homepath ... is set* | En Grafana 13 `grafana-cli` está obsoleto y no encuentra la carpeta de instalación por sí solo | `sudo grafana cli --homepath /usr/share/grafana plugins install alexanderzobnin-zabbix-app` y reinicio del servicio: plugin v6.10.3 instalado |
| S-09 | Zabbix: *No se pudo agregar el usuario – no debe contener el nombre, apellido o código de usuario* | La política de contraseñas de Zabbix rechaza claves que incluyan el usuario o el nombre (`grafana`, `soc`) | Se eligió una clave sin esas palabras; usuario creado |
| S-10 | Dashboard importado: paneles con triángulo rojo y *No data* (salvo los que no usaban funciones de alias) | Las funciones de alias del plugin Zabbix (`setAliasByRegex`, `setAlias`) agregadas a las consultas fallan en la versión 6.10.3 del plugin con Grafana 13 | Se eliminaron las funciones de alias de las consultas y los nombres cortos (Temuco, Talca, Concepción, Los Ángeles, Tunnel1 · Talca…) se aplican con *overrides* de Grafana por expresión regular sobre el nombre de la serie. Dashboard v4 operativo |
| S-11 | Tras importar los switches, ACC2-CONCEPCION en rojo: *Authentication failure (incorrect password, community or key)*; los otros 11 en verde | La clave del usuario SNMPv3 quedó mal escrita al reconstruir el switch (P-10). Se confirmó con `snmpget` desde SRV-NOC: mismo error con las claves que funcionan en el resto | `no snmp-server user zabbix GRP-NOC v3` y nueva línea `snmp-server user` con las claves correctas; SNMP verde |
| S-12 | Dashboard: "Equipos de red en línea" 4/16 y disponibilidad de la red 21,7 %; el estado por equipo solo mostraba routers | (1) El grupo `Switches Agroprodel` se creó al importar los switches y el grupo de usuarios `Grafana Lectura` no tenía permiso sobre él. (2) Tras otorgarlo, el plugin seguía usando la lista de grupos en caché (*Cache TTL* = 1 h) | Permiso de lectura sobre `Switches Agroprodel` en `Grafana Lectura`; *Cache TTL* de la fuente de datos reducido a 5 min y *Save & test* (reinicia la caché). Resultado: 16/16, disponibilidad de la red 96,8 % |
