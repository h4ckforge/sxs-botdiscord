# ANNA Bot — Sangre x Sangre

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Discord.py](https://img.shields.io/badge/discord.py-2.7.1-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**Bot de Discord para gestión de comunidad — The Division 2**

</div>

---

## 📋 Tabla de Contenidos

- [✨ Características](#-características)
- [🚀 Instalación](#-instalación)
- [⚙️ Configuración](#️-configuración)
- [🎮 Comandos](#-comandos)
- [📂 Estructura del Proyecto](#-estructura-del-proyecto)
- [🤝 Contribuir](#-contribuir)
- [📄 Licencia](#-licencia)

---

## ✨ Características

### 🏆 Sistema de Rank y XP
- XP por participar y crear eventos
- Niveles progresivos (Nv0 → Nv4+)
- XP Shepherd (nunca se resetea)
- Rankings actualizados automáticamente cada 30 minutos

### ⚔️ Gestión de Eventos
- Crear y gestionar eventos de comunidad
- Lista de espera automática
- Confirmación de participación
- Historial de raids y eventos

### 🔄 Reportes Automatizados
- **Escalation Target Loot** — Diario a las 6:30 CLT
- Reporte de eventos de The Division 2

### 🔐 Sistema de Staff
- Gestión de miembros del clan
- Control de temporadas
- Permisos diferenciados por rol

---

## 🚀 Instalación

### Requisitos Previos

- Python 3.11 o superior
- Discord Bot Token ([Cómo obtenerlo](https://discord.com/developers/applications))
- Git

### Pasos

#### 1. Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/sxs-botdiscord.git
cd sxs-botdiscord
```

#### 2. Crear entorno virtual (recomendado)

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

#### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

O manualmente:

```bash
pip install discord.py==2.7.1 python-dotenv==1.1.1 requests==2.32.4 supabase==2.30.0 pytest==9.0.3
```

#### 4. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```bash
cp .env.example .env
```

Edita `.env` y agrega tu token:

```env
DISCORD_TOKEN=tu_token_de_discord_aqui
```

#### 5. Configurar en Discord Developer Portal

1. Ve a [Discord Developer Portal](https://discord.com/developers/applications)
2. Selecciona tu aplicación → Bot
3. Habilita estos **Privileged Gateway Intents**:
   - ✅ **Message Content Intent** (para leer comandos)
   - ✅ **Server Members Intent** (para gestionar miembros)
   - ✅ **Presence Intent** (opcional, para futuro)

4. En **OAuth2 → URL Generator**:
   - Scopes: `bot`, `applications.commands`
   - Permissions: `Send Messages`, `Manage Messages`, `Embed Links`, `Read Message History`

#### 6. Agregar el bot a tu servidor

Usa la URL generada en el paso anterior.

#### 7. Ejecutar

```bash
python bot.py
```

Deberías ver:

```
2026-05-13 15:00:00 INFO     discord.client logging in using static token
Bot conectado como ANNA#8170
```

---

## ⚙️ Configuración

### Variables de Entorno

| Variable | Descripción | Requerido |
|----------|-------------|-----------|
| `DISCORD_TOKEN` | Token del bot de Discord | ✅ Sí |
| `SUPABASE_URL` | URL de tu proyecto Supabase | No (futuro) |
| `SUPABASE_KEY` | Key de Supabase | No (futuro) |

### Canales y Roles

Algunos comandos envían mensajes a canales específicos. Edita los `CHANNEL_ID` y `ROLE_ID` en cada cog según tu servidor:

- `cogs/rank.py` — `CANAL_RANKING_ID`, `CANAL_RAIDS_ID`
- `cogs/eventos.py` — IDs de canales de eventos
- `cogs/escalation.py` — `REPORT_CHANNEL_ID`, roles de Discord

---

## 🎮 Comandos

Usa el prefijo `!` seguido del comando.

### ℹ️ Información

| Comando | Descripción |
|---------|-------------|
| `!ayuda` | Muestra todos los comandos disponibles |
| `!plataformas` | Muestra plataformas del clan |
| `!raid` | Información sobre la próxima raid |
| `!info-xp` | Explica el sistema de XP |

### 🏆 Rank & Perfil

| Comando | Descripción |
|---------|-------------|
| `!rank [@usuario]` | Muestra XP y posición del agente |
| `!ranking [tipo]` | Muestra ranking (general/eventos/shepherd) |
| `!shepherd [@usuario]` | Muestra XP Shepherd acumulado |
| `!historial [@usuario]` | Últimos eventos confirmados |
| `!perfil` | Perfil del usuario (futuro) |

### ⚔️ Eventos

| Comando | Descripción |
|---------|-------------|
| `!evento` | Crear un nuevo evento |
| `!lista-espera` | Ver lista de espera actual |
| `!salir-lista` | Salir de la lista de espera |

### 🔐 Staff (solo admins)

| Comando | Descripción |
|---------|-------------|
| `!registrar <usuario>` | Registrar un miembro al clan |
| `!baja-agente <usuario>` | Dar de baja a un agente |
| `!baja-clan <usuario>` | Remover del clan |
| `!ver-lista` | Ver lista de espera completa |
| `!temporada-nueva <nombre>` | Crear nueva temporada |
| `!temporada-actual` | Ver temporada activa |
| `!permisos` | Gestionar permisos |
| `!reload <cog>` | Recargar un cog sin reiniciar |

---

## 📂 Estructura del Proyecto

```
sxs-botdiscord/
├── bot.py              # Entry point principal
├── cogs/               # Módulos/extensiones de Discord
│   ├── ayuda.py        # Comando !ayuda
│   ├── eventos.py      # Gestión de eventos
│   ├── rank.py         # Sistema de XP y rankings
│   ├── miembros.py     # Gestión de miembros
│   ├── temporadas.py   # Sistema de temporadas
│   ├── lista_espera.py # Lista de espera
│   ├── Mee6.py         # Integración Mee6
│   ├── permisos.py      # Sistema de permisos
│   ├── baja_agente.py  # Baja de agentes
│   ├── reload.py       # Recarga de cogs
│   └── escalation.py   # Reportes automáticos
├── utils/              # Utilidades
│   ├── db.py           # Cliente de base de datos
│   ├── xp_calc.py      # Cálculos de XP
│   ├── ratelimit.py    # Rate limiting
│   └── validation.py   # Validación de inputs
├── .env                # Variables de entorno (NO commitear)
├── requirements.txt    # Dependencias de Python
└── README.md           # Este archivo
```

---

---

## 🔄 Persistencia (Mantener el bot corriendo)

Por defecto, el bot se cierra al cerrar la terminal. Para mantenerlo corriendo 24/7:

### Windows — NSSM (Non-Sucking Service Manager)

1. Descargar NSSM desde https://nssm.cc/download
2. Extraer y copiar `nssm.exe` a una carpeta en el PATH, o usar la ruta completa

```bash
# 1. Instalar como servicio (ejecutar como Administrador)
nssm install ANNA-Bot "C:\ruta\a\python.exe" "C:\ruta\a\sxs-botdiscord\bot.py"

# 2. Configurar el working directory
nssm set ANNA-Bot AppDirectory "C:\ruta\a\sxs-botdiscord"

# 3. Configurar variables de entorno (necesario para .env)
nssm set ANNA-Bot AppEnvironment "DISCORD_TOKEN=tu_token_aqui"

# 4. Iniciar el servicio
nssm start ANNA-Bot

# 5. Ver estado
nssm status ANNA-Bot
```

**Comandos útiles:**
```bash
nssm start ANNA-Bot    # Iniciar
nssm stop ANNA-Bot     # Detener
nssm restart ANNA-Bot  # Reiniciar
nssm edit ANNA-Bot     # Editar configuración
nssm remove ANNA-Bot   # Desinstalar
```

### Windows — Task Scheduler (alternativa sin NSSM)

1. Abrir Task Scheduler (`taskschd.msc`)
2. **Crear tarea básica:**
   - Nombre: `ANNA-Bot`
   - Trigger: `Al iniciar`
   - Acción: `Iniciar un programa`
   - Programa: `python`
   - Argumentos: `bot.py`
   - Iniciar en: `C:\ruta\a\sxs-botdiscord`

3. Marcar "Ejecutar tanto si el usuario ha iniciado sesión como si no"

### Linux — Systemd

```bash
# 1. Crear servicio
sudo nano /etc/systemd/system/anna-bot.service
```

```ini
[Unit]
Description=ANNA Discord Bot
After=network.target

[Service]
Type=simple
User=tu_usuario
WorkingDirectory=/home/tu_usuario/sxs-botdiscord
ExecStart=/usr/bin/python3 bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 2. Activar
sudo systemctl daemon-reload
sudo systemctl enable anna-bot
sudo systemctl start anna-bot
```

---

## 🔒 Seguridad

Este proyecto implementa buenas prácticas de seguridad:

- **Intents mínimos** — Solo los permisos necesarios
- **Rate limiting** — Cooldown por usuario (3/10s normal, 10/60s admin)
- **Validación de inputs** — Sanitización de datos de usuario
- **Logging** — Errores guardados en `bot.log` (nunca expuestos a usuarios)
- **Permisos** — Comandos de staff protegidos con `@is_owner()`

---

## 🤝 Contribuir

1. Haz un Fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

---

## 🙏 Créditos

- **Desarrollado para** [Sangre x Sangre](https://discord.gg/) — Comunidad de The Division 2
- **Framework**: [discord.py](https://discordpy.readthedocs.io/) por Rapptz
- **Inspiración**: Sistema de ranking de MEE6

---

<div align="center">

Hecho con ❤️ para la comunidad de Sangre x Sangre

</div>