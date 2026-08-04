#!/usr/bin/env bash
# ─── SymptomScope AI — single boot script ───────────────────────────────
# Starts MongoDB, backend (uvicorn), frontend (next dev), and waits for
# health-check before opening the browser.
# Kill with Ctrl+C to stop everything cleanly.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"
MONGO_LOG="$(mktemp /tmp/symptomscope-mongod.XXX.log 2>/dev/null || echo "$ROOT/mongod.log")"
BACKEND_PID=""
FRONTEND_PID=""
MONGO_PID=""

# ── colours ─────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'
BOLD='\033[1m'; NC='\033[0m'

info()  { echo -e "${CYAN}  →${NC} $1"; }
ok()    { echo -e "${GREEN}  ✓${NC} $1"; }
warn()  { echo -e "${YELLOW}  ⚠${NC} $1"; }
err()   { echo -e "${RED}  ✗${NC} $1"; }
header(){ echo -e "\n${BOLD}━━━ $1 ━━━${NC}"; }

# ── cleanup ─────────────────────────────────────────────────────────────
cleanup() {
    echo -e "\n${YELLOW}Shutting down…${NC}"
    [ -n "$BACKEND_PID" ] && kill "$BACKEND_PID" 2>/dev/null && info "Backend stopped"
    [ -n "$FRONTEND_PID" ] && kill "$FRONTEND_PID" 2>/dev/null && info "Frontend stopped"
    [ -n "$MONGO_PID" ] && kill "$MONGO_PID" 2>/dev/null && info "MongoDB stopped"
    wait 2>/dev/null
    ok "All services stopped"
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# ── 1. Prerequisites ────────────────────────────────────────────────────
header "Prerequisites"

check_cmd() { command -v "$1" >/dev/null 2>&1; }

check_cmd mongod    || { err "mongod not found. Install MongoDB Community Edition."; exit 1; }
check_cmd node      || { err "node not found. Install Node.js 18+."; exit 1; }
check_cmd npm       || { err "npm not found."; exit 1; }
check_cmd python3   || check_cmd python || { err "python not found. Install Python 3.11+."; exit 1; }

PYTHON_CMD="python3"
check_cmd python3 || PYTHON_CMD="python"

ok "mongod $(mongod --version 2>&1 | head -1 | grep -oP 'v[\d.]+' || echo 'found')"
ok "node $(node --version)"
ok "npm $(npm --version)"
ok "python $($PYTHON_CMD --version 2>&1)"

# ── 2. Start MongoDB ───────────────────────────────────────────────────
header "MongoDB"

if pgrep -x mongod >/dev/null 2>&1; then
    warn "MongoDB already running"
else
    info "Starting mongod…"
    mongod --config /dev/null --logpath "$MONGO_LOG" --fork 2>&1 || \
    mongod --config /dev/null --logpath "$MONGO_LOG" &
    MONGO_PID=$!
    # wait for port 27017
    for i in $(seq 1 30); do
        if command -v mongosh >/dev/null 2>&1; then
            mongosh --quiet --eval "db.runCommand({ping:1})" >/dev/null 2>&1 && break
        elif command -v python3 >/dev/null 2>&1 || command -v python >/dev/null 2>&1; then
            $PYTHON_CMD -c "import socket;s=socket.socket();s.settimeout(1);s.connect(('localhost',27017));s.close()" 2>/dev/null && break
        fi
        sleep 1
    done
    ok "MongoDB ready on port 27017"
fi

# ── 3. Start backend ───────────────────────────────────────────────────
header "Backend"

cd "$BACKEND"

# Detect venv python path (Linux/macOS: bin, Windows: Scripts)
if [ -f "$BACKEND/.venv/bin/python" ]; then
    VENV_PYTHON="$BACKEND/.venv/bin/python"
    UVICORN="$BACKEND/.venv/bin/uvicorn"
elif [ -f "$BACKEND/.venv/Scripts/python.exe" ]; then
    VENV_PYTHON="$BACKEND/.venv/Scripts/python.exe"
    UVICORN="$BACKEND/.venv/Scripts/uvicorn.exe"
else
    info "Creating virtual environment…"
    $PYTHON_CMD -m venv .venv
    if [ -f "$BACKEND/.venv/bin/python" ]; then
        VENV_PYTHON="$BACKEND/.venv/bin/python"
        UVICORN="$BACKEND/.venv/bin/uvicorn"
    else
        VENV_PYTHON="$BACKEND/.venv/Scripts/python.exe"
        UVICORN="$BACKEND/.venv/Scripts/uvicorn.exe"
    fi
    "$VENV_PYTHON" -m pip install -q -r requirements.txt
fi

info "Starting uvicorn on port 8080…"
"$UVICORN" main:app --host 0.0.0.0 --port 8080 --workers 1 &
BACKEND_PID=$!

# wait for health
for i in $(seq 1 60); do
    if curl -sf http://localhost:8080/health >/dev/null 2>&1; then
        break
    fi
    sleep 1
done
if curl -sf http://localhost:8080/health >/dev/null 2>&1; then
    ok "Backend healthy on http://localhost:8080"
    curl -s http://localhost:8080/health | $PYTHON_CMD -m json.tool 2>/dev/null || true
else
    err "Backend failed to start within 60s — check backend/uvicorn.log"
    exit 1
fi

# Verify Gemini API configuration via health endpoint
HEALTH_JSON=$(curl -s http://localhost:8080/health 2>/dev/null || echo '{}')
if echo "$HEALTH_JSON" | grep -q '"gemini_api": "configured"'; then
    ok "Gemini API configured"
else
    warn "Gemini API not configured - AI features will be unavailable"
fi

# ── 4. Start frontend ──────────────────────────────────────────────────
header "Frontend"

cd "$FRONTEND"
if [ ! -d node_modules ]; then
    info "Installing npm dependencies…"
    npm install
fi

info "Starting Next.js dev server on port 3000…"
npx next dev --port 3000 &
FRONTEND_PID=$!

# wait for port 3000
for i in $(seq 1 60); do
    if curl -sf http://localhost:3000 >/dev/null 2>&1; then
        break
    fi
    sleep 1
done
if curl -sf http://localhost:3000 >/dev/null 2>&1; then
    ok "Frontend ready on http://localhost:3000"
else
    warn "Frontend may still be compiling — check http://localhost:3000 manually"
fi

# ── 5. Running ─────────────────────────────────────────────────────────
header "Running"
echo -e "  ${BOLD}Frontend:${NC}  http://localhost:3000"
echo -e "  ${BOLD}Backend:${NC}   http://localhost:8080"
echo -e "  ${BOLD}API Docs:${NC}  http://localhost:8080/docs"
echo -e "  ${BOLD}Health:${NC}    http://localhost:8080/health"
echo -e ""
echo -e "  Press ${RED}Ctrl+C${NC} to stop all services"
echo -e ""

# Auto-open browser
if command -v xdg-open >/dev/null 2>&1; then
    xdg-open http://localhost:3000 >/dev/null 2>&1 &
elif command -v open >/dev/null 2>&1; then
    open http://localhost:3000 >/dev/null 2>&1 &
fi

# Keep running while child processes are alive
wait