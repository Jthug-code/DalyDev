#!/usr/bin/env bash
set -euo pipefail
# Creates github.com/Jthug-code/exo-mcp and pushes main. Requires: gh auth login (repo scope).
OWNER="${GITHUB_OWNER:-Jthug-code}"
REPO="${GITHUB_REPO:-exo-mcp}"
if ! gh auth status >/dev/null 2>&1; then
  echo "Run: gh auth login"
  exit 1
fi
if gh repo view "${OWNER}/${REPO}" >/dev/null 2>&1; then
  echo "Repository ${OWNER}/${REPO} already exists."
else
  gh repo create "${OWNER}/${REPO}" --public \
    --description "MCP bridge for managing exo clusters from Cursor" \
    --source "$(cd "$(dirname "$0")/.." && pwd)" \
    --remote origin --push
  exit 0
fi
git remote add origin "https://github.com/${OWNER}/${REPO}.git" 2>/dev/null || true
git push -u origin main
echo "Pushed to https://github.com/${OWNER}/${REPO}"
