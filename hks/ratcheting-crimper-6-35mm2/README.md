# HKS — Ratcheting crimper, 6–35 mm²

Source photo: `IMG_1811.jpeg`

No part number is marked anywhere on the tool; the body is plain black oxide
and the only stamping is the die's wire range (6 / 10 / 16 / 25 / 35 mm²),
which is what this folder is named for.

| | |
|---|---|
| Part number | none found |
| Die range | 6–35 mm² |
| Measured length | 235 mm |
| Measured width | 80 mm (see note) |
| Cutout depth | 20 mm |
| Bin size | 3x7 units (125.38 x 293.38 mm) |
| Clearance | 1.5 mm radial |
| Mirrored | yes — flipped relative to the source photo |

**Note on width:** the traced outline is 75.2 mm wide when scaled to the
235 mm length, against 80 mm measured — 5.8% apart. The widest point of the
trace is the rigid black body, not the handles, so the body dimension is
sound; the discrepancy is most likely the handles sitting at a different
spread when measured than when photographed. With 1.5 mm clearance the
pocket is 78.1 mm wide, about 1.9 mm narrower than the measurement. If the
handles bind, rebuild with `--offset 3`.

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
