# Klein Tools — Diagonal cutters

Source photo: `IMG_1804.jpeg`

| | |
|---|---|
| Measured length | 206 mm |
| Measured width | 49 mm |
| Cutout depth | 20 mm |
| Clearance | 1.5 mm radial |

## Files

- `cutout.stl` — cutting body. Subtract from a bin to produce the pocket.
- `cutout.dxf` — 2D outline in mm (outline only; the finger slot is not included).

## Regenerate

```
python3 ../../scripts/make_tool.py <photo> diagonal-cutters --length 206 --width 49 --outdir .
```
