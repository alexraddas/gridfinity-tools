# Doyle — Cable cutters

Source photo: `IMG_1806.jpeg`

No part number found. The head carries only the safety stamping
("WEAR EYE PROTECTION / WARNING NOT INSULATED / WILL NOT PROTECT AGAINST
ELECTRICAL SHOCK") and the handles are plain dipped vinyl. The reverse face
was not photographed, so a number may exist there.

| | |
|---|---|
| Part number | none found on the photographed face |
| Measured length | 240 mm |
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
python3 ../../scripts/make_tool.py <photo> doyle-cutters --length 240 --width 51 --outdir .
python3 ../../scripts/make_bin.py --meta meta.json --out . --stem bin
```
