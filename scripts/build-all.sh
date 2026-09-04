#!/usr/bin/env bash
# Rebuild every tool from its source photo. Requires Fusion running with its
# MCP server. Run from the repository root:  bash scripts/build-all.sh
set -euo pipefail
S="$(cd "$(dirname "$0")" && pwd)"
PHOTOS="${PHOTOS:-$HOME/Desktop/tools}"

# dir | photo | name | length | width | extra flags
TOOLS=(
"klein-tools/d228-8-diagonal-cutters|$S/../photos/IMG_1804_crop_d228-8.jpg|klein-d228-8|206|49|"
"klein-tools/1005-crimper|$PHOTOS/IMG_1805.jpeg|klein-1005|246|51|"
"klein-tools/1019-wire-stripper|$PHOTOS/IMG_1810.jpeg|klein-1019|196|55|--mirror"
"klein-tools/d2755-flush-cutter|$PHOTOS/IMG_1814.jpeg|klein-d2755|131|81|"
"tool-aid/18880-deutsch-crimper|$PHOTOS/IMG_1809.jpeg|toolaid-18880|155|103|--units-l 4"
"hks/ratcheting-crimper-6-35mm2|$PHOTOS/IMG_1811.jpeg|hks-crimper|235|80|--mirror"
"doyle/cable-cutters|$PHOTOS/IMG_1806.jpeg|doyle-cutters|240|51|"
)

for t in "${TOOLS[@]}"; do
  IFS='|' read -r dir photo name len wid extra <<< "$t"
  echo "=== $dir ==="
  mkdir -p "$dir"
  python3 "$S/make_tool.py" "$photo" "$name" --length "$len" --width "$wid" $extra --outdir "$dir"
  python3 "$S/make_bin.py" --meta "$dir/meta.json" --out "$dir" --stem bin --name "$name-bin"
done
