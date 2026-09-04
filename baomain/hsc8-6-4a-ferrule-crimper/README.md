# Baomain HSC8 6-4A — Self-adjusting ferrule crimper

Source photo: `IMG_1812.jpeg`

HSC8 6-4A is a model designation sold by many vendors. Nothing is marked on
the tool itself — the body is plain black with only crimp-size marks on the
hex die — so the manufacturer is recorded from the owner rather than read off
the tool.

| | |
|---|---|
| Model | HSC8 6-4A |
| Manufacturer | Baomain |
| Measured length | 171 mm |
| Measured width | 81 mm at the handle ends (see note) |
| Cutout depth | 20 mm |
| Bin size | 3x5 units (125.38 x 209.38 mm) |
| Clearance | 1.5 mm radial |

**Built as photographed.** The traced handle ends span 68 mm when scaled to
the 171 mm length, against 81 mm measured — 13.3% apart. The handles are
spring-loaded and sat closer together in the photo than when measured. The
pocket therefore matches the photo, and the tool seats with the handles
squeezed inward rather than at full rest. Reshoot with the handles at their
measured spread and rebuild if it needs to drop straight in.

## Files

- `cutout.stl` — cutting body. Subtract from a bin to produce the pocket.
- `cutout.dxf` — 2D outline in mm (outline only; the finger slot is not included).
- `bin.stl` — finished gridfinity container, pocket already subtracted.
- `meta.json` — every parameter used, including the outline points.

## Regenerate

```
python3 ../../scripts/make_tool.py <photo> hsc8-6-4a --length 171 --width 81 --outdir .
python3 ../../scripts/make_bin.py --meta meta.json --out . --stem bin
```
