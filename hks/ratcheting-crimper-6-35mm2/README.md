# HKS — Ratcheting crimper, 6–35 mm²

Source photo: `IMG_1823.jpeg` (reshoot; see note)

No part number is marked on the tool. The body carries an "HKS" logo and the
die is stamped with its wire range (6 / 10 / 16 / 25 / 35 mm²), which is what
this folder is named for.

| | |
|---|---|
| Part number | none found |
| Die range | 6–35 mm² |
| Measured length | 235 mm |
| Measured width | 79 mm across the red grip flares |
| Traced (raw) | 234.89 x 75.07 mm |
| Cutout depth | 20 mm |
| Bin size | 3x7 units (125.38 x 293.38 mm) |
| Clearance | 1.5 mm radial |
| Mirrored | yes — flipped relative to the source photo |

**Why the reshoot.** The original `IMG_1811.jpeg` was taken on wood under hard
directional light, throwing a shadow alongside each handle that read L=11 —
darker than the tool's own black body at L=28, and neutral in hue where the
body is cool. Neither the darkness nor the warm/cool channel could separate
them, so the shadow was traced as part of the tool and the handle ends came out
angled. The reshoot on white paper has no such shadow and traces cleanly.

**Note on width:** the widest point is the pair of pointed red flares where the
grips meet the body — not the black body and not the handle tips. The trace
follows them faithfully and gives 76.1 mm when scaled to the 235 mm length,
against 79 mm measured, an aspect agreement of 3.7%.

The residual difference is handle position. The flares sit just below the
pivot, so they swing outward as the handles open. This photo has the handles
closed, which is the narrow extreme; the earlier wood photo had them spread and
traced slightly wider (384 px against 368 px on a comparable length). If the
tool is stored with its handles relaxed rather than squeezed shut, reshoot in
that position and rebuild.

## Files

- `cutout.stl` — cutting body. Subtract from a bin to produce the pocket.
- `cutout.dxf` — 2D outline in mm (outline only; the finger slot is not included).
- `bin.stl` — finished gridfinity container, pocket already subtracted.
- `meta.json` — every parameter used, including the outline points.

## Regenerate

```
python3 ../../scripts/make_tool.py <photo> hks-crimper --length 235 --width 80 --mirror --outdir .
python3 ../../scripts/make_bin.py --meta meta.json --out . --stem bin
```
