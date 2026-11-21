const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, AlignmentType, Table, TableRow, TableCell, WidthType, ShadingType,
  BorderStyle, SequentialIdentifier } = require("docx");
const F = "Arial", CM = 567, W = 12240 - 4 * CM - 2.5 * CM;
const bd = { style: BorderStyle.SINGLE, size: 4, color: "808080" };
const borders = { top: bd, bottom: bd, left: bd, right: bd };
const mk = (widthsPct) => { const w = widthsPct.map((p) => Math.round(W * p / 100)); w[w.length - 1] = W - w.slice(0, -1).reduce((a, b) => a + b, 0); return w; };
const cell = (t, w, head, center) => new TableCell({ borders, width: { size: w, type: WidthType.DXA },
  shading: head ? { fill: "1F3864", type: ShadingType.CLEAR, color: "auto" } : undefined,
  margins: { top: 40, bottom: 40, left: 70, right: 70 },
  children: [new Paragraph({ alignment: head || center ? AlignmentType.CENTER : AlignmentType.LEFT,
    children: [new TextRun({ text: t, font: F, size: 18, bold: head, color: head ? "FFFFFF" : "000000" })] })] });
const cap = (t) => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 240, after: 80 }, keepNext: true,
  children: [new TextRun({ text: "Tabla ", font: F, size: 20, bold: true }), new SequentialIdentifier("Tabla"),
    new TextRun({ text: `. ${t}`, font: F, size: 20, bold: true })] });
const src = (t) => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 60, after: 200 },
  children: [new TextRun({ text: t, font: F, size: 20 })] });
function table(head, rows, pct, centerCols = []) {
  const w = mk(pct);
  return new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: w,
    rows: [new TableRow({ tableHeader: true, children: head.map((h, i) => cell(h, w[i], true)) }),
      ...rows.map((r) => new TableRow({ cantSplit: true, children: r.map((v, i) => cell(v, w[i], false, centerCols.includes(i))) }))] });
}
const DISP = [
  ["Router de borde", "Cisco ISR C1121-8P", "4", "Una por sede", "Gateway de las VLAN, DHCP, PAT, túneles GRE/IPsec y OSPF"],
  ["Firewall perimetral", "OPNsense Deciso DEC2750", "1", "Temuco", "Protección perimetral e IDS Suricata"],
  ["Switch de distribución", "Cisco Catalyst C9200L-24T-4G", "4", "Una por sede", "Núcleo colapsado, raíz Rapid-PVST+ y agregación LACP"],
  ["Switch de acceso 48 puertos", "Cisco Catalyst C9200L-48P-4G (PoE+)", "5", "Temuco 2, Talca 2, Concepción 1", "Conexión de usuarios, teléfonos y AP con PoE+"],
  ["Switch de acceso 24 puertos", "Cisco Catalyst C9200L-24P-4G (PoE+)", "4", "Temuco 1, Concepción 1, Los Ángeles 2", "Conexión de usuarios, teléfonos y AP con PoE+"],
  ["Licencia de switch", "Cisco DNA Essentials, 3 años", "13", "Todas las sedes", "Licencia obligatoria de los Catalyst 9200L"],
  ["Teléfono IP", "Cisco CP-7841-3PCC (SIP)", "40", "10 por sede", "Telefonía IP registrada en Issabel"],
  ["Access point", "Cisco Business CBW150AX (Wi-Fi 6)", "4", "Sala de ventas de cada sede", "Red inalámbrica de invitados (VLAN 60)"],
  ["Servidor", "HPE ProLiant DL20 Gen11", "2", "Temuco", "Clúster Proxmox: Issabel, Active Directory, archivos e impresión"],
  ["NAS de respaldo", "Synology RackStation RS422+ (4 discos 4 TB)", "2", "Temuco y Talca", "Respaldo diario y réplica fuera de sitio"],
  ["UPS", "APC Smart-UPS SMT1500RMI2UC", "6", "Temuco 3, sucursales 1", "Respaldo eléctrico de equipos críticos"],
  ["Gateway de voz", "Gateway FXO de 2 puertos", "1", "Temuco", "Respaldo de llamadas por líneas PSTN"],
  ["Adaptador telefónico", "ATA SIP de 2 puertos", "3", "Una por sucursal", "Línea analógica de emergencia"],
  ["Controlador IoT", "ESP32 (38 pines)", "4", "Una por sede", "Lectura de humedad y control del riego"],
  ["Sensor", "Sensor capacitivo de humedad de suelo", "8", "Dos por sede", "Medición de la humedad del suelo"],
  ["Actuador", "Electroválvula 12 VDC de 3/4\"", "4", "Una por sede", "Apertura y cierre del riego"],
];
const INS = [
  ["Cable UTP Cat6", "Cableado horizontal de los puntos de red", "290 puntos"],
  ["Conectores RJ45 Cat6 y jacks", "Terminación de los puntos de red", "Según puntos"],
  ["Patch panel Cat6 de 24 puertos", "Organización del cableado en rack", "Según puntos"],
  ["Patch cords Cat6", "Conexión entre patch panel y switches", "Según puertos"],
  ["Rack de piso 24U", "Equipos de la casa matriz", "1"],
  ["Gabinete mural 12U", "Equipos de cada sucursal", "3"],
  ["Organizadores de cable y bandejas", "Orden dentro de los racks", "Según rack"],
  ["Canaletas y escalerillas", "Canalización del cableado", "Según recorrido"],
  ["Amarras velcro y etiquetas", "Identificación y orden del cableado", "Según puntos"],
  ["Fuente 12 V y módulo relé", "Alimentación y control de la electroválvula", "4"],
];
const HERR = [
  ["Crimpadora RJ45", "Terminación de patch cords"],
  ["Herramienta de impacto (ponchadora 110)", "Terminación en jacks y patch panel"],
  ["Pelacables", "Preparación del cable UTP"],
  ["Certificador de cableado Cat6", "Certificación de los puntos de red"],
  ["Tester de continuidad", "Verificación rápida de cables"],
  ["Cable de consola USB a RJ45", "Configuración inicial de equipos Cisco"],
  ["Notebook con PuTTY, Wireshark y navegador", "Configuración, pruebas y análisis de tráfico"],
  ["Multímetro", "Medición eléctrica del prototipo IoT"],
  ["Taladro, juego de destornilladores y escalera", "Montaje de racks, AP y canalizaciones"],
  ["Software: EVE-NG, draw.io, Arduino IDE", "Simulación, diseño y programación del ESP32"],
];
const EPP = [
  ["Casco de seguridad", "Protección ante golpes en montaje de racks y canalizaciones"],
  ["Lentes de seguridad", "Protección ante partículas al perforar"],
  ["Guantes anticorte", "Manipulación de cables, racks y herramientas"],
  ["Guantes dieléctricos", "Trabajo cerca de tableros eléctricos"],
  ["Calzado de seguridad dieléctrico", "Protección de pies y aislación eléctrica"],
  ["Arnés de seguridad", "Trabajo en altura (instalación de AP y canalizaciones)"],
  ["Chaleco reflectante", "Visibilidad en plantas y bodegas"],
  ["Protector auditivo", "Trabajo en áreas de molienda"],
  ["Mascarilla para polvo", "Exposición a polvo de harina en planta"],
  ["Pulsera antiestática", "Protección de los equipos ante descargas electrostáticas"],
];
const children = [
  cap("Dispositivos del proyecto"),
  table(["Tipo", "Modelo", "Cant.", "Ubicación", "Función"], DISP, [19, 25, 7, 19, 30], [2]),
  src("Fuente: elaboración propia a partir del presupuesto del proyecto."),
  cap("Insumos"),
  table(["Insumo", "Uso", "Cantidad"], INS, [34, 46, 20], [2]),
  src("Fuente: elaboración propia."),
  cap("Herramientas"),
  table(["Herramienta", "Uso"], HERR, [42, 58]),
  src("Fuente: elaboración propia."),
  cap("Elementos de protección personal (EPP)"),
  table(["Elemento", "Uso"], EPP, [38, 62]),
  src("Fuente: elaboración propia."),
];
const doc = new Document({ styles: { default: { document: { run: { font: F, size: 24, color: "000000" } } } },
  sections: [{ properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 4 * CM, left: 4 * CM, right: 2.5 * CM, bottom: 2.5 * CM } } }, children }] });
Packer.toBuffer(doc).then((b) => { fs.writeFileSync(process.argv[2], b); console.log("ok"); });
