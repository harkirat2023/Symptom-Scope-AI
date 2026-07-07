#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# SymptomScope AI - Deployment Script
# =============================================================================
# Usage:
#   ./scripts/deploy.sh [frontend|backend|all]
#
# Prerequisites:
#   - Vercel CLI installed (npm i -g vercel)
#   - Railway CLI installed (npm i -g railway)
#   - Logged into Vercel: vercel login
#   - Logged into Railway: railway login
# =============================================================================

DEPLOY_TARGET="${1:-all}"

info()  { printf "\033[34m[INFO]\033[0m %s\n" "$*"; }
ok()    { printf "\033[32m[OK]\033[0m   %s\n" "$*"; }
err()   { printf "\033[31m[ERR]\033[0m  %s\n" "$*" >&2; }

deploy_frontend() {
  info "Deploying frontend to Vercel..."
  cd frontend

  if [ ! -f .env.local ]; then
    err ".env.local not found in frontend/. Copy .env.example to .env.local"
    exit 1
  fi

  vercel --prod --yes
  ok "Frontend deployed to Vercel"
  cd ..
}

deploy_backend() {
  info "Deploying backend to Railway..."
  cd backend

  if [ ! -f .env ]; then
    err ".env not found in backend/. Copy .env.example to .env"
    exit 1
  fi

  railway up --service symptomscope-api --detach
  ok "Backend deployed to Railway"
  cd ..
}

case "$DEPLOY_TARGET" in
  frontend)
    deploy_frontend
    ;;
  backend)
    deploy_backend
    ;;
  all)
    deploy_frontend
    deploy_backend
    ok "Full deployment complete!"
    ;;
  *)
    echo "Usage: $0 [frontend|backend|all]"
    exit 1
    ;;
esac
