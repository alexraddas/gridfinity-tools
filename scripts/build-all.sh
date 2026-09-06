#!/usr/bin/env bash
# Rebuild every tool from its source photo. Requires Fusion running with its
# MCP server. Run from the repository root:  bash scripts/build-all.sh
set -euo pipefail
S="$(cd "$(dirname "$0")" && pwd)"
PHOTOS="${PHOTOS:-$S/../photos}"

# NO_BUILD=1 refreshes meta.json and the validation sheets from the photos
# without touching Fusion -- useful after a segmentation change, since the
# STL/DXF only need regenerating when the outline actually moves.
NO_BUILD="${NO_BUILD:-}"

# dir | photo | name | length | width | extra flags
TOOLS=(
"klein-tools/d228-8-diagonal-cutters|$PHOTOS/IMG_1804_crop_d228-8.jpg|klein-d228-8|206|49|"
"klein-tools/1005-crimper|$PHOTOS/IMG_1805.jpeg|klein-1005|246|51|"
"klein-tools/1019-wire-stripper|$PHOTOS/IMG_1810.jpeg|klein-1019|196|55|--mirror"
"klein-tools/d2755-flush-cutter|$PHOTOS/IMG_1814.jpeg|klein-d2755|131|81|"
"tool-aid/18880-deutsch-crimper|$PHOTOS/IMG_1809.jpeg|toolaid-18880|155|103|--units-l 4"
"hks/ratcheting-crimper-6-35mm2|$PHOTOS/IMG_1823.jpeg|hks-crimper|235|79|--mirror"
"doyle/cable-cutters|$PHOTOS/IMG_1806.jpeg|doyle-cutters|240|51|--units-l 7 --symmetric"
"baomain/hsc8-6-4a-ferrule-crimper|$PHOTOS/IMG_1812.jpeg|hsc8-6-4a|171|81|--symmetric --offset 2.0"
"iwiss/iwd-12-deutsch-crimper|$PHOTOS/IMG_1824.jpeg|iwiss-iwd-12|160|103|"
"heschen/hs-07fl-crimper|$PHOTOS/IMG_1822.jpeg|hs-07fl|226|71|--units-w 2"
"pressmaster/krb-0560-crimper|$PHOTOS/IMG_1826.jpeg|pressmaster-krb-0560|253|73|"
"milwaukee/48-22-3079-wire-stripper|$PHOTOS/IMG_48-22-3079.jpeg|milwaukee-48-22-3079|196|54|--units-l 5 --symmetric"
"milwaukee/48-22-4047-scissors|$PHOTOS/IMG_1827.jpeg|milwaukee-48-22-4047|253|96|--length-mode tip --dl-strict 50 --dl-mid 35"
)

for t in "${TOOLS[@]}"; do
  IFS='|' read -r dir photo name len wid extra <<< "$t"
  echo "=== $dir ==="
  mkdir -p "$dir"
  if [ -n "$NO_BUILD" ]; then
    python3 "$S/make_tool.py" "$photo" "$name" --length "$len" --width "$wid" $extra \
            --no-build --outdir "$dir"
  else
    python3 "$S/make_tool.py" "$photo" "$name" --length "$len" --width "$wid" $extra --outdir "$dir"
    python3 "$S/make_bin.py" --meta "$dir/meta.json" --out "$dir" --stem bin --name "$name-bin"
  fi
  python3 "$S/make_sheet.py" "$dir/meta.json"
done
