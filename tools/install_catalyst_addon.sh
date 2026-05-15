#!/usr/bin/env bash
set -euo pipefail

# Installs the official Godot Catalyst editor addon into this repo's `addons/`
# folder by extracting it from the published npm package tarball.
#
# Run from anywhere:
#   bash tools/install_catalyst_addon.sh

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
cleanup() {
  rm -rf "$TMP"
}
trap cleanup EXIT

VERSION="${GODOT_CATALYST_VERSION:-1.2.0}"
URL="https://registry.npmjs.org/godot-catalyst/-/godot-catalyst-${VERSION}.tgz"

echo "Downloading ${URL}"
curl -fsSL "${URL}" -o "${TMP}/pkg.tgz"

tar -xzf "${TMP}/pkg.tgz" -C "${TMP}"

mkdir -p "${ROOT}/addons"
rm -rf "${ROOT}/addons/godot_catalyst"
cp -R "${TMP}/package/godot-plugin/addons/godot_catalyst" "${ROOT}/addons/"

echo ""
echo "Installed Godot Catalyst to:"
echo "  ${ROOT}/addons/godot_catalyst"
echo ""
echo "Next steps:"
echo "  1) Open the project in Godot 4.x"
echo "  2) Project -> Project Settings -> Plugins -> enable \"Godot Catalyst\""
echo "  3) Configure your MCP client with GODOT_PROJECT_PATH pointing at:"
echo "       ${ROOT}"
