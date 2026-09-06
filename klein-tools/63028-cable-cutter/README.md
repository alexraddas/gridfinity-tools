# Klein Tools 63028 — Cable cutter

Traced from Klein's published product photograph, not from a photo taken here, and scaled to the **overall length Klein publishes** for this catalogue number — a nominal figure, not a measurement taken off the tool.

**Nobody has printed this bin or put the tool in it.** Everything below follows from that one published length, so if it is wrong the bin is uniformly tight or loose. Print `outline_sheet.pdf` at 100% and lay the tool on it before committing filament to it.

The product photograph is not in this repository — only the traced geometry.

| | |
|---|---|
| Catalogue length (nominal) | 216 mm |
| Width | 43.8 mm (derived from the photo) |
| Traced (raw) | 215.95 x 43.85 mm |
| Pocket | 218.85 x 46.81 mm |
| Cutout depth | 20 mm |
| Bin size | 2x6 units (83.38 x 251.38 mm) |
| Clearance | 1.5 mm radial |
| Lip margin | 13.32 mm per end |

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
python3 ../../scripts/make_tool.py <photo> klein-63028 --length 216 --outdir .
python3 ../../scripts/make_bin.py --meta meta.json --out . --stem bin
python3 ../../scripts/make_sheet.py meta.json
```
