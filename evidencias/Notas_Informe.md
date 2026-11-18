# Notas para el informe final (redacción técnica)

## Principio de mínimo privilegio (segmentación con ACL)
El mínimo privilegio (ISO/IEC 27001, NIST SP 800-53 AC-6) consiste en otorgar a cada segmento exactamente el
acceso que necesita para su función, y nada más.

| | Máximo privilegio | Mínimo privilegio (aplicado) |
|---|---|---|
| PC de Ventas | Alcanza todo: otros departamentos, switches, IoT y teléfonos | Solo Internet, la nube y los servidores (Issabel) |
| Equipo infectado con malware | Se propaga a toda la empresa | Queda contenido en su VLAN |
| Intento de acceso a un switch | Posible | Bloqueado y registrado (`DEPTOS-IN denied`) |

Beneficios: contención de incidentes, menor superficie de ataque, sin impacto en la operación y trazabilidad.

Redacción sugerida: *"Se aplicó el principio de mínimo privilegio: cada VLAN accede únicamente a los recursos
necesarios para su función. Si un equipo se ve comprometido, el incidente queda contenido en su segmento y no se
propaga al resto de la empresa. La política se implementó por igual en IPv4 (DEPTOS-IN, VOZ-IN, IOT-IN,
INVITADOS-IN) e IPv6 (DEPTOS-IN-V6)."*

## SLAAC (IPv6)
Autoconfiguración sin estado: el router anuncia el prefijo (Router Advertisement) y cada equipo completa su
dirección. Se usa en las VLAN de usuarios; servidores y gestión usan direcciones estáticas
(`ipv6 nd prefix ... no-autoconfig`). Evidencia: PC de Talca con `2001:db8:a9:210:2050:79ff:fe66:6823/64`.

## IoT de riego
Prototipo ESP32 con sensor de humedad del suelo y temperatura; activa el riego bajo el umbral, lo detiene al
alcanzar la humedad objetivo y notifica por Telegram. En laboratorio se conecta por Wi-Fi directo; en producción se
integra a la VLAN 70 mediante un AP, con la ACL IOT-IN (solo Internet).

## Telefonía: 10 teléfonos por sede
Plataforma validada con un terminal por sede; las 40 extensiones se habilitan en Issabel por CSV. Red dimensionada:
VLAN 50 /28 (14 hosts) y LLQ de 1 Mbps (≈10 llamadas G.711 simultáneas).

## Reserva de crecimiento de Temuco
192.168.41.0/24, contigua a 192.168.40.0/24 (resumen 192.168.40.0/23). Se usa agregando subinterfaces, pools y
VLAN nuevas, sin renumerar lo existente.

## IPv6 y costos
Equipos y licencias con soporte nativo (sin costo). Prefijo entregado por cada ISP (opción B, sin costo según
antecedentes públicos; confirmar en cotización). Única partida: 10 h de ingeniería.

## Diseño: modelo de arquitectura y documentación por vistas
Archivo: `diseno/Topologia_Antes_Despues_Agroprodel.drawio` (draw.io, íconos Cisco 2019). 5 páginas:
AS-IS · arquitectura general (TO-BE) · enrutamiento OSPF · LAN Temuco · LAN sucursales.

- **Modelo de Arquitectura Empresarial Cisco (Enterprise Composite):** divide la red en módulos que calzan con
  la empresa: Enterprise Campus (Temuco), Enterprise Edge (R-TEMUCO + FW-TEMUCO), Service Provider Edge
  (ISP, proveedor VoIP, PSTN), Enterprise Data Center (sala de servidores + AWS) y Enterprise Branch (sucursales).
- **Jerárquico de 2 capas (núcleo colapsado):** en sedes de este tamaño, núcleo y distribución se unen en un
  solo switch sin perder escalabilidad; un núcleo separado se justifica en campus grandes con varios edificios.
- **Por qué un diagrama por vista:** cada uno responde una pregunta (cómo se organiza, cómo se enruta, cómo se
  conectan los usuarios) y sirve a un público distinto (gerencia / operación). Es la práctica de las guías de
  diseño validadas de Cisco (CVD): vista general por módulos + detalle de capa 2 y capa 3.
- **AS-IS:** el enunciado no describe la red existente; la situación inicial es una deducción razonable
  (sedes aisladas, red plana, switches en cascada, telefonía analógica, sin nube ni IoT).
- **Metodología de diseño:** Top-Down de Cisco (requisitos del negocio → diseño lógico → diseño físico →
  pruebas → documentación), gestionada con Scrum (sprints alineados a las 3 fases del proyecto).

## Cantidad de switches de acceso por sede
Criterio: usuarios + 4 puertos (AP, controlador IoT, 2 impresoras), con margen de crecimiento ≥ 20 %.

| Sede | Puertos necesarios | Switches de acceso | Puertos | Libres |
|---|---|---|---|---|
| Temuco | 88 + 4 = 92 | 48 + 48 + 24 | 120 | 28 (30 %) |
| Talca | 76 + 4 = 80 | 48 + 48 | 96 | 16 (20 %) |
| Concepción | 51 + 4 = 55 | 48 + 24 | 72 | 17 (31 %) |
| Los Ángeles | 31 + 4 = 35 | 24 + 24 | 48 | 13 (37 %) |

Temuco lleva un tercer switch porque con 2 × 48 quedarían 4 puertos libres y no cubriría los 102 puntos de
cableado presupuestados. En el laboratorio (EVE-NG) se simularon 2 switches de acceso por sede por límite de RAM.
La familia Catalyst 2960 está fuera de venta (2960-X: último pedido 31-10-2022); el equipamiento real
presupuestado es Catalyst 9200L, reemplazo oficial indicado por Cisco.

## Sala de servidores (diseño real)
Clúster Proxmox VE de 2 nodos (HPE DL20 Gen11): si un nodo falla, sus VM se reinician en el otro.
VM: DC01 y DC02 (Active Directory, DNS interno, GPO), SRV-ISSABEL (central IP e IVR), SRV-ARCHIVOS,
SRV-IMPRESION. NAS Synology RS422+ con respaldo diario y réplica en Talca (copia fuera de sitio). 3 UPS.
Corresponde al escenario B del presupuesto.

## Telefonía: ahorro y respaldo
| | Antes | Ahora |
|---|---|---|
| Llamadas entre sedes | Larga distancia por PSTN (con costo) | Por los túneles GRE/IPsec: costo $0 |
| Llamadas a clientes | 4 grupos de líneas analógicas | Un troncal SIP centralizado en Temuco (menor tarifa, DID, canales escalables) |
| Atención | Cada sede por separado | IVR opciones 1-4 |
| Administración | 4 contratos y centrales | 1 central (Issabel) |

Respaldo: GW-FXO con 2 líneas analógicas en Temuco (si cae el troncal SIP o Internet) · ATA con línea
analógica de emergencia en cada sucursal (si cae el túnel) · Issabel en el clúster Proxmox con respaldo en NAS.
En el laboratorio se probaron llamadas internas entre sedes e IVR; troncal SIP y FXO son parte del diseño real.

## Enrutamiento: OSPF área única, sin BGP
- **OSPF proceso 1, área 0 única:** 4 routers en hub-and-spoke sobre los túneles (Tunnel1-3, 172.16.0.0/28);
  RID 1.1.1.1 a 4.4.4.4; LAN pasivas (vecindad solo por túneles); R-TEMUCO es ASBR y redistribuye
  10.40.0.0/16 (AWS) como externa E2; OSPFv3 para IPv6. Dividir en áreas se justifica en redes grandes
  (decenas de routers); con 4 routers un área es más simple y converge igual.
- **Hub-and-spoke:** telefonía y servidores están en Temuco; 3 túneles en vez de 6 (malla completa).
- **GRE + IPsec:** IPsec solo no transporta multicast; GRE sí (permite OSPF) e IPsec cifra con AES-256.
- **Sin BGP:** cada sede tiene un único enlace a Internet (single-homed); la salida se resuelve con una ruta
  por defecto estática. BGP solo se justifica con ASN y bloque público propio conectado a 2+ ISP
  (multihoming). El BGP lo opera el ISP dentro de su red, fuera de la responsabilidad de la empresa.

Redacción sugerida: *"Cada sede tiene un único enlace a Internet (single-homed), por lo que el enrutamiento
hacia Internet se resuelve con una ruta por defecto estática hacia el ISP. BGP no se justifica, ya que la
empresa no posee un sistema autónomo ni direccionamiento público propio; el enrutamiento interno entre sedes
se realiza con OSPF sobre los túneles."*

Evolución con segundo ISP o 4G en Temuco: ruta estática flotante con IP SLA (misma técnica del keepalive de
la VPN a AWS), sin necesidad de BGP.

## Riesgo principal y trabajo futuro
Temuco es punto único de falla (1 router, 1 firewall, 1 ISP) y concentra telefonía, túneles y VPN.
Mejoras: segundo router con HSRP y segundo ISP/4G, DIST en stack, 4G de respaldo en sucursales, firewall en
alta disponibilidad (CARP), IPS en modo bloqueo, 802.1X. SD-WAN / SD-Access como evolución futura
(requieren controladores y licencias).

## Cisco SAFE (seguridad por zonas)
Modelo de referencia de Cisco para diseñar la seguridad: qué se protege, de qué amenaza y con qué control.
Método: flujos del negocio → amenazas → capacidades → arquitectura.

| Dominio SAFE | Controles en Agroprodel |
|---|---|
| Gestión | SSH, SNMPv3 authPriv, VLAN 99, administración de AWS solo por VPN |
| Inteligencia de seguridad | Reglas ET Open (Suricata) |
| Cumplimiento | Syslog a Wazuh, regla 4721 (cambios de configuración), NTP |
| Segmentación | VLAN por departamento, ACL entre VLAN, invitados e IoT solo Internet |
| Defensa contra amenazas | Firewall, IDS Suricata, correlación de escaneos (100102), alertas a Telegram |
| Servicios seguros | IPsec AES-256, VPN IKEv2, HTTPS/FTPS, RA Guard, BPDU Guard |

Lugares de la red: Campus (Temuco) · Sucursales · Borde · WAN (túneles) · Data Center (sala de servidores) ·
Nube (AWS).
