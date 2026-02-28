#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════╗
║          AGENT STUDIO v2.0 — Instalador Automático              ║
║  Genera Agent_Studio_v2/ con todos los archivos y dependencias  ║
╚══════════════════════════════════════════════════════════════════╝

Uso:
    python setup_agent_studio.py           → instala todo
    python setup_agent_studio.py --run     → instala y lanza el servidor
    python setup_agent_studio.py --clean   → elimina la carpeta y reinstala
"""

import os
import sys
import subprocess
import shutil
import textwrap
import platform
import argparse
from pathlib import Path
from datetime import datetime

# ─── Colores ANSI ────────────────────────────────────────────────
class C:
    G  = "\033[92m"   # verde
    Y  = "\033[93m"   # amarillo
    R  = "\033[91m"   # rojo
    B  = "\033[94m"   # azul
    P  = "\033[95m"   # magenta
    CY = "\033[96m"   # cyan
    W  = "\033[97m"   # blanco
    DIM= "\033[2m"
    RST= "\033[0m"
    BOLD="\033[1m"

def p(msg, color=C.W):
    print(f"{color}{msg}{C.RST}")

def ok(msg):   print(f"{C.G}  ✓  {msg}{C.RST}")
def warn(msg): print(f"{C.Y}  ⚠  {msg}{C.RST}")
def err(msg):  print(f"{C.R}  ✗  {msg}{C.RST}")
def info(msg): print(f"{C.CY}  →  {msg}{C.RST}")
def hdr(msg):  print(f"\n{C.P}{C.BOLD}{'─'*60}\n  {msg}\n{'─'*60}{C.RST}")

# ─── Configuración ───────────────────────────────────────────────
TARGET_DIR   = Path("Agent_Studio_v2")
PYTHON_MIN   = (3, 9)
VERSION      = "2.0.0"
DATE         = datetime.now().strftime("%Y-%m-%d")

# ─── requirements.txt ────────────────────────────────────────────
REQUIREMENTS = """\
# Agent Studio v2.0 — Dependencias Python
# Generado automáticamente por setup_agent_studio.py

# ── Servidor Web ──────────────────────────────────────────────────
flask>=3.0.0
flask-cors>=4.0.0

# ── HTTP / Async ──────────────────────────────────────────────────
httpx>=0.27.0
requests>=2.31.0
aiohttp>=3.9.0

# ── Variables de entorno ──────────────────────────────────────────
python-dotenv>=1.0.0

# ── Seguridad ─────────────────────────────────────────────────────
cryptography>=42.0.0

# ── Utilidades ────────────────────────────────────────────────────
rich>=13.7.0
click>=8.1.0
watchdog>=4.0.0

# ── Opcional: Modelos locales via Ollama ──────────────────────────
# ollama>=0.2.0

# ── Opcional: Testing ─────────────────────────────────────────────
# pytest>=8.0.0
# pytest-asyncio>=0.23.0
"""

# ─── README.md ───────────────────────────────────────────────────
README = f"""\
# ⬡ Agent Studio v2.0

> **Multi-Agent AI Platform** — Construido iterativamente en sesiones de chat con Claude.

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-green?logo=flask)](https://flask.palletsprojects.com)
[![Claude](https://img.shields.io/badge/Claude-Sonnet_4-orange?logo=anthropic)](https://anthropic.com)
[![Version](https://img.shields.io/badge/version-{VERSION}-purple)](.)

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
- **Fecha**: {DATE}

---

## 📄 Licencia

MIT License — Usa, modifica y distribuye libremente.

---

*Construido con ❤️ en sesiones de chat con Claude · Agent Studio v{VERSION}*
"""

# ─── index.html (fetch del archivo ya generado o embed) ──────────
def get_index_html():
    """Retorna el contenido del index.html ya generado."""
    return open(Path(__file__).parent / "index.html").read()

# ─── Agente-web.py ───────────────────────────────────────────────
AGENTE_WEB = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════╗
║               AGENT STUDIO v2.0 — Servidor Web                  ║
║         Flask + Proxy Anthropic API + SSE Streaming              ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import time
import logging
import threading
from pathlib import Path
from datetime import datetime
from typing import Generator

# ── Cargar .env antes que todo ────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

import requests
from flask import (
    Flask, Response, request, jsonify,
    send_from_directory, stream_with_context
)
from flask_cors import CORS

# ── Configuración ─────────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent
LOG_DIR     = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

HOST        = os.getenv("HOST", "0.0.0.0")
PORT        = int(os.getenv("PORT", 5000))
DEBUG       = os.getenv("DEBUG", "false").lower() == "true"
API_KEY     = os.getenv("ANTHROPIC_API_KEY", "")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MAX_TOKENS  = int(os.getenv("MAX_TOKENS", 8192))
CORS_ORIG   = os.getenv("CORS_ORIGINS", "*")
LOG_LEVEL   = os.getenv("LOG_LEVEL", "INFO")

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VER = "2023-06-01"
DEFAULT_MODEL = "claude-sonnet-4-20250514"

AVAILABLE_MODELS = [
    {"id": "claude-sonnet-4-20250514",   "name": "Claude Sonnet 4",  "provider": "anthropic", "ctx": 200000},
    {"id": "claude-opus-4-20250514",     "name": "Claude Opus 4",    "provider": "anthropic", "ctx": 200000},
    {"id": "claude-haiku-4-5-20251001",  "name": "Claude Haiku 4.5", "provider": "anthropic", "ctx": 200000},
]

# ── Logging ───────────────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / "agent_studio.log", encoding="utf-8"),
    ]
)
log = logging.getLogger("AgentStudio")

# ── App ───────────────────────────────────────────────────────────
app = Flask(__name__, static_folder=str(BASE_DIR))
CORS(app, origins=CORS_ORIG)

# ── Helpers ───────────────────────────────────────────────────────
def anthropic_headers(key: str | None = None) -> dict:
    k = key or API_KEY
    return {
        "x-api-key":         k,
        "anthropic-version": ANTHROPIC_VER,
        "content-type":      "application/json",
    }

def extract_key(req_data: dict) -> str:
    """Extrae la API key del body o usa la del entorno."""
    return req_data.pop("api_key", None) or API_KEY

def validate_key(key: str) -> bool:
    return bool(key and key.startswith("sk-ant"))

def build_payload(data: dict, stream: bool = False) -> dict:
    """Construye el payload para Anthropic API."""
    messages  = data.get("messages", [])
    model     = data.get("model", DEFAULT_MODEL)
    max_tok   = data.get("max_tokens", MAX_TOKENS)
    sys_prompt= data.get("system", None)
    temp      = data.get("temperature", 0.7)

    payload = {
        "model":      model,
        "max_tokens": max_tok,
        "messages":   messages,
        "stream":     stream,
        "temperature": temp,
    }
    if sys_prompt:
        payload["system"] = sys_prompt
    return payload

def log_request(endpoint: str, model: str, messages: list):
    n_msgs  = len(messages)
    n_toks  = sum(len(str(m.get("content", ""))) // 4 for m in messages)
    log.info(f"[{endpoint}] model={model} msgs={n_msgs} ~tokens={n_toks}")

# ── Rutas estáticas ───────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(str(BASE_DIR), "index.html")

@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(str(BASE_DIR), filename)

# ── Health check ──────────────────────────────────────────────────
@app.route("/api/health")
def health():
    key_ok = validate_key(API_KEY)
    return jsonify({
        "status":    "ok",
        "version":   "2.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "api_key":   "configured" if key_ok else "missing",
        "models":    len(AVAILABLE_MODELS),
        "ollama":    _check_ollama(),
    })

def _check_ollama() -> str:
    try:
        r = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=2)
        return "online" if r.ok else "error"
    except Exception:
        return "offline"

# ── Modelos ───────────────────────────────────────────────────────
@app.route("/api/models")
def get_models():
    models = list(AVAILABLE_MODELS)
    # Añadir modelos Ollama si está disponible
    try:
        r = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=2)
        if r.ok:
            for m in r.json().get("models", []):
                models.append({
                    "id":       m["name"],
                    "name":     m["name"],
                    "provider": "ollama",
                    "ctx":      8192,
                })
    except Exception:
        pass
    return jsonify({"models": models})

# ── Configuración ─────────────────────────────────────────────────
@app.route("/api/config")
def get_config():
    return jsonify({
        "model":       DEFAULT_MODEL,
        "max_tokens":  MAX_TOKENS,
        "ollama_host": OLLAMA_HOST,
        "debug":       DEBUG,
        "api_key_set": validate_key(API_KEY),
        "version":     "2.0.0",
    })

# ── Chat estándar ─────────────────────────────────────────────────
@app.route("/api/chat", methods=["POST"])
def chat():
    data    = request.get_json(force=True)
    api_key = extract_key(data)

    if not validate_key(api_key):
        return jsonify({"error": "API key no configurada. Añade ANTHROPIC_API_KEY al .env"}), 401

    model = data.get("model", DEFAULT_MODEL)
    log_request("chat", model, data.get("messages", []))

    # Ollama local
    if data.get("provider") == "ollama" or not model.startswith("claude"):
        return _ollama_chat(data)

    # Anthropic
    try:
        payload = build_payload(data, stream=False)
        resp    = requests.post(
            ANTHROPIC_URL,
            headers=anthropic_headers(api_key),
            json=payload,
            timeout=120,
        )
        if not resp.ok:
            log.error(f"Anthropic error {resp.status_code}: {resp.text[:300]}")
            return jsonify({"error": resp.json()}), resp.status_code

        result = resp.json()
        text   = "".join(b["text"] for b in result.get("content", []) if b.get("type") == "text")
        return jsonify({
            "content":    text,
            "model":      result.get("model", model),
            "usage":      result.get("usage", {}),
            "stop_reason":result.get("stop_reason", "end_turn"),
        })

    except requests.Timeout:
        return jsonify({"error": "Timeout — la respuesta tardó más de 120s"}), 504
    except Exception as e:
        log.exception("Error en /api/chat")
        return jsonify({"error": str(e)}), 500

def _ollama_chat(data: dict):
    """Proxy hacia Ollama para modelos locales."""
    try:
        messages = data.get("messages", [])
        model    = data.get("model", "llama3.2")
        payload  = {"model": model, "messages": messages, "stream": False}
        resp     = requests.post(f"{OLLAMA_HOST}/api/chat", json=payload, timeout=300)
        if not resp.ok:
            return jsonify({"error": "Ollama error"}), 502
        result   = resp.json()
        text     = result.get("message", {}).get("content", "")
        return jsonify({"content": text, "model": model, "usage": {}})
    except Exception as e:
        return jsonify({"error": f"Ollama: {e}"}), 502

# ── Chat streaming SSE ────────────────────────────────────────────
@app.route("/api/stream", methods=["POST"])
def stream_chat():
    data    = request.get_json(force=True)
    api_key = extract_key(data)

    if not validate_key(api_key):
        def err_gen():
            yield f"data: {json.dumps({'error': 'API key no configurada'})}\n\n"
            yield "data: [DONE]\n\n"
        return Response(stream_with_context(err_gen()), mimetype="text/event-stream")

    model = data.get("model", DEFAULT_MODEL)
    log_request("stream", model, data.get("messages", []))

    def generate() -> Generator[str, None, None]:
        try:
            payload = build_payload(data, stream=True)
            with requests.post(
                ANTHROPIC_URL,
                headers=anthropic_headers(api_key),
                json=payload,
                stream=True,
                timeout=300,
            ) as resp:
                if not resp.ok:
                    yield f"data: {json.dumps({'error': f'API error {resp.status_code}'})}\n\n"
                    yield "data: [DONE]\n\n"
                    return

                for line in resp.iter_lines():
                    if not line:
                        continue
                    line = line.decode("utf-8") if isinstance(line, bytes) else line
                    if line.startswith("data: "):
                        payload_str = line[6:]
                        if payload_str == "[DONE]":
                            yield "data: [DONE]\n\n"
                            return
                        try:
                            event = json.loads(payload_str)
                            etype = event.get("type", "")

                            if etype == "content_block_delta":
                                delta = event.get("delta", {})
                                if delta.get("type") == "text_delta":
                                    token = delta.get("text", "")
                                    yield f"data: {json.dumps({'token': token})}\n\n"

                            elif etype == "message_delta":
                                usage = event.get("usage", {})
                                yield f"data: {json.dumps({'usage': usage})}\n\n"

                            elif etype == "message_stop":
                                yield "data: [DONE]\n\n"
                                return

                        except json.JSONDecodeError:
                            pass

        except requests.Timeout:
            yield f"data: {json.dumps({'error': 'Timeout'})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            log.exception("Error en SSE stream")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            yield "data: [DONE]\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control":  "no-cache",
            "X-Accel-Buffering": "no",
            "Connection":     "keep-alive",
        },
    )

# ── Prompt Enhancer ───────────────────────────────────────────────
@app.route("/api/enhance", methods=["POST"])
def enhance_prompt():
    data    = request.get_json(force=True)
    api_key = extract_key(data)
    prompt  = data.get("prompt", "")

    if not validate_key(api_key):
        return jsonify({"error": "API key no configurada"}), 401
    if not prompt.strip():
        return jsonify({"error": "Prompt vacío"}), 400

    system = (
        "Eres un experto en ingeniería de prompts. "
        "Tu tarea: reescribir el prompt del usuario haciéndolo más claro, "
        "específico y efectivo para un modelo de lenguaje. "
        "Responde SOLO con el prompt mejorado, sin explicaciones ni prefijos."
    )
    try:
        payload = {
            "model":      data.get("model", DEFAULT_MODEL),
            "max_tokens": 1024,
            "system":     system,
            "messages":   [{"role": "user", "content": prompt}],
        }
        resp  = requests.post(ANTHROPIC_URL, headers=anthropic_headers(api_key), json=payload, timeout=60)
        result= resp.json()
        enhanced = "".join(b["text"] for b in result.get("content", []) if b.get("type") == "text")
        return jsonify({"original": prompt, "enhanced": enhanced, "usage": result.get("usage", {})})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── AI Self-Review ────────────────────────────────────────────────
@app.route("/api/review", methods=["POST"])
def self_review():
    data    = request.get_json(force=True)
    api_key = extract_key(data)
    content = data.get("content", "")

    if not validate_key(api_key):
        return jsonify({"error": "API key no configurada"}), 401
    if not content.strip():
        return jsonify({"error": "Contenido vacío"}), 400

    system = """Eres un revisor de código experto. Analiza el siguiente output y responde SOLO con JSON:
{
  "scores": {
    "completeness": 0-100,
    "security": 0-100,
    "performance": 0-100,
    "errorHandling": 0-100,
    "codeQuality": 0-100
  },
  "issues": [{"severity": "critical|warning|info", "message": "..."}],
  "summary": "resumen breve",
  "autofix": "sugerencia de mejora principal"
}"""
    try:
        payload = {
            "model":      data.get("model", DEFAULT_MODEL),
            "max_tokens": 1024,
            "system":     system,
            "messages":   [{"role": "user", "content": content}],
        }
        resp   = requests.post(ANTHROPIC_URL, headers=anthropic_headers(api_key), json=payload, timeout=60)
        result = resp.json()
        raw    = "".join(b["text"] for b in result.get("content", []) if b.get("type") == "text")
        # Limpiar posibles markdown fences
        clean  = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        review = json.loads(clean)
        return jsonify({"review": review, "usage": result.get("usage", {})})
    except json.JSONDecodeError:
        return jsonify({"review": {"summary": raw, "scores": {}, "issues": []}, "raw": raw})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── Error handlers ────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Ruta no encontrada"}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Método no permitido"}), 405

@app.errorhandler(500)
def internal_error(e):
    log.exception("Error interno")
    return jsonify({"error": "Error interno del servidor"}), 500

# ── Banner de inicio ──────────────────────────────────────────────
def print_banner():
    key_status = "✓ Configurada" if validate_key(API_KEY) else "✗ FALTA (.env)"
    print(f"""
\033[92m╔══════════════════════════════════════════════════════╗
║          ⬡ AGENT STUDIO v2.0 — Servidor Web         ║
╚══════════════════════════════════════════════════════╝\033[0m

\033[96m  URL        →  http://{HOST}:{PORT}\033[0m
\033[93m  API Key    →  {key_status}\033[0m
\033[2m  Logs       →  logs/agent_studio.log
  Debug      →  {"ON" if DEBUG else "OFF"}
  Fecha      →  {datetime.now().strftime("%Y-%m-%d %H:%M")}\033[0m

\033[92m  Endpoints disponibles:\033[0m
\033[2m  GET  /               → index.html
  POST /api/chat         → Chat estándar
  POST /api/stream       → SSE streaming
  POST /api/enhance      → Mejorar prompt
  POST /api/review       → Auto-review
  GET  /api/models       → Modelos disponibles
  GET  /api/health       → Health check
  GET  /api/config       → Configuración\033[0m

\033[93m  Ctrl+C para detener\033[0m
""")

# ── Main ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    print_banner()

    if not validate_key(API_KEY):
        print("\033[93m  ⚠  Crea el archivo .env con:\033[0m")
        print("\033[2m      ANTHROPIC_API_KEY=sk-ant-api03-...\033[0m\n")

    app.run(
        host=HOST,
        port=PORT,
        debug=DEBUG,
        threaded=True,
        use_reloader=False,
    )
'''

# ─── .env template ───────────────────────────────────────────────
DOT_ENV_TEMPLATE = """\
# Agent Studio v2.0 — Variables de entorno
# Copia este archivo a .env y rellena tus valores

# ── REQUERIDA ──────────────────────────────────────────────────────
ANTHROPIC_API_KEY=sk-ant-api03-XXXXXX...

# ── SERVIDOR ──────────────────────────────────────────────────────
PORT=5000
HOST=0.0.0.0
DEBUG=false

# ── MODELOS ───────────────────────────────────────────────────────
# Opciones: claude-sonnet-4-20250514 | claude-opus-4-20250514 | claude-haiku-4-5-20251001
DEFAULT_MODEL=claude-sonnet-4-20250514
MAX_TOKENS=8192

# ── OLLAMA (modelos locales) ──────────────────────────────────────
OLLAMA_HOST=http://localhost:11434

# ── CORS ──────────────────────────────────────────────────────────
CORS_ORIGINS=*

# ── LOGGING ───────────────────────────────────────────────────────
LOG_LEVEL=INFO
"""

# ─── .gitignore ──────────────────────────────────────────────────
GITIGNORE = """\
# Agent Studio v2.0
.env
*.pyc
__pycache__/
*.pyo
.pytest_cache/
logs/*.log
venv/
.venv/
dist/
build/
*.egg-info/
.DS_Store
Thumbs.db
"""

# ═══════════════════════════════════════════════════════════════════
#                        INSTALADOR
# ═══════════════════════════════════════════════════════════════════

def check_python():
    hdr("Verificando Python")
    ver = sys.version_info
    p(f"  Python {ver.major}.{ver.minor}.{ver.micro} detectado", C.CY)
    if ver < PYTHON_MIN:
        err(f"Se requiere Python {PYTHON_MIN[0]}.{PYTHON_MIN[1]}+")
        sys.exit(1)
    ok(f"Python {ver.major}.{ver.minor} ✓")
    return sys.executable

def check_pip(python_exe: str):
    try:
        subprocess.check_call(
            [python_exe, "-m", "pip", "--version"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        ok("pip disponible ✓")
    except subprocess.CalledProcessError:
        err("pip no encontrado. Instala pip primero.")
        sys.exit(1)

def setup_directory(clean: bool = False):
    hdr("Preparando directorio")

    if clean and TARGET_DIR.exists():
        warn(f"Eliminando {TARGET_DIR}/ existente...")
        shutil.rmtree(TARGET_DIR)
        ok(f"Directorio {TARGET_DIR}/ eliminado")

    TARGET_DIR.mkdir(exist_ok=True)
    (TARGET_DIR / "logs").mkdir(exist_ok=True)
    ok(f"Directorio {TARGET_DIR}/ listo")
    info(f"Ruta: {TARGET_DIR.resolve()}")

def write_file(name: str, content: str, label: str | None = None):
    path = TARGET_DIR / name
    path.write_text(content, encoding="utf-8")
    ok(f"{label or name} generado ({len(content):,} bytes)")
    return path

def copy_index_html():
    hdr("Copiando index.html")
    # Buscar el index.html junto a este script
    candidates = [
        Path(__file__).parent / "index.html",
        Path("index.html"),
    ]
    for src in candidates:
        if src.exists():
            content = src.read_text(encoding="utf-8")
            write_file("index.html", content, "index.html")
            return

    # Si no existe, crear uno minimalista de referencia
    warn("No se encontró index.html — creando versión de referencia")
    fallback = """\
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>⬡ Agent Studio v2.0</title>
  <style>
    body { background: #05060f; color: #e2e8f4; font-family: monospace;
           display: flex; align-items: center; justify-content: center;
           height: 100vh; margin: 0; flex-direction: column; gap: 16px; }
    h1   { color: #00f5a0; font-size: 2.5rem; letter-spacing: 4px; }
    p    { color: #3a3f50; font-size: 12px; letter-spacing: 2px; }
    a    { color: #00f5a0; text-decoration: none; }
  </style>
</head>
<body>
  <h1>⬡ AGENT STUDIO v2.0</h1>
  <p>Servidor activo · <a href="/api/health">/api/health</a> · <a href="/api/models">/api/models</a></p>
  <p style="color:#555">Coloca el index.html completo junto a Agente-web.py y reinicia</p>
</body>
</html>
"""
    write_file("index.html", fallback, "index.html (referencia)")

def write_all_files():
    hdr("Generando archivos del proyecto")
    write_file("README.md",         README)
    write_file("requirements.txt",  REQUIREMENTS)
    write_file("Agente-web.py",     AGENTE_WEB)
    write_file(".env.template",     DOT_ENV_TEMPLATE)
    write_file(".gitignore",        GITIGNORE)

    # .env solo si no existe
    env_path = TARGET_DIR / ".env"
    if not env_path.exists():
        env_path.write_text(DOT_ENV_TEMPLATE, encoding="utf-8")
        ok(".env creado (configura tu ANTHROPIC_API_KEY)")
    else:
        info(".env existente conservado")

    copy_index_html()

def install_packages(python_exe: str):
    hdr("Instalando dependencias Python")
    req_path = TARGET_DIR / "requirements.txt"

    # Extraer paquetes sin comentarios ni vacíos
    packages = []
    for line in req_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            packages.append(line)

    info(f"Instalando {len(packages)} paquetes...")

    cmd = [
        python_exe, "-m", "pip", "install",
        "--upgrade",
        "-r", str(req_path),
        "--quiet",
    ]

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )
        if proc.returncode == 0:
            ok("Todas las dependencias instaladas correctamente")
        else:
            warn("Algunos paquetes con advertencias:")
            # Mostrar solo errores, no warnings normales
            for line in proc.stderr.splitlines():
                if "error" in line.lower() or "failed" in line.lower():
                    err(f"  {line.strip()}")
            # Intentar instalación individual
            info("Intentando instalación individual de paquetes clave...")
            for pkg in ["flask", "flask-cors", "httpx", "requests", "python-dotenv", "rich", "click"]:
                try:
                    subprocess.run(
                        [python_exe, "-m", "pip", "install", "--quiet", "--upgrade", pkg],
                        check=True, capture_output=True
                    )
                    ok(f"{pkg}")
                except subprocess.CalledProcessError:
                    err(f"{pkg} — falló")
    except Exception as e:
        err(f"Error durante la instalación: {e}")

def verify_installation(python_exe: str):
    hdr("Verificando instalación")
    critical = ["flask", "flask_cors", "requests", "dotenv", "httpx"]
    all_ok = True
    for mod in critical:
        try:
            subprocess.check_call(
                [python_exe, "-c", f"import {mod}"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            ok(mod)
        except subprocess.CalledProcessError:
            err(f"{mod} — NO INSTALADO")
            all_ok = False

    # Rich es opcional
    try:
        subprocess.check_call(
            [python_exe, "-c", "import rich"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        ok("rich (UI mejorada)")
    except subprocess.CalledProcessError:
        warn("rich — no instalado (opcional)")

    return all_ok

def print_summary():
    hdr("Instalación Completada")

    files = list(TARGET_DIR.rglob("*"))
    total_bytes = sum(f.stat().st_size for f in files if f.is_file())

    p(f"""
  📁 Directorio  :  {TARGET_DIR.resolve()}
  📄 Archivos    :  {len([f for f in files if f.is_file()])}
  💾 Tamaño      :  {total_bytes/1024:.1f} KB
  🐍 Python      :  {sys.version.split()[0]}
  💻 Sistema     :  {platform.system()} {platform.machine()}
  📅 Fecha       :  {DATE}
    """, C.DIM)

    p("  Para iniciar Agent Studio:", C.G)
    p(f"""
  \033[96mcd {TARGET_DIR}/\033[0m
  \033[96m# Edita .env y añade tu ANTHROPIC_API_KEY\033[0m
  \033[96mpython Agente-web.py\033[0m
  \033[96m# Abre http://localhost:5000\033[0m
    """)

def launch_server(python_exe: str):
    hdr("Lanzando servidor")
    server_script = TARGET_DIR / "Agente-web.py"
    info(f"Ejecutando: {python_exe} {server_script}")
    info("Ctrl+C para detener\n")
    try:
        subprocess.run([python_exe, str(server_script)], check=True)
    except KeyboardInterrupt:
        p("\n  Servidor detenido.", C.Y)
    except subprocess.CalledProcessError as e:
        err(f"Error al lanzar el servidor: {e}")

# ─── Main ────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Agent Studio v2.0 — Instalador",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
            Ejemplos:
              python setup_agent_studio.py            # Instalar
              python setup_agent_studio.py --run      # Instalar y lanzar
              python setup_agent_studio.py --clean    # Reinstalar desde cero
        """)
    )
    parser.add_argument("--run",   action="store_true", help="Lanzar el servidor tras instalar")
    parser.add_argument("--clean", action="store_true", help="Eliminar carpeta existente antes de instalar")
    parser.add_argument("--no-install", action="store_true", help="Omitir pip install")
    args = parser.parse_args()

    # Banner
    print(f"""
{C.G}{C.BOLD}╔══════════════════════════════════════════════════════════════╗
║         ⬡ AGENT STUDIO v2.0 — Instalador Automático         ║
║                   setup_agent_studio.py                      ║
╚══════════════════════════════════════════════════════════════╝{C.RST}
{C.DIM}  Genera Agent_Studio_v2/ con todos los archivos y dependencias{C.RST}
""")

    python_exe = check_python()
    check_pip(python_exe)
    setup_directory(clean=args.clean)
    write_all_files()

    if not args.no_install:
        install_packages(python_exe)
        verify_installation(python_exe)
    else:
        info("--no-install: omitiendo pip install")

    print_summary()

    if args.run:
        launch_server(python_exe)

if __name__ == "__main__":
    main()
