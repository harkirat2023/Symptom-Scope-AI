#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# SymptomScope AI - Local Development Setup Script
# =============================================================================
# This script sets up the entire project for local development.
# Run from the project root: ./scripts/setup-local.sh
# =============================================================================

info()  { printf "\033[34m[INFO]\033[0m %s\n" "$*"; }
ok()    { printf "\033[32m[OK]\033[0m   %s\n" "$*"; }
err()   { printf "\033[31m[ERR]\033[0m  %s\n" "$*" >&2; }

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# --- Backend Setup ---
info "Setting up backend..."
cd "$ROOT_DIR/backend"

if [ ! -d venv ]; then
  python3 -m venv venv
  ok "Created Python virtual environment"
fi

source venv/bin/activate
pip install -r requirements.txt --quiet
ok "Installed Python dependencies"

if [ ! -f .env ]; then
  cp .env.example .env
  ok "Created .env from .env.example (please edit with your values)"
fi

# --- Frontend Setup ---
info "Setting up frontend..."
cd "$ROOT_DIR/frontend"

if [ ! -d node_modules ]; then
  npm ci
  ok "Installed Node.js dependencies"
fi

if [ ! -f .env.local ]; then
  cp .env.example .env.local
  ok "Created .env.local from .env.example (please edit with your values)"
fi

# --- Done ---
ok "Setup complete!"
echo ""
echo "To start developing:"
echo "  1. Start MongoDB:   mongod (or use docker-compose)"
echo "  2. Start backend:    cd backend && source venv/bin/activate && uvicorn main:app --reload"
echo "  3. Start frontend:   cd frontend && npm run dev"
echo ""
echo "Or use Docker:"
echo "  docker-compose up --build"
