# Klein Tools 1019 — Wire stripper / crimper

Source photo: `IMG_1810.jpeg`

| | |
|---|---|
| Part number | 1019 |
| Measured length | 196 mm |
| Measured width | 55 mm |
| Cutout depth | 20 mm |
| Bin size | 2x6 units (83.38 x 251.38 mm) |
| Clearance | 1.5 mm radial |
| Mirrored | yes — flipped relative to the source photo |

## Files

- `cutout.stl` — cutting body. Subtract from a bin to produce the pocket.
- `cutout.dxf` — 2D outline in mm (outline only; the finger slot is not included).
- `bin.stl` — finished gridfinity container, pocket already subtracted.
- `meta.json` — every parameter used, including the outline points.

## Regenerate

```
python3 ../../scripts/make_tool.py <photo> klein-1019 --length 196 --width 55 --mirror --outdir .
```

Regenerate the bin from `meta.json`:

```
python3 ../../scripts/make_bin.py --meta meta.json --out . --stem bin
```
