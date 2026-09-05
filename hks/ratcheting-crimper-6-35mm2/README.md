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
| Measured width | 80 mm (see note) |
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

**Note on width:** the trace gives 75.1 mm when scaled to the 235 mm length,
against 80 mm measured — 5.0% apart. Two independent photos agree with each
other (3.109 and 3.085 aspect) and disagree with the caliper, so the
measurement is the more likely culprit. The widest point of the trace is the
rigid black body, not the handles. Worth re-measuring across the body.

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
