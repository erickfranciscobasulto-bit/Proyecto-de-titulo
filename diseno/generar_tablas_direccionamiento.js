const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, AlignmentType, Table, TableRow, TableCell, WidthType, ShadingType,
  BorderStyle, SequentialIdentifier } = require("docx");
const data = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const OUT = process.argv[3];
const F = "Arial";
const CM = 567;
const W = 12240 - 4 * CM - 2.5 * CM; // ancho util carta con margenes Duoc
const widths = [1100, 1550, 1345, 1434, 1780]; // ultima columna = resto
widths.push(W - widths.reduce((a, b) => a + b, 0));
const bd = { style: BorderStyle.SINGLE, size: 4, color: "808080" };
const borders = { top: bd, bottom: bd, left: bd, right: bd };
const cell = (t, i, head) => new TableCell({
  borders, width: { size: widths[i], type: WidthType.DXA },
  shading: head ? { fill: "1F3864", type: ShadingType.CLEAR, color: "auto" } : undefined,
  margins: { top: 40, bottom: 40, left: 50, right: 50 },
  children: [new Paragraph({ alignment: head ? AlignmentType.CENTER : AlignmentType.LEFT,
    children: [new TextRun({ text: t, font: F, size: 16, bold: head, color: head ? "FFFFFF" : "000000" })] })],
});
const H = ["Dispositivo", "Interfaz", "IPv4", "Máscara", "IPv6", "Gateway"];
const children = [];
for (const [titulo, rows] of data) {
  children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 240, after: 80 }, keepNext: true,
    children: [new TextRun({ text: "Tabla ", font: F, size: 20, bold: true }), new SequentialIdentifier("Tabla"),
      new TextRun({ text: `. Direccionamiento IP – ${titulo}`, font: F, size: 20, bold: true })] }));
  children.push(new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: widths,
    rows: [new TableRow({ tableHeader: true, children: H.map((h, i) => cell(h, i, true)) }),
      ...rows.map((r) => new TableRow({ cantSplit: true, children: r.map((v, i) => cell(v, i, false)) }))] }));
  children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 60, after: 200 },
    children: [new TextRun({ text: "Fuente: configuración de los equipos del proyecto.", font: F, size: 20 })] }));
}
children.push(new Paragraph({ alignment: AlignmentType.JUSTIFIED, spacing: { line: 360 },
  children: [new TextRun({ text: "Notas: las VLAN de voz (50), invitados (60) e IoT (70) no tienen IPv6 por decisión de " +
    "seguridad. Los switches se administran por la VLAN 99 y usan como gateway la subinterfaz .99 del router de su sede. " +
    "En AWS, 10.40.1.1 es el router de la subred de la VPC.", font: F, size: 20 })] }));
const doc = new Document({
  styles: { default: { document: { run: { font: F, size: 24, color: "000000" } } } },
  sections: [{ properties: { page: { size: { width: 12240, height: 15840 },
    margin: { top: 4 * CM, left: 4 * CM, right: 2.5 * CM, bottom: 2.5 * CM } } }, children }],
});
Packer.toBuffer(doc).then((b) => { fs.writeFileSync(OUT, b); console.log("ok"); });
