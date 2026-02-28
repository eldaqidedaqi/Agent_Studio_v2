#!/usr/bin/env python3
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
