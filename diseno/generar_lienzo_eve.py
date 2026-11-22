W, H = 1600, 1040
N = {}   # nombre -> (x, y, tipo, sub)
def n(name, x, y, kind, sub=''): N[name] = (x, y, kind, sub)
L = []   # (a, b, estilo, etiqueta)
def l(a, b, st='lan', lab=''): L.append((a, b, st, lab))
# ---------------- Temuco
n('CLIENTE-WIFI', 70, 250, 'pc', 'VLAN 60'); n('AP-TEM', 165, 250, 'ap', 'VLAN 60'); n('SRV-ISSABEL', 260, 250, 'srv', 'VLAN 80 · .40.226')
n('RACK-FISICO', 370, 120, 'cloud', 'teléfono y PC físicos'); n('SW-PUENTE', 480, 120, 'sw', 'puente de laboratorio')
n('DIST-TEMUCO', 290, 430, 'sw', 'raíz Rapid-PVST+')
n('ACC1-TEMUCO', 150, 640, 'sw'); n('ACC2-TEMUCO', 430, 640, 'sw')
for i, (nm, k, sub) in enumerate([('PC-V10-TEM', 'pc', 'VLAN 10'), ('PC-V20-TEM', 'pc', 'VLAN 20'), ('TEL-V50-TEM', 'tel', 'VLAN 50')]):
    n(nm, 60 + i * 90, 840, k, sub); l('ACC1-TEMUCO', nm)
for i, (nm, k, sub) in enumerate([('PC-V30-TEM', 'pc', 'VLAN 30'), ('PC-V40-TEM', 'pc', 'VLAN 40'), ('PC-V10B-TEM', 'pc', 'VLAN 10')]):
    n(nm, 340 + i * 90, 840, k, sub); l('ACC2-TEMUCO', nm)
for a in ('CLIENTE-WIFI', 'AP-TEM', 'SRV-ISSABEL'): l(a, 'DIST-TEMUCO')
l('RACK-FISICO', 'SW-PUENTE', 'puente'); l('SW-PUENTE', 'DIST-TEMUCO', 'puente')
l('DIST-TEMUCO', 'ACC1-TEMUCO', 'po', 'Po1'); l('DIST-TEMUCO', 'ACC2-TEMUCO', 'po', 'Po2'); l('ACC1-TEMUCO', 'ACC2-TEMUCO', 'po', 'Po3')
# ---------------- Edge
n('MGMT', 590, 300, 'cloud', 'Web GUI'); n('FW-TEMUCO', 680, 300, 'fw', 'OPNsense'); n('R-TEMUCO', 680, 430, 'rt', 'hub GRE/IPsec')
l('MGMT', 'FW-TEMUCO', 'mgmt'); l('FW-TEMUCO', 'R-TEMUCO', 'wan'); l('R-TEMUCO', 'DIST-TEMUCO', 'lan', 'troncal 802.1Q')
# ---------------- ISP
n('ISP', 880, 300, 'rt', 'IOL L3 · NAT'); n('INTERNET', 880, 440, 'cloud', 'salida real')
l('FW-TEMUCO', 'ISP', 'wan'); l('ISP', 'INTERNET', 'mgmt')
# ---------------- Sucursales
blocks = [('CON', 'CONCEPCION', 'Concepción', 255, '192.168.20.0/24', 'Tunnel2'), ('TAL', 'TALCA', 'Talca', 520, '192.168.10.0/24', 'Tunnel1'),
          ('LAN', 'LOS-ANGELES', 'Los Ángeles', 785, '192.168.30.0/24', 'Tunnel3')]
for ab, full, _, cy, _, tun in blocks:
    n('R-' + full, 1060, cy, 'rt', tun); n('DIST-' + ab, 1190, cy, 'sw'); n('ACC1-' + ab, 1330, cy - 62, 'sw'); n('ACC2-' + ab, 1330, cy + 62, 'sw')
    l('ISP', 'R-' + full, 'wan'); l('R-' + full, 'DIST-' + ab); l('DIST-' + ab, 'ACC1-' + ab, 'po', 'Po1'); l('DIST-' + ab, 'ACC2-' + ab, 'po', 'Po2')
    l('ACC1-' + ab, 'ACC2-' + ab, 'po', 'Po3')
    for i, (nm, k) in enumerate([('PC-V10', 'pc'), ('PC-V20', 'pc'), ('TEL-V50', 'tel')]):
        nn = '%s-%s' % (nm, ab); n(nn, 1490, cy - 100 + i * 33, k); l('ACC1-' + ab, nn)
    for i, (nm, k) in enumerate([('PC-V30', 'pc'), ('PC-V40', 'pc'), ('AP', 'ap')]):
        nn = '%s-%s' % (nm, ab); n(nn, 1490, cy + 34 + i * 33, k); l('ACC2-' + ab, nn)
l('SW-PUENTE', 'DIST-CON', 'puente', 'VLAN 210→10 · 250→50')

COL = {'lan': '#6aa6ff', 'po': '#6aa6ff', 'wan': '#ff6b6b', 'mgmt': '#b48cff', 'puente': '#f5c542'}
ICON = {'rt': '#2f6fe0', 'sw': '#2f6fe0', 'fw': '#e0443a', 'srv': '#5b6b80', 'pc': '#3c4a5e', 'tel': '#e08a2f', 'ap': '#20a4a4', 'cloud': '#8da2bf'}
o = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" font-family="Arial, Helvetica, sans-serif">' % (W, H, W, H),
     '<rect width="100%" height="100%" fill="#0f1726"/>']
for gx in range(0, W, 40): o.append('<line x1="%d" y1="0" x2="%d" y2="%d" stroke="#16223a" stroke-width="1"/>' % (gx, gx, H))
for gy in range(0, H, 40): o.append('<line x1="0" y1="%d" x2="%d" y2="%d" stroke="#16223a" stroke-width="1"/>' % (gy, W, gy))
def zone(x, y, w, h, col, title, sub=''):
    o.append('<rect x="%d" y="%d" width="%d" height="%d" rx="12" fill="%s" fill-opacity="0.06" stroke="%s" stroke-width="2" stroke-dasharray="8 6"/>' % (x, y, w, h, col, col))
    o.append('<text x="%d" y="%d" fill="%s" font-size="15" font-weight="bold">%s</text>' % (x + 14, y + 24, col, title))
    if sub: o.append('<text x="%d" y="%d" fill="%s" font-size="13">%s</text>' % (x + 14, y + 42, col, sub))
o.append('<text x="30" y="40" fill="#ffffff" font-size="24" font-weight="bold">AGROPRODEL LTDA. · Lienzo de laboratorio EVE-NG</text>')
o.append('<text x="30" y="64" fill="#9fb0c8" font-size="14">Orden sugerido: cables rectos y sin cruces · casa matriz · edge · proveedor · sucursales</text>')
zone(20, 80, 530, 890, '#4f8cff', 'CASA MATRIZ TEMUCO', '192.168.40.0/24')
zone(560, 80, 200, 890, '#ff9a3c', 'EDGE')
zone(770, 80, 220, 890, '#ff6b6b', 'PROVEEDOR (ISP)')
zone(1000, 80, 580, 890, '#3ccf91', 'SUCURSALES')
o.append('<rect x="30" y="200" width="290" height="100" rx="8" fill="none" stroke="#4f8cff" stroke-opacity="0.5" stroke-dasharray="4 4"/>')
o.append('<text x="50" y="216" fill="#8fb4ff" font-size="11">Servicios · VLAN 80 / AP y clientes · VLAN 60</text>')
for ab, full, nm, cy, net, _ in blocks:
    o.append('<rect x="1012" y="%d" width="556" height="255" rx="10" fill="none" stroke="#3ccf91" stroke-opacity="0.55"/>' % (cy - 135 + 5))
    o.append('<text x="1024" y="%d" fill="#7fe3b5" font-size="13" font-weight="bold">Sucursal %s</text>' % (cy - 112, nm))
    o.append('<text x="1556" y="%d" fill="#7fe3b5" font-size="12" text-anchor="end">%s</text>' % (cy - 112, net))
# AWS
o.append('<rect x="790" y="600" width="180" height="150" rx="10" fill="#ff9900" fill-opacity="0.08" stroke="#ff9900" stroke-width="2" stroke-dasharray="6 5"/>')
o.append('<line x1="880" y1="465" x2="880" y2="600" stroke="#ff9900" stroke-width="2" stroke-dasharray="6 5"/>')
for i, t in enumerate(['NUBE AWS (fuera de EVE)', 'VPC 10.40.0.0/16', 'SRV-AGROPRODEL: WEB·DNS·FTPS', 'SRV-NOC: Zabbix·Grafana', 'SRV-SIEM: Wazuh', 'VPN IKEv2 desde R-TEMUCO']):
    o.append('<text x="880" y="%d" fill="%s" font-size="%d" text-anchor="middle"%s>%s</text>' % (625 + i * 21, '#ffb84d' if i == 0 else '#ffd9a0', 12 if i == 0 else 11, ' font-weight="bold"' if i == 0 else '', t))
# enlaces
for a, b, st, lab in L:
    x1, y1 = N[a][:2]; x2, y2 = N[b][:2]
    dash = ' stroke-dasharray="7 5"' if st == 'puente' else ''
    if st == 'po':
        import math
        dx, dy = x2 - x1, y2 - y1; d = math.hypot(dx, dy); px, py = -dy / d * 3, dx / d * 3
        for s in (1, -1):
            o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.8"/>' % (x1 + s * px, y1 + s * py, x2 + s * px, y2 + s * py, COL[st]))
    else:
        o.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="2"%s/>' % (x1, y1, x2, y2, COL[st], dash))
    if lab:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        if st == 'puente' and b == 'DIST-CON': mx, my = x1 + (x2 - x1) * 0.45, y1 + (y2 - y1) * 0.45
        w = 7 * len(lab) + 10
        o.append('<rect x="%.0f" y="%.0f" width="%d" height="17" rx="4" fill="%s"/>' % (mx - w / 2, my - 9, w, '#2a3b5c' if st != 'puente' else '#5c4a12'))
        o.append('<text x="%.0f" y="%.0f" fill="#ffffff" font-size="11" text-anchor="middle">%s</text>' % (mx, my + 4, lab))
# nodos
def node(name, x, y, k, sub):
    c = ICON[k]
    if k == 'cloud':
        o.append('<ellipse cx="%d" cy="%d" rx="30" ry="18" fill="%s"/>' % (x, y, c))
    elif k in ('pc', 'tel', 'ap'):
        o.append('<rect x="%d" y="%d" width="24" height="18" rx="3" fill="%s" stroke="#9fb0c8"/>' % (x - 12, y - 9, c))
    else:
        o.append('<rect x="%d" y="%d" width="40" height="40" rx="%d" fill="%s" stroke="#cfe0ff" stroke-width="1.5"/>' % (x - 20, y - 20, 20 if k == 'rt' else 6, c))
        sym = {'rt': '⨯', 'sw': '⇄', 'fw': '▦', 'srv': '≡'}[k]
        o.append('<text x="%d" y="%d" fill="#ffffff" font-size="20" text-anchor="middle">%s</text>' % (x, y + 7, sym))
    small = k in ('pc', 'tel', 'ap')
    if small and x > 1400:   # equipos de usuario de sucursales: nombre a la derecha
        o.append('<text x="%d" y="%d" fill="#dfe8f7" font-size="11">%s</text>' % (x + 18, y + 4, name))
        return
    ty = y + (24 if small else (30 if k == 'cloud' else 36))
    o.append('<text x="%d" y="%d" fill="#ffffff" font-size="%d" font-weight="bold" text-anchor="middle">%s</text>' % (x, ty, 11 if small else 12, name))
    if sub: o.append('<text x="%d" y="%d" fill="#9fb0c8" font-size="10" text-anchor="middle">%s</text>' % (x, ty + 13, sub))
for nm, (x, y, k, sub) in N.items(): node(nm, x, y, k, sub)
# leyenda
items = [('lan', 'Enlace LAN / acceso', False), ('po', 'EtherChannel LACP', True), ('wan', 'Enlace WAN', False), ('mgmt', 'Gestión / Internet', False), ('puente', 'Puente de laboratorio', False)]
lx = 40
for st, t, dbl in items:
    yy = 1012
    if dbl:
        o.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1.8"/>' % (lx, yy - 3, lx + 30, yy - 3, COL[st]))
        o.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1.8"/>' % (lx, yy + 3, lx + 30, yy + 3, COL[st]))
    else:
        o.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="2"%s/>' % (lx, yy, lx + 30, yy, COL[st], ' stroke-dasharray="7 5"' if st == 'puente' else ''))
    o.append('<text x="%d" y="%d" fill="#cfd8e6" font-size="12">%s</text>' % (lx + 38, yy + 4, t)); lx += 60 + 7 * len(t)
o.append('<text x="1570" y="1016" fill="#ffb07a" font-size="12" text-anchor="end">Túneles GRE + IPsec (lógicos): Talca, Concepción y Los Ángeles → R-TEMUCO · OSPF área 0</text>')
o.append('</svg>')
open('lienzo.svg', 'w').write('\n'.join(o))
