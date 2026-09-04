# Klein Tools — Wire stripper / crimper

Source photo: `IMG_1810.jpeg`

| | |
|---|---|
| Measured length | 196 mm |
| Measured width | 55 mm |
| Cutout depth | 20 mm |
| Clearance | 1.5 mm radial |
| Mirrored | yes — flipped relative to the source photo |

## Files

- `cutout.stl` — cutting body. Subtract from a bin to produce the pocket.
- `cutout.dxf` — 2D outline in mm (outline only; the finger slot is not included).

## Regenerate

```
python3 ../../scripts/make_tool.py <photo> wire-stripper --length 196 --width 55 --mirror --outdir .
```
