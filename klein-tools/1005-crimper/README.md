# Klein Tools 1005 — Wire crimper / cutter

Source photo: `IMG_1805.jpeg`

| | |
|---|---|
| Part number | 1005 |
| Measured length | 246 mm |
| Measured width | 51 mm |
| Cutout depth | 20 mm |
| Bin size | 2x7 units (83.38 x 293.38 mm) |
| Clearance | 1.5 mm radial |

## Files

- `cutout.stl` — cutting body. Subtract from a bin to produce the pocket.
- `cutout.dxf` — 2D outline in mm (outline only; the finger slot is not included).
- `bin.stl` — finished gridfinity container, pocket already subtracted.
- `meta.json` — every parameter used, including the outline points.

## Regenerate

```
python3 ../../scripts/make_tool.py <photo> klein-1005 --length 246 --width 51 --outdir .
```

Regenerate the bin from `meta.json`:

```
python3 ../../scripts/make_bin.py --meta meta.json --out . --stem bin
```
