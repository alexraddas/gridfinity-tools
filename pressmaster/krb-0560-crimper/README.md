# Pressmaster KRB 0560 — Ratcheting crimper

Source photo: `IMG_1826.jpeg` (supersedes IMG_1816 and IMG_1821)

Marked "pressmaster", "KRB 0560", "Made in Sweden",
"US PATENT NO. 5,649,444/5,038,291". Die stamped 1.5 / 2.5 / 6.

| | |
|---|---|
| Part number | KRB 0560 |
| Measured length | 253 mm |
| Measured width | 73 mm |
| Traced (raw) | 252.89 x 71.39 mm |
| Cutout depth | 20 mm |
| Bin size | 3x7 units (125.38 x 293.38 mm) |
| Clearance | 1.5 mm radial |

**On bin width:** 3 units gives 22.5 mm per side. 2 units would fit, but with
only 1.55 mm per side — below the 5 mm minimum and tight enough to be a real
risk. Rebuild with `--units-w 2` if you would rather have the narrower bin.

Two earlier photographs of this tool were unusable: `IMG_1816.jpeg` picked up
shadow between the handles, and `IMG_1821.jpeg` had the tool running off the
edge of the paper backdrop.

## Files

- `cutout.stl` — cutting body. Subtract from a bin to produce the pocket.
- `cutout.dxf` — 2D outline in mm (outline only; the finger slot is not included).
- `bin.stl` — finished gridfinity container, pocket already subtracted.
- `meta.json` — every parameter used, including the outline points.

## Regenerate

```
python3 ../../scripts/make_tool.py <photo> pressmaster-krb-0560 --length 253 --width 73 --outdir .
python3 ../../scripts/make_bin.py --meta meta.json --out . --stem bin
```
