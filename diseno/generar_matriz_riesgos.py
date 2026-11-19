import sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.formatting.rule import FormulaRule
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter

OUT = sys.argv[1]
F = "Arial"
BLUE_IN = Font(name=F, size=10, color="0000FF")
BODY = Font(name=F, size=10)
BOLD = Font(name=F, size=10, bold=True)
HDR = Font(name=F, size=10, bold=True, color="FFFFFF")
HFILL = PatternFill("solid", fgColor="1F3864")
SUBFILL = PatternFill("solid", fgColor="D9E1F2")
GREYFILL = PatternFill("solid", fgColor="F2F2F2")
thin = Side(style="thin", color="A6A6A6")
BRD = Border(left=thin, right=thin, top=thin, bottom=thin)
WRAP = Alignment(wrap_text=True, vertical="top")
CEN = Alignment(horizontal="center", vertical="center", wrap_text=True)
COL = {"Bajo": "C6EFCE", "Medio": "FFEB9C", "Alto": "F8CBAD", "Crítico": "FF7C80"}

wb = Workbook()

# ------------------------------------------------------------------ Criterios
cr = wb.active
cr.title = "Criterios"
cr["A1"] = "Matriz de riesgos — Proyecto Agroprodel Ltda. · Criterios de evaluación"
cr["A1"].font = Font(name=F, size=14, bold=True)
cr["A2"] = ("Metodología: identificación, análisis y tratamiento de riesgos (enfoque ISO 31000). "
            "Nivel = Probabilidad × Impacto (escala 1 a 5).")
cr["A2"].font = BODY

def table(ws, r0, headers, rows, widths=None):
    for j, h in enumerate(headers):
        c = ws.cell(r0, 1 + j, h)
        c.font, c.fill, c.alignment, c.border = HDR, HFILL, CEN, BRD
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            c = ws.cell(r0 + 1 + i, 1 + j, v)
            c.font, c.alignment, c.border = BODY, WRAP, BRD
    return r0 + 1 + len(rows)

cr["A4"] = "Probabilidad (P)"; cr["A4"].font = Font(name=F, size=12, bold=True)
table(cr, 5, ["Valor", "Nivel", "Descripción"], [
    (1, "Muy baja", "Excepcional; no se espera durante el proyecto ni en el primer año de operación"),
    (2, "Baja", "Podría ocurrir una vez en varios años"),
    (3, "Media", "Puede ocurrir alguna vez en el año / durante el proyecto"),
    (4, "Alta", "Ocurrirá probablemente varias veces en el año / ya ocurrió en el laboratorio"),
    (5, "Muy alta", "Ocurre de forma frecuente o es casi seguro")])
cr["A12"] = "Impacto (I)"; cr["A12"].font = Font(name=F, size=12, bold=True)
table(cr, 13, ["Valor", "Nivel", "Descripción"], [
    (1, "Insignificante", "Sin efecto en usuarios ni plazos; se corrige en minutos"),
    (2, "Menor", "Afecta a pocos usuarios o retrasa una tarea menos de 1 día"),
    (3, "Moderado", "Afecta a un departamento o servicio, o retrasa un hito algunos días"),
    (4, "Mayor", "Deja sin servicio a una sede completa o compromete un entregable"),
    (5, "Catastrófico", "Deja sin servicio a toda la empresa (voz/datos), pérdida de datos o fracaso del proyecto")])
cr["A20"] = "Clasificación del nivel (P × I)"; cr["A20"].font = Font(name=F, size=12, bold=True)
for j, h in enumerate(["Clasificación", "Desde (≥)", "Respuesta exigida"]):
    c = cr.cell(21, 1 + j, h); c.font, c.fill, c.alignment, c.border = HDR, HFILL, CEN, BRD
CLS = [("Bajo", 1, "Aceptar y monitorear"), ("Medio", 5, "Mitigar con controles estándar; revisar en cada sprint"),
       ("Alto", 10, "Mitigar con prioridad; plan de contingencia documentado"),
       ("Crítico", 15, "Acción inmediata; escalar al líder del proyecto")]
for i, (n, d, r) in enumerate(CLS):
    rr = 22 + i
    cr.cell(rr, 1, n).fill = PatternFill("solid", fgColor=COL[n])
    cr.cell(rr, 2, d).font = BLUE_IN
    cr.cell(rr, 3, r)
    for j in range(3):
        cr.cell(rr, 1 + j).border = BRD
        cr.cell(rr, 1 + j).alignment = WRAP
        if j != 1:
            cr.cell(rr, 1 + j).font = BODY
cr["A27"] = ("Cómo usar: las celdas en azul son editables (umbrales, P, I, estrategia, estado). "
             "Nivel y clasificación se calculan solos; el mapa de calor y el resumen se actualizan automáticamente.")
cr["A27"].font = Font(name=F, size=10, italic=True)
for col, w in zip("ABC", (16, 16, 90)):
    cr.column_dimensions[col].width = w
# umbrales: Medio B23, Alto B24, Critico B25
TH = "Criterios!$B$23", "Criterios!$B$24", "Criterios!$B$25"

def clasif(cell):
    return (f'=IF({cell}="","",IF({cell}>={TH[2]},"Crítico",IF({cell}>={TH[1]},"Alto",'
            f'IF({cell}>={TH[0]},"Medio","Bajo"))))')

# ------------------------------------------------------------------ Matriz
m = wb.create_sheet("Matriz de riesgos")
m["A1"] = "Matriz de riesgos — Proyecto: Diseño de red de datos, telefonía IP y servicios para Agroprodel Ltda."
m["A1"].font = Font(name=F, size=14, bold=True)
m["A2"] = ("P/I = probabilidad e impacto antes de los controles (inherente) · Residual = después de aplicar las medidas. "
           "Evidencia: códigos del registro de problemas (P-xx red, S-xx SOC) en el repositorio.")
m["A2"].font = BODY
m.merge_cells("A3:K3"); m["A3"] = "Riesgo inherente"
m.merge_cells("L3:O3"); m["L3"] = "Tratamiento"
m.merge_cells("P3:T3"); m["P3"] = "Riesgo residual"
for c in ("A3", "L3", "P3"):
    m[c].font, m[c].fill, m[c].alignment = BOLD, SUBFILL, CEN
H = ["ID", "Tipo", "Categoría", "Riesgo", "Causa", "Consecuencia", "P", "I", "Nivel", "Clasificación",
     "Estrategia", "Medidas de mitigación (preventivas)", "Plan de contingencia", "Responsable", "Estado",
     "P res.", "I res.", "Nivel res.", "Clasificación res.", "Evidencia / referencia"]
for j, h in enumerate(H):
    c = m.cell(4, 1 + j, h); c.font, c.fill, c.alignment, c.border = HDR, HFILL, CEN, BRD

RS = [
 # Proyecto
 ("Proyecto", "Plazos", "Retraso de entregables o hitos", "Complejidad técnica alta (4 sedes, SOC, IoT) y tiempo acotado del semestre",
  "Entrega incompleta o fuera de plazo", 3, 4, "Mitigar",
  "Sprints Scrum con backlog priorizado según el enunciado; carta Gantt con hitos; avance revisado semanalmente",
  "Repriorizar: primero requisitos obligatorios del enunciado, luego mejoras (SOC, IPv6)", "Líder del proyecto",
  "Controlado", 2, 3, "Carta Gantt · Estado_Proyecto.md"),
 ("Proyecto", "Recursos", "RAM insuficiente para simular todos los nodos en EVE-NG",
  "Equipo anfitrión con memoria limitada para routers, switches, firewall y servidores",
  "No se pueden simular todos los equipos del diseño real; nodos inestables", 4, 3, "Mitigar",
  "Imágenes IOL livianas; 2 switches de acceso por sede en el laboratorio; el diseño real (ACC3, servidores) se documenta en los diagramas",
  "Apagar nodos que no participan de la prueba; desplazar servicios a AWS", "Redes y SOC", "Materializado y controlado",
  2, 2, "P-09 · S-19 · diseno/*.drawio"),
 ("Proyecto", "Equipo", "Dependencia del conocimiento en un solo integrante",
  "Tareas técnicas concentradas en una persona", "Bloqueo del avance si esa persona no está disponible", 3, 4,
  "Mitigar", "Documentación de cada paso en el repositorio, guía de la red para el equipo, roles cruzados en las pruebas",
  "Otro integrante continúa con la guía y los registros de comandos", "Líder del proyecto", "Controlado", 2, 3,
  "Guia_Red_y_SOC_equipo.html"),
 ("Proyecto", "Información", "Pérdida de configuraciones o evidencias",
  "Falla del PC, NVRAM dañada en EVE-NG, uso de Wipe o cierre del laboratorio AWS",
  "Rehacer configuraciones; pérdida de evidencias para el informe", 3, 5, "Mitigar",
  "Repositorio GitHub con todas las configuraciones; exportación de configs; no usar Wipe en EVE ni Reset en AWS",
  "Restaurar desde el repositorio y reaplicar por bloques", "Redes y SOC", "Materializado y controlado", 1, 4,
  "P-10 · evidencias/configuraciones"),
 ("Proyecto", "Plataforma", "Indisponibilidad del laboratorio AWS (Learner Lab)",
  "Sesión que expira, créditos limitados, IP pública cambiante del lugar de trabajo",
  "Servicios en la nube y SOC no disponibles para pruebas o la presentación", 3, 4, "Mitigar",
  "IP elásticas, comandos documentados para reconstruir, grupos de seguridad por IP de origen",
  "Agregar la IP del lugar en los grupos de seguridad; respaldo por hotspot móvil", "Redes y SOC", "Controlado", 2, 3,
  "Comandos_SRV-NOC.md · Registro_SOC.md"),
 ("Proyecto", "Financiero", "Variación del tipo de cambio en el presupuesto",
  "Equipos Cisco cotizados en USD", "Mayor costo de la inversión", 3, 3, "Mitigar",
  "Contingencia del 10 % sobre la inversión; escenarios A y B; tipo de cambio como supuesto editable",
  "Cotizar con distribuidor local al momento de la compra; ajustar escenario", "Gestión de proyecto", "Controlado",
  2, 2, "Presupuesto (hojas Supuestos y Escenarios)"),
 ("Proyecto", "Tecnología", "Equipos propuestos fuera de venta o soporte",
  "Ciclo de vida de los productos (Catalyst 2960-X, ISR 1111)", "Equipos sin soporte ni actualizaciones de seguridad",
  3, 3, "Evitar", "Verificar anuncios de fin de vida; proponer Catalyst 9200L y C1121-8P",
  "Reemplazar el modelo por el sucesor oficial antes de la compra", "Redes y SOC", "Controlado", 1, 2,
  "Notas_Informe.md (cantidad de switches)"),
 ("Proyecto", "Alcance", "Cambios en los requerimientos del cliente o del docente",
  "Nuevas exigencias durante el semestre", "Retrabajo y desvío del plan", 2, 3, "Mitigar",
  "Backlog Scrum y revisión al cierre de cada sprint; trazabilidad requisito → evidencia",
  "Evaluar impacto en plazo y presupuesto antes de aceptar el cambio", "Líder del proyecto", "Abierto", 2, 2,
  "Estado_Proyecto.md"),
 ("Proyecto", "Seguridad", "Exposición de credenciales durante el trabajo",
  "Claves visibles en capturas, chat o historial de comandos", "Acceso no autorizado a equipos o servicios",
  4, 4, "Mitigar", "Claves nunca documentadas; capturas revisadas antes de compartir; historial limpiado",
  "Rotar la clave expuesta de inmediato", "Redes y SOC", "Materializado y controlado", 2, 3, "S-03 · S-15"),
 # Tecnicos / operacionales
 ("Técnico", "Disponibilidad", "Caída del router, firewall o enlace a Internet de la casa matriz",
  "Punto único de falla en Temuco (hub de túneles, telefonía y VPN)",
  "Las 4 sedes pierden la telefonía interna y el acceso a servidores", 2, 5, "Mitigar",
  "Diseño: segundo router con HSRP, segundo ISP o 4G con ruta flotante e IP SLA, DIST en stack (escenario B)",
  "Líneas analógicas de emergencia (ATA) en cada sede; procedimiento F-01/F-20", "Redes y SOC",
  "En diseño (escenario B)", 1, 5, "Notas_Informe.md (riesgo principal) · Manual F-01, F-20"),
 ("Técnico", "Disponibilidad", "Caída del enlace a Internet de una sucursal",
  "Falla del proveedor o del router de la sede", "La sucursal queda sin datos ni telefonía con la matriz",
  3, 4, "Mitigar", "Monitoreo en Zabbix con alerta; ATA con línea de emergencia; 4G de respaldo (trabajo futuro)",
  "Escalar al proveedor; usar línea de emergencia", "Redes y SOC", "Controlado", 3, 2, "Manual F-01 · F-02"),
 ("Técnico", "Telefonía", "Falla de la central Issabel", "Falla del servidor o actualización fallida",
  "Ninguna sede puede llamar ni recibir llamadas", 2, 5, "Mitigar",
  "Clúster Proxmox (la VM se reinicia en el otro nodo); snapshot antes de actualizar; respaldo en NAS",
  "Restaurar snapshot o respaldo; procedimiento F-16", "Telefonía", "Controlado", 1, 4, "Manual F-16"),
 ("Técnico", "Capa 2", "Bucle de capa 2 o tormenta de broadcast", "Cable mal conectado o switch no autorizado",
  "Caída de toda la sede", 2, 4, "Mitigar", "Rapid-PVST+ con raíz definida; PortFast + BPDU Guard en acceso",
  "Aislar el puerto; procedimiento F-09", "Redes y SOC", "Controlado", 1, 3, "Manual F-07 · F-09"),
 ("Técnico", "Capa 2", "Falla de un enlace o switch de acceso", "Falla de hardware o cable",
  "Usuarios de un switch sin red", 3, 3, "Mitigar",
  "EtherChannel LACP y enlaces redundantes con STP; 2 o más switches de acceso por sede",
  "Reemplazo del equipo con configuración desde el repositorio", "Redes y SOC", "Materializado y controlado", 2, 2,
  "P-05 · P-06 · P-12 · P-13"),
 ("Técnico", "Seguridad", "Ataque desde Internet (escaneo o explotación)", "Exposición del perímetro",
  "Compromiso de equipos o fuga de información", 4, 4, "Mitigar",
  "Firewall perimetral, IDS Suricata (ET Open), Wazuh con alertas a Telegram",
  "Bloquear origen en el firewall; análisis en Wazuh", "Redes y SOC", "Controlado", 2, 3,
  "Registro_SOC.md (Suricata, Telegram)"),
 ("Técnico", "Seguridad", "Propagación de malware entre departamentos", "Equipo de usuario infectado",
  "Infección de otros segmentos de la empresa", 3, 4, "Mitigar",
  "VLAN por departamento, ACL DEPTOS-IN (mínimo privilegio), regla 100102 de escaneo con alerta",
  "Aislar el puerto del equipo; revisión con el panel de Wazuh", "Redes y SOC", "Controlado", 2, 2,
  "Registro_SOC.md (100100-100102)"),
 ("Técnico", "Seguridad", "Acceso de invitados a la red interna", "Wi-Fi de clientes sin aislamiento",
  "Exposición de servidores y equipos internos", 3, 4, "Mitigar", "VLAN 60 + ACL INVITADOS-IN (solo Internet)",
  "Desactivar el SSID de invitados; procedimiento F-17", "Redes y SOC", "Controlado", 1, 2, "Manual F-17"),
 ("Técnico", "Seguridad", "Dispositivo IoT de riego comprometido", "Firmware débil del ESP32",
  "Pivote hacia la red interna o riego manipulado", 3, 3, "Mitigar", "VLAN 70 + ACL IOT-IN (solo Internet)",
  "Desconectar el dispositivo; riego manual; procedimiento F-18", "Redes y SOC", "Controlado", 1, 2, "Manual F-18"),
 ("Técnico", "Calidad", "Mala calidad de voz", "Congestión en los enlaces WAN",
  "Cortes, eco o voz robótica en llamadas a clientes", 3, 3, "Mitigar",
  "QoS: voz DSCP EF, cola de prioridad (LLQ), marca conservada en los túneles", "Procedimiento F-14",
  "Telefonía", "Controlado", 1, 2, "Manual F-14"),
 ("Técnico", "Energía", "Corte de energía", "Falla del suministro eléctrico",
  "Caída de servidores y equipos de red; daño de hardware", 3, 4, "Mitigar",
  "UPS en servidores, NAS, firewall y router; apagado ordenado", "Procedimiento F-22", "Redes y SOC",
  "En diseño", 2, 2, "Manual F-22"),
 ("Técnico", "Datos", "Ransomware o pérdida de datos en servidores", "Malware o falla de discos",
  "Pérdida de archivos y del servicio", 2, 5, "Mitigar",
  "Respaldo diario en NAS con réplica en Talca (fuera de sitio); permisos por departamento en AD; RAID 1",
  "Restaurar desde la réplica de Talca", "Redes y SOC", "En diseño", 1, 4, "Diagrama pág. 4 y 6"),
 ("Técnico", "Operación", "Error humano en un cambio de configuración",
  "Comando mal aplicado o en el equipo equivocado", "Caída parcial o total de un servicio", 3, 4, "Mitigar",
  "Respaldo antes de cada cambio; cambios por bloques; regla 4721 registra cada cambio en Wazuh",
  "Revertir con la configuración del repositorio; procedimiento F-23", "Redes y SOC",
  "Materializado y controlado", 2, 2, "P-04 · S-13 · Manual F-23"),
 ("Técnico", "Monitoreo", "Caída de la VPN hacia AWS", "Túnel inactivo o desincronizado",
  "Pérdida de monitoreo (Zabbix) y de registros (Wazuh)", 3, 3, "Mitigar",
  "IP SLA mantiene el túnel activo; cambios de cifrado en ambos extremos en la misma ventana",
  "Reiniciar sesiones IKE en ambos extremos", "Redes y SOC", "Materializado y controlado", 2, 2, "S-06 · S-13"),
 ("Técnico", "Seguridad", "IDS fuera de servicio por falta de recursos",
  "Demasiadas reglas para la memoria del firewall", "El tráfico deja de inspeccionarse sin aviso", 3, 3, "Mitigar",
  "Firewall real con 8 GB (DEC2750); selección de categorías de reglas; monitoreo del servicio",
  "Reducir reglas y reiniciar Suricata", "Redes y SOC", "Materializado y controlado", 1, 2, "S-18 · S-19"),
 ("Técnico", "Mantenimiento", "Vulnerabilidades por falta de actualizaciones",
  "Firmware y sistemas sin parches", "Explotación de fallas conocidas", 3, 4, "Mitigar",
  "Plan de mantenimiento preventivo; firmware del firewall actualizado; reglas IDS semanales",
  "Aplicar parche de emergencia en ventana de mantenimiento", "Redes y SOC", "Controlado", 2, 3,
  "Manual §9 (mantenimiento)"),
]
N = len(RS)
first, last = 5, 4 + N
for i, (tipo, cat, rie, cau, con, p, im, est, mit, cont, resp, estado, pr, ir, evi) in enumerate(RS):
    r = first + i
    vals = [f"R-{i + 1:02d}", tipo, cat, rie, cau, con, p, im, f"=G{r}*H{r}", clasif(f"I{r}"), est, mit, cont, resp,
            estado, pr, ir, f"=P{r}*Q{r}", clasif(f"R{r}"), evi]
    for j, v in enumerate(vals):
        c = m.cell(r, 1 + j, v)
        c.border, c.alignment = BRD, WRAP
        c.font = BLUE_IN if (1 + j) in (7, 8, 11, 15, 16, 17) else BODY
        if (1 + j) in (1, 7, 8, 9, 10, 16, 17, 18, 19):
            c.alignment = CEN
    m.row_dimensions[r].height = 62
widths = [7, 10, 13, 30, 30, 30, 5, 5, 7, 12, 11, 42, 34, 16, 18, 6, 6, 8, 13, 24]
for j, w in enumerate(widths):
    m.column_dimensions[get_column_letter(1 + j)].width = w
m.row_dimensions[4].height = 32
m.freeze_panes = "E5"
m.auto_filter.ref = f"A4:T{last}"
for col in ("J", "S"):
    rng = f"{col}{first}:{col}{last}"
    for n, colr in COL.items():
        m.conditional_formatting.add(rng, FormulaRule(formula=[f'{col}{first}="{n}"'],
                                     fill=PatternFill("solid", fgColor=colr)))
for col in ("I", "R"):
    rng = f"{col}{first}:{col}{last}"
    for n, lo in (("Crítico", TH[2]), ("Alto", TH[1]), ("Medio", TH[0])):
        pass
dv = DataValidation(type="whole", operator="between", formula1="1", formula2="5", allow_blank=True)
m.add_data_validation(dv)
for col in ("G", "H", "P", "Q"):
    dv.add(f"{col}{first}:{col}{last}")
dv2 = DataValidation(type="list", formula1='"Evitar,Mitigar,Transferir,Aceptar"', allow_blank=True)
m.add_data_validation(dv2); dv2.add(f"K{first}:K{last}")
dv3 = DataValidation(type="list", formula1='"Abierto,Controlado,Materializado y controlado,En diseño,En diseño (escenario B),Cerrado"',
                     allow_blank=True)
m.add_data_validation(dv3); dv3.add(f"O{first}:O{last}")
m.cell(last + 2, 1, f"Total de riesgos identificados: {N}. Celdas en azul = editables; Nivel y Clasificación son fórmulas.").font = Font(name=F, size=10, italic=True)

# ------------------------------------------------------------------ Mapa de calor
h = wb.create_sheet("Mapa de calor")
h["A1"] = "Mapa de calor — cantidad de riesgos por celda (Probabilidad × Impacto)"
h["A1"].font = Font(name=F, size=14, bold=True)
MR = "'Matriz de riesgos'"
def heat(r0, title, pcol, icol):
    h.cell(r0, 1, title).font = Font(name=F, size=12, bold=True)
    h.cell(r0 + 1, 1, "Probabilidad ↓ / Impacto →").font = BOLD
    for i in range(1, 6):
        c = h.cell(r0 + 1, 1 + i, i); c.font, c.fill, c.alignment, c.border = HDR, HFILL, CEN, BRD
    for k, pv in enumerate(range(5, 0, -1)):
        rr = r0 + 2 + k
        c = h.cell(rr, 1, pv); c.font, c.fill, c.alignment, c.border = HDR, HFILL, CEN, BRD
        for iv in range(1, 6):
            lvl = pv * iv
            n = "Crítico" if lvl >= 15 else "Alto" if lvl >= 10 else "Medio" if lvl >= 5 else "Bajo"
            c = h.cell(rr, 1 + iv, f"=COUNTIFS({MR}!${pcol}${first}:${pcol}${last},{pv},{MR}!${icol}${first}:${icol}${last},{iv})")
            c.fill = PatternFill("solid", fgColor=COL[n]); c.font = Font(name=F, size=12, bold=True)
            c.alignment, c.border = CEN, BRD
            c.number_format = '0;-0;""'
        h.row_dimensions[rr].height = 34
heat(3, "Riesgo inherente (antes de los controles)", "G", "H")
heat(12, "Riesgo residual (después de los controles)", "P", "Q")
h.column_dimensions["A"].width = 26
for col in "BCDEF":
    h.column_dimensions[col].width = 12
h["H4"] = "Colores según el nivel P × I de cada celda (umbrales de referencia: hoja Criterios)."
h["H4"].font = Font(name=F, size=10, italic=True)
for k, (n, colr) in enumerate(COL.items()):
    c = h.cell(6 + k, 8, n); c.fill = PatternFill("solid", fgColor=colr); c.font = BODY; c.border = BRD
h.column_dimensions["H"].width = 14

# ------------------------------------------------------------------ Resumen
s = wb.create_sheet("Resumen")
s["A1"] = "Resumen de la matriz de riesgos"; s["A1"].font = Font(name=F, size=14, bold=True)
for j, hh in enumerate(["Clasificación", "Inherente", "Residual", "Variación"]):
    c = s.cell(3, 1 + j, hh); c.font, c.fill, c.alignment, c.border = HDR, HFILL, CEN, BRD
for k, n in enumerate(["Crítico", "Alto", "Medio", "Bajo"]):
    r = 4 + k
    s.cell(r, 1, n).fill = PatternFill("solid", fgColor=COL[n])
    s.cell(r, 2, f'=COUNTIF({MR}!$J${first}:$J${last},A{r})')
    s.cell(r, 3, f'=COUNTIF({MR}!$S${first}:$S${last},A{r})')
    s.cell(r, 4, f"=C{r}-B{r}")
    for j in range(4):
        cc = s.cell(r, 1 + j); cc.border = BRD; cc.font = BODY; cc.alignment = CEN
    s.cell(r, 4).number_format = '+0;-0;0'
s.cell(8, 1, "Total").font = BOLD
for j, col in enumerate("BC"):
    c = s.cell(8, 2 + j, f"=SUM({col}4:{col}7)"); c.font = BOLD; c.alignment = CEN; c.border = BRD
s.cell(8, 1).border = BRD
for j, hh in enumerate(["Tipo", "Cantidad", "Nivel promedio inherente", "Nivel promedio residual", "Reducción"]):
    c = s.cell(10, 1 + j, hh); c.font, c.fill, c.alignment, c.border = HDR, HFILL, CEN, BRD
for k, tp in enumerate(["Proyecto", "Técnico"]):
    r = 11 + k
    s.cell(r, 1, tp)
    s.cell(r, 2, f'=COUNTIF({MR}!$B${first}:$B${last},A{r})')
    s.cell(r, 3, f'=IFERROR(AVERAGEIF({MR}!$B${first}:$B${last},A{r},{MR}!$I${first}:$I${last}),0)')
    s.cell(r, 4, f'=IFERROR(AVERAGEIF({MR}!$B${first}:$B${last},A{r},{MR}!$R${first}:$R${last}),0)')
    s.cell(r, 5, f'=IF(C{r}=0,0,1-D{r}/C{r})')
    for j in range(5):
        cc = s.cell(r, 1 + j); cc.border = BRD; cc.font = BODY; cc.alignment = CEN
    s.cell(r, 3).number_format = s.cell(r, 4).number_format = "0.0"
    s.cell(r, 5).number_format = "0.0%"
s["A14"] = ("Lectura: la reducción indica cuánto bajan, en promedio, los niveles de riesgo gracias a los controles "
            "implementados o diseñados. Los riesgos 'En diseño' dependen de ejecutar el escenario B del presupuesto.")
s["A14"].font = Font(name=F, size=10, italic=True)
for col, w in zip("ABCDE", (16, 12, 24, 24, 12)):
    s.column_dimensions[col].width = w

wb.move_sheet("Matriz de riesgos", offset=-1)
wb.active = 0
wb.save(OUT)
print("ok", N)
