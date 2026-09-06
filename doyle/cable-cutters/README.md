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

**The pocket is symmetric, and has to be.** A cable cutter head is 180-degree
rotationally symmetric, not mirror symmetric -- the heel of one jaw stands
proud on the left, the other's on the right. `IMG_1806.jpeg` shows the "WEAR
EYE PROTECTION" face; laid in with the "GENUINE DOYLE QUALITY" face up the
tool presents the mirror of that silhouette and fouled the first pocket at 38
of 134 vertices, worst case 2.73 mm, which jammed the head at one corner and
left an empty crescent at the other. Built with `--symmetric`, which unions the
outline with its mirror. Both orientations now clear by at least 1.35 mm.
Costs 640 mm2 of extra pocket area and nothing in bin size -- the outline is
centred on its bounding box, so mirroring cannot widen it.

**Back to 2x7 after a 2x6 was printed and rejected.** The 242.76 mm outline
does clear the 2x6 lip opening (245.48 mm), but only by 1.36 mm per end, which
leaves a lip shelf too thin to be worth having at the handle end. 2x7 gives
22.36 mm per end. The extra grid row is the price of a bin end you can actually
grip.

## Files

- `cutout.stl` — cutting body. Subtract from a bin to produce the pocket.
- `cutout.dxf` — 2D outline in mm (outline only; the finger slot is not included).
- `bin.stl` — finished gridfinity container, pocket already subtracted.
- `meta.json` — every parameter used, including the outline points.

## Regenerate

```
python3 ../../scripts/make_tool.py <photo> doyle-cutters --length 240 --width 51 --units-l 7 --symmetric --outdir .
python3 ../../scripts/make_bin.py --meta meta.json --out . --stem bin
```
