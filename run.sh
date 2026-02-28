#!/usr/bin/env bash
# ╔══════════════════════════════════════════════╗
# ║    Agent Studio v2.0 — Lanzador Rápido      ║
# ╚══════════════════════════════════════════════╝
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

# Colores
G="\033[92m"; Y="\033[93m"; R="\033[91m"; CY="\033[96m"; RST="\033[0m"

echo -e "${G}⬡ Agent Studio v2.0${RST}"
echo ""

# Verificar Python 3.9+
PYTHON=$(command -v python3 || command -v python)
if [ -z "$PYTHON" ]; then
  echo -e "${R}✗ Python no encontrado${RST}"; exit 1
fi

PY_VER=$($PYTHON -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo -e "${CY}  Python $PY_VER detectado${RST}"

# Instalar deps si no están
if ! $PYTHON -c "import flask" 2>/dev/null; then
  echo -e "${Y}  Instalando dependencias...${RST}"
  $PYTHON -m pip install -r requirements.txt -q
fi

# Crear .env si no existe
if [ ! -f .env ]; then
  cp .env.template .env
  echo -e "${Y}  ⚠  .env creado — edita ANTHROPIC_API_KEY antes de continuar${RST}"
  echo -e "${Y}     nano .env${RST}"
  echo ""
fi

# Lanzar
echo -e "${G}  Iniciando servidor → http://localhost:5000${RST}"
echo -e "\033[2m  Ctrl+C para detener\033[0m"
echo ""
$PYTHON Agente-web.py
