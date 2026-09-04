# Klein Tools 1005 — Wire crimper / cutter

Source photo: `IMG_1805.jpeg`

| | |
|---|---|
| Part number | 1005 |
| Measured length | 246 mm |
| Measured width | 51 mm |
| Cutout depth | 20 mm |
| Clearance | 1.5 mm radial |

## Files

- `cutout.stl` — cutting body. Subtract from a bin to produce the pocket.
- `cutout.dxf` — 2D outline in mm (outline only; the finger slot is not included).

## Regenerate

```
python3 ../../scripts/make_tool.py <photo> klein-1005 --length 246 --width 51 --outdir .
```
