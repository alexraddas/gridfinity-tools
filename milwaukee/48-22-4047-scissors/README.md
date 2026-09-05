# Milwaukee 48-22-4047 — Offset scissors

Source photo: `IMG_1827.jpeg`

| | |
|---|---|
| Part number | 48-22-4047 |
| Measured length | 253 mm, blade tip to the tip of the larger handle |
| Measured width | 96 mm across the handles |
| Traced (raw) | 252.89 mm tip-to-tip, 94.55 mm wide |
| Cutout depth | 20 mm |
| Bin size | 3x7 units (125.38 x 293.38 mm) |
| Clearance | 1.5 mm radial |

**Scaled tip-to-tip, not by bounding extent.** These scissors are offset, so
the blade-tip-to-handle-tip distance is 4.2% longer than the tightest bounding
rectangle. Scaling the rectangle to 253 mm would have made the model about
10 mm too long. Built with `--length-mode tip`; the result is within 0.11 mm
of the measurement.

**Finger loops are filled.** The pocket is a solid scissor silhouette. Keeping
the loops open would have meant two thin 20 mm posts standing up through them —
fragile, and the scissors would have to be lifted straight up to clear them.

**Luminance thresholds are lowered for this tool** (`--dl-strict 50
--dl-mid 35`, against defaults of 85/80). The defaults were tuned for dark
tools on wood. Bare steel on a pale backdrop is far lower contrast: measured
across the blade, the tool sits at dL 43-60 where the backdrop is 16-27 —
clearly separable, but well under the default threshold. At the defaults the
contour ran down the middle of the blade, following the dark line between the
two halves and cutting off the bright sharpened bevel, losing roughly a third
of the blade width.

An earlier photograph, `IMG_1828.jpeg`, was taken on a dark laptop lid. That
inverts the luminance test — the polished blades are *brighter* than the
backdrop — and only the red handles were traced. Shoot metal tools on a light
backdrop and lower the thresholds instead.

## Files

- `cutout.stl` — cutting body. Subtract from a bin to produce the pocket.
- `cutout.dxf` — 2D outline in mm (outline only; the finger slot is not included).
- `bin.stl` — finished gridfinity container, pocket already subtracted.
- `meta.json` — every parameter used, including the outline points.

## Regenerate

```
python3 ../../scripts/make_tool.py <photo> milwaukee-48-22-4047 \
    --length 253 --width 96 --length-mode tip --outdir .
python3 ../../scripts/make_bin.py --meta meta.json --out . --stem bin
```
