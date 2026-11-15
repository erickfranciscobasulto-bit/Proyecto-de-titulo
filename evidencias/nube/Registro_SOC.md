# SOC en la nube (AWS) – Registro de implementación

## Arquitectura
| Servidor | Función | Herramientas | Instancia | IP privada |
|---|---|---|---|---|
| SRV-AGROPRODEL (existente) | Servicios | Nginx (HTTPS), BIND, vsftpd (FTPS) | t3.micro | 10.40.1.10 |
| SRV-NOC | Disponibilidad, visualización y concentrador VPN | Zabbix, Grafana, strongSwan | t3.small | 10.40.1.30 |
| SRV-SIEM | Seguridad | Wazuh (manager, indexer, dashboard) | t3.large | 10.40.1.20 |

Suricata (IDS) se habilita en OPNsense (FW-TEMUCO), que ya inspecciona el tráfico hacia Internet.

**Por qué en la nube:** el monitoreo queda fuera de la infraestructura que supervisa; si una sede (incluida la
casa matriz) falla, el SOC sigue operando y alerta la caída.

**Por qué VPN propia (strongSwan) y no Site-to-Site VPN administrada de AWS:** el laboratorio sale a Internet con
IP dinámica (red doméstica y red de Duoc). La VPN administrada exige registrar una IP pública fija del cliente
(Customer Gateway); con strongSwan, R-TEMUCO inicia el túnel IPsec (NAT-T) desde cualquier red y se autentica
con clave compartida.

## Grupos de seguridad
### SG_SOC_NOC (SRV-NOC) – sg-009f0cbc448d25185
| Tipo | Puerto | Origen | Descripción |
|---|---|---|---|
| UDP | 500 | 0.0.0.0/0 | VPN IKE |
| UDP | 4500 | 0.0.0.0/0 | VPN IPsec NAT-T |
| SSH | 22 | IP pública de cada administrador /32 | Administración |
| HTTP | 80 | IP del administrador /32 | Zabbix web |
| TCP | 3000 | IP del administrador /32 | Grafana |
| Todo | Todos | 10.40.0.0/16 | Tráfico interno de la VPC |

UDP 500/4500 se abren a cualquier origen porque el extremo del laboratorio cambia de IP; el túnel exige clave
compartida y cifrado, sin los cuales la negociación se rechaza.

### SG_SOC_SIEM (SRV-SIEM) – sg-04301cb151e77d101
| Tipo | Puerto | Origen | Descripción |
|---|---|---|---|
| UDP | 514 | 192.168.0.0/16 | Syslog de routers y switches (por la VPN) |
| TCP | 1514-1515 | 192.168.0.0/16 | Agentes Wazuh de las sedes |
| HTTPS | 443 | IP del administrador /32 | Panel de Wazuh |
| HTTPS | 443 | 192.168.40.224/27 | Panel de Wazuh desde VLAN 80/99 de Temuco (por la VPN) |
| SSH | 22 | IP pública de cada administrador /32 | Administración |
| Todo | Todos | 10.40.0.0/16 | Tráfico interno de la VPC |

El SIEM no expone ningún puerto a Internet.

## Instancias
### SRV-NOC
| Dato | Valor |
|---|---|
| ID | i-0149582ee2a3b6e88 |
| Tipo / SO | t3.small (2 vCPU, 2 GiB) · Ubuntu Server 24.04 LTS |
| Red | VPC_AGROPRODEL-vpc · subnet-03f4cc1647d14719c (pública 10.40.1.0/24) · IP privada 10.40.1.30 |
| Grupo de seguridad | SG_SOC_NOC |
| Disco | 20 GiB gp3 |
| Perfil IAM / créditos | LabInstanceProfile · standard |
| Llave | LLAVE-NOC (exclusiva del servidor; no se documenta) |
| IP elástica | 98.83.92.138 (eipalloc-0a80a0ba5323a9f9a): extremo fijo de la VPN para R-TEMUCO |
