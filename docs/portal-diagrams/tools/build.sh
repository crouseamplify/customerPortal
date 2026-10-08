#!/usr/bin/env bash
# Rebuild every diagram and the interactive explorer.
#   tools/build.sh <path-to-retrieved-metadata>   e.g. /tmp/portal_proj/force-app/main/default
# Needs: python3, node 18+. Renderer packages are installed outside this folder so Drive does not sync node_modules.
set -euo pipefail
SRC="${1:?path to retrieved force-app/main/default (see README)}"
HERE="$(cd "$(dirname "$0")/.." && pwd)"
TOOLS="${PORTAL_TOOLS_DIR:-$HOME/.cache/portal-diagram-tools}"
LWC="$HERE/../../force-app/main/default/lwc"

mkdir -p "$TOOLS"
cp "$HERE/tools/package.json" "$HERE/tools/render.mjs" "$TOOLS/"
(cd "$TOOLS" && [ -d node_modules ] || npm install --silent)

rm -rf "$HERE/static"
python3 -I "$HERE/tools/build_model.py" --src "$SRC" --lwc "$LWC" --out "$HERE"
python3 -I "$HERE/tools/build_diagrams.py" "$HERE"
python3 -I "$HERE/tools/matrices.py" "$HERE"
(cd "$TOOLS" && node render.mjs "$HERE/static")
python3 -I "$HERE/tools/build_explorer.py" "$HERE"
