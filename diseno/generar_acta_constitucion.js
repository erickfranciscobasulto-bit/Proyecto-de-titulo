const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, AlignmentType, Table, TableRow, TableCell, WidthType, ShadingType,
  BorderStyle, LevelFormat } = require("docx");
const F = "Arial", CM = 567, W = 12240 - 4 * CM - 2.5 * CM, C1 = 2700, C2 = W - C1;
const bd = { style: BorderStyle.SINGLE, size: 4, color: "808080" };
const borders = { top: bd, bottom: bd, left: bd, right: bd };
const P = (t, o = {}) => new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: t, font: F, size: 22, ...o })] });
const B = (t) => new Paragraph({ numbering: { reference: "b", level: 0 }, spacing: { after: 20 },
  children: [new TextRun({ text: t, font: F, size: 22 })] });
const PEND = (t) => P(t, { color: "7F7F7F", italics: true });
const cell = (kids, w, head, shade) => new TableCell({ borders, width: { size: w, type: WidthType.DXA },
  shading: head ? { fill: "1F3864", type: ShadingType.CLEAR, color: "auto" } : shade ? { fill: "F2F2F2", type: ShadingType.CLEAR, color: "auto" } : undefined,
  margins: { top: 60, bottom: 60, left: 100, right: 100 }, children: kids });
const row = (k, kids) => new TableRow({ cantSplit: true, children: [cell([P(k, { bold: true })], C1, false, true), cell(kids, C2)] });
const rows = [
  new TableRow({ tableHeader: true, children: [cell([P("Ítem", { bold: true, color: "FFFFFF" })], C1, true),
    cell([P("Contenido", { bold: true, color: "FFFFFF" })], C2, true)] }),
  row("Nombre del proyecto", [P("Diseño de Red de Datos, Telefonía IP y Servicios para una Empresa (Agroprodel Ltda.)")]),
  row("Fecha de inicio y término", [PEND("[Fechas de la carta Gantt]")]),
  row("Cliente o patrocinador", [P("Agroprodel Ltda. (gerencia)")]),
  row("Gerente o líder del proyecto", [PEND("[Nombre del líder]")]),
  row("Breve descripción", [P("Diseño e implementación de una red convergente de datos y voz para las cuatro sedes de Agroprodel Ltda., con telefonía IP centralizada, servicios esenciales en la nube, un prototipo IoT para el riego y mecanismos de seguridad y monitoreo.")]),
  row("Objetivos", [P("General:", { bold: true }), P("Diseñar e implementar una red convergente de datos y voz que garantice alta disponibilidad e integre telefonía IP, servicios en la nube y monitoreo IoT del riego."),
    P("Específicos:", { bold: true }), B("Diseñar la topología lógica y física y el plan de direccionamiento."),
    B("Implementar y configurar los equipos de red, la telefonía IP y los servicios en la nube."),
    B("Justificar técnicamente la elección de cada dispositivo."), B("Elaborar el presupuesto y evaluar su factibilidad económica."),
    B("Simular y probar la red y los servicios virtualizados.")]),
  row("Alcance", [P("Incluye:", { bold: true }), B("Red de datos de las cuatro sedes, con redundancia en capa 2."), B("Telefonía IP centralizada con IVR."),
    B("Servicios FTP, DNS y WEB en AWS."), B("Prototipo IoT de riego."), B("Seguridad y monitoreo de la red."),
    P("No incluye:", { bold: true }), B("Compra e instalación física de los equipos en las sedes."),
    B("Redundancia completa de la casa matriz (mejora futura).")]),
  row("Factores de éxito", [B("Llamadas entre las cuatro sedes y IVR operativo."), B("Continuidad del servicio ante la falla de un enlace."),
    B("Servicios en la nube accesibles desde las sedes."), B("Activación del riego según el umbral de humedad."),
    B("Cumplimiento del plazo y del presupuesto.")]),
  row("Fases y principales entregables", [B("Fase 1, diseño: topología y plan de direccionamiento."),
    B("Fase 2, implementación: configuraciones de los equipos y servicios."), B("Fase 3, pruebas: resultados y ajustes, informe final.")]),
  row("Interesados clave", [P("Gerencia de Agroprodel Ltda., usuarios de las cuatro sedes, docente guía, equipo del proyecto, proveedor de Internet (ISP), distribuidor Cisco y proveedor de telefonía VoIP.")]),
  row("Riesgos", [B("Retraso en la entrega de equipos."), B("Demora del ISP en habilitar los enlaces."), B("Corte de servicio durante la migración."),
    B("Caída del router o enlace de la casa matriz."), B("Ataques desde Internet."), P("Detalle en la matriz de riesgos (anexo).", { italics: true })]),
  row("Hitos principales", [PEND("[Fechas de la carta Gantt: diseño aprobado, red implementada, pruebas finalizadas, entrega y defensa]")]),
  row("Presupuesto", [PEND("[Inversión total neta y costo operacional anual]")]),
  row("Requerimientos de aprobación", [B("Pruebas de aceptación superadas."), B("Documentación completa entregada."),
    B("Aprobación del docente guía."), B("Cierre: entrega del informe final y defensa aprobada.")]),
  row("Firmas de aprobación", [P("Líder del proyecto: ______________________   Fecha: ________"), P(" "),
    P("Docente guía: ___________________________   Fecha: ________")]),
];
const doc = new Document({
  numbering: { config: [{ reference: "b", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
    style: { paragraph: { indent: { left: 280, hanging: 200 } } } }] }] },
  styles: { default: { document: { run: { font: F, size: 22, color: "000000" } } } },
  sections: [{ properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 4 * CM, left: 4 * CM, right: 2.5 * CM, bottom: 2.5 * CM } } },
    children: [new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: [C1, C2], rows })] }],
});
Packer.toBuffer(doc).then((b) => { fs.writeFileSync(process.argv[2], b); console.log("ok"); });
