# Heschen HS-07FL — Ratcheting crimper, 0.25–2.5 mm²

Source photo: `IMG_1822.jpeg`

Labelled "HS-07FL / INSULATED CABLE LINKS+BUTT CONNECTORS / 0.25-2.5mm²".
No brand is printed on the tool; the manufacturer is recorded from the owner.

| | |
|---|---|
| Model | HS-07FL |
| Range | 0.25–2.5 mm² |
| Measured length | 226 mm |
| Measured width | 71 mm |
| Traced (raw) | 225.82 x 67.79 mm |
| Cutout depth | 20 mm |
| Bin size | 2x6 units (83.38 x 251.38 mm) |
| Clearance | 1.5 mm radial |

**Bin width is a deliberate override.** The 5 mm end-margin rule would pick 3
units wide, but 2 units fits with 3.34 mm per side and saves a whole grid
column. Rebuild with `--units-w 2` to reproduce; drop the flag for the roomier
3x6.

**Consequence:** the finger slot is capped at the bin width minus 8 mm, so on a
2-unit bin it is 76 mm against a 70.8 mm tool — only **2.6 mm of access each
side**. On a 3x6 the slot would be 118 mm, giving 23.6 mm a side. If the tool
proves hard to lift out, that is the reason, and `--units-w 3` fixes it.

## Files

- `cutout.stl` — cutting body. Subtract from a bin to produce the pocket.
- `cutout.dxf` — 2D outline in mm (outline only; the finger slot is not included).
- `bin.stl` — finished gridfinity container, pocket already subtracted.
- `meta.json` — every parameter used, including the outline points.

## Regenerate

```
python3 ../../scripts/make_tool.py <photo> hs-07fl --length 226 --width 71 --units-w 2 --outdir .
python3 ../../scripts/make_bin.py --meta meta.json --out . --stem bin
```
