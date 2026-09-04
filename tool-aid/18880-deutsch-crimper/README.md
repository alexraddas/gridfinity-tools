# Tool Aid 18880 — Deutsch terminal crimper

Source photo: `IMG_1809.jpeg`

| | |
|---|---|
| Part number | 18880 |
| Measured length | 155 mm |
| Measured width | 103 mm |
| Cutout depth | 20 mm |
| Bin size | 3x4 units (125.38 x 167.38 mm) |
| Clearance | 1.5 mm radial |

**Tight fit:** the outline is 157.89 mm against a 161.48 mm lip opening, so
only **1.80 mm per end** — below the 5 mm minimum the generator normally
enforces. Kept deliberately at 3x4 rather than growing to 3x5; the lip was
checked and is intact all the way round. Rebuild with `--units-l 4` to
reproduce, or drop the flag for a roomier 3x5.

## Files

- `cutout.stl` — cutting body. Subtract from a bin to produce the pocket.
- `cutout.dxf` — 2D outline in mm (outline only; the finger slot is not included).
- `bin.stl` — finished gridfinity container, pocket already subtracted.
- `meta.json` — every parameter used, including the outline points.

## Regenerate

```
python3 ../../scripts/make_tool.py <photo> toolaid-18880 --length 155 --width 103 --units-l 4 --outdir .
python3 ../../scripts/make_bin.py --meta meta.json --out . --stem bin
```
