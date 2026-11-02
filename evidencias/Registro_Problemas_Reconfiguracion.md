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
