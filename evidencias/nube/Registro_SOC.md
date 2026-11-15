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

Se monitorea por la IP de la VLAN 99 (gestión): pertenece a 192.168.0.0/16, por lo que el tráfico viaja cifrado
en la VPN, y la ACL `SNMP-NOC` del router solo acepta consultas de 10.40.1.30. Se mantiene marcada la opción de
solicitudes combinadas (varias OID por paquete) para reducir tráfico por la VPN.
| S-07 | R-TALCA: `% Invalid input detected` en `snmp-server user ...` y `show snmp user` vacío | Al reemplazar las claves en la plantilla del comando se borró el espacio entre la clave de autenticación y la palabra `priv`; IOS no reconoce la línea y el usuario no se crea (el resto del bloque sí se aplica) | Se reingresó la línea con los espacios correctos; `show snmp user` muestra `zabbix` (SHA/AES128, GRP-NOC) |
