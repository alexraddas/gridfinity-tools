# Klein Tools D228-8 — Diagonal cutters

Source photo: `IMG_1804.jpeg` (two tools in frame; cropped to x < 2100 px — see `photos/IMG_1804_crop_d228-8.jpg`)

| | |
|---|---|
| Part number | D228-8 |
| Measured length | 206 mm |
| Measured width | 49 mm |
| Cutout depth | 20 mm |
| Bin size | 2x6 units (83.38 x 251.38 mm) |
| Clearance | 1.5 mm radial |

## Files

- `cutout.stl` — cutting body. Subtract from a bin to produce the pocket.
- `cutout.dxf` — 2D outline in mm (outline only; the finger slot is not included).
- `bin.stl` — finished gridfinity container, pocket already subtracted.
- `meta.json` — every parameter used, including the outline points.

## Regenerate

```
python3 ../../scripts/make_tool.py <photo> klein-d228-8 --length 206 --width 49 --outdir .
```

Regenerate the bin from `meta.json`:

```
python3 ../../scripts/make_bin.py --meta meta.json --out . --stem bin
```
