# Klein Tools D2755 — Flush cutter

Source photo: `IMG_1814.jpeg`

| | |
|---|---|
| Part number | D2755 |
| Measured length | 131 mm |
| Measured width | 81 mm (see note) |
| Cutout depth | 20 mm |
| Bin size | 3x4 units (125.38 x 167.38 mm) |
| Clearance | 1.5 mm radial |

**Note on width:** the traced outline is 87.3 mm wide when scaled to the
131 mm length, against the 81 mm measured — a 6.8% disagreement. The handles
are spring-loaded and splay to a variable width, so the photo and the caliper
caught them at different positions. Scaling is driven by the length, which is
fixed. If the pocket feels loose, re-shoot with the handles held at rest.

## Files

- `cutout.stl` — cutting body. Subtract from a bin to produce the pocket.
- `cutout.dxf` — 2D outline in mm (outline only; the finger slot is not included).
- `bin.stl` — finished gridfinity container, pocket already subtracted.
- `meta.json` — every parameter used, including the outline points.

## Regenerate

```
python3 ../../scripts/make_tool.py <photo> klein-d2755 --length 131 --width 81 --outdir .
python3 ../../scripts/make_bin.py --meta meta.json --out . --stem bin
```
