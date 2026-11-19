# Checklist del informe final (formato Duoc – Portafolio de Título)

Estado al 19-11-2026. ✅ listo en el repo · ⚠️ existe pero falta adaptarlo · ❌ falta

| # | Sección exigida | Estado | Fuente en el repo / qué falta |
|---|---|---|---|
| 1 | Portada (integrantes, proyecto, asignatura, docente) | ❌ | Falta nombre del docente |
| 2 | Índice decimal dinámico + índice de figuras | ❌ | Se genera en Word al armar el informe |
| 3 | Resumen ejecutivo (1 plana) | ⚠️ | `Informe_Tecnico_Networking` §1 · ajustar a 1 plana con requerimientos y etapas |
| 4 | Introducción (contexto) | ⚠️ | `Informe_Implementacion` §1.1 |
| 5 | Descripción del problema | ⚠️ | `Bitacora_Evolucion` §1 + página AS-IS del diagrama |
| 6 | Solución (recursos humanos, técnicos, financieros) | ⚠️ | Unir arquitectura (diagrama), equipo (roles) y presupuesto |
| 7 | Objetivo general | ⚠️ | Enunciado: "Diseñar e implementar una red convergente..." |
| 8 | Objetivos específicos (≥ 3, medibles) | ⚠️ | Enunciado (5); falta hacerlos medibles (plazo e indicador) |
| 9 | Competencias del perfil de egreso (≥ 3) | ⚠️ | Enunciado trae 2; agregar al menos 1 (p. ej. seguridad de redes) |
| 10 | Acta de constitución (nombre, descripción, objetivos, factores de éxito, fases y entregables, interesados, **riesgos**, hitos, presupuesto, aprobación, líder) | ⚠️ | Riesgos: `Matriz_Riesgos_Agroprodel.xlsx` (30 riesgos de implementación y operación) · falta el resto del acta |
| 11 | Asignación de roles (funciones y tareas por integrante) | ❌ | Erick: networking y SOC · Issabel y Gantt: compañeros |
| 12 | Metodología (fases y función de cada una) | ⚠️ | Scrum + Top-Down Cisco (`Notas_Informe.md`) |
| 13 | Carta Gantt (+ archivo .mpp) | ⏳ | A cargo de un integrante |
| 14 | Topología del proyecto (imagen) | ⚠️ | `diseno/*.drawio` (lógica, 6 vistas) · **falta topología física** |
| 15 | Tabla de direccionamiento por dispositivo e interfaz (IPv4 + IPv6, máscara, gateway) | ⚠️ | VLSM/IPv6 por subred y `Plan_Puertos`; falta tabla dispositivo-interfaz consolidada |
| 16 | Requerimientos técnicos: dispositivos, **insumos, herramientas, EPP** | ❌ | Equipos en el presupuesto; faltan insumos, herramientas y EPP |
| 17 | Datasheets de cada equipo (anexo) | ❌ | Descargar PDF oficiales (C1121, C9200L, CBW150AX, CP-7841, DEC2750, DL20, RS422+, UPS, ESP32) |
| 18 | Desarrollo de la solución (todas las configuraciones + capturas) | ✅ | `Informe_Implementacion`, `evidencias/configuraciones`, registros SOC/telefonía |
| 19 | Resultados (pruebas) | ✅ | `Informe_Tecnico` §9, `Registro_SOC.md`, `Registro_Telefonia.md` |
| 20 | Factibilidad: flujo de caja, VAN, TIR (objetivo + cálculo + interpretación) | ⚠️ | Hoja "Flujo de caja"; falta texto explicativo e interpretación de la TIR |
| 21 | Conclusión | ⚠️ | `Informe_Tecnico` §14 |
| 22 | Acrónimos | ❌ | Lista a generar |
| 23 | Bibliografía APA 7 | ❌ | Lista a generar |
| 24 | Anexos (configs .txt/.cfg, .drawio, xlsx, capturas) | ⚠️ | Todo está en el repo; falta ordenarlo para la entrega |

## Formato
Arial 12 (párrafos), 13 (subtítulos), 14 (títulos), negro · márgenes sup./izq. 4 cm, der./inf. 2,5 cm ·
interlineado 1,5 · justificado · número de página abajo a la derecha · tablas en gris o azul ·
figuras numeradas ("Figura N. ...") · índice dinámico.

## Diseño: elementos del diseño real que no se implementaron en EVE-NG (deben aparecer como "diseño")
ACC3-TEMUCO · clúster Proxmox (DC01/DC02 AD, archivos, impresión) · NAS + réplica en Talca · UPS ·
troncal SIP · GW-FXO + líneas PSTN · ATA por sucursal · AP CBW150AX físicos · Catalyst 9200L / C1121 reales.
