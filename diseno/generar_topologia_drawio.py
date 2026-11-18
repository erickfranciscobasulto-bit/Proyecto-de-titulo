#!/usr/bin/env python3
"""Genera Topologia_Antes_Despues_Agroprodel.drawio (2 paginas) con iconos Cisco 2019 de draw.io."""
import sys, html
from xml.sax.saxutils import escape

OUT = sys.argv[1]

S_RECT = ("sketch=0;points=[[0.015,0.015,0],[0.985,0.015,0],[0.985,0.985,0],[0.015,0.985,0],[0.25,0,0],[0.5,0,0],"
          "[0.75,0,0],[1,0.25,0],[1,0.5,0],[1,0.75,0],[0.75,1,0],[0.5,1,0],[0.25,1,0],[0,0.75,0],[0,0.5,0],[0,0.25,0]];"
          "verticalLabelPosition=bottom;html=1;verticalAlign=top;aspect=fixed;align=center;pointerEvents=1;"
          "shape=mxgraph.cisco19.rect;fillColor=#FAFAFA;fontSize=11;fontStyle=1;")
S_RND = ("sketch=0;points=[[0.5,0,0],[1,0.5,0],[0.5,1,0],[0,0.5,0],[0.145,0.145,0],[0.8555,0.145,0],[0.855,0.8555,0],"
         "[0.145,0.855,0]];verticalLabelPosition=bottom;html=1;verticalAlign=top;aspect=fixed;align=center;"
         "pointerEvents=1;shape=mxgraph.cisco19.rect;fillColor=#FAFAFA;perimeter=ellipsePerimeter;fontSize=11;fontStyle=1;")
S3 = "verticalLabelPosition=bottom;sketch=0;html=1;verticalAlign=top;aspect=fixed;align=center;pointerEvents=1;fontSize=10;"
BLUE, GREY = "#005073", "#8A9BA8"


class Page:
    def __init__(self, name, w, h):
        self.name, self.w, self.h, self.cells, self.n = name, w, h, [], 1

    def _id(self):
        self.n += 1
        return f"c{self.n}"

    def v(self, style, x, y, w, h, label="", parent="1"):
        i = self._id()
        self.cells.append(f'<mxCell id="{i}" value="{escape(label, {chr(34): "&quot;"})}" style="{style}" vertex="1" '
                          f'parent="{parent}"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
        return i

    def e(self, a, b, style="", label="", pts=None):
        i = self._id()
        base = "endArrow=none;html=1;rounded=0;strokeWidth=2;fontSize=10;labelBackgroundColor=#FFFFFF;"
        g = '<mxGeometry relative="1" as="geometry">'
        if pts:
            g += '<Array as="points">' + "".join(f'<mxPoint x="{x}" y="{y}"/>' for x, y in pts) + "</Array>"
        g += "</mxGeometry>"
        self.cells.append(f'<mxCell id="{i}" value="{escape(label, {chr(34): "&quot;"})}" style="{base}{style}" edge="1" '
                          f'parent="1" source="{a}" target="{b}">{g}</mxCell>')
        return i

    # ---- helpers -------------------------------------------------------
    def box(self, x, y, w, h, title, fill, stroke, dashed=False, fs=13):
        st = (f"rounded=1;arcSize=3;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};strokeWidth=2;"
              f"verticalAlign=top;align=left;spacingLeft=10;spacingTop=4;fontSize={fs};fontStyle=1;fontColor={stroke};"
              + ("dashed=1;" if dashed else ""))
        return self.v(st, x, y, w, h, title)

    def text(self, x, y, w, h, label, fs=11, color="#333333", align="left", bold=False, fill="none", stroke="none"):
        st = (f"text;html=1;whiteSpace=wrap;align={align};verticalAlign=top;fontSize={fs};fontColor={color};"
              f"fillColor={fill};strokeColor={stroke};spacing=4;" + ("fontStyle=1;" if bold else ""))
        return self.v(st, x, y, w, h, label)

    def icon(self, kind, x, y, label, color=BLUE, dashed=False, size=50):
        extra = f"strokeColor={color};" + ("dashed=1;opacity=70;" if dashed else "")
        if kind in ("router", "router_with_firewall"):
            return self.v(S_RND + f"prIcon={kind};" + extra, x, y, size, size, label)
        if kind in ("l2_switch", "l3_switch", "workgroup_switch", "firewall", "wireless_lan_controller", "vpn_concentrator",
                    "net_mgmt_appliance", "ips_ids", "communications_manager", "monitoring", "security_management"):
            return self.v(S_RECT + f"prIcon={kind};" + extra, x, y, size, size, label)
        shapes = {"server": ("server2", .55, 1), "dns": ("dns_server2", .55, 1), "secure_server": ("secure_server2", .55, 1),
                  "phone": ("ip_phone2", 1, 1), "pc": ("workstation2", 1, .8), "laptop": ("laptop2", 1, .8),
                  "ap": ("wireless_access_point2", 1, .7), "cloud": ("cloud2", 1.6, 1), "user": ("user2", .8, 1),
                  "cell": ("cell_phone2", .5, 1), "branch": ("branch2", 1, 1), "printer": ("printer2", 1, .8),
                  "camera": ("surveillance_camera2", 1, 1)}
        sh, fw, fh = shapes[kind]
        fill = "#FFE9AA" if kind == "cloud" else "#FAFAFA"
        sc = "strokeColor=none;" if kind == "cloud" else extra
        return self.v(S3 + f"shape=mxgraph.cisco19.{sh};fillColor={fill};{sc}", x, y, size * fw, size * fh, label)

    def xml(self):
        return (f'<diagram name="{escape(self.name)}" id="{self.name[:8].replace(" ", "_")}">'
                f'<mxGraphModel dx="1600" dy="1000" grid="0" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" '
                f'fold="1" page="1" pageScale="1" pageWidth="{self.w}" pageHeight="{self.h}" background="#FFFFFF" math="0" shadow="0">'
                f'<root><mxCell id="0"/><mxCell id="1" parent="0"/>{"".join(self.cells)}</root></mxGraphModel></diagram>')


LACP = "shape=link;width=4;strokeWidth=1.5;strokeColor=#2E7D32;"
TRUNK = "strokeColor=#005073;"
WAN = "strokeColor=#5D4037;"
GRE = "dashed=1;dashPattern=8 4;strokeColor=#E65100;strokeWidth=2;"
VPN = "dashed=1;dashPattern=8 4;strokeColor=#6A1B9A;strokeWidth=2.5;"
BAD = "#C62828"

# =====================================================================================================
# PAGINA 2: DESPUES (TO-BE) - Modelo Cisco Enterprise Composite / Enterprise Architecture
# =====================================================================================================
p = Page("2 - Red propuesta (TO-BE)", 2000, 1250)
p.text(20, 10, 1500, 34, "Agroprodel Ltda. — Red propuesta e implementada (TO-BE) · Modelo de Arquitectura Empresarial Cisco",
       fs=20, color="#0D47A1", bold=True)
p.text(20, 44, 1900, 22, "Red convergente datos + voz · 4 sedes · Alta disponibilidad capa 2 (Rapid-PVST+ / 802.1w) · "
       "EtherChannel LACP · GRE sobre IPsec AES-256 · Servicios y SOC virtualizados en AWS", fs=12, color="#455A64")

# --- Enterprise Campus (Temuco) ---
p.box(20, 80, 820, 1030, "ENTERPRISE CAMPUS — Casa matriz Temuco · 192.168.40.0/23 (reserva 192.168.41.0/24)",
      "#E3F2FD", "#1565C0")
p.box(40, 125, 780, 150, "Distribución / núcleo colapsado", "#FFFFFF", "#90CAF9", dashed=True, fs=11)
p.box(40, 300, 780, 150, "Acceso (Building Access)", "#FFFFFF", "#90CAF9", dashed=True, fs=11)
p.box(40, 475, 780, 230, "Usuarios y dispositivos finales", "#FFFFFF", "#90CAF9", dashed=True, fs=11)
p.box(40, 730, 380, 160, "Server Farm (VLAN 80)", "#FFFFFF", "#90CAF9", dashed=True, fs=11)

dist = p.icon("l2_switch", 405, 160, "DIST-TEMUCO<br><span style='font-weight:normal'>Raíz Rapid-PVST+</span>")
a1 = p.icon("l2_switch", 145, 335, "ACC1-TEMUCO")
a2 = p.icon("l2_switch", 405, 335, "ACC2-TEMUCO")
a3 = p.icon("l2_switch", 665, 335, "ACC3-TEMUCO<br><span style='font-weight:normal'>(proyectado)</span>", dashed=True)
p.e(dist, a1, LACP, "Po1 · LACP")
p.e(dist, a2, LACP, "Po2 · LACP")
p.e(dist, a3, LACP + "dashed=1;", "Po3 · LACP")
p.e(a1, a2, "strokeColor=#9E9E9E;dashed=1;strokeWidth=1.5;", "enlace redundante (STP)")

# endpoints
ph1 = p.icon("phone", 75, 520, "Teléfonos IP<br>VLAN 50 (voz)", size=42)
pc1 = p.icon("pc", 175, 525, "PC (detrás del<br>teléfono) VLAN 10-40", size=46)
pc2 = p.icon("pc", 335, 525, "PC departamentos<br>VLAN 10/20/30/40", size=46)
ap = p.icon("ap", 470, 530, "AP CBW150AX<br>VLAN 60 invitados", size=50)
iot = p.v("rounded=1;whiteSpace=wrap;html=1;fillColor=#E8F5E9;strokeColor=#2E7D32;fontSize=10;fontStyle=1;",
          615, 520, 110, 46, "ESP32 + sensor<br>humedad (IoT)<br>VLAN 70")
valve = p.text(615, 570, 160, 60, "Electroválvula 12 V<br>umbral → riego<br>aviso Telegram", fs=9, color="#2E7D32")
for a, b in ((a1, ph1), (a1, pc1), (a2, pc2), (a2, ap), (a3, iot)):
    p.e(a, b, "strokeColor=#78909C;strokeWidth=1.5;")
p.text(55, 640, 760, 60,
       "<b>Dotación Temuco:</b> 88 usuarios (Siembra 20 · Cosecha 26 · Envasado 32 · Ventas 10) · 10 teléfonos IP · "
       "QoS: voz DSCP EF + LLQ · RA Guard, BPDU Guard, PortFast en acceso", fs=10, color="#37474F")

iss = p.icon("server", 110, 770, "SRV-ISSABEL<br><span style='font-weight:normal'>192.168.40.226 · IVR 1-4</span>",
             size=60)
p.text(230, 770, 180, 110, "Central IP centralizada (Issabel/Asterisk)<br>Extensiones 1001 · 2001 · 3001 · 4001<br>"
       "IVR: 1 Temuco · 2 Talca · 3 Concepción · 4 Los Ángeles", fs=9.5, color="#37474F")
p.e(dist, iss, "strokeColor=#78909C;strokeWidth=1.5;", "", pts=[(470, 290), (60, 290), (60, 800)])

vl = ("<b>VLAN por sede</b><br>10 Siembra y riego · 20 Cosecha y molienda · 30 Envasado y bodega · 40 Ventas<br>"
      "50 Voz · 60 Invitados (solo Internet) · 70 IoT riego · 80 Servidores · 99 Gestión · 999 Nativa<br>"
      "<b>DHCP:</b> en cada router (router-on-a-stick, subinterfaces 802.1Q) · <b>Doble pila</b> IPv4/IPv6")
p.text(440, 735, 390, 150, vl, fs=10, color="#263238", fill="#FFFFFF", stroke="#90CAF9")
p.text(40, 905, 790, 195,
       "<b>Por qué este diseño (modelo jerárquico Cisco):</b><br>"
       "• Acceso: conecta usuarios, teléfonos, AP e IoT; aplica seguridad de puerto y QoS.<br>"
       "• Distribución / núcleo colapsado: agrega el acceso con EtherChannel y es raíz de Rapid-PVST+; "
       "en una sede de este tamaño núcleo y distribución se unen para ahorrar equipos sin perder escalabilidad.<br>"
       "• Si cae un enlace, STP converge en ~1-2 s por el camino redundante; si cae un cable de un EtherChannel, el canal sigue arriba.",
       fs=10.5, color="#263238")

# --- Enterprise Edge ---
p.box(870, 80, 310, 500, "ENTERPRISE EDGE", "#FFF3E0", "#E65100")
rt = p.icon("router", 905, 160, "R-TEMUCO<br><span style='font-weight:normal'>PAT · hub GRE/IPsec<br>VPN a AWS · OSPF</span>")
fw = p.icon("firewall", 1085, 160, "FW-TEMUCO<br><span style='font-weight:normal'>OPNsense<br>IDS Suricata</span>")
p.e(dist, rt, TRUNK, "Troncal 802.1Q")
p.e(rt, fw, WAN, "203.0.113.0/30")
p.text(885, 300, 285, 270,
       "<b>Funciones del borde</b><br>• PAT: los equipos internos salen con la IP pública de la sede.<br>"
       "• Hub de túneles GRE cifrados con IPsec (AES-256) hacia las 3 sucursales.<br>"
       "• Enrutamiento dinámico OSPF entre sedes por los túneles.<br>"
       "• VPN IKEv2 hacia la nube (gestión SNMPv3, syslog, Zabbix).<br>"
       "• Firewall perimetral + IDS Suricata (alertas a Wazuh).<br>"
       "• ACL entre VLAN: invitados e IoT solo Internet.", fs=10, color="#4E342E")

# --- Service provider edge ---
p.box(1210, 80, 290, 500, "SERVICE PROVIDER EDGE", "#F3E5F5", "#6A1B9A")
inet = p.icon("cloud", 1285, 165, "Internet / ISP<br><span style='font-weight:normal'>IP pública por sede</span>", size=85)
p.e(fw, inet, WAN, "WAN 203.0.113.18/30")
p.text(1225, 320, 265, 250,
       "<b>Enlaces a Internet independientes</b><br>Temuco 203.0.113.18 (vía firewall)<br>Talca 203.0.113.6<br>"
       "Concepción 203.0.113.10<br>Los Ángeles 203.0.113.14<br><br>Cada sede navega por su propio enlace; el tráfico "
       "entre sedes viaja dentro de los túneles cifrados.", fs=10, color="#4A148C")

# --- Data center en la nube ---
p.box(1530, 80, 450, 500, "ENTERPRISE DATA CENTER — Nube AWS (VPC 10.40.0.0/16)", "#E8F5E9", "#2E7D32")
s1 = p.icon("dns", 1570, 140, "SRV-AGROPRODEL<br><span style='font-weight:normal'>Web HTTPS · DNS · FTPS<br>10.40.1.10</span>", size=60)
s2 = p.icon("server", 1730, 140, "SRV-NOC<br><span style='font-weight:normal'>Zabbix · Grafana<br>strongSwan · 10.40.1.30</span>", size=60)
s3 = p.icon("secure_server", 1890, 140, "SRV-SIEM<br><span style='font-weight:normal'>Wazuh SIEM<br>10.40.1.20</span>", size=60)
tg = p.icon("cell", 1900, 330, "Telegram<br><span style='font-weight:normal'>alertas ≥ nivel 10</span>", size=55)
p.e(s3, tg, "strokeColor=#2E7D32;strokeWidth=1.5;endArrow=classic;dashed=1;")
p.e(inet, s1, WAN + "endArrow=none;", "Internet Gateway", pts=[(1500, 205), (1500, 120), (1600, 120)])
p.text(1545, 330, 330, 240,
       "<b>Servicios esenciales virtualizados</b> (FTP, DNS, WEB)<br>+ <b>SOC</b>: disponibilidad (Zabbix/Grafana), "
       "eventos de seguridad (Wazuh) y alertas al celular.<br><br>Grupos de seguridad con mínimo privilegio; "
       "gestión solo por la VPN.", fs=10, color="#1B5E20")
p.e(rt, s2, VPN, "VPN IPsec IKEv2 (gestión)", pts=[(930, 105), (1760, 105)])

# --- Branches ---
p.box(870, 610, 1110, 500, "ENTERPRISE BRANCH — Sucursales (mismo diseño jerárquico de 2 capas, misma plantilla de configuración)",
      "#E0F7FA", "#00838F")
sedes = [("Talca", "192.168.10.0/24", "76 usuarios", 885), ("Concepción", "192.168.20.0/24", "51 usuarios", 1250),
         ("Los Ángeles", "192.168.30.0/24", "31 usuarios", 1615)]
for nombre, red, us, x0 in sedes:
    p.box(x0, 650, 350, 445, f"{nombre} · {red} · {us}", "#FFFFFF", "#4DD0E1", dashed=True, fs=11)
    tag = nombre.upper().replace("Á", "A").replace("Ó", "O").replace(" ", "-")
    r = p.icon("router", x0 + 150, 690, f"R-{tag}<br><span style='font-weight:normal'>PAT · GRE/IPsec · DHCP</span>")
    d = p.icon("l2_switch", x0 + 150, 815, f"DIST-{tag}")
    c1 = p.icon("l2_switch", x0 + 45, 935, f"ACC1-{tag}")
    c2 = p.icon("l2_switch", x0 + 255, 935, f"ACC2-{tag}")
    p.e(r, d, TRUNK, "802.1Q")
    p.e(d, c1, LACP, "LACP")
    p.e(d, c2, LACP, "LACP")
    p.e(c1, c2, "strokeColor=#9E9E9E;dashed=1;strokeWidth=1.5;")
    p.text(x0 + 10, 1030, 330, 60, "10 teléfonos IP · PC por departamento · AP invitados (VLAN 60) · ESP32 riego (VLAN 70)",
           fs=9.5, color="#006064", align="center")
    p.e(r, inet, WAN, "", pts=[(x0 + 175, 598), (1195, 598), (1195, 235)])
    p.e(r, rt, GRE, "GRE/IPsec" if x0 == 885 else "", pts=[(x0 + 120, 632), (855, 632), (855, 235)])

# legend
L = 1125
p.box(20, L, 1960, 110, "Leyenda", "#FAFAFA", "#9E9E9E", fs=11)
items = [("shape=link;width=4;strokeColor=#2E7D32;", "EtherChannel LACP (agregación)"),
         ("strokeColor=#005073;strokeWidth=2;", "Troncal 802.1Q"),
         ("strokeColor=#5D4037;strokeWidth=2;", "Enlace WAN / Internet"),
         ("dashed=1;dashPattern=8 4;strokeColor=#E65100;strokeWidth=2;", "Túnel GRE sobre IPsec (sucursal → matriz)"),
         ("dashed=1;dashPattern=8 4;strokeColor=#6A1B9A;strokeWidth=2.5;", "VPN IPsec IKEv2 matriz ↔ AWS"),
         ("strokeColor=#9E9E9E;dashed=1;strokeWidth=1.5;", "Enlace redundante bloqueado por STP")]
for k, (st, lab) in enumerate(items):
    x = 40 + (k % 3) * 640
    y = L + 40 + (k // 3) * 32
    a = p.v("text;html=1;", x, y, 1, 1)
    b = p.v("text;html=1;", x + 60, y, 1, 1)
    p.e(a, b, st)
    p.text(x + 70, y - 10, 540, 22, lab, fs=11, color="#212121")

# =====================================================================================================
# PAGINA 1: ANTES (AS-IS)
# =====================================================================================================
q = Page("1 - Situación inicial (AS-IS)", 2000, 1250)
q.text(20, 10, 1500, 34, "Agroprodel Ltda. — Situación inicial (AS-IS)", fs=20, color="#B71C1C", bold=True)
q.text(20, 44, 1900, 22, "Escenario de partida deducido del enunciado: sin red robusta, sin alta disponibilidad, "
       "telefonía tradicional costosa, sedes aisladas, sin servicios en la nube ni IoT", fs=12, color="#455A64")
cloud = q.icon("cloud", 900, 110, "Internet", size=110)
pstn = q.icon("cloud", 900, 560, "Red telefónica pública (PSTN)<br><span style='font-weight:normal'>líneas analógicas por sede · "
              "llamadas entre sedes con costo</span>", size=110)


def sede_asis(x0, y0, nombre, usuarios, right):
    X = (lambda dx, w=50: x0 + dx) if right else (lambda dx, w=50: x0 + 700 - dx - w)
    q.box(x0, y0, 700, 450, f"{nombre} · {usuarios}", "#FAFAFA", "#90A4AE")
    mod = q.icon("router", X(20), y0 + 55, "Router/módem del ISP<br><span style='font-weight:normal'>"
                 "doméstico, no gestionable</span>", color=GREY)
    s1_ = q.icon("workgroup_switch", X(200), y0 + 190, "Switch no administrable", color=GREY)
    s2_ = q.icon("workgroup_switch", X(390), y0 + 190, "Switch en cascada", color=GREY)
    s3_ = q.icon("workgroup_switch", X(580), y0 + 190, "Switch en cascada", color=GREY)
    q.e(mod, s1_, "strokeColor=#78909C;")
    q.e(s1_, s2_, "strokeColor=#78909C;")
    q.e(s2_, s3_, "strokeColor=#78909C;")
    tel = q.icon("phone", X(25, 42), y0 + 330, "Teléfonos<br>analógicos", color=GREY, size=42)
    wifi = q.icon("ap", X(200, 46), y0 + 325, "Wi-Fi doméstico<br>(clientes en la<br>misma red)", color=GREY, size=46)
    pcs = q.icon("pc", X(390, 46), y0 + 325, "PC de todos los<br>departamentos<br>(red plana)", color=GREY, size=46)
    prn = q.icon("printer", X(580, 46), y0 + 325, "Impresora", color=GREY, size=46)
    q.e(s1_, wifi, "strokeColor=#B0BEC5;strokeWidth=1.5;")
    q.e(s2_, pcs, "strokeColor=#B0BEC5;strokeWidth=1.5;")
    q.e(s3_, prn, "strokeColor=#B0BEC5;strokeWidth=1.5;")
    return mod, tel


sites = [("Temuco (casa matriz)", "88 usuarios", 20, 90), ("Talca", "76 usuarios", 1280, 90),
         ("Concepción", "51 usuarios", 20, 580), ("Los Ángeles", "31 usuarios", 1280, 580)]
for nombre, us, x0, y0 in sites:
    mod, tel = sede_asis(x0, y0, nombre, us, x0 > 1000)
    q.e(mod, cloud, "strokeColor=#78909C;")
    q.e(tel, pstn, "strokeColor=#B0BEC5;dashed=1;")

probs = ["✖ Sedes aisladas: sin enlace privado entre ellas; los datos se comparten por correo",
         "✖ Punto único de falla: switches en cascada sin enlaces redundantes (sin alta disponibilidad capa 2)",
         "✖ Red plana sin VLAN: todos los departamentos y visitantes en el mismo dominio de broadcast",
         "✖ Telefonía analógica por sede: alto costo, sin IVR ni central unificada",
         "✖ Equipos domésticos de distintas marcas: sin gestión, sin QoS, sin soporte",
         "✖ Sin monitoreo ni registro de eventos de seguridad",
         "✖ Sin servicios en la nube (web, DNS, FTP) y riego manual sin datos"]
q.text(20, 1050, 1180, 190, "<b>Problemas detectados</b><br>" + "<br>".join(probs), fs=11.5, color=BAD,
       fill="#FFEBEE", stroke="#E57373")
q.text(1220, 1050, 760, 120, "<b>Requerimientos del cliente que motivan el proyecto:</b> reducir costos de telefonía, "
       "comunicación con clientes (IVR), alta disponibilidad, equipamiento Cisco, servicios virtualizados en la nube "
       "y automatización del riego con IoT.", fs=11, color="#1A237E", fill="#E8EAF6", stroke="#7986CB")
q.text(1220, 1180, 760, 50, "Nota: el enunciado no entrega la red existente en detalle; este AS-IS es una deducción "
       "razonable a partir de las necesidades descritas por la empresa.", fs=10, color="#757575")

with open(OUT, "w", encoding="utf-8") as f:
    f.write('<mxfile host="drawio" version="24.7.17">' + q.xml() + p.xml() + "</mxfile>")
print("ok", OUT)
