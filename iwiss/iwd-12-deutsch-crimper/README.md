# IWISS IWD-12 — Deutsch terminal crimper

Source photo: `IMG_1824.jpeg` (reshoot; the original IMG_1808 was unusable)

| | |
|---|---|
| Part number | IWD-12 |
| Measured length | 160 mm |
| Measured width | 103 mm |
| Traced (raw) | 159.84 x 100.94 mm |
| Cutout depth | 20 mm |
| Bin size | 3x5 units (125.38 x 209.38 mm) |
| Clearance | 1.5 mm radial |

The first photo caught the spring-loaded handles nearly closed, tracing 25%
narrower than measured. The reshoot has them at their measured spread and now
agrees to 1.8% — length within 0.16 mm, width within 2 mm.

## Files

- `cutout.stl` — cutting body. Subtract from a bin to produce the pocket.
- `cutout.dxf` — 2D outline in mm (outline only; the finger slot is not included).
- `bin.stl` — finished gridfinity container, pocket already subtracted.
- `meta.json` — every parameter used, including the outline points.

## Regenerate

```
python3 ../../scripts/make_tool.py <photo> iwiss-iwd-12 --length 160 --width 103 --outdir .
python3 ../../scripts/make_bin.py --meta meta.json --out . --stem bin
```
