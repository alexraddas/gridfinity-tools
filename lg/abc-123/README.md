# lg-abc-123

Generated automatically from a submitted photograph ([#5](../../issues/5)). Nobody has written notes on this tool yet, so treat anything unusual about it as undocumented rather than absent.

| | |
|---|---|
| Measured length | 180 mm |
| Width | 41.4 mm (derived from the photo) |
| Traced (raw) | 179.99 x 41.43 mm |
| Pocket | 182.93 x 44.42 mm |
| Cutout depth | 20 mm |
| Bin size | 2x5 units (83.38 x 209.38 mm) |
| Clearance | 1.5 mm radial |
| Lip margin | 10.27 mm per end |

## Files

- `bin.stl` — finished gridfinity container, pocket already subtracted.
- `cutout.stl` — tool-shaped cutting body, to subtract from your own bin.
- `cutout.dxf` — 2D outline in millimetres, for CAD.
- `outline_sheet.pdf` / `.jpg` — dimensioned 1:1 drawing. Print at 100%.
- `meta.json` — every parameter used, including the outline points.

## Accuracy

The outline is traced from a photograph and scaled to the measured length, so
the whole model rests on that one number. Print `outline_sheet.pdf` at 100% and
lay the tool on it before printing a bin: a bin that grips or rattles
*uniformly* is a mis-measured length, not a bad trace.

## Regenerate

```
python3 ../../scripts/make_tool.py <photo> lg-abc-123 --length 180 --outdir .
python3 ../../scripts/make_bin.py --meta meta.json --out . --stem bin
python3 ../../scripts/make_sheet.py meta.json
```
