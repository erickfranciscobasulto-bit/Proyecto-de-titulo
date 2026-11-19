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
cr["A2"] = ("Metodología: identificación, análisis, evaluación y tratamiento de riesgos según ISO 31000:2018. "
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
    (4, "Alta", "Ocurrirá probablemente varias veces en el año"),
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
m["A2"] = ("Fase: Implementación = riesgos del proyecto de instalación · Operación = riesgos de la red ya en servicio. "
           "P e I antes de los controles (riesgo inherente); P res. e I res. después de aplicar las medidas (riesgo residual).")
m["A2"].font = BODY
m.merge_cells("A3:K3"); m["A3"] = "Riesgo inherente"
m.merge_cells("L3:P3"); m["L3"] = "Tratamiento"
m.merge_cells("Q3:T3"); m["Q3"] = "Riesgo residual"
for c in ("A3", "L3", "Q3"):
    m[c].font, m[c].fill, m[c].alignment = BOLD, SUBFILL, CEN
H = ["ID", "Fase", "Categoría", "Riesgo", "Causa", "Consecuencia", "P", "I", "Nivel", "Clasificación",
     "Estrategia", "Medidas preventivas", "Plan de contingencia", "Disparador (señal de alerta)", "Responsable",
     "Estado", "P res.", "I res.", "Nivel res.", "Clasificación res."]
for j, h in enumerate(H):
    c = m.cell(4, 1 + j, h); c.font, c.fill, c.alignment, c.border = HDR, HFILL, CEN, BRD

R_JP, R_RED, R_TEL, R_TI, R_PROV = ("Jefe de proyecto", "Ingeniero de redes", "Especialista en telefonía",
                                     "Encargado TI Agroprodel", "Proveedor / distribuidor")
RS = [
 # ---------------------------------------------------------------- Implementación
 ("Implementación", "Externo", "Retraso en la entrega de equipos",
  "Importación, quiebre de stock o demora del distribuidor Cisco", "Se desplaza el inicio de la instalación en las sedes",
  3, 4, "Mitigar", "Orden de compra al aprobarse el proyecto; cotizar con dos distribuidores; recibir primero los equipos de la casa matriz",
  "Reprogramar la secuencia de sedes; arriendo temporal de equipos equivalentes", "Fecha de despacho confirmada posterior a la planificada",
  R_JP, "Con plan de respuesta", 2, 3),
 ("Implementación", "Externo", "Demora del ISP en habilitar enlaces o IP públicas",
  "Plazos de instalación del proveedor en zonas industriales o rurales", "Sedes sin salida a Internet ni túneles hacia la matriz",
  3, 4, "Mitigar", "Solicitar los enlaces al inicio del proyecto con fecha comprometida por contrato; validar factibilidad técnica por sede",
  "Enlace 4G provisorio para la sede afectada", "Proveedor sin fecha de instalación a dos semanas del hito",
  R_JP, "Con plan de respuesta", 2, 3),
 ("Implementación", "Externo", "Alza del tipo de cambio", "Equipos y licencias cotizados en dólares",
  "Mayor costo de la inversión respecto del presupuesto aprobado", 3, 3, "Mitigar",
  "Contingencia del 10 % sobre la inversión; fijar precio con el distribuidor al emitir la orden de compra",
  "Diferir compras no críticas (escenario B) a una segunda etapa", "Dólar sobre el valor usado en el presupuesto",
  R_JP, "Con plan de respuesta", 2, 2),
 ("Implementación", "Gestión del proyecto", "Sobrecosto del proyecto",
  "Trabajos no previstos (cableado adicional, accesorios, horas extra)", "El proyecto excede el presupuesto aprobado",
  2, 4, "Mitigar", "Levantamiento en terreno antes de comprar; control de gastos por sede contra el presupuesto",
  "Usar la contingencia; aprobar el ajuste con la gerencia antes de ejecutarlo", "Gasto acumulado sobre el 90 % del presupuesto de la etapa",
  R_JP, "Con plan de respuesta", 1, 3),
 ("Implementación", "Técnico", "Corte de servicio durante la migración",
  "Reemplazo de equipos y cambio de direccionamiento en horario laboral", "Usuarios sin red ni teléfono; pérdida de ventas",
  3, 5, "Mitigar", "Migración por sede en ventanas fuera de horario; plan de vuelta atrás (rollback) por cada cambio; aviso previo a los usuarios",
  "Volver a la configuración anterior y reagendar la ventana", "Pruebas de aceptación fallidas al cierre de la ventana",
  R_RED, "Con plan de respuesta", 2, 3),
 ("Implementación", "Técnico", "Errores de configuración en la puesta en marcha",
  "Configuración manual de muchos equipos en poco tiempo", "Fallas de conectividad, VLAN o enrutamiento después de la migración",
  3, 4, "Mitigar", "Plantillas de configuración validadas en laboratorio; revisión por un segundo ingeniero; protocolo de pruebas por sede",
  "Restaurar la configuración respaldada y corregir en ventana", "Alertas de Zabbix o reclamos de usuarios tras el cambio",
  R_RED, "Con plan de respuesta", 2, 2),
 ("Implementación", "Técnico", "Problemas al portar los números telefónicos",
  "Trámite de portabilidad hacia el proveedor SIP o datos incompletos", "Clientes no logran comunicarse con la empresa",
  2, 4, "Mitigar", "Iniciar la portabilidad con anticipación; mantener las líneas actuales hasta confirmar el traspaso",
  "Desviar los números antiguos al troncal SIP mientras se completa el trámite", "Rechazo o atraso en la solicitud de portabilidad",
  R_TEL, "Con plan de respuesta", 1, 3),
 ("Implementación", "Externo", "Atraso en las obras de cableado estructurado",
  "Permisos del recinto, faenas productivas activas o falta de canalización", "No se pueden conectar puestos de trabajo nuevos",
  3, 3, "Mitigar", "Coordinar con la administración de cada sede; contratista con certificación de puntos Cat6",
  "Priorizar puntos críticos (teléfonos, servidores) y completar el resto después", "Avance del cableado bajo lo planificado",
  R_PROV, "Con plan de respuesta", 2, 2),
 ("Implementación", "Seguridad y salud", "Accidente durante la instalación",
  "Trabajo en altura, manipulación de racks o riesgo eléctrico", "Lesiones al personal y detención de la obra",
  2, 4, "Mitigar", "Uso obligatorio de EPP; procedimientos de trabajo seguro; personal acreditado para trabajos eléctricos",
  "Primeros auxilios, aviso a la mutualidad y suspensión de la faena", "Incumplimiento de EPP detectado en terreno",
  R_JP, "Con plan de respuesta", 1, 4),
 ("Implementación", "Organizacional", "Resistencia de los usuarios al cambio",
  "Nueva telefonía, inicio de sesión con usuario de dominio y nuevas políticas", "Baja adopción y aumento de solicitudes de soporte",
  3, 3, "Mitigar", "Capacitación por departamento; manual de uso breve; acompañamiento la primera semana",
  "Reforzar la capacitación en las áreas con más reclamos", "Aumento de tickets de soporte después de la puesta en marcha",
  R_TI, "Con plan de respuesta", 2, 2),
 ("Implementación", "Gestión del proyecto", "Cambios de alcance durante la ejecución",
  "Nuevas necesidades de la empresa no consideradas al inicio", "Atrasos y costos adicionales",
  3, 3, "Mitigar", "Alcance firmado en el acta de constitución; control de cambios con evaluación de plazo y costo",
  "Incorporar el cambio en una etapa posterior", "Solicitudes nuevas fuera del acta", R_JP, "Con plan de respuesta", 2, 2),
 ("Implementación", "Organizacional", "Ausencia de personal clave",
  "Licencias, renuncias o conocimiento concentrado en una persona", "Detención de tareas críticas",
  2, 4, "Mitigar", "Documentación completa del diseño y las configuraciones; roles de respaldo definidos",
  "Reasignar la tarea al rol de respaldo", "Tareas críticas sin avance por más de 3 días", R_JP, "Con plan de respuesta", 1, 3),
 # ---------------------------------------------------------------- Operación
 ("Operación", "Disponibilidad", "Caída del router, firewall o enlace de la casa matriz",
  "Temuco concentra la telefonía, los túneles y la conexión a la nube", "Las cuatro sedes quedan sin telefonía interna ni acceso a los servidores",
  2, 5, "Mitigar", "Segundo router con HSRP, segundo ISP o 4G con ruta flotante e IP SLA, switches de distribución en stack",
  "Líneas analógicas de emergencia en cada sede; atención del proveedor con SLA", "Alerta de Zabbix por caída del enlace o del router",
  R_RED, "Con plan de respuesta", 1, 5),
 ("Operación", "Disponibilidad", "Caída del enlace a Internet de una sucursal",
  "Falla del proveedor o del router de la sede", "La sucursal queda sin datos ni telefonía con la matriz",
  3, 4, "Mitigar", "Monitoreo permanente con alerta; enlace 4G de respaldo; contrato con tiempo de reposición",
  "Línea analógica de emergencia; escalamiento al ISP", "Pérdida de paquetes sobre el 5 % o enlace caído",
  R_RED, "Con plan de respuesta", 2, 3),
 ("Operación", "Telefonía", "Falla de la central telefónica", "Falla de hardware o actualización defectuosa",
  "Ninguna sede puede llamar ni recibir llamadas", 2, 5, "Mitigar",
  "Central en clúster de virtualización; snapshot antes de cada actualización; respaldo diario",
  "Restaurar el snapshot o el último respaldo", "Teléfonos sin registro en la central", R_TEL, "Con plan de respuesta", 1, 4),
 ("Operación", "Telefonía", "Falla del proveedor SIP", "Incidente en la plataforma del proveedor",
  "No se pueden hacer ni recibir llamadas externas", 2, 4, "Mitigar",
  "Gateway FXO con dos líneas analógicas como ruta de respaldo",
  "Desviar llamadas salientes por las líneas analógicas", "Troncal SIP sin registro", R_TEL, "Con plan de respuesta", 1, 3),
 ("Operación", "Telefonía", "Mala calidad de voz", "Congestión de los enlaces WAN",
  "Cortes, eco o voz entrecortada en llamadas con clientes", 3, 3, "Mitigar",
  "QoS con prioridad para la voz (DSCP EF y LLQ) conservada dentro de los túneles",
  "Revisar el consumo del enlace y limitar el tráfico no prioritario", "Reclamos de calidad o jitter alto en el monitoreo",
  R_TEL, "Con plan de respuesta", 1, 2),
 ("Operación", "Red local", "Bucle de capa 2 o tormenta de broadcast", "Conexión indebida de cables o equipos no autorizados",
  "Caída de la red de una sede completa", 2, 4, "Mitigar",
  "Rapid-PVST+ con raíz definida; PortFast y BPDU Guard en los puertos de usuario",
  "Aislar el puerto afectado y revisar la conexión", "Puerto en estado err-disabled o CPU alta en el switch",
  R_RED, "Con plan de respuesta", 1, 3),
 ("Operación", "Red local", "Falla de un switch o de un enlace entre switches", "Falla de hardware o daño en el cableado",
  "Usuarios de un switch sin red", 3, 3, "Mitigar",
  "Agregación de enlaces LACP, enlaces redundantes y al menos dos switches de acceso por sede",
  "Reemplazo del equipo y carga de la configuración respaldada", "Alerta de interfaz caída en Zabbix",
  R_RED, "Con plan de respuesta", 2, 2),
 ("Operación", "Ciberseguridad", "Ataque desde Internet", "Exposición del perímetro y vulnerabilidades conocidas",
  "Compromiso de equipos o fuga de información", 4, 4, "Mitigar",
  "Firewall perimetral, IDS con firmas actualizadas, correlación en el SIEM y alertas en tiempo real",
  "Bloquear el origen, contener y analizar el incidente", "Alerta de nivel alto en el SIEM", R_RED, "Con plan de respuesta", 2, 3),
 ("Operación", "Ciberseguridad", "Ransomware o malware en la red interna", "Correo malicioso o equipo de usuario infectado",
  "Cifrado de archivos, propagación entre áreas y detención de la operación", 3, 5, "Mitigar",
  "Segmentación por VLAN con ACL de mínimo privilegio; permisos por departamento; respaldo diario con copia fuera de sitio",
  "Aislar el segmento afectado y restaurar desde la copia de Talca", "Bloqueos repetidos de ACL o escaneos detectados por el SIEM",
  R_RED, "Con plan de respuesta", 2, 3),
 ("Operación", "Ciberseguridad", "Acceso de visitantes a la red interna", "Red Wi-Fi de clientes en la sala de ventas",
  "Exposición de servidores y equipos de la empresa", 3, 4, "Mitigar",
  "Red de invitados aislada con salida solo a Internet", "Desactivar la red de invitados y revisar la configuración",
  "Tráfico de invitados hacia redes internas en los registros", R_RED, "Con plan de respuesta", 1, 2),
 ("Operación", "Ciberseguridad", "Compromiso de los sensores de riego", "Dispositivos IoT con firmware poco robusto",
  "Uso del dispositivo como puerta de entrada o riego alterado", 3, 3, "Mitigar",
  "Red IoT aislada con salida solo a Internet; credenciales propias por dispositivo",
  "Desconectar el dispositivo y operar el riego en modo manual", "Tráfico anómalo desde la red IoT", R_RED, "Con plan de respuesta", 1, 2),
 ("Operación", "Ciberseguridad", "Robo de credenciales de administración",
  "Contraseñas reutilizadas o compartidas por medios inseguros", "Control no autorizado de equipos de red o servidores",
  2, 5, "Mitigar", "Gestor de contraseñas, rotación periódica, acceso de gestión solo desde la red de administración y autenticación multifactor",
  "Cambiar todas las credenciales afectadas y revisar los registros de acceso", "Inicio de sesión desde un origen no habitual",
  R_TI, "Con plan de respuesta", 1, 4),
 ("Operación", "Infraestructura", "Corte de energía", "Falla del suministro eléctrico", "Caída de servidores y equipos de red; daño de hardware",
  3, 4, "Mitigar", "UPS en servidores, almacenamiento, firewall y router; procedimiento de apagado ordenado",
  "Apagado controlado y verificación de servicios al volver la energía", "UPS operando con batería", R_TI, "Con plan de respuesta", 2, 2),
 ("Operación", "Infraestructura", "Falla de hardware en servidores o almacenamiento", "Desgaste de discos o falla de un nodo",
  "Servicios internos detenidos o pérdida de información", 2, 4, "Mitigar",
  "Clúster de dos nodos, discos en RAID 1 y respaldo diario en NAS", "Migrar las máquinas virtuales al nodo disponible y reemplazar la pieza",
  "Alerta de disco o nodo degradado", R_TI, "Con plan de respuesta", 1, 3),
 ("Operación", "Gestión del cambio", "Error humano en un cambio de configuración", "Comando mal aplicado o en el equipo equivocado",
  "Caída parcial o total de un servicio", 3, 4, "Mitigar",
  "Procedimiento de cambios con respaldo previo, ventana aprobada y registro automático de cada cambio en el SIEM",
  "Revertir con la configuración respaldada", "Evento de cambio de configuración fuera de una ventana aprobada",
  R_RED, "Con plan de respuesta", 2, 2),
 ("Operación", "Monitoreo", "Pérdida del monitoreo y de los registros de seguridad", "Caída de la VPN hacia la nube",
  "Incidentes sin detectar durante la interrupción", 2, 3, "Mitigar",
  "Túnel con mantención automática (IP SLA) y alerta por falta de datos", "Restablecer la VPN y revisar los eventos del periodo",
  "Equipos sin datos en el monitoreo por más de 5 minutos", R_RED, "Con plan de respuesta", 1, 2),
 ("Operación", "Ciclo de vida", "Vencimiento de licencias y fin de soporte",
  "Suscripciones a tres años y fin de vida anunciado por el fabricante", "Equipos sin actualizaciones de seguridad ni soporte",
  3, 3, "Mitigar", "Calendario de renovaciones incluido en el OPEX; revisión anual de los anuncios de fin de vida",
  "Renovar o reemplazar el equipo afectado", "Licencia a menos de 90 días de vencer", R_TI, "Con plan de respuesta", 1, 2),
 ("Operación", "Proveedores", "Indisponibilidad o alza de costos del servicio en la nube",
  "Incidente del proveedor o cambio de tarifas", "Sitio web, DNS y FTP fuera de servicio o mayor OPEX",
  2, 4, "Mitigar", "Copias de las instancias, infraestructura documentada para reconstruir y control mensual del gasto",
  "Restaurar desde las copias en otra zona de disponibilidad", "Alerta de servicio caído o gasto sobre lo presupuestado",
  R_TI, "Con plan de respuesta", 1, 3),
]
N = len(RS)
first, last = 5, 4 + N
for i, (fase, cat, rie, cau, con, p, im, est, mit, cont, disp, resp, estado, pr, ir) in enumerate(RS):
    r = first + i
    vals = [f"R-{i + 1:02d}", fase, cat, rie, cau, con, p, im, f"=G{r}*H{r}", clasif(f"I{r}"), est, mit, cont, disp,
            resp, estado, pr, ir, f"=Q{r}*R{r}", clasif(f"S{r}")]
    for j, v in enumerate(vals):
        c = m.cell(r, 1 + j, v)
        c.border, c.alignment = BRD, WRAP
        c.font = BLUE_IN if (1 + j) in (7, 8, 11, 16, 17, 18) else BODY
        if (1 + j) in (1, 7, 8, 9, 10, 17, 18, 19, 20):
            c.alignment = CEN
    m.row_dimensions[r].height = 62
widths = [7, 15, 16, 30, 32, 32, 5, 5, 7, 13, 11, 44, 36, 30, 20, 20, 6, 6, 8, 13]
for j, w in enumerate(widths):
    m.column_dimensions[get_column_letter(1 + j)].width = w
m.row_dimensions[4].height = 32
m.freeze_panes = "E5"
m.auto_filter.ref = f"A4:T{last}"
for col in ("J", "T"):
    rng = f"{col}{first}:{col}{last}"
    for n, colr in COL.items():
        m.conditional_formatting.add(rng, FormulaRule(formula=[f'{col}{first}="{n}"'],
                                     fill=PatternFill("solid", fgColor=colr)))
dv = DataValidation(type="whole", operator="between", formula1="1", formula2="5", allow_blank=True)
m.add_data_validation(dv)
for col in ("G", "H", "Q", "R"):
    dv.add(f"{col}{first}:{col}{last}")
dv2 = DataValidation(type="list", formula1='"Evitar,Mitigar,Transferir,Aceptar"', allow_blank=True)
m.add_data_validation(dv2); dv2.add(f"K{first}:K{last}")
dv3 = DataValidation(type="list", formula1='"Identificado,Con plan de respuesta,En seguimiento,Materializado,Cerrado"',
                     allow_blank=True)
m.add_data_validation(dv3); dv3.add(f"P{first}:P{last}")
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
heat(12, "Riesgo residual (después de los controles)", "Q", "R")
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
    s.cell(r, 3, f'=COUNTIF({MR}!$T${first}:$T${last},A{r})')
    s.cell(r, 4, f"=C{r}-B{r}")
    for j in range(4):
        cc = s.cell(r, 1 + j); cc.border = BRD; cc.font = BODY; cc.alignment = CEN
    s.cell(r, 4).number_format = '+0;-0;0'
s.cell(8, 1, "Total").font = BOLD
for j, col in enumerate("BC"):
    c = s.cell(8, 2 + j, f"=SUM({col}4:{col}7)"); c.font = BOLD; c.alignment = CEN; c.border = BRD
s.cell(8, 1).border = BRD
for j, hh in enumerate(["Fase", "Cantidad", "Nivel promedio inherente", "Nivel promedio residual", "Reducción"]):
    c = s.cell(10, 1 + j, hh); c.font, c.fill, c.alignment, c.border = HDR, HFILL, CEN, BRD
for k, tp in enumerate(["Implementación", "Operación"]):
    r = 11 + k
    s.cell(r, 1, tp)
    s.cell(r, 2, f'=COUNTIF({MR}!$B${first}:$B${last},A{r})')
    s.cell(r, 3, f'=IFERROR(AVERAGEIF({MR}!$B${first}:$B${last},A{r},{MR}!$I${first}:$I${last}),0)')
    s.cell(r, 4, f'=IFERROR(AVERAGEIF({MR}!$B${first}:$B${last},A{r},{MR}!$S${first}:$S${last}),0)')
    s.cell(r, 5, f'=IF(C{r}=0,0,1-D{r}/C{r})')
    for j in range(5):
        cc = s.cell(r, 1 + j); cc.border = BRD; cc.font = BODY; cc.alignment = CEN
    s.cell(r, 3).number_format = s.cell(r, 4).number_format = "0.0"
    s.cell(r, 5).number_format = "0.0%"
s["A14"] = ("Lectura: la reducción indica cuánto baja, en promedio, el nivel de riesgo al aplicar las medidas preventivas. "
            "El riesgo residual de la casa matriz (R-13) supone la redundancia del escenario B del presupuesto.")
s["A14"].font = Font(name=F, size=10, italic=True)
for col, w in zip("ABCDE", (16, 12, 24, 24, 12)):
    s.column_dimensions[col].width = w

wb.move_sheet("Matriz de riesgos", offset=-1)
wb.active = 0
wb.save(OUT)
print("ok", N)
