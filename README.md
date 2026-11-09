# Proyecto de título – Red de datos, telefonía IP y servicios para Agroprodel Ltda.

**Duoc UC · Ingeniería en Conectividad y Redes · Proyecto APT**
Equipo: Erick Basulto · Nabidh Ulloa · Rodolfo Verdejo

Agroprodel Ltda. (siembra de trigo y producción de harina) tiene su casa matriz en Temuco y sucursales en Talca, Concepción y Los Ángeles. El proyecto diseña e implementa una red convergente Cisco para las cuatro sedes:
- **Direccionamiento:** VLSM por departamento.
- **Routers:** DHCP y PAT en cada router.
- **Conexión entre sedes:** túneles GRE cifrados con IPsec hacia la matriz.
- **Alta disponibilidad en capa 2:** Rapid-PVST+ y EtherChannel.
- **Telefonía:** IP centralizada con IVR.
- **Wi-Fi:** para clientes, aislado de la red interna.
- **IoT:** riego automatizado.
- **Nube:** servicios FTP, DNS y WEB.

La red se implementó en EVE-NG y se validó con un switch físico Cisco Catalyst 2960.

## Documentos principales

| Documento | Contenido | Para quién |
|---|---|---|
| [Informe_Tecnico_Networking_Agroprodel.docx](Informe_Tecnico_Networking_Agroprodel.docx) | Informe técnico del diseño:<br>- Arquitectura y direccionamiento<br>- Capa 2 y enrutamiento<br>- Telefonía y QoS<br>- Seguridad, pruebas y redundancia<br>- Riesgos y continuidad | Evaluadores y jefatura |
| [Informe_Implementacion_Red_Agroprodel.docx](Informe_Implementacion_Red_Agroprodel.docx) | Configuración aplicada en cada equipo, en orden y con su justificación técnica. Incluye las pruebas, los problemas encontrados (P-01 a P-04) y la integración del rack físico. | Técnicos y evaluadores |
| [Manual_Fallas_Procedimientos_Agroprodel.docx](Manual_Fallas_Procedimientos_Agroprodel.docx) | Manual de fallas con 23 fichas (F-01 a F-23):<br>- Diagnóstico paso a paso<br>- Análisis técnico y solución<br>- Registro de incidentes y escalamiento | Soporte y operación |
| [Presupuesto_Evaluacion_Economica_Agroprodel.xlsx](Presupuesto_Evaluacion_Economica_Agroprodel.xlsx) | Presupuesto con precios reales:<br>- Equipos por sede y licencias<br>- Comparación de marcas<br>- Escenario A (cumplimiento) y B (recomendado)<br>- OPEX, VAN y TIR | Evaluación económica |
| [Direccionamiento_VLSM_Agroprodel.docx](Direccionamiento_VLSM_Agroprodel.docx) | Plan de direcciones de cada sede y departamento, con máscaras y ACL de seguridad | Técnicos |
| [Guia_Defensa_VLSM_Agroprodel.docx](Guia_Defensa_VLSM_Agroprodel.docx) | Cálculo y verificación del VLSM (264/264) y preguntas frecuentes para la defensa | Equipo del proyecto |
| [Bitacora_Evolucion_Red_Agroprodel.docx](Bitacora_Evolucion_Red_Agroprodel.docx) | Evolución del diseño y decisiones técnicas (puntos 1 a 27) | Evaluadores |

## Diagramas

| Archivo | Contenido |
|---|---|
| [Topologia_Final_Agroprodel.png](Topologia_Final_Agroprodel.png) | Topología lógica final |
| [Lienzo_EVE-NG_Agroprodel.png](Lienzo_EVE-NG_Agroprodel.png) | Laboratorio en EVE-NG con las interfaces utilizadas |

## Evidencias

| Carpeta / archivo | Contenido |
|---|---|
| [evidencias/configuraciones/](evidencias/configuraciones/) | Configuración de cada equipo:<br>- ISP y firewall<br>- 4 routers y 12 switches<br>- SW-PUENTE, SW-FISICO-2960 y servidor Issabel |
| [evidencias/Registro_Problemas_Reconfiguracion.md](evidencias/Registro_Problemas_Reconfiguracion.md) | Problemas de red P-01 a P-04 con diagnóstico y solución |
| [evidencias/telefonia/Registro_Telefonia.md](evidencias/telefonia/Registro_Telefonia.md) | Registro de la implementación de la telefonía (a cargo del integrante de comunicaciones unificadas) |

## Datos clave de la red

| Sede | Red | Router | IP WAN | Túnel |
|---|---|---|---|---|
| Temuco (matriz) | 192.168.40.0/24 | R-TEMUCO (1.1.1.1) | 203.0.113.2 (detrás de OPNsense) | Tunnel1-3: 172.16.0.1 / .5 / .9 |
| Talca | 192.168.10.0/24 | R-TALCA (2.2.2.2) | 203.0.113.6 | Tunnel1: 172.16.0.2 |
| Concepción | 192.168.20.0/24 | R-CONCEPCION (3.3.3.3) | 203.0.113.10 | Tunnel2: 172.16.0.6 |
| Los Ángeles | 192.168.30.0/24 | R-LOS-ANGELES (4.4.4.4) | 203.0.113.14 | Tunnel3: 172.16.0.10 |

| VLAN | 10 | 20 | 30 | 40 | 50 | 60 | 70 | 80 | 99 | 999 |
|---|---|---|---|---|---|---|---|---|---|---|
| **Uso** | Siembra y Riego | Cosecha y Molienda | Envasado y Bodega | Ventas | Voz | Invitados | IoT | Servidores (Temuco) | Gestión | Nativa (sin IP) |
