# Estado del proyecto – Agroprodel Ltda. (networking)

Última actualización: 15-11-2026

## Cumplimiento del enunciado
| # | Requisito | Estado | Evidencia / nota |
|---|---|---|---|
| 1 | Red convergente datos + voz | ✅ | Llamadas entre las 4 sedes |
| 2 | Telefonía centralizada en la matriz | ✅ | Issabel en Temuco; 1001/2001/3001/4001 vía túneles |
| 3 | 10 teléfonos habilitados por sitio | ⚠️ | Validado con 1 terminal por sede. Pendiente (telefonía): crear las 40 extensiones por CSV (1001-1010, 2001-2010, 3001-3010, 4001-4010). Red dimensionada: VLAN 50 /28 y LLQ 1 Mbps (≈10 llamadas G.711) |
| 4 | IVR opciones 1-4 | ⚠️ | Pendiente prueba documentada (telefonía) |
| 5 | Internet independiente con IP pública WAN | ✅ | ISP simulado |
| 6 | PAT en cada router | ✅ | |
| 7 | GRE sucursal → matriz | ✅ | + IPsec AES-256 |
| 8 | Alta disponibilidad capa 2 (802.1w) | ✅ | Po3 de Concepción apagado temporalmente (P-06) |
| 9 | Agregación de enlaces | ✅ | LACP |
| 10 | Clase C privada + VLSM | ✅ | Verificado sin errores. Reserva de crecimiento de Temuco: 192.168.41.0/24 (resumen 192.168.40.0/23, sin renumerar) |
| 11 | Routers como DHCP | ✅ | DNS de la nube + respaldo 1.1.1.1 en VLAN 10-40 y 70 |
| 12 | Demostración física o simulada | ✅ | EVE-NG + Catalyst 2960 |
| 13 | Etapas según carta Gantt | ❌ | Pendiente (equipo) |
| 14 | IoT de riego (humedad + umbral) | ✅ | Prototipo ESP32 con notificaciones por Telegram. En laboratorio sale por Wi-Fi directo; en producción se integra a la VLAN 70 mediante un AP (ACL IOT-IN: solo Internet) |
| 15 | Wi-Fi clientes en ventas, solo Internet | ✅ | VLAN 60 + INVITADOS-IN |
| 16 | FTP, DNS, WEB en la nube | ✅ | AWS: HTTPS (Let's Encrypt) y FTPS implícito TLS 1.3 |

## Evidencias de entrega
| Evidencia | Estado |
|---|---|
| Topología lógica | ✅ (actualizar con 4 PC físicos, IPv6) |
| Topología física | ❌ |
| Direccionamiento IP | ✅ (agregar reserva Temuco e IPv6) |
| Archivos de configuración | ✅ |
| Especificaciones técnicas de cada dispositivo | ❌ (incluye ficha IoT: placa, sensores, actuador, umbrales) |
| Justificación técnica de equipos | ⚠️ |
| Presupuesto | ✅ |
| Simulación de red y de servicios en la nube | ✅ |

## Pendientes
1. IPv6 doble pila (plan listo en `evidencias/Plan_IPv6_Agroprodel.md`): piloto Temuco–Talca → resto.
2. Imagen IOL 15.2 en ACC1/ACC2-CONCEPCION y reactivar Po3.
3. Seguridad de gestión en SW-FISICO-TEM (+ apagar puertos sin uso).
4. Probar llamadas con las ACL entre VLAN activas (Issabel del compañero).
5. Topología física, especificaciones técnicas, actualización de informes y bitácora.
6. Carta Gantt y formato de informe final Duoc (docente, roles, fechas).
