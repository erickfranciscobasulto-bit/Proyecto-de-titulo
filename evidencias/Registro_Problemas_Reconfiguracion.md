# Registro de problemas – Reconfiguración con VLSM nuevo

Proyecto Agroprodel Ltda. · Fase 2 (implementación)

Cada entrada indica el equipo, el síntoma, la causa técnica, la solución aplicada y cómo se verificó.

---

## P-01 · DIST-TEMUCO sin salida a Internet desde la VLAN de gestión

| Campo | Detalle |
|---|---|
| **Equipo** | DIST-TEMUCO (IOL L2) |
| **Síntoma** | Desde el switch, `ping 192.168.40.241` (gateway VLAN 99) responde, pero `ping 8.8.8.8` falla. |
| **Diagnóstico** | `show ip route` muestra una tabla de enrutamiento con `Gateway of last resort is not set` en lugar de `Default gateway is 192.168.40.241`. |
| **Causa** | La imagen IOL L2 trae `ip routing` activo por defecto. Con el enrutamiento activo, el switch ignora el comando `ip default-gateway` y solo usa su tabla de rutas, donde no existía una ruta por defecto. |
| **Solución** | Se agregó una ruta estática por defecto hacia el gateway de la VLAN 99: `ip route 0.0.0.0 0.0.0.0 192.168.40.241` (se mantiene también `ip default-gateway`). |
| **Verificación** | `ping 8.8.8.8` responde desde DIST-TEMUCO. |
| **Prevención** | El mismo ajuste se incluye en todos los switches IOL de la red (ACC1/ACC2 de Temuco y DIST/ACC de las sucursales). |

---

## P-02 · Ping fallido desde DIST-TALCA (error de digitación)

| Campo | Detalle |
|---|---|
| **Equipo** | DIST-TALCA (IOL L2) |
| **Síntoma** | El ping al gateway de gestión falla de forma repetida (0/5). |
| **Diagnóstico** | Vlan99 y e0/0 up/up; CDP confirma el cable hacia R-TALCA e0/1; la subinterfaz e0/1.99 del router tiene dot1Q 99 y 192.168.10.193/28; el troncal tiene la VLAN 99 en forwarding; duplex Full. `show arp` muestra 192.168.10.193 resuelta con la MAC del router. |
| **Causa** | El ping se escribió hacia 192.169.10.193 en lugar de 192.168.10.193. |
| **Solución** | Repetir el ping con la IP correcta: exitoso. |
| **Aprendizaje** | Si la IP del gateway aparece en la tabla ARP, la capa 2 funciona; el problema está en capa 3 o en el comando. |

---

## P-03 · Mensajes NATIVE_VLAN_MISMATCH en los puertos del puente (comportamiento esperado)

| Campo | Detalle |
|---|---|
| **Equipos** | SW-PUENTE (e0/1, e0/2) y DIST-CONCEPCION (e2/2, e2/3) |
| **Síntoma** | `%CDP-4-NATIVE_VLAN_MISMATCH: ... Ethernet0/1 (210), with DIST-CONCEPCION Ethernet2/2 (10)` y lo mismo para 250/50. |
| **Causa** | CDP informa la VLAN de acceso de cada extremo. En estos puertos la diferencia es **intencional**: es la traducción de VLAN 210→10 y 250→50 que permite que los equipos físicos operen como Concepción. |
| **Impacto** | Ninguno; el tráfico funciona. Solo genera mensajes en la consola. |
| **Solución (opcional)** | `no cdp enable` en SW-PUENTE e0/1-2 y DIST-CONCEPCION e2/2-3 para limpiar los logs. |

---

## P-04 · option 150 aplicada en un pool DHCP nuevo y vacío

| Campo | Detalle |
|---|---|
| **Equipo** | R-TEMUCO |
| **Síntoma** | Tras agregar `option 150`, `show ip dhcp pool V50-VOZ-TEM` indica *Total addresses 0* y *0 subnet is currently in the pool*. |
| **Diagnóstico** | `show running-config \| section dhcp` muestra que los pools reales del router se llaman **VLAN10-SIEMBRA-TEM … VLAN70-IOT-TEM** (el de voz es **VLAN50-VOZ-TEM**, con su red y gateway correctos). El comando `ip dhcp pool V50-VOZ-TEM` no editó ese pool: **creó uno nuevo**, vacío, que solo contenía la option 150. |
| **Causa** | Diferencia entre el nombre de pool de la guía (V50-…) y el usado al configurar el equipo (VLAN50-…). En IOS, `ip dhcp pool <nombre>` crea el pool si el nombre no existe, sin advertencia. |
| **Solución** | `no ip dhcp pool V50-VOZ-TEM` y agregar `option 150 ip 192.168.40.226` dentro de `ip dhcp pool VLAN50-VOZ-TEM`. |
| **Verificación** | `show running-config \| section VLAN50-VOZ-TEM` incluye network, default-router, dns-server y option 150. |
| **Aprendizaje** | Antes de modificar un pool, confirmar su nombre exacto con `show ip dhcp pool` o `show running-config \| section dhcp`. La documentación del equipo se actualizó con los nombres reales. |

---

## P-05 · SSH sin cifrado en común con los switches de acceso de Concepción

| Campo | Detalle |
|---|---|
| **Equipos** | ACC1-CONCEPCION y ACC2-CONCEPCION |
| **Síntoma** | Desde R-CONCEPCION, `ssh -l admin 192.168.20.163` termina con *Connection aborted* y el log muestra `%SSH-3-NO_MATCH: No matching cipher found: client aes128-ctr,... server aes128-cbc,3des-cbc,...`. |
| **Diagnóstico** | `show running-config` indica `version 15.1`: estos dos nodos usan una imagen IOL más antigua que el resto (15.2). Esa versión solo ofrece cifrados CBC y no acepta `ip ssh server algorithm encryption`. |
| **Solución** | Conectar indicando un cifrado CBC desde el cliente: `ssh -c aes256-cbc -l admin 192.168.20.163` (y .164). |
| **Recomendación** | Actualizar ambos nodos a IOS 15.2 o superior para usar AES-CTR, igual que el resto de la red. 3DES-CBC se considera obsoleto. |

---

## P-06 · Bucle de capa 2 en ACC2-CONCEPCION tras reiniciar el EtherChannel

| Campo | Detalle |
|---|---|
| **Equipos** | ACC2-CONCEPCION (IOS 15.1), ACC1-CONCEPCION, DIST-CONCEPCION |
| **Origen** | Se corrigió un `%CDP-4-DUPLEX_MISMATCH` aplicando `duplex full` en e0/0-3 de ACC1 y ACC2 (la imagen 15.1 había quedado en `duplex auto`). Los EtherChannel se reiniciaron. |
| **Síntoma** | Los PC de ACC2 (VLAN 10, 30 y 40) no obtienen IP. `debug ip dhcp server packet` en R-CONCEPCION muestra DISCOVER recibido y OFFER enviado, pero el cliente sigue enviando DISCOVER. |
| **Diagnóstico** | DIST aprende la MAC del PC en Po2 (correcto), pero ACC2 la aprende en **Et0/3** (miembro de Po3). `show interfaces` en ACC2: Et0/2 y Et0/3 reciben ~30 000 pps y Po2 transmite ~15 000 pps hacia DIST. `show spanning-tree vlan 30` indica Po3 *Altn BLK* y Po2 *Root FWD*: el plano de control está bien, pero los miembros de Po3 seguían reenviando tráfico como puertos sueltos. |
| **Causa** | Falla de la imagen IOL 15.1 al reconstruir el Port-channel: el bloqueo de spanning tree no se aplicó a los puertos miembros, formando el bucle DIST → Po1 → ACC1 → Po3 → ACC2 → Po2 → DIST. |
| **Solución** | `shutdown` en e0/2-3 de ACC2 (corta el bucle: Po2 baja de 15 135 a 347 pps y los tres PC obtienen IP); luego `no shutdown` con `load-interval 30`. Po3 vuelve como *Altn BLK* con ~127 pps de entrada (tráfico normal descartado). |
| **Verificación** | `show etherchannel summary` Po2(SU) y Po3(SU); `show spanning-tree vlan 30` Po3 Altn BLK; tasas de entrada/salida normales; DHCP funcionando en los tres PC. |
| **Recurrencia** | Minutos después de reactivar Po3 el bucle volvió (Po3 ~3 500 pps de entrada y Po2 la misma tasa de salida; MAC de los PC aprendidas también en la VLAN nativa 999). Persistió tras `reload` de ACC2 y con `duplex auto` en ACC1 y ACC2 (hipótesis de duplex descartada). La imagen 15.1 además no conserva `duplex full` tras reiniciar. |
| **Causa confirmada** | La imagen IOL 15.1 de ACC2-CONCEPCION no aplica el estado *Alternate/BLK* de RSTP a los puertos miembros de un Port-channel: reenvía hacia Po2 lo que recibe por Po3. Los equipos con 15.2 no presentan la falla. |
| **Solución temporal** | `shutdown` en e0/2-3 de ACC2 (Po3), `duplex full` en ACC1/ACC2, `clear mac address-table dynamic` en DIST, ACC1 y ACC2. Resultado: los tres PC obtienen IP y llegan a internet. Se pierde temporalmente la redundancia ACC1–ACC2. |
| **Solución definitiva** | Cambiar la imagen de ACC1 y ACC2 de Concepción a la misma IOL 15.2 del resto de los switches y reactivar Po3 vigilando las tasas. Resuelve también P-05 (SSH con AES-CTR). |
| **Aprendizaje** | Un enlace bloqueado por STP que muestra miles de pps de entrada y MAC aprendidas en un puerto miembro indica un bucle en el plano de datos. Cortar primero el enlace redundante, verificar, descartar hipótesis una a una (reinicio, duplex) y, si la causa es el software, estandarizar la versión de IOS en toda la red. |


## P-09 – Caída simultánea de las adyacencias OSPFv2/OSPFv3 en R-TEMUCO (evento del laboratorio)

**Síntoma.** En el log de R-TEMUCO, a las 17:35:08 y a las 18:20:30 (hora UTC del router; 14:35 y 15:20 en Chile),
las 6 adyacencias (OSPFv2 y OSPFv3 con 2.2.2.2, 3.3.3.3 y 4.4.4.4 por Tunnel1-3) pasan a DOWN por
*Dead timer expired* en el mismo milisegundo y vuelven a FULL entre 35 y 65 ms después.

**Análisis.**
- Si un túnel o un enlace hubiese fallado, solo caerían los vecinos de ese túnel y la recuperación tomaría al menos
  un intervalo de hello (10 s) más el intercambio de bases de datos.
- Aquí caen los 6 vecinos a la vez, en los tres túneles y en ambas versiones de OSPF, y se recuperan en milisegundos.
  Ese patrón corresponde a que el proceso del router dejó de ejecutarse durante más de 40 s (dead interval): al
  reanudarse vence el temporizador de todos los vecinos y, de inmediato, procesa los hellos en cola y vuelve a FULL.
- La causa es del host de virtualización (EVE-NG sobre el notebook: suspensión, ahorro de energía o falta de CPU),
  no de la configuración de red.

**Verificación.** `show ip ospf neighbor` y `show ipv6 ospf neighbor`: 3 vecinos FULL en cada versión.

**Acción.** Desactivar la suspensión y el ahorro de energía del notebook que ejecuta EVE-NG durante las pruebas.
Este tipo de evento queda visible en Zabbix como una pérdida de datos simultánea en los 4 routers.

**Recurrencia detectada por el SOC (20:28:36 UTC / 17:28 Chile).** Grafana (fuente Zabbix) mostró para R-TEMUCO la
latencia ICMP en 0 ms entre las 17:19 y las 17:27 (sin respuesta desde AWS). El log del router registra a las 20:28:36 UTC
la misma firma de P-09: las 6 adyacencias OSPFv2/OSPFv3 caen por *Dead timer expired* y vuelven a FULL en ~100 ms.
Conclusión: el router estuvo detenido unos 9 minutos y, al reanudarse, vencieron todos los temporizadores. Además,
`show ip sla statistics 10` indica 43 ejecuciones (40 OK, 3 fallos) desde su creación a las 18:02 UTC, cuando a una
frecuencia de 30 s correspondían cerca de 300: el proceso del router pasó gran parte de ese tiempo sin ejecutarse.
El hueco sin datos entre 16:48 y 16:54 no coincide con eventos en el router y queda pendiente de revisar en el log de
Zabbix server.

**Acción correctiva propuesta.** En el notebook Arch que ejecuta EVE-NG, impedir la suspensión durante las pruebas:
`sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target` (reversible con `unmask`),
y desactivar el bloqueo y el ahorro de energía de la pantalla.

**Valor para el proyecto.** El evento fue detectado desde el SOC en la nube (Zabbix + Grafana) y su causa se confirmó
correlacionando la métrica con el log del equipo, sin intervención en la sede.


## P-10 – ACC2-CONCEPCION se apaga al encenderlo (NVRAM dañada) y migración a IOS 15.2

**Síntoma.** Tras reiniciar el host EVE-NG, el nodo ACC2-CONCEPCION (IOL 15.1a) se detiene a los 3 s de encenderlo.
El resto de los IOL arranca con normalidad (incluido ACC1-CONCEPCION, con la misma imagen).

**Diagnóstico.**
1. `unl_wrapper -a fixpermissions`: sin cambios.
2. `/opt/unetlab/tmp/0/<lab>/17/wrapper.txt`: `Error while connecting local AF_UNIX: Connection refused` y
   `Cannot listen at AF_UNIX (272)`; el envoltorio de EVE no logra conectarse porque el proceso IOL ya terminó.
3. Se descartan memoria (10 GiB libres), permisos, procesos o sockets residuales (`pgrep` y `ps`: ninguno) e imagen
   (ACC1-CONCEPCION arranca con la misma).
4. La diferencia es el archivo de configuración guardada `nvram_00272` (fecha 14-11 19:31). Se respaldó en
   `/root/nvram_00272_ACC2-CONCEPCION.bak` y se apartó (`nvram_00272.old`): el nodo arranca y permanece encendido.
   **Causa: NVRAM dañada.**

**Solución.** Se aprovechó la reconstrucción para migrar el nodo a `i86bi_Linux-L2-AdvEnterpriseK9-M_152_May_2018.bin`
(IOS 15.2), pendiente desde P-05/P-06, y se restauró la configuración desde `ACC2-CONCEPCION.txt` en 4 bloques
(VLAN y STP · enlaces, puertos y gestión · seguridad y RA Guard · SNMPv3).

**Incidencias durante la restauración.**
- Po2 quedó *suspended* en ambos extremos y `show lacp neighbor` vacío: los puertos se configuraron con
  DIST-CONCEPCION apagado. Con dúplex verificado (Full en los 4 puertos), un `shutdown`/`no shutdown` en ambos
  extremos formó el canal: LACP con DIST (`aabb.cc80.e000`) por Et0/0 y Et0/1 y ping al gateway 5/5.
- Error en el archivo de configuración: el `shutdown` temporal del Po3 (P-06) estaba antes de un `no shutdown` en el
  mismo bloque, por lo que al restaurar se habría reactivado el bucle. Se corrigió el orden.
- `%AMDP2_FE-6-EXCESSCOLL` en puertos sin equipo conectado (artefacto del emulador con 15.2): Et2/0-3 se apagaron
  como puertos sin uso; Et1/3 (AP) se mantiene habilitado según el diseño.

**Resultado.** ACC2-CONCEPCION con IOS 15.2: SSH con AES-CTR (resuelve P-05 en este equipo), RA Guard aplicado en
Et1/0-3 (7 de 8 switches de acceso), SNMPv3 activo y configuración guardada. Po3 se mantiene apagado hasta migrar
ACC1-CONCEPCION (aún 15.1).

**Acción aplicada (15-11-2026, 20:40).** En el notebook Arch con EVE-NG:
`sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target` → `Loaded: masked`, más la
suspensión y el apagado de pantalla del escritorio en "Nunca". Al terminar el proyecto se revierte con
`systemctl unmask` sobre las mismas unidades.


## Cierre de P-05 y P-06 – Migración de ACC1-CONCEPCION a IOS 15.2 y reactivación del Po3 (16-11-2026)

1. ACC1-CONCEPCION: `write memory`, cambio de imagen en EVE-NG a `i86bi_Linux-L2-AdvEnterpriseK9-M_152_May_2018.bin`.
   La 15.2 cargó la NVRAM escrita por la 15.1 (hostname, IP de gestión y SNMPv3 intactos). Al guardar, IOS advierte
   *NVRAM configuration previously written by a different version* y se confirma.
2. Po1 hacia DIST en *suspended*: los puertos habían perdido `duplex full` con la 15.1 (origen del aviso
   CDP-4-DUPLEX_MISMATCH y de P-06). Se aplicó `duplex full` en Et0/0-3 y `shutdown`/`no shutdown` en ambos extremos:
   Po1(SU) y ping al gateway 5/5.
3. RA Guard (`RA-GUARD-USUARIOS`) en Et1/0-2 → **8 de 8 switches de acceso con RA Guard**. Puertos sin uso
   Et1/3 y Et2/0-3 apagados. Ubicación SNMP corregida a "Concepcion - Acceso 1".
4. Po3 (ACC1 ↔ ACC2) reactivado: `no shutdown` en ACC2 Et0/2-3 y reinicio de puertos en ambos extremos.
   Resultado: **Po3(SU)** con Et0/2(P) Et0/3(P); Rapid-PVST deja Po2 *Root FWD* y Po3 *Altn BLK* (enlace redundante en
   reserva, sin bucle); ping al gateway 20/20.

**Causa raíz de P-06 confirmada:** la imagen IOL 15.1 no conservaba `duplex full` en los miembros del EtherChannel; con
puertos en half duplex LACP no agrupa correctamente y el enlace redundante generaba el bucle. Con ambos extremos en 15.2 y
full duplex, el Po3 opera como respaldo normal. P-05 (SSH solo CBC) también queda resuelto en los dos equipos.

---

## P-11 · R-CONCEPCION sin las ACL IPv4 entre VLAN en la configuración activa (16-11-2026)

| Campo | Detalle |
|---|---|
| **Equipo** | R-CONCEPCION |
| **Síntoma** | Durante la prueba de telefonía con ACL, `show access-lists DEPTOS-IN` no devolvía nada aunque la llamada 3001 → IVR → 1001 funcionaba. |
| **Diagnóstico** | `show ip access-lists` listaba GESTION-SSH, NAT-CONCEPCION, SNMP-NOC, INVITADOS-IN, VOZ-RTP y VOZ-SIP, pero **no** DEPTOS-IN, VOZ-IN ni IOT-IN. `DEPTOS-IN-V6` sí estaba cargada y con tráfico. |
| **Causa** | El bloque de ACL IPv4 entre VLAN de `R-CONCEPCION.txt` no quedó en la configuración guardada del router (no se aplicó o se perdió en un reinicio del nodo sin `write memory`). Las VLAN 10-50 y 70 operaban sin filtrado. |
| **Solución** | Se reaplicó el bloque desde `R-CONCEPCION.txt` (ACL DEPTOS-IN, VOZ-IN, IOT-IN y sus `ip access-group ... in` en Et0/1.10-.50 y .70) y `write memory` [OK]. |
| **Verificación** | `show ip interface ethernet 0/1.10 \| include access list` → *Inbound access list is DEPTOS-IN*. Prueba positiva (llamada) y negativa (ping a 192.168.10.65 bloqueado) documentadas en `telefonia/Registro_Telefonia.md`. Revisión en las otras 3 sedes: `show running-config \| include interface\|access-group` en R-TEMUCO, R-TALCA y R-LOS-ANGELES muestra DEPTOS-IN en .10-.40, VOZ-IN en .50, INVITADOS-IN en .60 e IOT-IN en .70: **segmentación activa en las 4 sedes**. |
| **Aprendizaje** | Verificar el estado real del equipo (`show ip access-lists`, `show ip interface`) y no solo el archivo de configuración; terminar cada cambio con `write memory`. |

---

## P-12 · ACC1-CONCEPCION sin gestión: SNMP en rojo en Zabbix por LACP suspendido (16-11-2026)

| Campo | Detalle |
|---|---|
| **Equipo** | ACC1-CONCEPCION · DIST-CONCEPCION |
| **Síntoma** | Zabbix muestra SNMP en rojo para ACC1-CONCEPCION (y ACC2). En ACC1 aparece `%AMDP2_FE-6-EXCESSCOLL: Ethernet0/3`. |
| **Diagnóstico** | `show snmp user` y `show snmp engineID`: usuario `zabbix` correcto y engine ID coincidente (se descarta SNMP). `show ip interface brief \| include Vlan99`: **down/down** (no *administratively down*). `show etherchannel summary`: **Po1(SD)** y **Po3(SD)** con todos los puertos `(s)` suspendidos; `show interfaces trunk` vacío. En DIST-CONCEPCION también Po1 y Po2 en (SD); `show cdp neighbors` solo ve a R-CONCEPCION y `show lacp neighbor` sale vacío. Configuración de ambos extremos correcta (full duplex, troncal nativa 999, `channel-group 1 mode active`) y enlaces presentes en el lienzo de EVE-NG (Status up, Protocol down). |
| **Causa** | LACP trabado en IOL tras los cambios del día (misma firma que el cierre de P-05/P-06). Sin troncal activo la VLAN 99 no tiene salida, la SVI queda down/down y SRV-NOC no alcanza al switch. La ausencia de CDP era consecuencia del protocolo down, no de un enlace roto. |
| **Solución** | `shutdown` en ACC1 Et0/0-1 → `shutdown`/`no shutdown` en DIST Et0/1-2 → `no shutdown` en ACC1 Et0/0-1, para que ambos extremos renegocien LACP a la vez. `write memory` en ambos equipos. |
| **Verificación** | Po1(SU), Vlan99 up/up, ping a 10.40.1.30 desde la VLAN 99 exitoso y SNMP en verde en Zabbix. |
| **Aprendizaje** | En una SVI, down/down indica que ningún puerto activo lleva la VLAN: revisar troncales y EtherChannel antes que la propia interfaz VLAN. |

---

## P-13 · ACC2-CONCEPCION rechaza la contraseña de consola (16-11-2026)

| Campo | Detalle |
|---|---|
| **Equipo** | ACC2-CONCEPCION |
| **Síntoma** | La consola rechaza la clave del usuario local; la misma clave funciona al instante en otros switches desde la misma consola (se descarta teclado). SNMP en rojo en Zabbix. |
| **Causa** | Credenciales del equipo distintas a las documentadas tras la reconstrucción de P-10 (clave mal ingresada o NVRAM nuevamente dañada). IOL no permite recuperación de contraseña por ROMMON. |
| **Solución** | En EVE-NG: Stop → **Wipe** → Start con IOS 15.2 (`i86bi_Linux-L2-AdvEnterpriseK9-M_152_May_2018.bin`, *signature verified*). Se reaplicó `ACC2-CONCEPCION.txt` en 6 bloques (base y VLAN, EtherChannel, acceso y gestión, seguridad, RA Guard, SNMPv3), con las claves ingresadas a mano. Antes de `write memory` la clave se validó por SSH desde DIST-CONCEPCION. |
| **Verificación** | Po2 y Po3 operativos, `show snmp user` con `zabbix` (SHA/AES128, GRP-NOC), ping a SRV-NOC desde la VLAN 99 y SNMP en verde en Zabbix. |
| **Aprendizaje** | Probar el acceso con la clave nueva (SSH desde otro equipo) antes de guardar y cerrar la sesión de consola. |
