# ⬡ Agent Studio v2.0

> **Multi-Agent AI Platform** — Construido iterativamente en sesiones de chat con Claude.

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-green?logo=flask)](https://flask.palletsprojects.com)
[![Claude](https://img.shields.io/badge/Claude-Sonnet_4-orange?logo=anthropic)](https://anthropic.com)
[![Version](https://img.shields.io/badge/version-2.0.0-purple)](.)

---

## 🚀 Inicio Rápido

```bash
# 1. Instalar y configurar
python setup_agent_studio.py

# 2. Entrar a la carpeta
cd Agent_Studio_v2/

# 3. Configurar tu API key de Anthropic
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env

# 4. Lanzar el servidor
python Agente-web.py

# 5. Abrir en el navegador
# http://localhost:5000
```

---

## 📁 Estructura del Proyecto

```
Agent_Studio_v2/
├── Agente-web.py        ← Servidor Flask + proxy API + SSE streaming
├── index.html           ← Frontend multi-agente (React en CDN)
├── requirements.txt     ← Dependencias Python
├── README.md            ← Esta documentación
├── .env                 ← Tu API key (NO subir a git)
└── logs/
    └── agent_studio.log ← Logs del servidor
```

---

## ✨ Features Implementadas (16+)

| # | Feature | Descripción |
|---|---------|-------------|
| 01 | ⚡ Multi-Agent Pipeline | Planner → Detector → Executor → Debugger |
| 02 | 🧠 RAG / Vector Memory | Embeddings locales con similitud coseno |
| 03 | 🔧 20 MCP Tools | Context7, GitHub, Brave, Qdrant, E2B… |
| 04 | 🔑 API Key Vault | 35 providers, cifrado XOR, auto-inject |
| 05 | 📁 File System API | Acceso nativo al OS del navegador |
| 06 | ⌨️ Terminal Emulator | 15 comandos reales integrados |
| 07 | 🎙 Voice Input | Web Speech API en español |
| 08 | 📋 12 Templates | Next.js, FastAPI, Django, Docker… |
| 09 | 📦 ZIP Export | Bundle HTML auto-extraíble |
| 10 | 🌊 Streaming SSE | Token a token en tiempo real |
| 11 | 🪄 Prompt Enhancer | La IA mejora tu prompt automáticamente |
| 12 | ▶️ Code Runner | Sandbox iframe aislado JS/HTML/CSS |
| 13 | 📊 Token Budget | Monitor de 200k tokens con auto-compress |
| 14 | 🔬 AI Self-Review | 5 métricas de calidad + auto-fix |
| 15 | 🗂 Snippet Bank | Extracción automática de código |
| 16 | 🤖 Agent Builder | Agentes personalizados + Analytics |

---

## 🌐 Endpoints de la API

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/` | Sirve index.html |
| `POST` | `/api/chat` | Chat estándar (respuesta completa) |
| `POST` | `/api/stream` | Chat con SSE streaming token a token |
| `POST` | `/api/enhance` | Mejora automática de prompts |
| `POST` | `/api/review` | Auto-review del último output |
| `GET` | `/api/models` | Lista modelos disponibles |
| `GET` | `/api/health` | Health check del servidor |
| `GET` | `/api/config` | Configuración actual (sin keys) |

---

## ⚙️ Variables de Entorno

Crea un archivo `.env` en `Agent_Studio_v2/`:

```env
# Requerida
ANTHROPIC_API_KEY=sk-ant-api03-...

# Opcionales
PORT=5000
HOST=0.0.0.0
DEBUG=false
OLLAMA_HOST=http://localhost:11434
MAX_TOKENS=8192
CORS_ORIGINS=*
LOG_LEVEL=INFO
```

---

## 🔧 Modelos Disponibles

- `claude-sonnet-4-20250514` *(por defecto — recomendado)*
- `claude-opus-4-20250514`
- `claude-haiku-4-5-20251001`
- Modelos Ollama locales (requiere Ollama instalado)

---

## 📋 Requisitos del Sistema

- **Python**: 3.9 o superior
- **OS**: Linux, macOS, Windows
- **RAM**: 512 MB mínimo, 2 GB recomendado
- **Navegador**: Chrome/Edge (para File System API y Voice Input)
- **Internet**: Requerido para Anthropic API

---

## 🐛 Bugs Corregidos en Sesión 7

1. `Welcome` component: prop `agents` no declarada en firma → corregida
2. 5 features sin botón en cabecera (AgentBuilder, Analytics, Branches, Diff, Streaming) → añadidos
3. Falsos positivos en auditoría de paréntesis (dentro de strings/template literals) → documentados

---

## 📊 Estadísticas del Proyecto

- **Sesiones de desarrollo**: 7 conversaciones de chat
- **Líneas de JSX**: 4,027
- **useState hooks**: 80+
- **Funciones**: 100+
- **MCP Tools**: 20
- **API Providers**: 35
- **Fecha**: 2026-02-28

---

## 📄 Licencia

MIT License — Usa, modifica y distribuye libremente.

---

*Construido con ❤️ en sesiones de chat con Claude · Agent Studio v2.0.0*
