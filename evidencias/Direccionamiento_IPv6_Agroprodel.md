# Direccionamiento IPv6 – Agroprodel Ltda.

Plan verificado: 25 redes /64 sin solapamientos, cada sede contenida en su /56 y todo dentro del /48 corporativo.

## 1. Jerarquía
| Nivel | Prefijo | Capacidad |
|---|---|---|
| Empresa | `2001:db8:a9::/48` | 65 536 subredes /64 |
| Sede Temuco | `2001:db8:a9:100::/56` | 256 subredes /64 |
| Sede Talca | `2001:db8:a9:200::/56` | 256 subredes /64 |
| Sede Concepción | `2001:db8:a9:300::/56` | 256 subredes /64 |
| Sede Los Ángeles | `2001:db8:a9:400::/56` | 256 subredes /64 |
| Infraestructura (túneles y loopbacks) | `2001:db8:a9:f00::/56` | 256 subredes /64 |

**Por qué no hay VLSM en IPv6:** toda LAN usa /64. Es obligatorio para SLAAC (RFC 4862) y recomendado por RFC 7421; el ahorro de direcciones no aplica porque un /64 ofrece 18 trillones de direcciones. La jerarquía (/48 → /56 → /64) cumple el rol que en IPv4 cumple el VLSM: orden, crecimiento y resumen de rutas.

**Regla de lectura del 4.º bloque (S VV):** S = sede, VV = VLAN. Ej.: `2001:db8:a9:230::/64` → Talca, VLAN 30.

**Convención de hosts estáticos:** el identificador de interfaz repite el último octeto IPv4 (Issabel 192.168.40.226 → `::226`), lo que facilita la operación en doble pila.

## 2.1 Temuco – R-TEMUCO (router-id 1.1.1.1)
| VLAN | Uso | Prefijo | Gateway | Link-local GW | Asignación |
|---|---|---|---|---|---|
| 10 | Siembra y Riego | `2001:db8:a9:110::/64` | `2001:db8:a9:110::1` | `fe80::1` | SLAAC |
| 20 | Cosecha y Molienda | `2001:db8:a9:120::/64` | `2001:db8:a9:120::1` | `fe80::1` | SLAAC |
| 30 | Envasado y Bodega | `2001:db8:a9:130::/64` | `2001:db8:a9:130::1` | `fe80::1` | SLAAC |
| 40 | Ventas | `2001:db8:a9:140::/64` | `2001:db8:a9:140::1` | `fe80::1` | SLAAC |
| 80 | Servidores | `2001:db8:a9:180::/64` | `2001:db8:a9:180::1` | `fe80::1` | Estática |
| 99 | Gestión | `2001:db8:a9:199::/64` | `2001:db8:a9:199::1` | `fe80::1` | Estática |
| 50 / 60 / 70 | Voz / Invitados / IoT | — | — | — | Sin IPv6 (decisión de seguridad) |

## 2.2 Talca – R-TALCA (router-id 2.2.2.2)
| VLAN | Uso | Prefijo | Gateway | Link-local GW | Asignación |
|---|---|---|---|---|---|
| 10 | Siembra y Riego | `2001:db8:a9:210::/64` | `2001:db8:a9:210::1` | `fe80::1` | SLAAC |
| 20 | Cosecha y Molienda | `2001:db8:a9:220::/64` | `2001:db8:a9:220::1` | `fe80::1` | SLAAC |
| 30 | Envasado y Bodega | `2001:db8:a9:230::/64` | `2001:db8:a9:230::1` | `fe80::1` | SLAAC |
| 40 | Ventas | `2001:db8:a9:240::/64` | `2001:db8:a9:240::1` | `fe80::1` | SLAAC |
| 99 | Gestión | `2001:db8:a9:299::/64` | `2001:db8:a9:299::1` | `fe80::1` | Estática |
| 50 / 60 / 70 | Voz / Invitados / IoT | — | — | — | Sin IPv6 (decisión de seguridad) |

## 2.3 Concepción – R-CONCEPCION (router-id 3.3.3.3)
| VLAN | Uso | Prefijo | Gateway | Link-local GW | Asignación |
|---|---|---|---|---|---|
| 10 | Siembra y Riego | `2001:db8:a9:310::/64` | `2001:db8:a9:310::1` | `fe80::1` | SLAAC |
| 20 | Cosecha y Molienda | `2001:db8:a9:320::/64` | `2001:db8:a9:320::1` | `fe80::1` | SLAAC |
| 30 | Envasado y Bodega | `2001:db8:a9:330::/64` | `2001:db8:a9:330::1` | `fe80::1` | SLAAC |
| 40 | Ventas | `2001:db8:a9:340::/64` | `2001:db8:a9:340::1` | `fe80::1` | SLAAC |
| 99 | Gestión | `2001:db8:a9:399::/64` | `2001:db8:a9:399::1` | `fe80::1` | Estática |
| 50 / 60 / 70 | Voz / Invitados / IoT | — | — | — | Sin IPv6 (decisión de seguridad) |

## 2.4 Los Ángeles – R-LOS-ANGELES (router-id 4.4.4.4)
| VLAN | Uso | Prefijo | Gateway | Link-local GW | Asignación |
|---|---|---|---|---|---|
| 10 | Siembra y Riego | `2001:db8:a9:410::/64` | `2001:db8:a9:410::1` | `fe80::1` | SLAAC |
| 20 | Cosecha y Molienda | `2001:db8:a9:420::/64` | `2001:db8:a9:420::1` | `fe80::1` | SLAAC |
| 30 | Envasado y Bodega | `2001:db8:a9:430::/64` | `2001:db8:a9:430::1` | `fe80::1` | SLAAC |
| 40 | Ventas | `2001:db8:a9:440::/64` | `2001:db8:a9:440::1` | `fe80::1` | SLAAC |
| 99 | Gestión | `2001:db8:a9:499::/64` | `2001:db8:a9:499::1` | `fe80::1` | Estática |
| 50 / 60 / 70 | Voz / Invitados / IoT | — | — | — | Sin IPv6 (decisión de seguridad) |

## 3. Infraestructura
| Elemento | Temuco | Sucursal | Prefijo |
|---|---|---|---|
| Tunnel1 Temuco ↔ Talca | `2001:db8:a9:f01::1` | `2001:db8:a9:f01::2` | `2001:db8:a9:f01::/64` |
| Tunnel2 Temuco ↔ Concepción | `2001:db8:a9:f02::1` | `2001:db8:a9:f02::2` | `2001:db8:a9:f02::/64` |
| Tunnel3 Temuco ↔ Los Ángeles | `2001:db8:a9:f03::1` | `2001:db8:a9:f03::2` | `2001:db8:a9:f03::/64` |

| Router | Loopback0 (/128) |
|---|---|
| R-TEMUCO | `2001:db8:a9:fff::1/128` |
| R-TALCA | `2001:db8:a9:fff::2/128` |
| R-CONCEPCION | `2001:db8:a9:fff::3/128` |
| R-LOS-ANGELES | `2001:db8:a9:fff::4/128` |

## 4. Asignaciones estáticas reservadas
| Equipo | IPv4 | IPv6 |
|---|---|---|
| Issabel (VM) | 192.168.40.226 | `2001:db8:a9:180::226` |
| PC de gestión Temuco (host Issabel) | 192.168.40.232 | `2001:db8:a9:180::232` |
| DIST-TEMUCO (VLAN 99) | 192.168.40.242 | `2001:db8:a9:199::242` |
| ACC1-TEMUCO (VLAN 99) | 192.168.40.243 | `2001:db8:a9:199::243` |
| ACC2-TEMUCO (VLAN 99) | 192.168.40.244 | `2001:db8:a9:199::244` |
| DIST-TALCA (VLAN 99) | 192.168.10.194 | `2001:db8:a9:299::194` |
| ACC1-TALCA (VLAN 99) | 192.168.10.195 | `2001:db8:a9:299::195` |
| ACC2-TALCA (VLAN 99) | 192.168.10.196 | `2001:db8:a9:299::196` |
| DIST-CONCEPCION (VLAN 99) | 192.168.20.162 | `2001:db8:a9:399::162` |
| ACC1-CONCEPCION (VLAN 99) | 192.168.20.163 | `2001:db8:a9:399::163` |
| ACC2-CONCEPCION (VLAN 99) | 192.168.20.164 | `2001:db8:a9:399::164` |
| DIST-LOS-ANGELES (VLAN 99) | 192.168.30.130 | `2001:db8:a9:499::130` |
| ACC1-LOS-ANGELES (VLAN 99) | 192.168.30.131 | `2001:db8:a9:499::131` |
| ACC2-LOS-ANGELES (VLAN 99) | 192.168.30.132 | `2001:db8:a9:499::132` |

Las direcciones de gestión de switches quedan **reservadas** (fase siguiente); en el piloto solo se habilita IPv6 en los routers.

## 5. Verificación del plan
| Comprobación | Resultado |
|---|---|
| Solapamiento entre las 25 redes /64 | Ninguno |
| Cada VLAN dentro del /56 de su sede | Sí |
| Sedes e infraestructura dentro del /48 | Sí |
| Alineación a nibble (/48, /52, /56, /64) | Sí: permite delegación y lectura directa |
| Coherencia con IPv4 | VLAN, gateway (::1 ↔ .1/.65/…) y último octeto de hosts estáticos |
