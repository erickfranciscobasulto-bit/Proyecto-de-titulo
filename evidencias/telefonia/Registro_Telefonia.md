# Registro de implementación – Telefonía IP

Proyecto Agroprodel Ltda. · Fase 2 (implementación)

## Arquitectura

- **Central:** Issabel (Asterisk) en VM VirtualBox, servidor centralizado en Temuco (requerimiento del enunciado).
- **IP del servidor:** 192.168.40.226/28 · gateway 192.168.40.225 (VLAN 80 Servidores) · conectado a SW-FISICO-TEM Fa0/3.
- **Plan de numeración:** 1xxx Temuco · 2xxx Talca · 3xxx Concepción · 4xxx Los Ángeles.
- **IVR previsto:** 1 → 1001 (asistente Temuco) · 2 → 2001 (Talca) · 3 → 3001 (Concepción) · 4 → 4001 (Los Ángeles).

## Terminales

| Extensión | Sede | Terminal | Tecnología | Red / puerto |
|---|---|---|---|---|
| 1001 | Temuco | MicroSIP (PC con Issabel) | PJSIP | 192.168.40.230 (VLAN 80) |
| 2001 | Talca | Teléfono físico Cisco CP-8861 (MAC 7802.B142.A521, SEP7802B142A521) | PJSIP | SW-FISICO-TEM Fa0/5, VLAN de voz 50 (192.168.40.178–.190) |

## Conexión física del teléfono CP-8861

1. Inyector PoE 3Com conectado a la corriente (LED POWER verde).
2. Switch Fa0/5 → puerto **"To Hub/Switch"** del inyector (solo datos).
3. Puerto **"To Network Jack"** del inyector → puerto de **red** del teléfono (datos + PoE).
4. Puerto de **PC** del teléfono disponible para un equipo detrás del teléfono (VLAN 10).

### Verificación realizada

- Fa0/5 up/up (el puerto baja y sube una vez durante el arranque del teléfono: normal).
- `show cdp neighbors` → **SEP7802B142A521** en Fa0/5, plataforma IP Phone.
- `show mac address-table interface fa0/5` → MAC del teléfono en **VLAN 50** (también en VLAN 10 por el primer paquete antes de aprender la VLAN de voz por CDP).
- El teléfono obtuvo IP por DHCP de R-TEMUCO (pool V50-VOZ-TEM) y responde ping.

## Registro del CP-8861 en Issabel (firmware Enterprise → aprovisionamiento por TFTP)

El CP-8861-K9 no se configura desde pantalla ni web: al arrancar descarga `SEP<MAC>.cnf.xml` desde el servidor TFTP indicado por la **opción DHCP 150**.

### Paso 1 – Extensión 2001 en Issabel ✅
- PBX → PBX Configuration → Extensions → 2001 · tecnología **PJSIP** · secret anotado.

### Paso 2 – Servidor TFTP en Issabel (en curso)
```
yum install -y tftp-server xinetd
sed -i 's/disable.*= yes/disable = no/' /etc/xinetd.d/tftp
mkdir -p /tftpboot
systemctl enable xinetd
systemctl restart xinetd
systemctl status xinetd      # active (running)
```
