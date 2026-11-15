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
