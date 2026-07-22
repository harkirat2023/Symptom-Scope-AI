#!/usr/bin/env bash
# =============================================================================
# SymptomScope AI — Docker Startup Script (Linux/macOS)
# =============================================================================
# Builds and starts all services via Docker Compose, waits for health checks,
# and opens the frontend in the default browser.
# =============================================================================
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
COMPOSE_CMD="docker compose"
TIMEOUT=120

# ── colours ─────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'
BOLD='\033[1m'; NC='\033[0m'

info()  { echo -e "${CYAN}[INFO]${NC} $1"; }
ok()    { echo -e "${GREEN}[OK]${NC}   $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
err()   { echo -e "${RED}[ERR]${NC}  $1"; }

cleanup() {
    echo ""
    info "Shutting down services..."
    $COMPOSE_CMD down 2>/dev/null || true
    ok "All services stopped"
}
trap cleanup EXIT INT TERM

# ── 1. Prerequisites ────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}━━━ SymptomScope AI — Docker Startup ━━━${NC}"
echo ""

if ! command -v docker &>/dev/null; then
    err "Docker not found. Install from https://docs.docker.com/get-docker/"
    exit 1
fi

if ! docker compose version &>/dev/null; then
    warn "docker compose V2 not found, trying docker-compose..."
    if command -v docker-compose &>/dev/null; then
        COMPOSE_CMD="docker-compose"
    else
        err "Neither docker compose nor docker-compose found."
        exit 1
    fi
fi

# ── 2. Environment files ────────────────────────────────────────────────────
if [ ! -f "$ROOT/backend/.env" ]; then
    warn "backend/.env not found — creating from .env.example"
    cp "$ROOT/backend/.env.example" "$ROOT/backend/.env"
    warn "Edit backend/.env with your GEMINI_API_KEY and other settings"
fi

if [ ! -f "$ROOT/frontend/.env.local" ]; then
    warn "frontend/.env.local not found — creating from .env.example"
    cp "$ROOT/frontend/.env.example" "$ROOT/frontend/.env.local"
    warn "Edit frontend/.env.local with your Clerk keys"
fi

# ── 3. Build and start ──────────────────────────────────────────────────────
info "Building and starting services..."
$COMPOSE_CMD up --build -d

# ── 4. Wait for backend ─────────────────────────────────────────────────────
info "Waiting for backend to become healthy..."
elapsed=0
while [ $elapsed -lt $TIMEOUT ]; do
    if curl -sf http://localhost:8080/health >/dev/null 2>&1; then
        ok "Backend healthy on http://localhost:8080"
        break
    fi
    sleep 5
    elapsed=$((elapsed + 5))
    echo -n "."
done
echo ""

if [ $elapsed -ge $TIMEOUT ]; then
    err "Backend failed to start within ${TIMEOUT}s"
    $COMPOSE_CMD logs backend --tail=30
    exit 1
fi

# ── 5. Wait for frontend ────────────────────────────────────────────────────
info "Waiting for frontend to become ready..."
elapsed=0
while [ $elapsed -lt $TIMEOUT ]; do
    if curl -sf -o /dev/null http://localhost:3000 2>/dev/null; then
        ok "Frontend ready on http://localhost:3000"
        break
    fi
    sleep 5
    elapsed=$((elapsed + 5))
    echo -n "."
done
echo ""

if [ $elapsed -ge $TIMEOUT ]; then
    warn "Frontend may still be compiling — check http://localhost:3000 manually"
fi

# ── 6. Running ──────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}━━━ SymptomScope AI is fully operational! ━━━${NC}"
echo ""
echo -e "  ${BOLD}Frontend:${NC}  http://localhost:3000"
echo -e "  ${BOLD}Backend:${NC}   http://localhost:8080"
echo -e "  ${BOLD}API Docs:${NC}  http://localhost:8080/docs"
echo ""

if command -v xdg-open &>/dev/null; then
    xdg-open http://localhost:3000
elif command -v open &>/dev/null; then
    open http://localhost:3000
fi

echo -e "  Press ${RED}Ctrl+C${NC} to stop all services"
echo ""
wait
