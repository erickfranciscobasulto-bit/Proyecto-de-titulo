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
