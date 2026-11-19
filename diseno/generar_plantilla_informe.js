const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, TableOfContents, Footer, PageNumber,
  LevelFormat, Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle, PageBreak, SequentialIdentifier,
} = require("docx");

const OUT = process.argv[2];
const CM = 567; // 1 cm en DXA
const FONT = "Arial";
const W = 12240 - 4 * CM - 2.5 * CM; // ancho util (carta) en DXA

const body = (t, o = {}) => new Paragraph({
  alignment: AlignmentType.JUSTIFIED, spacing: { line: 360, after: 120 },
  children: [new TextRun({ text: t, font: FONT, size: 24, ...o })],
});
const guide = (t) => body(`[${t}]`, { italics: true, color: "7F7F7F" });
let figN = 0;
const h = (lvl, t) => new Paragraph({
  heading: [HeadingLevel.HEADING_1, HeadingLevel.HEADING_2, HeadingLevel.HEADING_3][lvl - 1],
  numbering: { reference: "titulos", level: lvl - 1 },
  children: [new TextRun({ text: t })],
});
const hNoNum = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: t })] });
const brk = () => new Paragraph({ children: [new PageBreak()] });
const center = (t, size, bold = false, after = 120) => new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { after },
  children: [new TextRun({ text: t, font: FONT, size, bold })],
});
const caption = (t) => new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { before: 60, after: 240 },
  children: [
    new TextRun({ text: "Figura ", font: FONT, size: 20, bold: true }),
    new SequentialIdentifier("Figura"),
    new TextRun({ text: `. ${t}`, font: FONT, size: 20 }),
  ],
});

const border = { style: BorderStyle.SINGLE, size: 4, color: "808080" };
const borders = { top: border, bottom: border, left: border, right: border };
function table(headers, rows, widths) {
  const cell = (t, head, w) => new TableCell({
    borders, width: { size: w, type: WidthType.DXA },
    shading: head ? { fill: "1F3864", type: ShadingType.CLEAR, color: "auto" } : undefined,
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: [new Paragraph({ children: [new TextRun({ text: t, font: FONT, size: 22, bold: head,
      color: head ? "FFFFFF" : (t.startsWith("[") ? "7F7F7F" : "000000"), italics: t.startsWith("[") })] })],
  });
  return new Table({
    width: { size: W, type: WidthType.DXA }, columnWidths: widths,
    rows: [new TableRow({ tableHeader: true, children: headers.map((x, i) => cell(x, true, widths[i])) }),
      ...rows.map((r) => new TableRow({ children: r.map((x, i) => cell(x, false, widths[i])) }))],
  });
}

// ---------------------------------------------------------------- portada
const portada = [
  center("Duoc UC", 28, true, 60),
  center("Escuela de Informática y Telecomunicaciones", 24, false, 60),
  center("Ingeniería en Conectividad y Redes", 24, false, 1800),
  center("Informe Final", 32, true, 240),
  center("Diseño de Red de Datos, Telefonía IP y Servicios para una Empresa", 28, true, 120),
  center("Caso: Agroprodel Ltda.", 26, false, 1800),
  center("Asignatura: Portafolio de Título", 24, false, 120),
  center("Docente: [Nombre del docente]", 24, false, 480),
  center("Integrantes:", 24, true, 60),
  center("Erick Basulto", 24, false, 40),
  center("Nabidh Ulloa", 24, false, 40),
  center("Rodrigo Verdejo", 24, false, 1200),
  center("Sede [nombre de la sede] · [mes] de 2026", 24, false, 0),
];

// ---------------------------------------------------------------- indices
const indices = [
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 240 },
    children: [new TextRun({ text: "Índice", font: FONT, size: 28, bold: true })] }),
  new TableOfContents("Índice", { hyperlink: true, headingStyleRange: "1-3" }),
  brk(),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 240 },
    children: [new TextRun({ text: "Índice de figuras", font: FONT, size: 28, bold: true })] }),
  new TableOfContents("Índice de figuras", { hyperlink: true, captionLabelIncludingNumbers: "Figura" }),
  brk(),
];

// ---------------------------------------------------------------- cuerpo
const C = [];
const add = (...x) => C.push(...x);
add(h(1, "Resumen ejecutivo"), guide("Una plana: problema de la empresa, solución, principales requerimientos y etapas del proyecto."), brk());
add(h(1, "Introducción"), guide("Contexto: empresa, rubro, sedes y escenario en que se ejecuta el proyecto."));
add(h(1, "Descripción del problema o necesidad del proyecto"), guide("Características del problema, antecedentes y evidencias (situación inicial AS-IS)."));
add(h(1, "Solución al problema"), guide("Narrativa técnica de la solución, con recursos humanos, técnicos y financieros."));
add(h(1, "Objetivo general"), guide("¿Para qué? Un solo objetivo."));
add(h(1, "Objetivos específicos"), guide("¿Cómo? Mínimo tres, concretos y medibles (plazo e indicador)."));
add(h(1, "Competencias del perfil de egreso"), guide("Mínimo tres competencias técnicas relacionadas con el proyecto."), brk());
add(h(1, "Acta de constitución del proyecto"), table(["Ítem", "Contenido"], [
  ["Nombre del proyecto", "Diseño de Red de Datos, Telefonía IP y Servicios para una Empresa (Agroprodel Ltda.)"],
  ["Breve descripción", "[Completar]"], ["Objetivos generales y específicos", "[Completar]"],
  ["Factores de éxito", "[Completar]"], ["Fases y principales entregables", "[Completar]"],
  ["Interesados clave", "[Completar]"], ["Riesgos", "[Resumen de los principales riesgos de la matriz]"],
  ["Hitos principales", "[Fechas de la carta Gantt]"], ["Presupuesto", "[Total del presupuesto]"],
  ["Requerimientos de aprobación", "[Completar]"], ["Gerente o líder del proyecto", "[Nombre]"],
], [3000, W - 3000]), brk());
add(h(1, "Asignación de roles"), table(["Integrante", "Rol", "Funciones y tareas"], [
  ["Erick Basulto", "[Rol]", "[Funciones y tareas]"], ["Nabidh Ulloa", "[Rol]", "[Funciones y tareas]"],
  ["Rodrigo Verdejo", "[Rol]", "[Funciones y tareas]"],
], [2400, 2200, W - 4600]));
add(h(1, "Metodología utilizada en el proyecto"), guide("Metodología, fases y función de cada fase."));
add(h(1, "Carta Gantt"), guide("Imagen de la carta Gantt con etapas, recursos y fechas. Adjuntar el archivo .mpp."), brk());
add(h(1, "Implementación del proyecto"));
add(h(2, "Topología del proyecto"), guide("Insertar cada vista del diagrama como figura."), caption("Topología de la red (reemplazar)"));
add(h(2, "Plan de direccionamiento IP"), guide("Tabla por dispositivo e interfaz: IPv4, IPv6, máscara y gateway."));
add(h(2, "Requerimientos técnicos"), guide("Dispositivos, insumos, herramientas y EPP. Datasheets en anexos."));
add(h(2, "Desarrollo de la solución"));
for (const t of ["Networking", "Telefonía IP", "Servicios en la nube", "Monitoreo y seguridad (SOC)", "IoT de riego"])
  add(h(3, t), guide("Configuraciones con capturas y breve explicación de cada paso."));
add(h(2, "Resultados de la solución"));
for (const t of ["Pruebas de networking", "Pruebas de telefonía IP", "Pruebas de servicios en la nube",
  "Pruebas de monitoreo y seguridad", "Pruebas de IoT de riego"])
  add(h(3, t), guide("Pruebas ejecutadas y resultados con capturas."));
add(brk(), h(1, "Factibilidad económica"));
add(h(2, "Flujo de caja"), guide("Objetivo del flujo de caja, relación con el proyecto y cálculos por periodo."));
add(h(2, "VAN"), guide("Objetivo del VAN, relación con el proyecto y cálculos."));
add(h(2, "TIR"), guide("Objetivo de la TIR, cálculos e interpretación del resultado."), brk());
add(h(1, "Conclusión"), guide("Desde el problema detectado, pasando por el desarrollo, hasta las pruebas finales."));
add(h(1, "Acrónimos"), guide("Lista de todos los acrónimos usados en el documento."));
add(h(1, "Bibliografía"), guide("Referencias en formato APA, séptima edición."), brk());
add(h(1, "Anexos"), guide("Configuraciones, diagramas, presupuesto, matriz de riesgos, datasheets y capturas."));

const hd = (size, before) => ({ run: { font: FONT, size, bold: true, color: "000000" },
  paragraph: { spacing: { before, after: 120, line: 360 }, keepNext: true } });
const doc = new Document({
  features: { updateFields: true },
  styles: {
    default: {
      document: { run: { font: FONT, size: 24, color: "000000" }, paragraph: { spacing: { line: 360 } } },
      heading1: hd(28, 360), heading2: hd(26, 240), heading3: hd(24, 200),
    },
  },
  numbering: { config: [{ reference: "titulos", levels: [
    { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 432, hanging: 432 } } } },
    { level: 1, format: LevelFormat.DECIMAL, text: "%1.%2.", alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 576, hanging: 576 } } } },
    { level: 2, format: LevelFormat.DECIMAL, text: "%1.%2.%3.", alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 720, hanging: 720 } } } },
  ] }] },
  sections: [
    { properties: { page: { size: { width: 12240, height: 15840 },
        margin: { top: 4 * CM, left: 4 * CM, right: 2.5 * CM, bottom: 2.5 * CM } } }, children: portada },
    { properties: { page: { size: { width: 12240, height: 15840 },
        margin: { top: 4 * CM, left: 4 * CM, right: 2.5 * CM, bottom: 2.5 * CM } } },
      footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT,
        children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 24, color: "000000" })] })] }) },
      children: [...indices, ...C] },
  ],
});
Packer.toBuffer(doc).then((b) => { fs.writeFileSync(OUT, b); console.log("ok", OUT); });
