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
        if kind in ("router", "router_with_firewall", "router_with_voice"):
            return self.v(S_RND + f"prIcon={kind};" + extra, x, y, size, size, label)
        if kind in ("l2_switch", "l3_switch", "workgroup_switch", "firewall", "wireless_lan_controller", "vpn_concentrator",
                    "net_mgmt_appliance", "ips_ids", "storage", "ups", "communications_manager", "monitoring", "security_management"):
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


OSPF_HALO = "ellipse;html=1;fillColor=#FFF59D;strokeColor=#F9A825;strokeWidth=2;dashed=1;opacity=80;"
SIP = "dashed=1;dashPattern=2 3;strokeColor=#00897B;strokeWidth=2.5;"
LACP = "shape=link;width=4;strokeWidth=1.5;strokeColor=#2E7D32;"
TRUNK = "strokeColor=#005073;"
WAN = "strokeColor=#5D4037;"
GRE = "dashed=1;dashPattern=8 4;strokeColor=#E65100;strokeWidth=2;"
VPN = "dashed=1;dashPattern=8 4;strokeColor=#6A1B9A;strokeWidth=2.5;"
BAD = "#C62828"

# =====================================================================================================
# PAGINA 2: DESPUES (TO-BE) - Modelo Cisco Enterprise Composite / Enterprise Architecture
# =====================================================================================================
p = Page("2 - Red propuesta (TO-BE)", 2000, 1300)
p.text(20, 10, 1500, 34, "Agroprodel Ltda. — Red propuesta e implementada (TO-BE) · Modelo de Arquitectura Empresarial Cisco",
       fs=20, color="#0D47A1", bold=True)
p.text(20, 44, 1900, 22, "Red convergente datos + voz · 4 sedes · Alta disponibilidad capa 2 (Rapid-PVST+ / 802.1w) · "
       "EtherChannel LACP · GRE sobre IPsec AES-256 · OSPF área 0 · Telefonía IP con troncal SIP · Servicios y SOC en AWS", fs=12, color="#455A64")

# --- Enterprise Campus (Temuco) ---
p.box(20, 80, 820, 1030, "ENTERPRISE CAMPUS — Casa matriz Temuco · 192.168.40.0/23 (reserva 192.168.41.0/24)",
      "#E3F2FD", "#1565C0")
p.box(40, 125, 780, 150, "Distribución / núcleo colapsado", "#FFFFFF", "#90CAF9", dashed=True, fs=11)
p.box(40, 295, 780, 145, "Acceso (Building Access)", "#FFFFFF", "#90CAF9", dashed=True, fs=11)
p.box(40, 455, 780, 205, "Usuarios y dispositivos finales", "#FFFFFF", "#90CAF9", dashed=True, fs=11)
p.box(40, 675, 780, 250, "Sala de servidores — Server Farm (VLAN 80 · 192.168.40.224/28)", "#FFFFFF", "#90CAF9",
      dashed=True, fs=11)

dist = p.icon("l2_switch", 405, 160, "DIST-TEMUCO<br><span style='font-weight:normal'>Raíz Rapid-PVST+</span>")
a1 = p.icon("l2_switch", 145, 330, "ACC1-TEMUCO<br><span style='font-weight:normal'>48 PoE+</span>")
a2 = p.icon("l2_switch", 405, 330, "ACC2-TEMUCO<br><span style='font-weight:normal'>48 PoE+</span>")
a3 = p.icon("l2_switch", 665, 330, "ACC3-TEMUCO<br><span style='font-weight:normal'>24 PoE+</span>")
p.e(dist, a1, LACP, "Po1 · LACP")
p.e(dist, a2, LACP, "Po2 · LACP")
p.e(dist, a3, LACP, "Po3 · LACP")
p.e(a1, a2, "strokeColor=#9E9E9E;dashed=1;strokeWidth=1.5;", "enlace redundante (STP)")
p.e(a2, a3, "strokeColor=#9E9E9E;dashed=1;strokeWidth=1.5;")

# endpoints
ph1 = p.icon("phone", 75, 495, "Teléfonos IP<br>VLAN 50 (voz)", size=42)
pc1 = p.icon("pc", 175, 500, "PC (detrás del<br>teléfono) VLAN 10-40", size=46)
pc2 = p.icon("pc", 335, 500, "PC departamentos<br>VLAN 10/20/30/40", size=46)
ap = p.icon("ap", 470, 505, "AP CBW150AX<br>VLAN 60 invitados", size=50)
prn = p.icon("printer", 590, 500, "Impresoras<br>de red", size=46)
iot = p.v("rounded=1;whiteSpace=wrap;html=1;fillColor=#E8F5E9;strokeColor=#2E7D32;fontSize=10;fontStyle=1;",
          690, 495, 110, 46, "ESP32 + sensor<br>humedad (IoT)<br>VLAN 70")
p.text(690, 545, 125, 50, "Electroválvula 12 V<br>umbral → riego<br>aviso Telegram", fs=9, color="#2E7D32")
for a, b in ((a1, ph1), (a1, pc1), (a2, pc2), (a2, ap), (a3, prn), (a3, iot)):
    p.e(a, b, "strokeColor=#78909C;strokeWidth=1.5;")
p.text(55, 605, 760, 50,
       "<b>Dotación Temuco:</b> 88 usuarios (Siembra 20 · Cosecha 26 · Envasado 32 · Ventas 10) · 10 teléfonos IP · "
       "120 puertos de acceso (28 libres para crecer) · QoS voz DSCP EF + LLQ · RA Guard, BPDU Guard, PortFast",
       fs=10, color="#37474F")

# sala de servidores: bus VLAN 80 + cluster Proxmox + respaldo + energia
bus = p.v("rounded=1;html=1;fillColor=#1565C0;strokeColor=none;fontColor=#FFFFFF;fontSize=10;fontStyle=1;",
          60, 712, 740, 18, "Switch de distribución · VLAN 80 Servidores (gateway 192.168.40.225)")
p.e(dist, bus, "strokeColor=#1565C0;strokeWidth=2.5;", "", pts=[(30, 185), (30, 721)])
pve1 = p.icon("server", 85, 760, "PVE-01<br><span style='font-weight:normal'>HPE DL20 Gen11</span>", size=62)
pve2 = p.icon("server", 185, 760, "PVE-02<br><span style='font-weight:normal'>HPE DL20 Gen11</span>", size=62)
nas = p.icon("storage", 615, 755, "NAS-RESPALDO<br><span style='font-weight:normal'>Synology RS422+</span>", size=55)
ups = p.icon("ups", 730, 755, "UPS 1500 VA<br><span style='font-weight:normal'>x3 (rack)</span>", size=55)
for s_ in (pve1, pve2, nas):
    p.e(bus, s_, "strokeColor=#1565C0;strokeWidth=1.5;")
p.e(pve1, pve2, "strokeColor=#2E7D32;strokeWidth=1.5;dashed=1;", "clúster")
vms = ("<b>Clúster Proxmox VE (alta disponibilidad de VM)</b><br>"
       "• <b>DC01</b> Active Directory · DNS interno · GPO<br>"
       "• <b>DC02</b> controlador de dominio réplica<br>"
       "• <b>SRV-ISSABEL</b> central IP · 192.168.40.226 · IVR 1-4<br>"
       "• <b>SRV-ARCHIVOS</b> carpetas por departamento (permisos AD)<br>"
       "• <b>SRV-IMPRESION</b> cola de impresión y escaneo<br>"
       "Si un nodo falla, sus VM se reinician en el otro.")
p.text(268, 740, 305, 180, vms, fs=9.5, color="#263238", fill="#F5F9FF", stroke="#90CAF9")
p.text(598, 845, 220, 75, "Respaldo diario de VM y archivos (Active Backup), copia en Talca. UPS para servidores, "
       "NAS, firewall y router.", fs=9, color="#37474F")

vl = ("<b>VLAN por sede</b><br>10 Siembra y riego · 20 Cosecha y molienda · 30 Envasado y bodega · 40 Ventas · "
      "50 Voz · 60 Invitados (solo Internet) · 70 IoT riego · 80 Servidores · 99 Gestión · 999 Nativa<br>"
      "<b>DHCP:</b> en cada router (subinterfaces 802.1Q) · <b>DNS:</b> AD interno + reenvío · <b>Doble pila</b> IPv4/IPv6")
p.text(40, 935, 385, 165, vl, fs=9.5, color="#263238", fill="#FFFFFF", stroke="#90CAF9")
p.text(435, 935, 395, 170,
       "<b>Modelo jerárquico Cisco</b><br>"
       "• <b>Acceso:</b> usuarios, teléfonos, AP e IoT; seguridad de puerto y QoS.<br>"
       "• <b>Distribución / núcleo colapsado:</b> agrega el acceso con EtherChannel y es raíz de Rapid-PVST+; "
       "en una sede de este tamaño núcleo y distribución se unen sin perder escalabilidad.<br>"
       "• Si cae un enlace, STP converge en ~1-2 s; si cae un cable de un EtherChannel, el canal sigue arriba.",
       fs=9.5, color="#263238")

# --- Enterprise Edge ---
p.box(870, 80, 310, 500, "ENTERPRISE EDGE", "#FFF3E0", "#E65100")
p.v(OSPF_HALO, 890, 145, 80, 80)
rt = p.icon("router", 905, 160, "R-TEMUCO<br><span style='font-weight:normal'>RID 1.1.1.1 · ASBR<br>hub GRE/IPsec · PAT</span>")
fw = p.icon("firewall", 1085, 160, "FW-TEMUCO<br><span style='font-weight:normal'>OPNsense<br>IDS Suricata</span>")
p.e(dist, rt, TRUNK, "Troncal 802.1Q")
p.e(rt, fw, WAN, "203.0.113.0/30")
fxo = p.icon("router_with_voice", 1095, 300, "GW-FXO<br><span style='font-weight:normal'>respaldo PSTN</span>", size=40)
p.text(885, 290, 200, 75, "<b>Voz de respaldo:</b> si cae el troncal SIP, Issabel sale por 2 líneas analógicas (FXO).",
       fs=9, color="#004D40")
p.text(885, 370, 285, 200,
       "<b>Funciones del borde</b><br>• PAT: los equipos internos salen con la IP pública de la sede.<br>"
       "• Hub de túneles GRE cifrados con IPsec (AES-256) hacia las 3 sucursales.<br>"
       "• OSPF entre sedes por los túneles; redistribuye la ruta de AWS (10.40.0.0/16).<br>"
       "• VPN IKEv2 hacia la nube (gestión SNMPv3, syslog, Zabbix).<br>"
       "• Firewall perimetral + IDS Suricata (alertas a Wazuh).<br>"
       "• ACL entre VLAN: invitados e IoT solo Internet.", fs=9.5, color="#4E342E")

# --- Service provider edge ---
p.box(1210, 80, 290, 500, "SERVICE PROVIDER EDGE", "#F3E5F5", "#6A1B9A")
inet = p.icon("cloud", 1285, 165, "Internet / ISP<br><span style='font-weight:normal'>IP pública por sede</span>", size=85)
p.e(fw, inet, WAN, "WAN 203.0.113.18/30")
p.text(1225, 300, 265, 130,
       "<b>Enlaces a Internet independientes</b><br>Temuco 203.0.113.18 (vía firewall) · Talca 203.0.113.6<br>"
       "Concepción 203.0.113.10 · Los Ángeles 203.0.113.14<br>El tráfico entre sedes viaja dentro de los túneles.",
       fs=9.5, color="#4A148C")
sipc = p.icon("cloud", 1225, 450, "Proveedor VoIP<br><span style='font-weight:normal'>troncal SIP (DID)</span>", size=60)
pstnc = p.icon("cloud", 1385, 450, "PSTN<br><span style='font-weight:normal'>respaldo</span>", size=60)
p.e(fw, sipc, SIP, "SIP/RTP", pts=[(1150, 185), (1150, 480)])
p.e(fxo, pstnc, "strokeColor=#00897B;strokeWidth=1.5;", "", pts=[(1115, 545), (1415, 545)])

# --- Data center en la nube ---
p.box(1530, 80, 450, 500, "ENTERPRISE DATA CENTER — Nube AWS (VPC 10.40.0.0/16)", "#E8F5E9", "#2E7D32")
s1 = p.icon("dns", 1570, 140, "SRV-AGROPRODEL<br><span style='font-weight:normal'>Web HTTPS · DNS · FTPS<br>10.40.1.10</span>", size=60)
s2 = p.icon("server", 1730, 140, "SRV-NOC<br><span style='font-weight:normal'>Zabbix · Grafana<br>strongSwan · 10.40.1.30</span>", size=60)
s3 = p.icon("secure_server", 1890, 140, "SRV-SIEM<br><span style='font-weight:normal'>Wazuh SIEM<br>10.40.1.20</span>", size=60)
tg = p.icon("cell", 1900, 330, "Telegram<br><span style='font-weight:normal'>alertas ≥ nivel 10</span>", size=55)
p.e(s3, tg, "strokeColor=#2E7D32;strokeWidth=1.5;endArrow=classic;dashed=1;")
p.e(inet, s1, WAN, "Internet Gateway", pts=[(1545, 207), (1545, 170)])
p.text(1545, 330, 330, 240,
       "<b>Servicios esenciales virtualizados</b> (FTP, DNS, WEB)<br>+ <b>SOC</b>: disponibilidad (Zabbix/Grafana), "
       "eventos de seguridad (Wazuh) y alertas al celular.<br><br>Grupos de seguridad con mínimo privilegio; "
       "gestión solo por la VPN.", fs=10, color="#1B5E20")
p.e(rt, s2, VPN, "VPN IPsec IKEv2 (gestión)", pts=[(930, 115), (1760, 115)])

# --- Branches ---
p.box(870, 600, 1110, 510, "ENTERPRISE BRANCH — Sucursales (mismo diseño jerárquico de 2 capas, misma plantilla de configuración)",
      "#E0F7FA", "#00838F")
sedes = [("Talca", "192.168.10.0/24", "76 usuarios", 885, "2.2.2.2", 1, "172.16.0.0/30"),
         ("Concepción", "192.168.20.0/24", "51 usuarios", 1250, "3.3.3.3", 2, "172.16.0.4/30"),
         ("Los Ángeles", "192.168.30.0/24", "31 usuarios", 1615, "4.4.4.4", 3, "172.16.0.8/30")]
for nombre, red, us, x0, rid, tn, tnet in sedes:
    p.box(x0, 650, 350, 445, f"{nombre} · {red} · {us}", "#FFFFFF", "#4DD0E1", dashed=True, fs=11)
    tag = nombre.upper().replace("Á", "A").replace("Ó", "O").replace(" ", "-")
    p.v(OSPF_HALO, x0 + 135, 675, 80, 80)
    r = p.icon("router", x0 + 150, 690, f"R-{tag}<br><span style='font-weight:normal'>RID {rid} · Tunnel{tn} {tnet}<br>PAT · DHCP</span>")
    d = p.icon("l2_switch", x0 + 150, 815, f"DIST-{tag}")
    c1 = p.icon("l2_switch", x0 + 45, 935, f"ACC1-{tag}")
    c2 = p.icon("l2_switch", x0 + 255, 935, f"ACC2-{tag}")
    p.e(r, d, TRUNK, "802.1Q")
    p.e(d, c1, LACP, "LACP")
    p.e(d, c2, LACP, "LACP")
    p.e(c1, c2, "strokeColor=#9E9E9E;dashed=1;strokeWidth=1.5;")
    if nombre == "Talca":
        nr = p.icon("storage", x0 + 285, 815, "NAS réplica<br><span style='font-weight:normal'>copia fuera de sitio</span>", size=40)
        p.e(d, nr, "strokeColor=#78909C;strokeWidth=1.5;")
    p.text(x0 + 10, 1030, 330, 60, "10 teléfonos IP · PC por departamento · AP invitados (VLAN 60) · ESP32 riego (VLAN 70) · ATA + línea analógica de emergencia",
           fs=9.5, color="#006064", align="center")
    p.e(r, inet, WAN, "", pts=[(x0 + 300, 705), (x0 + 300, 590), (1195, 590), (1195, 235)])
    p.e(r, rt, GRE, "GRE/IPsec" if x0 == 885 else "", pts=[(x0 + 320, 725), (x0 + 320, 642), (855, 642), (855, 235)])

# legend
L = 1125
p.box(20, L, 1960, 160, "Leyenda", "#FAFAFA", "#9E9E9E", fs=11)
items = [("shape=link;width=4;strokeColor=#2E7D32;", "EtherChannel LACP (agregación)"),
         ("strokeColor=#005073;strokeWidth=2;", "Troncal 802.1Q"),
         ("strokeColor=#5D4037;strokeWidth=2;", "Enlace WAN / Internet"),
         ("dashed=1;dashPattern=8 4;strokeColor=#E65100;strokeWidth=2;", "Túnel GRE sobre IPsec (sucursal → matriz)"),
         ("dashed=1;dashPattern=8 4;strokeColor=#6A1B9A;strokeWidth=2.5;", "VPN IPsec IKEv2 matriz ↔ AWS"),
         ("strokeColor=#9E9E9E;dashed=1;strokeWidth=1.5;", "Enlace redundante bloqueado por STP"),
         ("dashed=1;dashPattern=2 3;strokeColor=#00897B;strokeWidth=2.5;", "Troncal SIP hacia el proveedor VoIP"),
         ("strokeColor=#F9A825;strokeWidth=6;opacity=60;", "Router OSPF área 0 (halo amarillo)")]
for k, (st, lab) in enumerate(items):
    x = 40 + (k % 4) * 490
    y = L + 40 + (k // 4) * 32
    a = p.v("text;html=1;", x, y, 1, 1)
    b = p.v("text;html=1;", x + 60, y, 1, 1)
    p.e(a, b, st)
    p.text(x + 70, y - 10, 410, 22, lab, fs=11, color="#212121")

p.text(40, L + 105, 1920, 50,
       "<b>Enrutamiento:</b> OSPF proceso 1, <b>área 0 única (backbone)</b> · 4 routers en hub-and-spoke sobre los túneles GRE "
       "(Tunnel1-3, 172.16.0.0/28) · LAN pasivas (vecindad solo por túneles) · R-TEMUCO es <b>ASBR</b>: redistribuye "
       "10.40.0.0/16 (AWS) como ruta externa E2 · OSPFv3 para IPv6 · con 4 routers un área única es lo recomendado "
       "(multiárea se justifica en redes grandes, del orden de 50+ routers).", fs=10.5, color="#5D4037",
       fill="#FFFDE7", stroke="#F9A825")

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
    if y0 > 300:
        xs = 760 if x0 < 1000 else 1240
        q.e(tel, pstn, "strokeColor=#B0BEC5;dashed=1;", "", pts=[(xs, y0 + 350), (xs, 615)])
    else:
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
