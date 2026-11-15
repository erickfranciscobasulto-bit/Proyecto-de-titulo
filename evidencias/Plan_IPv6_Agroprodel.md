# Plan de implementación IPv6 – Agroprodel Ltda.

## 1. Objetivo y alcance
Habilitar IPv6 en **doble pila** (IPv4 + IPv6) en la red corporativa de las cuatro sedes, sin alterar los
servicios IPv4 en producción y manteniendo **la misma política de seguridad** en ambos protocolos.

- IPv6 interno entre sedes, transportado por los túneles GRE ya cifrados con IPsec.
- Internet y nube continúan por IPv4 (el ISP del laboratorio no entrega IPv6).
- Despliegue por fases: Temuco + Talca (piloto) → Concepción → Los Ángeles.

## 2. Plan de direccionamiento
Prefijo corporativo: **2001:db8:a9::/48** (prefijo de documentación, RFC 3849). En producción se reemplaza
por el /48 asignado por el ISP o el RIR; el plan es jerárquico y alineado a nibble, por lo que el cambio
solo afecta a los primeros 48 bits.

| Nivel | Tamaño | Regla |
|---|---|---|
| Empresa | /48 | `2001:db8:a9::/48` |
| Sede | /56 (256 subredes por sede) | `2001:db8:a9:S00::/56`, S = 1 Temuco, 2 Talca, 3 Concepción, 4 Los Ángeles |
| VLAN | /64 | `2001:db8:a9:SVV::/64`, VV = número de VLAN (10, 20, 30, 40, 80, 99) |
| Infraestructura | /56 | `2001:db8:a9:f00::/56` (túneles y loopbacks) |
| Túneles | /64 | `2001:db8:a9:f0N::/64`, N = 1 Talca, 2 Concepción, 3 Los Ángeles; Temuco `::1`, sucursal `::2` |
| Loopback0 | /128 | `2001:db8:a9:fff::R/128`, R = 1 Temuco, 2 Talca, 3 Concepción, 4 Los Ángeles |

| VLAN | Temuco | Talca | Concepción | Los Ángeles | Asignación |
|---|---|---|---|---|---|
| 10 Siembra y Riego | `:110::/64` | `:210::/64` | `:310::/64` | `:410::/64` | SLAAC |
| 20 Cosecha y Molienda | `:120::/64` | `:220::/64` | `:320::/64` | `:420::/64` | SLAAC |
| 30 Envasado y Bodega | `:130::/64` | `:230::/64` | `:330::/64` | `:430::/64` | SLAAC |
| 40 Ventas | `:140::/64` | `:240::/64` | `:340::/64` | `:440::/64` | SLAAC |
| 80 Servidores | `:180::/64` | — | — | — | Estática |
| 99 Gestión | `:199::/64` | `:299::/64` | `:399::/64` | `:499::/64` | Estática |
| 50 Voz, 60 Invitados, 70 IoT | sin IPv6 | sin IPv6 | sin IPv6 | sin IPv6 | — |

Puerta de enlace en cada VLAN: `::1` y link-local fija `FE80::1` (siguiente salto idéntico en todas las redes).

**Por qué /64 en los túneles y no /127 (RFC 6164):** el riesgo que motiva /127 es el agotamiento de la caché
de vecinos (ND) en enlaces multiacceso; un túnel GRE punto a punto no usa ND, por lo que /64 con `::1`/`::2`
es seguro y más legible.

## 3. Enrutamiento
OSPFv3 (proceso 1, área 0) con los mismos router-id de OSPFv2 (1.1.1.1 … 4.4.4.4). `passive-interface default`;
adyacencias solo por los túneles. Las Loopback0 /128 se anuncian para gestión y diagnóstico.

## 4. Seguridad (paridad con IPv4)
| Control | IPv4 (existente) | IPv6 (nuevo) |
|---|---|---|
| Aislamiento entre VLAN | `DEPTOS-IN` | `DEPTOS-IN-V6`: permite servidores `:180::/64` y lo externo, deniega `2001:db8:a9::/48` con registro |
| Gestión de equipos | `GESTION-SSH` en vty | `GESTION-SSH-V6` en vty (`ipv6 access-class`): solo las VLAN 99 de las 4 sedes |
| Antisuplantación de origen | — | uRPF estricto (`ipv6 verify unicast source reachable-via rx`) en las VLAN de usuarios (BCP 38) |
| Redirecciones ICMPv6 | — | `no ipv6 redirects` en las VLAN de usuarios |
| Anuncios de router (RA) | — | RA solo en VLAN de usuarios; suprimidos en túneles; en VLAN 80/99 sin autoconfiguración |
| VLAN 50/60/70 | ACL propias | Sin dirección IPv6 en el router: no hay enrutamiento IPv6 hacia ni desde esas redes |
| Cifrado entre sedes | GRE + IPsec | El mismo túnel cifra el tráfico IPv6 |

Sin la ACL `DEPTOS-IN-V6` y la `access-class` IPv6, habilitar IPv6 abriría un camino que evita los controles
de IPv4: es el error más común en implementaciones de doble pila y este plan lo cierra explícitamente.

Fase siguiente (switches de acceso): RA Guard y DHCPv6 Guard (*IPv6 First Hop Security*) en los puertos de usuario.

## 5. Calidad de servicio
Los `class-map` con `match dscp` clasifican IPv4 e IPv6 por igual; la voz se mantiene en IPv4.

## 6. Verificación por fase
- `show ipv6 interface brief`: subinterfaces y túneles up/up con su dirección global.
- `show ipv6 ospf neighbor`: vecino FULL por el túnel.
- `show ipv6 route ospf`: prefijos de la otra sede.
- PC (SLAAC): dirección `2001:db8:a9:SVV:...` y gateway `fe80::1`.
- Ping IPv6 permitido (hacia servidores) y denegado (hacia otro departamento), con registro en el router.

## 7. Resultado de la fase 1 (piloto Temuco – Talca) – 15-11-2026
| Prueba | Resultado |
|---|---|
| `show ipv6 ospf neighbor` (R-TALCA) | 1.1.1.1 **FULL** por Tunnel1 |
| `show ipv6 route ospf` (R-TALCA) | 7 rutas O de Temuco (VLAN 10, 20, 30, 40, 80, 99 y Loopback0) vía link-local de R-TEMUCO |
| Ping Loopback0 Talca → Temuco | 100 % (5/5), 5 ms, a través del túnel GRE/IPsec |
| SLAAC en PC de Talca VLAN 10 | `2001:db8:a9:210:2050:79ff:fe66:6823/64` (identificador derivado de la MAC, EUI-64); router `fe80::1` |
| Ping PC Talca → servidores Temuco `2001:db8:a9:180::1` | **Permitido** (5/5) |
| Ping PC Talca → Siembra Temuco `2001:db8:a9:110::1` | **Bloqueado**: ICMPv6 tipo 1 código 1 *administratively prohibited*; registro `%IPV6_ACL-6-ACCESSLOGDP: list DEPTOS-IN-V6/80 denied icmpv6 ... -> 2001:DB8:A9:110::1` |

Conclusión: IPv6 enruta entre sedes por el túnel cifrado y aplica la misma política de mínimo privilegio que IPv4.

## 8. Resultado de la fase 2 (Concepción y Los Ángeles) – 15-11-2026
| Prueba | Concepción | Los Ángeles |
|---|---|---|
| Vecino OSPFv3 | 1.1.1.1 FULL por Tunnel2 | 1.1.1.1 FULL por Tunnel3 |
| Rutas OSPFv3 | 14 rutas O (Temuco costo 1010; Talca costo 2010 vía Temuco) | 21 rutas O (las otras 3 sedes, túneles y loopbacks) |
| Ping Loopback0 → R-TEMUCO | 100 % (7 ms) | 100 % (4-5 ms) |

Topología hub-and-spoke confirmada: las sucursales se alcanzan entre sí a través de la casa matriz (costo 2010).
Incidencia: la base IPv6 de Concepción se aplicó primero por error en R-LOS-ANGELES; se corrigió la Loopback0
(::3 → ::4) y el router-ID (3.3.3.3 → 4.4.4.4) con `clear ipv6 ospf process` antes de formar vecinos, sin impacto.

**IPv6 en doble pila operativo en las 4 sedes**, con la política de seguridad equivalente a IPv4.

## 9. IPv6 First Hop Security – RA Guard
Política `RA-GUARD-USUARIOS` (`device-role host`) en los puertos de usuario y del AP de invitados:
ACC1/ACC2-TEMUCO, ACC1/ACC2-TALCA y ACC1/ACC2-LOS-ANGELES. Verificado: un PC de Temuco con la política activa
sigue obteniendo su dirección por SLAAC (el RA legítimo llega por el troncal).
No se aplica en troncales (bloquearía los RA del router). ACC1/ACC2-CONCEPCION (IOS 15.1) no soportan la
función: se resuelve con la migración a 15.2. Mejora recomendada: aplicar la política en los puertos de los DIST
que reciben el rack físico (Et2/2, y Et2/3 en Concepción) y en los puertos de usuario del Catalyst 2960.
