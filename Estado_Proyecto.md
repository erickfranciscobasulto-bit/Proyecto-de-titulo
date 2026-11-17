# Estado del proyecto – Agroprodel Ltda. (networking)

Última actualización: 16-11-2026

## Cumplimiento del enunciado
| # | Requisito | Estado | Evidencia / nota |
|---|---|---|---|
| 1 | Red convergente datos + voz | ✅ | Llamadas entre las 4 sedes |
| 2 | Telefonía centralizada en la matriz | ✅ | Issabel en Temuco; 1001/2001/3001/4001 vía túneles |
| 3 | 10 teléfonos habilitados por sitio | ✅ | Plataforma validada con 1 softphone por sede (1001, 2001, 3001, 4001). Red dimensionada para 10 por sede: VLAN 50 /28 y LLQ 1 Mbps (≈10 llamadas G.711) |
| 4 | IVR opciones 1-4 | ✅ | Prueba 3001 → IVR → 1 → 1001 (16-11), con ACL activas |
| 5 | Internet independiente con IP pública WAN | ✅ | ISP simulado |
| 6 | PAT en cada router | ✅ | |
| 7 | GRE sucursal → matriz | ✅ | + IPsec AES-256 |
| 8 | Alta disponibilidad capa 2 (802.1w) | ✅ | Po3 de Concepción apagado temporalmente (P-06) |
| 9 | Agregación de enlaces | ✅ | LACP |
| 10 | Clase C privada + VLSM | ✅ | Verificado sin errores. Reserva de crecimiento de Temuco: 192.168.41.0/24 (resumen 192.168.40.0/23, sin renumerar) |
| 11 | Routers como DHCP | ✅ | DNS de la nube + respaldo 1.1.1.1 en VLAN 10-40 y 70 |
| 12 | Demostración física o simulada | ✅ | EVE-NG + Catalyst 2960 |
| 13 | Etapas según carta Gantt | ⏳ | A cargo de un integrante del equipo |
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
1. ✅ IPv6 doble pila operativo en las 4 sedes. RA Guard en 8 de 8 switches de acceso.
2. ✅ ACC1/ACC2-CONCEPCION en IOS 15.2 y Po3 reactivado (P-05, P-06, P-10). ACC1 recuperado de LACP suspendido (P-12) y ACC2 reconstruido (P-13): 16/16 equipos de red en verde en Zabbix.
3. ✅ ACL entre VLAN verificadas y aplicadas en las 4 sedes (R-CONCEPCION corregido, P-11). Llamadas probadas con ACL activas.
4. ✅ SW-FISICO-TEM retirado tras cumplir su función de integración (configuración conservada en el repositorio).
5. ❌ Topología física.
6. ❌ Especificaciones técnicas de cada dispositivo (incluye ficha IoT) y justificación técnica de equipos.
7. ⚠️ Actualizar topología lógica y direccionamiento (IPv6 y reserva de Temuco).
8. Formato de informe final Duoc (docente, roles, fechas). La carta Gantt la desarrolla un integrante del equipo.
9. Opcional SOC: monitoreo de Issabel en Zabbix (ICMP) y Wazuh en SRV-SIEM (en curso).
