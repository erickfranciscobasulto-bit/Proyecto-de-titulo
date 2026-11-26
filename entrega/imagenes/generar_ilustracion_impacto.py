import random
random.seed(7)
o=[]; a=o.append
a('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" preserveAspectRatio="xMidYMid slice" font-family="Arial, Helvetica, sans-serif">
<defs>
 <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#07152E"/><stop offset=".28" stop-color="#1B2A5A"/><stop offset=".48" stop-color="#5B3577"/>
  <stop offset=".62" stop-color="#C4476A"/><stop offset=".72" stop-color="#F0803C"/><stop offset=".8" stop-color="#FFC56B"/></linearGradient>
 <radialGradient id="sun" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFF6D8"/><stop offset=".18" stop-color="#FFE39A"/><stop offset=".45" stop-color="#FFB24D" stop-opacity=".55"/><stop offset="1" stop-color="#FF8A3D" stop-opacity="0"/></radialGradient>
 <linearGradient id="field" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F7C25A"/><stop offset=".35" stop-color="#C77A1E"/><stop offset="1" stop-color="#3B1D08"/></linearGradient>
 <linearGradient id="silo" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#1A1830"/><stop offset=".55" stop-color="#2B2747"/><stop offset=".85" stop-color="#7A4A55"/><stop offset="1" stop-color="#E7925A"/></linearGradient>
 <linearGradient id="bld" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#161429"/><stop offset=".8" stop-color="#241F3D"/><stop offset="1" stop-color="#6B4250"/></linearGradient>
 <linearGradient id="fade" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#07152E" stop-opacity="FADE0"/><stop offset=".4" stop-color="#07152E" stop-opacity="FADE1"/><stop offset=".6" stop-color="#07152E" stop-opacity="0"/></linearGradient>
 <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
 <pattern id="hex" width="56" height="48.5" patternUnits="userSpaceOnUse"><path d="M14,0 L42,0 L56,24.25 L42,48.5 L14,48.5 L0,24.25Z" fill="none" stroke="#6FD3FF" stroke-width=".6" opacity=".18"/></pattern>
</defs>
<rect width="1600" height="900" fill="url(#sky)"/>
<rect width="1600" height="560" fill="url(#hex)" opacity=".7"/>''')
for _ in range(140):
    x=random.uniform(0,1600); y=random.uniform(0,330); r=random.choice([.6,.8,1,1.3,1.7])
    a('<circle cx="%.0f" cy="%.0f" r="%.1f" fill="#fff" opacity="%.2f"/>'%(x,y,r,random.uniform(.3,.9)))
a('<circle cx="1000" cy="575" r="330" fill="url(#sun)"/><circle cx="1000" cy="585" r="85" fill="#FFF1C4" opacity=".95"/>')
a('<polygon points="0,560 120,470 220,520 360,420 470,500 600,430 720,520 860,440 1000,515 1140,430 1260,500 1400,420 1520,490 1600,450 1600,600 0,600" fill="#3E2A55" opacity=".85"/>')
a('<polygon points="0,590 180,520 330,570 500,505 700,575 900,520 1100,580 1300,515 1460,570 1600,530 1600,620 0,620" fill="#2A1E40"/>')
a('<path d="M0,610 C400,590 1200,590 1600,610 L1600,900 L0,900Z" fill="url(#field)"/>')
for k in range(-12,13):
    a('<path d="M1000,600 L%d,900" stroke="#FFD98A" stroke-width="2" opacity=".22"/>'%(1000+k*170))
silos=[(690,300,62),(756,250,74),(834,280,64),(902,330,56)]
for x,top,w in silos:
    a('<rect x="%d" y="%d" width="%d" height="%d" fill="url(#silo)"/>'%(x,top,w,612-top))
    a('<polygon points="%d,%d %d,%d %d,%d" fill="#1C1A33"/>'%(x,top,x+w/2,top-30,x+w,top))
    for yy in range(top+40,600,70): a('<rect x="%d" y="%d" width="%d" height="4" fill="#E7925A" opacity=".35"/>'%(x,yy,w))
EX=972
a('<rect x="%d" y="210" width="56" height="402" fill="url(#bld)"/><polygon points="%d,210 %d,178 %d,210" fill="#1C1A33"/>'%(EX,EX-4,EX+28,EX+60))
a('<polygon points="%d,250 1090,330 1090,345 %d,265" fill="#1C1A33"/>'%(EX+56,EX+56))
for yy in range(240,600,44):
    a('<rect x="%d" y="%d" width="13" height="18" fill="#FFD27A" opacity=".85"/>'%(EX+8,yy)); a('<rect x="%d" y="%d" width="13" height="18" fill="#FFD27A" opacity=".6"/>'%(EX+32,yy))
a('<rect x="1050" y="380" width="300" height="232" fill="url(#bld)"/><polygon points="1040,385 1200,310 1360,385" fill="#151327"/>')
for r_ in range(3):
    for c_ in range(6):
        lit=random.random()<.75
        a('<rect x="%d" y="%d" width="30" height="26" fill="%s"/>'%(1072+c_*46,450+r_*48,'#FFD27A' if lit else '#2F2A4A'))
a('<g filter="url(#glow)"><rect x="1085" y="395" width="230" height="40" rx="4" fill="#0D1B3A" stroke="#6FD3FF" stroke-width="2"/></g>')
a('<text x="1200" y="423" font-size="22" font-weight="bold" fill="#FFFFFF" text-anchor="middle" letter-spacing="3">AGROPRODEL</text>')
a('<g transform="translate(1440,330)"><polygon points="22,0 0,282 44,282" fill="none" stroke="#151327" stroke-width="6"/><g stroke="#151327" stroke-width="4"><line x1="8" y1="200" x2="36" y2="200"/><line x1="13" y1="120" x2="31" y2="120"/><line x1="17" y1="60" x2="27" y2="60"/></g>')
a('<circle cx="22" cy="0" r="6" fill="#FF4B4B" filter="url(#glow)"/><g fill="none" stroke="#6FD3FF" stroke-width="4" stroke-linecap="round" filter="url(#glow)"><path d="M-6,-16 A32,32 0 0 1 50,-16"/><path d="M-22,-32 A56,56 0 0 1 66,-32" opacity=".7"/></g></g>')
import sys
TIT = sys.argv[1] == 'titulo'
nodes={'Temuco':(1200,300),'Talca':(330 if not TIT else 560,250 if not TIT else 230),'Concepción':(560 if not TIT else 720,150 if not TIT else 120),'Los Ángeles':(820 if not TIT else 900,215 if not TIT else 190),'AWS':(1350,140)}
links=[('Temuco','Talca'),('Temuco','Concepción'),('Temuco','Los Ángeles')]
a('<g filter="url(#glow)">')
for p,q in links:
    (x1,y1),(x2,y2)=nodes[p],nodes[q]; mx,my=(x1+x2)/2,min(y1,y2)-70
    a('<path d="M%d,%d Q%d,%d %d,%d" fill="none" stroke="#6FD3FF" stroke-width="2.4" stroke-dasharray="10 7" opacity=".9"/>'%(x1,y1,mx,my,x2,y2))
a('<path d="M1200,300 Q1250,180 1300,150" fill="none" stroke="#6FD3FF" stroke-width="2.4" stroke-dasharray="10 7"/>')
a('<line x1="1462" y1="318" x2="1380" y2="170" stroke="#6FD3FF" stroke-width="2" stroke-dasharray="6 6" opacity=".8"/>')
a('<line x1="1200" y1="300" x2="1200" y2="392" stroke="#6FD3FF" stroke-width="2" stroke-dasharray="6 6" opacity=".8"/>')
for n,(x,y) in nodes.items():
    if n=='AWS': continue
    a('<circle cx="%d" cy="%d" r="%d" fill="#0D1B3A" stroke="#6FD3FF" stroke-width="3"/><circle cx="%d" cy="%d" r="5" fill="#BFEFFF"/>'%(x,y,13 if n=='Temuco' else 10,x,y))
a('</g>')
for n,(x,y) in nodes.items():
    if n=='AWS': continue
    a('<text x="%d" y="%d" font-size="17" font-weight="bold" fill="#DDF5FF" text-anchor="middle" letter-spacing="1">%s</text>'%(x,y-22,n.upper()))
a('<g transform="translate(1290,95)" filter="url(#glow)"><path d="M30,70 C5,70 0,45 18,36 C16,12 48,4 62,22 C74,0 116,6 118,34 C142,36 144,70 118,70Z" fill="#0D1B3A" stroke="#6FD3FF" stroke-width="3"/></g>')
a('<text x="1361" y="150" font-size="14" font-weight="bold" fill="#DDF5FF" text-anchor="middle">NUBE · SOC</text>')
def stalk(x,base,hgt,sc,ang):
    s='<g transform="translate(%d,%d) rotate(%d) scale(%.2f)">'%(x,base,ang,sc)
    s+='<line x1="0" y1="0" x2="0" y2="-%d" stroke="#2A1405" stroke-width="3"/>'%hgt
    for k in range(6):
        yy=-hgt+10+k*13
        s+='<ellipse cx="-6" cy="%d" rx="6" ry="11" transform="rotate(-28 -6 %d)" fill="#3A1C07" stroke="#FFB347" stroke-width="1.2"/>'%(yy,yy)
        s+='<ellipse cx="6" cy="%d" rx="6" ry="11" transform="rotate(28 6 %d)" fill="#3A1C07" stroke="#FFB347" stroke-width="1.2"/>'%(yy,yy)
    s+='<line x1="0" y1="-%d" x2="0" y2="-%d" stroke="#FFB347" stroke-width="1.2"/>'%(hgt,hgt+40)
    return s+'</g>'
for _ in range(70):
    x=random.uniform(-20,1620)
    if 250<x<1350 and random.random()<.75: continue
    a(stalk(x,905,random.uniform(110,230),random.uniform(.8,1.3),random.uniform(-12,12)))
a('<rect width="1600" height="900" fill="url(#fade)"/>')
s='\n'.join(o)
if TIT:
    s=s.replace('FADE0','.92').replace('FADE1','.55')
    s+='''
 <text x="90" y="300" font-size="20" fill="#FFC56B" letter-spacing="6" font-weight="bold">TRIGO · HARINAS · TECNOLOGÍA</text>
 <text x="86" y="382" font-size="80" font-weight="bold" fill="#FFFFFF" letter-spacing="3">AGROPRODEL</text>
 <text x="90" y="425" font-size="28" fill="#DDF5FF" letter-spacing="2">Ltda.</text>
 <rect x="92" y="455" width="120" height="5" fill="#FFC56B"/>
 <text x="92" y="505" font-size="25" fill="#FFFFFF">Una plataforma tecnológica para cuatro sedes</text>
 <text x="92" y="541" font-size="19" fill="#C9D6EE">Temuco · Talca · Concepción · Los Ángeles</text>'''
else:
    s=s.replace('FADE0','.35').replace('FADE1','.1')
open(sys.argv[2],'w').write(s+'\n</svg>')
