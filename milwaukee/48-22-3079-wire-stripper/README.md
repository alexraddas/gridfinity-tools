# Milwaukee 48-22-3079 — 6-in-1 wire stripper

Source photo: `IMG_48-22-3079.jpeg`

| | |
|---|---|
| Part number | 48-22-3079 (stamped on the pivot disc) |
| Measured length | 196 mm |
| Measured width | 54 mm |
| Traced (raw) | 196.00 x 52.70 mm |
| Cutout depth | 20 mm |
| Bin size | 2x5 units (83.38 x 209.38 mm) |
| Clearance | 1.5 mm radial |

**Symmetric pocket.** The jaws cross, so the silhouette is 180-degree
rotationally symmetric rather than mirror symmetric, and a pocket cut from the
photographed face rejects the tool laid in the other way up -- measured 39 of
119 vertices fouling, worst case 4.70 mm, spread over nearly the full length
because the handles splay unevenly. Built with `--symmetric`; both orientations
now clear by at least 1.37 mm. Costs 634 mm2 of pocket area and nothing in bin
size.

**Packed to 2x5, not the 2x6 the grid rule picks.** The 198.89 mm outline
clears the 2x5 lip opening (203.48 mm) by 2.29 mm per end, under the 5 mm
minimum, so `--units-l 5` overrides it. 2x6 leaves 23 mm of dead bin at each
end for no benefit.

**Traced width is 1.3 mm under the measurement** (52.70 vs 54.0, aspect +2.5%,
inside the 4% check). Outlines are scaled by length only, and the segmentation
erodes the mask slightly, so every tool here comes out a fraction narrow. The
pocket is still 55.64 mm across, giving roughly 0.8 mm per side on a 54 mm
tool rather than the nominal 1.5 mm.

**Shot on pale quartz at the default thresholds.** Unlike the Milwaukee
scissors, this tool did not need `--dl-strict/--dl-mid` lowered — the body is
black oxide and the red grips are strongly saturated, so both the darkness and
the a\* channel fire hard against the near-neutral countertop. The polished
nose bevel traces correctly at the defaults.

**The handle gap stays open.** The 24.88 mm slot between the grips survives
the 1.5 mm offset at 22.12 mm, leaving a 20 mm-tall island of material in the
pocket. Wide enough to print without support.

## Files

- `cutout.stl` — cutting body. Subtract from a bin to produce the pocket.
- `cutout.dxf` — 2D outline in mm (outline only; the finger slot is not included).
- `bin.stl` — finished gridfinity container, pocket already subtracted.
- `meta.json` — every parameter used, including the outline points.

## Regenerate

```
python3 ../../scripts/make_tool.py <photo> milwaukee-48-22-3079 --length 196 --width 54 --units-l 5 --symmetric --outdir .
python3 ../../scripts/make_bin.py --meta meta.json --out . --stem bin
```
