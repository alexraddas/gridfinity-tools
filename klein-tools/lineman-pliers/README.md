# Klein Tools — Lineman's pliers

Source photo: `IMG_1805.jpeg`

| | |
|---|---|
| Measured length | 246 mm |
| Measured width | 51 mm |
| Cutout depth | 20 mm |
| Clearance | 1.5 mm radial |

## Files

- `cutout.stl` — cutting body. Subtract from a bin to produce the pocket.
- `cutout.dxf` — 2D outline in mm (outline only; the finger slot is not included).

## Regenerate

```
python3 ../../scripts/make_tool.py <photo> lineman-pliers --length 246 --width 51 --outdir .
```
