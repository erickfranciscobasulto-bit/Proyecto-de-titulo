#!/usr/bin/env python3
"""Genera Topologia_Agroprodel.drawio (5 paginas: AS-IS, arquitectura TO-BE, OSPF, LAN Temuco, LAN sucursales) con iconos Cisco 2019 de draw.io."""
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


LPOS = {"bottom": "", "right": "labelPosition=right;verticalLabelPosition=middle;align=left;verticalAlign=middle;spacingLeft=6;",
        "left": "labelPosition=left;verticalLabelPosition=middle;align=right;verticalAlign=middle;spacingRight=6;",
        "top": "verticalLabelPosition=top;verticalAlign=bottom;"}


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

    def icon(self, kind, x, y, label, color=BLUE, dashed=False, size=50, lp="bottom"):
        extra = f"strokeColor={color};" + ("dashed=1;opacity=70;" if dashed else "") + LPOS[lp]
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
        sc = ("strokeColor=none;" + LPOS[lp]) if kind == "cloud" else extra
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
# PAGINAS TO-BE: vistas por capas (arquitectura general, enrutamiento L3, LAN Temuco, LAN sucursales)
# =====================================================================================================
SUB = "<span style='font-weight:normal'>"


def legend(pg, y, items, w=1960, cols=4, extra=None):
    h = 40 + 32 * ((len(items) + cols - 1) // cols) + (55 if extra else 0)
    pg.box(20, y, w, h, "Leyenda", "#FAFAFA", "#9E9E9E", fs=11)
    for k, (st, lab) in enumerate(items):
        x = 40 + (k % cols) * (w // cols)
        yy = y + 40 + (k // cols) * 32
        a = pg.v("text;html=1;", x, yy, 1, 1)
        b = pg.v("text;html=1;", x + 60, yy, 1, 1)
        pg.e(a, b, st)
        pg.text(x + 70, yy - 10, w // cols - 90, 22, lab, fs=11, color="#212121")
    if extra:
        pg.text(40, y + h - 55, w - 40, 48, extra, fs=10.5, color="#5D4037", fill="#FFFDE7", stroke="#F9A825")


L_LACP = ("shape=link;width=4;strokeColor=#2E7D32;", "EtherChannel LACP")
L_TRK = ("strokeColor=#005073;strokeWidth=2;", "Troncal 802.1Q")
L_WAN = ("strokeColor=#5D4037;strokeWidth=2;", "Enlace WAN / Internet")
L_GRE = ("dashed=1;dashPattern=8 4;strokeColor=#E65100;strokeWidth=2;", "Túnel GRE sobre IPsec AES-256")
L_VPN = ("dashed=1;dashPattern=8 4;strokeColor=#6A1B9A;strokeWidth=2.5;", "VPN IPsec IKEv2 matriz ↔ AWS")
L_STP = ("strokeColor=#9E9E9E;dashed=1;strokeWidth=1.5;", "Enlace redundante bloqueado por STP")
L_SIP = ("dashed=1;dashPattern=2 3;strokeColor=#00897B;strokeWidth=2.5;", "Troncal SIP / respaldo PSTN")
L_OSPF = ("strokeColor=#F9A825;strokeWidth=8;opacity=60;", "Router OSPF área 0 (halo)")

SEDES = [  # nombre, tag, red, usuarios, rid, tunel, red tunel, accesos
    ("Talca", "TALCA", "192.168.10.0/24", 76, "2.2.2.2", 1, "172.16.0.0/30", ("48 PoE+", "48 PoE+"),
     "#1E88E5"),
    ("Concepción", "CONCEPCION", "192.168.20.0/24", 51, "3.3.3.3", 2, "172.16.0.4/30", ("48 PoE+", "24 PoE+"),
     "#43A047"),
    ("Los Ángeles", "LOS-ANGELES", "192.168.30.0/24", 31, "4.4.4.4", 3, "172.16.0.8/30", ("24 PoE+", "24 PoE+"),
     "#8E24AA"),
]

# -----------------------------------------------------------------------------------------------------
# PAGINA 2: ARQUITECTURA GENERAL (modelo de arquitectura empresarial Cisco)
# -----------------------------------------------------------------------------------------------------
p = Page("2 - Arquitectura general (TO-BE)", 2000, 1250)
p.text(20, 10, 1600, 34, "Agroprodel Ltda. — Arquitectura de red propuesta (TO-BE) · Modelo de Arquitectura Empresarial Cisco",
       fs=20, color="#0D47A1", bold=True)
p.text(20, 44, 1900, 22, "Vista general por módulos · el detalle de cada capa está en las páginas 3 (enrutamiento), "
       "4 (LAN Temuco) y 5 (LAN sucursales)", fs=12, color="#455A64")

# Campus
p.box(20, 90, 600, 900, "ENTERPRISE CAMPUS · Casa matriz Temuco", "#E3F2FD", "#1565C0")
p.box(40, 130, 560, 105, "Distribución / núcleo colapsado", "#FFFFFF", "#90CAF9", dashed=True, fs=11)
p.box(40, 255, 560, 140, "Acceso", "#FFFFFF", "#90CAF9", dashed=True, fs=11)
p.box(40, 415, 560, 125, "Usuarios y dispositivos (88 usuarios · 10 teléfonos IP)", "#FFFFFF", "#90CAF9", dashed=True, fs=11)
p.box(40, 560, 560, 300, "Sala de servidores (VLAN 80)", "#FFFFFF", "#90CAF9", dashed=True, fs=11)
dist = p.icon("l2_switch", 295, 160, "DIST-TEMUCO" + SUB + "<br>raíz Rapid-PVST+</span>", lp="left")
accs = []
for k, (x, cap) in enumerate(((90, "48 PoE+"), (295, "48 PoE+"), (500, "24 PoE+"))):
    a = p.icon("l2_switch", x, 290, f"ACC{k + 1}-TEMUCO" + SUB + f"<br>{cap}</span>")
    p.e(dist, a, LACP)
    accs.append(a)
p.e(accs[0], accs[1], "strokeColor=#9E9E9E;dashed=1;strokeWidth=1.5;")
p.e(accs[1], accs[2], "strokeColor=#9E9E9E;dashed=1;strokeWidth=1.5;")
for x, kind, lab, sz in ((70, "phone", "Teléfono IP<br>VLAN 50", 34), (165, "pc", "PC<br>VLAN 10-40", 38),
                         (265, "ap", "AP invitados<br>VLAN 60", 40), (370, "printer", "Impresoras", 38)):
    p.icon(kind, x, 450, lab, size=sz)
p.v("rounded=1;whiteSpace=wrap;html=1;fillColor=#E8F5E9;strokeColor=#2E7D32;fontSize=10;fontStyle=1;",
    465, 448, 115, 44, "ESP32 riego (IoT)<br>VLAN 70")
pve1 = p.icon("server", 75, 600, "PVE-01", size=55)
pve2 = p.icon("server", 150, 600, "PVE-02", size=55)
nas = p.icon("storage", 410, 600, "NAS respaldo", size=45)
ups = p.icon("ups", 510, 600, "UPS x3", size=45)
p.e(pve1, pve2, "strokeColor=#2E7D32;strokeWidth=1.5;dashed=1;")
p.e(dist, pve1, "strokeColor=#1565C0;strokeWidth=2;", "VLAN 80", pts=[(30, 185), (30, 627)])
p.text(60, 700, 520, 150,
       "<b>Clúster Proxmox VE</b> (2 × HPE DL20 Gen11, alta disponibilidad de VM)<br>"
       "• DC01 / DC02: Active Directory y DNS interno<br>• SRV-ISSABEL: central IP e IVR (192.168.40.226)<br>"
       "• SRV-ARCHIVOS y SRV-IMPRESION<br>• NAS Synology: respaldo diario, réplica en Talca",
       fs=10, color="#263238")
p.text(40, 875, 560, 105, "Modelo jerárquico de 2 capas (núcleo colapsado): el acceso se conecta a la distribución "
       "por EtherChannel LACP y Rapid-PVST+ bloquea los enlaces redundantes; si falla un cable o un switch de acceso, "
       "la sede sigue operando.", fs=10.5, color="#263238")

# Edge
p.box(650, 90, 300, 430, "ENTERPRISE EDGE", "#FFF3E0", "#E65100")
p.v(OSPF_HALO, 675, 145, 80, 80)
rt = p.icon("router", 690, 160, "R-TEMUCO" + SUB + "<br>RID 1.1.1.1 · ASBR</span>")
fw = p.icon("firewall", 860, 160, "FW-TEMUCO" + SUB + "<br>OPNsense · IDS</span>")
fxo = p.icon("router_with_voice", 865, 330, "GW-FXO" + SUB + "<br>2 líneas PSTN</span>", size=40)
p.e(dist, rt, TRUNK, "802.1Q")
p.e(rt, fw, WAN)
p.text(665, 420, 270, 95, "PAT · hub de túneles GRE/IPsec · VPN a AWS · ACL entre VLAN · firewall perimetral con "
       "IDS Suricata", fs=10, color="#4E342E")

# Service provider edge
p.box(980, 90, 350, 430, "SERVICE PROVIDER EDGE", "#F3E5F5", "#6A1B9A")
inet = p.icon("cloud", 1060, 140, "Internet / ISP" + SUB + "<br>IP pública por sede</span>", size=110)
sipc = p.icon("cloud", 1000, 300, "Proveedor VoIP" + SUB + "<br>troncal SIP (DID)</span>", size=55, lp="right")
pstnc = p.icon("cloud", 1000, 400, "PSTN" + SUB + "<br>respaldo de voz</span>", size=55, lp="right")
p.e(fw, inet, WAN, "WAN")
p.e(fw, sipc, SIP, "", pts=[(965, 185), (965, 327)])
p.e(fxo, pstnc, "strokeColor=#00897B;strokeWidth=1.5;", "", pts=[(940, 350), (940, 427)])
p.text(1150, 300, 170, 200, "<b>WAN por sede</b><br>Temuco 203.0.113.18<br>Talca 203.0.113.6<br>Concepción 203.0.113.10"
       "<br>Los Ángeles 203.0.113.14", fs=10, color="#4A148C")

# Data center (AWS)
p.box(1360, 90, 620, 430, "ENTERPRISE DATA CENTER · Nube AWS (VPC 10.40.0.0/16)", "#E8F5E9", "#2E7D32")
s1 = p.icon("dns", 1440, 150, "SRV-AGROPRODEL" + SUB + "<br>Web · DNS · FTPS<br>10.40.1.10</span>", size=60)
s2 = p.icon("server", 1620, 150, "SRV-NOC" + SUB + "<br>Zabbix · Grafana<br>10.40.1.30</span>", size=60)
s3 = p.icon("secure_server", 1800, 150, "SRV-SIEM" + SUB + "<br>Wazuh<br>10.40.1.20</span>", size=60)
tg = p.icon("cell", 1905, 330, "Telegram" + SUB + "<br>alertas</span>", size=50)
p.e(s3, tg, "strokeColor=#2E7D32;strokeWidth=1.5;endArrow=classic;dashed=1;")
p.e(inet, s1, WAN, "IGW", pts=[(1300, 160), (1400, 160)])
p.e(rt, s2, VPN, "VPN IPsec IKEv2 (gestión)", pts=[(715, 122), (1637, 122)])
p.text(1380, 300, 480, 200, "<b>Servicios esenciales virtualizados</b> (WEB, DNS, FTP)<br><b>SOC:</b> disponibilidad "
       "(Zabbix/Grafana), eventos de seguridad (Wazuh) y alertas al celular.<br>Grupos de seguridad con mínimo "
       "privilegio; administración solo por la VPN.", fs=10.5, color="#1B5E20")

# Branches
p.box(650, 560, 1330, 430, "ENTERPRISE BRANCH · Sucursales", "#E0F7FA", "#00838F")
for k, (nom, tag, red, us, rid, tn, tnet, caps, col) in enumerate(SEDES):
    x0 = 665 + k * 445
    p.box(x0, 600, 420, 375, f"{nom} · {red} · {us} usuarios", "#FFFFFF", "#4DD0E1", dashed=True, fs=11)
    p.v(OSPF_HALO, x0 + 315, 635, 80, 80)
    r = p.icon("router", x0 + 330, 650, f"R-{tag}" + SUB + f"<br>RID {rid} · Tunnel{tn}<br>PAT · DHCP</span>", lp="left")
    d = p.icon("l2_switch", x0 + 185, 765, f"DIST-{tag}", lp="right")
    c1 = p.icon("l2_switch", x0 + 70, 875, f"ACC1 · {caps[0]}")
    c2 = p.icon("l2_switch", x0 + 300, 875, f"ACC2 · {caps[1]}")
    p.e(r, d, TRUNK)
    p.e(d, c1, LACP)
    p.e(d, c2, LACP)
    p.e(c1, c2, "strokeColor=#9E9E9E;dashed=1;strokeWidth=1.5;")
    if tag == "TALCA":
        nr = p.icon("storage", x0 + 30, 770, "NAS réplica", size=36)
        p.e(d, nr, "strokeColor=#78909C;strokeWidth=1.5;")
    p.e(r, inet, WAN, "", pts=[(x0 + 355, 538), (1345, 538), (1345, 210)])
    p.e(r, rt, GRE, "GRE/IPsec ×3" if k == 0 else "", pts=[(x0 + 405, 675), (x0 + 405, 552), (635, 552), (635, 205)])

legend(p, 1005, [L_LACP, L_TRK, L_WAN, L_GRE, L_VPN, L_STP, L_SIP, L_OSPF],
       extra="Cada sucursal: 10 teléfonos IP · PC por departamento · AP de invitados (VLAN 60, solo Internet) · "
             "ESP32 de riego (VLAN 70) · ATA con línea analógica de emergencia. Doble pila IPv4/IPv6 en todas las sedes.")

# -----------------------------------------------------------------------------------------------------
# PAGINA 3: ENRUTAMIENTO (CAPA 3) - OSPF
# -----------------------------------------------------------------------------------------------------
o = Page("3 - Enrutamiento OSPF (capa 3)", 2000, 1150)
o.text(20, 10, 1600, 34, "Enrutamiento entre sedes — OSPF sobre túneles GRE/IPsec (topología hub-and-spoke)",
       fs=20, color="#0D47A1", bold=True)
o.text(20, 44, 1900, 22, "Los túneles GRE transportan OSPF (multicast) y IPsec cifra todo el tráfico; Internet es solo "
       "el transporte (underlay)", fs=12, color="#455A64")
o.v("rounded=1;arcSize=4;whiteSpace=wrap;html=1;fillColor=#FFFDE7;strokeColor=#F9A825;strokeWidth=3;dashed=1;"
    "verticalAlign=top;align=left;spacingLeft=14;spacingTop=8;fontSize=16;fontStyle=1;fontColor=#E65100;",
    40, 90, 1340, 860, "OSPF proceso 1 · ÁREA 0 (backbone)")
hub = o.icon("router", 678, 190, "R-TEMUCO (hub · ASBR)" + SUB + "<br>RID 1.1.1.1<br>LAN 192.168.40.0/24 (pasiva)</span>",
             size=64, lp="left")
o.v("rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF3E0;strokeColor=#E65100;fontSize=10;", 770, 120, 320, 50,
    "Tunnel1 172.16.0.1 · Tunnel2 172.16.0.5 · Tunnel3 172.16.0.9<br>origen de todos: WAN de Temuco")
for k, (nom, tag, red, us, rid, tn, tnet, caps, col) in enumerate(SEDES):
    x = 198 + k * 480
    sp = o.icon("router", x, 690, f"R-{tag}" + SUB + f"<br>RID {rid}<br>LAN {red} (pasiva)</span>", size=64)
    a, b = tnet.split("/")[0].rsplit(".", 1)
    ip_hub, ip_sp = f"{a}.{int(b) + 1}", f"{a}.{int(b) + 2}"
    o.e(hub, sp, f"strokeColor={col};strokeWidth=3.5;dashed=1;dashPattern=10 5;",
        f"<b>Tunnel{tn} · {tnet}</b><br>{ip_hub} ↔ {ip_sp}<br>GRE + IPsec AES-256")
o.text(70, 820, 1290, 115,
       "<b>Base de datos OSPF (LSDB):</b> 4 routers · 3 enlaces punto a punto (túneles) · 1 ruta externa (AWS).<br>"
       "<b>Interfaces LAN pasivas:</b> se anuncian las redes, pero no se envían hellos hacia los usuarios (nadie puede "
       "inyectar rutas desde una VLAN).<br><b>IPv6:</b> OSPFv3 con la misma topología (doble pila).",
       fs=11, color="#3E2723")
o.box(1420, 90, 540, 300, "Fuera del área: nube AWS", "#E8F5E9", "#2E7D32")
aws = o.icon("server", 1665, 150, "SRV-NOC · VPC 10.40.0.0/16" + SUB + "<br>(Zabbix, Grafana, Wazuh, servicios)</span>",
             size=60)
o.e(hub, aws, VPN, "VPN IKEv2 + ruta estática 10.40.0.0/16", pts=[(1100, 222), (1100, 180)])
o.text(1435, 280, 510, 105, "<b>R-TEMUCO es ASBR:</b> redistribuye la ruta estática de AWS en OSPF "
       "(<i>redistribute static subnets route-map RM-AWS</i>) como externa E2; así las 3 sucursales llegan a la nube "
       "a través de Temuco sin configurar nada en ellas.", fs=10.5, color="#1B5E20")
o.text(1420, 410, 540, 540,
       "<b>¿Por qué un área única?</b><br>Cisco recomienda dividir en áreas cuando la red crece (decenas de routers) "
       "para limitar el tamaño de la LSDB y el cálculo SPF. Con 4 routers, un área 0 es más simple, converge igual de "
       "rápido y evita ABR innecesarios.<br><br>"
       "<b>¿Por qué hub-and-spoke?</b><br>La telefonía y los servidores están en Temuco: todo el tráfico entre sedes "
       "pasa por la matriz. 3 túneles en vez de 6 (malla completa) simplifican la operación.<br><br>"
       "<b>¿Por qué GRE + IPsec?</b><br>IPsec solo no transporta multicast; GRE sí, y permite usar OSPF. IPsec cifra "
       "el túnel completo (AES-256).<br><br>"
       "<b>Escalabilidad:</b> Temuco se resume como 192.168.40.0/23 y una sucursal nueva solo agrega un túnel y una "
       "red /24 en el área 0.",
       fs=11, color="#263238", fill="#FFFFFF", stroke="#B0BEC5")
legend(o, 970, [L_GRE, L_VPN, L_OSPF, ("strokeColor=#1E88E5;strokeWidth=3.5;dashed=1;", "Color por sucursal")])

# -----------------------------------------------------------------------------------------------------
# PAGINA 4: LAN TEMUCO (capa 2 + servidores)
# -----------------------------------------------------------------------------------------------------
t = Page("4 - LAN casa matriz Temuco", 2000, 1250)
t.text(20, 10, 1600, 34, "LAN casa matriz Temuco — capa 2, usuarios y sala de servidores", fs=20, color="#0D47A1", bold=True)
t.text(20, 44, 1900, 22, "Distribución con núcleo colapsado · 3 switches de acceso · Rapid-PVST+ · EtherChannel LACP · "
       "QoS para voz", fs=12, color="#455A64")
# --- Enterprise Campus (Temuco) ---
t.box(20, 80, 820, 1030, "ENTERPRISE CAMPUS — Casa matriz Temuco · 192.168.40.0/23 (reserva 192.168.41.0/24)",
      "#E3F2FD", "#1565C0")
t.box(40, 125, 780, 150, "Distribución / núcleo colapsado", "#FFFFFF", "#90CAF9", dashed=True, fs=11)
t.box(40, 295, 780, 145, "Acceso (Building Access)", "#FFFFFF", "#90CAF9", dashed=True, fs=11)
t.box(40, 455, 780, 205, "Usuarios y dispositivos finales", "#FFFFFF", "#90CAF9", dashed=True, fs=11)
t.box(40, 675, 780, 250, "Sala de servidores — Server Farm (VLAN 80 · 192.168.40.224/28)", "#FFFFFF", "#90CAF9",
      dashed=True, fs=11)

dist = t.icon("l2_switch", 405, 160, "DIST-TEMUCO<br><span style='font-weight:normal'>Raíz Rapid-PVST+</span>")
a1 = t.icon("l2_switch", 145, 330, "ACC1-TEMUCO<br><span style='font-weight:normal'>48 PoE+</span>")
a2 = t.icon("l2_switch", 405, 330, "ACC2-TEMUCO<br><span style='font-weight:normal'>48 PoE+</span>")
a3 = t.icon("l2_switch", 665, 330, "ACC3-TEMUCO<br><span style='font-weight:normal'>24 PoE+</span>")
t.e(dist, a1, LACP, "Po1 · LACP")
t.e(dist, a2, LACP, "Po2 · LACP")
t.e(dist, a3, LACP, "Po3 · LACP")
t.e(a1, a2, "strokeColor=#9E9E9E;dashed=1;strokeWidth=1.5;", "enlace redundante (STP)")
t.e(a2, a3, "strokeColor=#9E9E9E;dashed=1;strokeWidth=1.5;")

# endpoints
ph1 = t.icon("phone", 75, 495, "Teléfonos IP<br>VLAN 50 (voz)", size=42)
pc1 = t.icon("pc", 175, 500, "PC (detrás del<br>teléfono) VLAN 10-40", size=46)
pc2 = t.icon("pc", 335, 500, "PC departamentos<br>VLAN 10/20/30/40", size=46)
ap = t.icon("ap", 470, 505, "AP CBW150AX<br>VLAN 60 invitados", size=50)
prn = t.icon("printer", 590, 500, "Impresoras<br>de red", size=46)
iot = t.v("rounded=1;whiteSpace=wrap;html=1;fillColor=#E8F5E9;strokeColor=#2E7D32;fontSize=10;fontStyle=1;",
          690, 495, 110, 46, "ESP32 + sensor<br>humedad (IoT)<br>VLAN 70")
t.text(690, 545, 125, 50, "Electroválvula 12 V<br>umbral → riego<br>aviso Telegram", fs=9, color="#2E7D32")
for a, b in ((a1, ph1), (a1, pc1), (a2, pc2), (a2, ap), (a3, prn), (a3, iot)):
    t.e(a, b, "strokeColor=#78909C;strokeWidth=1.5;")
t.text(55, 605, 760, 50,
       "<b>Dotación Temuco:</b> 88 usuarios (Siembra 20 · Cosecha 26 · Envasado 32 · Ventas 10) · 10 teléfonos IP · "
       "120 puertos de acceso (28 libres para crecer) · QoS voz DSCP EF + LLQ · RA Guard, BPDU Guard, PortFast",
       fs=10, color="#37474F")

# sala de servidores: bus VLAN 80 + cluster Proxmox + respaldo + energia
bus = t.v("rounded=1;html=1;fillColor=#1565C0;strokeColor=none;fontColor=#FFFFFF;fontSize=10;fontStyle=1;",
          60, 712, 740, 18, "Switch de distribución · VLAN 80 Servidores (gateway 192.168.40.225)")
t.e(dist, bus, "strokeColor=#1565C0;strokeWidth=2.5;", "", pts=[(30, 185), (30, 721)])
pve1 = t.icon("server", 85, 760, "PVE-01<br><span style='font-weight:normal'>HPE DL20 Gen11</span>", size=62)
pve2 = t.icon("server", 185, 760, "PVE-02<br><span style='font-weight:normal'>HPE DL20 Gen11</span>", size=62)
nas = t.icon("storage", 615, 755, "NAS-RESPALDO<br><span style='font-weight:normal'>Synology RS422+</span>", size=55)
ups = t.icon("ups", 730, 755, "UPS 1500 VA<br><span style='font-weight:normal'>x3 (rack)</span>", size=55)
for s_ in (pve1, pve2, nas):
    t.e(bus, s_, "strokeColor=#1565C0;strokeWidth=1.5;")
t.e(pve1, pve2, "strokeColor=#2E7D32;strokeWidth=1.5;dashed=1;", "clúster")
vms = ("<b>Clúster Proxmox VE (alta disponibilidad de VM)</b><br>"
       "• <b>DC01</b> Active Directory · DNS interno · GPO<br>"
       "• <b>DC02</b> controlador de dominio réplica<br>"
       "• <b>SRV-ISSABEL</b> central IP · 192.168.40.226 · IVR 1-4<br>"
       "• <b>SRV-ARCHIVOS</b> carpetas por departamento (permisos AD)<br>"
       "• <b>SRV-IMPRESION</b> cola de impresión y escaneo<br>"
       "Si un nodo falla, sus VM se reinician en el otro.")
t.text(268, 740, 305, 180, vms, fs=9.5, color="#263238", fill="#F5F9FF", stroke="#90CAF9")
t.text(598, 845, 220, 75, "Respaldo diario de VM y archivos (Active Backup), copia en Talca. UPS para servidores, "
       "NAS, firewall y router.", fs=9, color="#37474F")

vl = ("<b>VLAN por sede</b><br>10 Siembra y riego · 20 Cosecha y molienda · 30 Envasado y bodega · 40 Ventas · "
      "50 Voz · 60 Invitados (solo Internet) · 70 IoT riego · 80 Servidores · 99 Gestión · 999 Nativa<br>"
      "<b>DHCP:</b> en cada router (subinterfaces 802.1Q) · <b>DNS:</b> AD interno + reenvío · <b>Doble pila</b> IPv4/IPv6")
t.text(40, 935, 385, 165, vl, fs=9.5, color="#263238", fill="#FFFFFF", stroke="#90CAF9")
t.text(435, 935, 395, 170,
       "<b>Modelo jerárquico Cisco</b><br>"
       "• <b>Acceso:</b> usuarios, teléfonos, AP e IoT; seguridad de puerto y QoS.<br>"
       "• <b>Distribución / núcleo colapsado:</b> agrega el acceso con EtherChannel y es raíz de Rapid-PVST+; "
       "en una sede de este tamaño núcleo y distribución se unen sin perder escalabilidad.<br>"
       "• Si cae un enlace, STP converge en ~1-2 s; si cae un cable de un EtherChannel, el canal sigue arriba.",
       fs=9.5, color="#263238")


TEM = [("10", "Siembra y riego", "192.168.40.128/27", ".129"), ("20", "Cosecha y molienda", "192.168.40.0/26", ".1"),
       ("30", "Envasado y bodega", "192.168.40.64/26", ".65"), ("40", "Ventas", "192.168.40.160/28", ".161"),
       ("50", "Voz", "192.168.40.176/28", ".177"), ("60", "Invitados (solo Internet)", "192.168.40.192/28", ".193"),
       ("70", "IoT riego", "192.168.40.208/28", ".209"), ("80", "Servidores", "192.168.40.224/28", ".225"),
       ("99", "Gestión", "192.168.40.240/28", ".241")]
rows = "".join(f"<tr><td>{v}</td><td>{n}</td><td>{r}</td><td>{g}</td></tr>" for v, n, r, g in TEM)
t.text(870, 90, 1100, 330,
       "<b style='font-size:13px'>Direccionamiento Temuco (VLSM sobre 192.168.40.0/24 · reserva 192.168.41.0/24)</b>"
       "<table border='1' cellpadding='4' style='border-collapse:collapse;margin-top:6px;width:100%'>"
       "<tr style='background:#E3F2FD'><th>VLAN</th><th>Nombre</th><th>Red</th><th>Gateway (R-TEMUCO)</th></tr>"
       + rows + "</table>", fs=11, color="#263238")
t.text(870, 440, 1100, 330,
       "<b style='font-size:13px'>Capacidad de acceso</b><br>ACC1 48 PoE+ · ACC2 48 PoE+ · ACC3 24 PoE+ = 120 puertos "
       "para 92 equipos (88 usuarios + AP, IoT y 2 impresoras): 28 libres (30 %).<br>El PC se conecta detrás del "
       "teléfono IP: un solo punto de red por puesto.<br><br>"
       "<b style='font-size:13px'>Seguridad en el acceso</b><br>PortFast + BPDU Guard · RA Guard (IPv6) · VLAN nativa "
       "999 sin uso · puertos libres apagados en VLAN de cuarentena · ACL entre VLAN en el router.<br><br>"
       "<b style='font-size:13px'>Calidad de servicio</b><br>Voz marcada DSCP EF y cola de prioridad (LLQ) en el router; "
       "la marca se conserva dentro de los túneles.", fs=11, color="#263238", fill="#FFFFFF", stroke="#B0BEC5")
legend(t, 1125, [L_LACP, L_TRK, L_STP, ("strokeColor=#1565C0;strokeWidth=2.5;", "VLAN 80 servidores")])

# -----------------------------------------------------------------------------------------------------
# PAGINA 5: LAN SUCURSALES
# -----------------------------------------------------------------------------------------------------
b = Page("5 - LAN sucursales", 2000, 1250)
b.text(20, 10, 1600, 34, "LAN de sucursales — mismo diseño en las 3 sedes", fs=20, color="#0D47A1", bold=True)
b.text(20, 44, 1900, 22, "Router con subinterfaces 802.1Q (DHCP y gateway) · distribución + 2 accesos con EtherChannel "
       "LACP · el tamaño de los switches de acceso se ajusta a los usuarios de cada sede", fs=12, color="#455A64")
NETS = {"TALCA": [("10", "192.168.10.64/27"), ("20", "192.168.10.96/27"), ("30", "192.168.10.0/26"),
                  ("40", "192.168.10.128/28"), ("50", "192.168.10.144/28"), ("60", "192.168.10.160/28"),
                  ("70", "192.168.10.176/28"), ("99", "192.168.10.192/28")],
        "CONCEPCION": [("10", "192.168.20.0/27"), ("20", "192.168.20.32/27"), ("30", "192.168.20.64/27"),
                       ("40", "192.168.20.96/28"), ("50", "192.168.20.112/28"), ("60", "192.168.20.128/28"),
                       ("70", "192.168.20.144/28"), ("99", "192.168.20.160/28")],
        "LOS-ANGELES": [("10", "192.168.30.32/28"), ("20", "192.168.30.48/28"), ("30", "192.168.30.0/27"),
                        ("40", "192.168.30.64/28"), ("50", "192.168.30.80/28"), ("60", "192.168.30.96/28"),
                        ("70", "192.168.30.112/28"), ("99", "192.168.30.128/28")]}
VN = {"10": "Siembra", "20": "Cosecha", "30": "Envasado", "40": "Ventas", "50": "Voz", "60": "Invitados",
      "70": "IoT", "99": "Gestión"}
PUERTOS = {"TALCA": "80 equipos → 96 puertos (16 libres)", "CONCEPCION": "55 equipos → 72 puertos (17 libres)",
           "LOS-ANGELES": "35 equipos → 48 puertos (13 libres)"}
for k, (nom, tag, red, us, rid, tn, tnet, caps, col) in enumerate(SEDES):
    x0 = 20 + k * 655
    b.box(x0, 90, 635, 1015, f"{nom} · {red} · {us} usuarios", "#E0F7FA", "#00838F")
    r = b.icon("router", x0 + 292, 140, f"R-{tag}" + SUB + "<br>gateway · DHCP · PAT</span>", lp="right")
    d = b.icon("l2_switch", x0 + 292, 290, f"DIST-{tag}" + SUB + "<br>raíz Rapid-PVST+</span>", lp="right")
    c1 = b.icon("l2_switch", x0 + 120, 440, f"ACC1-{tag}" + SUB + f"<br>{caps[0]}</span>")
    c2 = b.icon("l2_switch", x0 + 465, 440, f"ACC2-{tag}" + SUB + f"<br>{caps[1]}</span>")
    b.e(r, d, TRUNK, "802.1Q")
    b.e(d, c1, LACP, "Po1")
    b.e(d, c2, LACP, "Po2")
    b.e(c1, c2, "strokeColor=#9E9E9E;dashed=1;strokeWidth=1.5;", "STP")
    for x, kind, lab, sz in ((x0 + 40, "phone", "Teléfono IP<br>VLAN 50", 34), (x0 + 140, "pc", "PC<br>VLAN 10-40", 38),
                             (x0 + 240, "ap", "AP invitados<br>VLAN 60", 40), (x0 + 345, "printer", "Impresoras", 38)):
        b.icon(kind, x, 570, lab, size=sz)
    b.v("rounded=1;whiteSpace=wrap;html=1;fillColor=#E8F5E9;strokeColor=#2E7D32;fontSize=10;fontStyle=1;",
        x0 + 450, 568, 120, 44, "ESP32 riego (IoT)<br>VLAN 70")
    if tag == "TALCA":
        nr = b.icon("storage", x0 + 40, 290, "NAS réplica" + SUB + "<br>respaldo fuera de sitio</span>", size=40)
        b.e(d, nr, "strokeColor=#78909C;strokeWidth=1.5;")
    rows = "".join(f"<tr><td>{v}</td><td>{VN[v]}</td><td>{n}</td></tr>" for v, n in NETS[tag])
    b.text(x0 + 20, 660, 595, 300, "<b>Direccionamiento</b><table border='1' cellpadding='3' "
           "style='border-collapse:collapse;margin-top:4px;width:100%'><tr style='background:#B2EBF2'><th>VLAN</th>"
           "<th>Nombre</th><th>Red</th></tr>" + rows + "</table>", fs=10.5, color="#263238")
    b.text(x0 + 20, 965, 595, 130, f"<b>Acceso:</b> {PUERTOS[tag]}<br><b>Túnel a Temuco:</b> Tunnel{tn} {tnet} · "
           f"OSPF RID {rid}<br><b>Voz de emergencia:</b> ATA con línea analógica local si se cae el túnel.",
           fs=10.5, color="#006064", fill="#FFFFFF", stroke="#4DD0E1")
legend(b, 1125, [L_LACP, L_TRK, L_STP])
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
    f.write('<mxfile host="drawio" version="24.7.17">' + "".join(pg.xml() for pg in (q, p, o, t, b)) + "</mxfile>")
print("ok", OUT)
