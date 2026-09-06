# Baomain HSC8 6-4A — Self-adjusting ferrule crimper

Source photo: `IMG_hsc8-6-4a.jpeg`

HSC8 6-4A is a model designation sold by many vendors. The head carries only
"HSC8 6-4A" and the crimp range, so the manufacturer is recorded from the owner
rather than read off the tool.

| | |
|---|---|
| Model | HSC8 6-4A |
| Manufacturer | Baomain |
| Measured length | 174 mm |
| Measured width | 81 mm at the handle ends (see note) |
| Traced (raw) | 173.90 x 74.81 mm |
| Pocket | 177.82 x 78.71 mm |
| Cutout depth | 20 mm |
| Bin size | 3x5 units (125.38 x 209.38 mm) |
| Clearance | 2.0 mm radial (the repo default is 1.5) |

**Shot on the label face, which is the fix for a mirrored pocket.** The previous
photo, `IMG_1812.jpeg`, showed the *reverse* face — no "HSC8 6-4A" stamping, and
the spring on the other side of centre. The frame is a single plate carrying the
fixed handle, with the moving handle a separate lever riveted to one face and
standing proud of it in plan view, so the two faces are not mirror images:
laid label-up, the tool fouled the old pocket at 50 of 106 vertices, worst case
4.98 mm. Rebuilt from a label-up photograph, so the pocket now matches the way
the tool naturally goes down. Checked by rasterising the finished outline
against the photo's own mask: IoU 0.930 as traced, 0.826 mirrored.

**This tool has a right way up.** A `--symmetric` build — union with the mirror,
so either face drops in — was tried and reverted. It cost 987 mm2 of pocket
area (+11.8%) and up to 6.63 mm of local slop, which is a poor trade on a tool
with an obvious correct orientation. It is not really a crossed-jaw tool
anyway: the hex die closes concentrically, and what breaks its mirror symmetry
is the riveted moving-handle lever.

**Traced width is 6.2 mm under the measurement** (74.81 vs 81.0, aspect +7.4%,
well past the 4% check). The handles are spring-loaded, so how far apart they
sit in the photograph sets the traced width. Three separate photographs traced
73.9, 74.8 and 74.8 mm at this length, so the photographed spread is at least
consistent; either the tool rests narrower than 81 mm or the 81 mm was taken
with the grips pushed apart. **Print `outline_sheet.pdf` and lay the tool on it
before printing a bin** — that settles it in a way no amount of arithmetic can.

**Clearance is 2.0 mm rather than the repo's 1.5, and may no longer be needed.**
The 2.0 was introduced to pay for a scale error inferred from the *old* photo
and an assumed 171 mm length: the squeezed pose made the photographed tool
172.4–173.6 mm long, so scaling that to 171 mm shrank the whole model by
0.8–1.5%. With the length corrected to 174 mm and a fresh photograph, that
justification is largely gone — but nothing has yet confirmed the new scale is
right, so it stays at 2.0. Drop it to the 1.5 mm default once the paper sheet
shows the outline matching the tool.

## Files

- `cutout.stl` — cutting body. Subtract from a bin to produce the pocket.
- `cutout.dxf` — 2D outline in mm (outline only; the finger slot is not included).
- `bin.stl` — finished gridfinity container, pocket already subtracted.
- `outline_sheet.pdf` / `.jpg` — dimensioned 1:1 drawing. Print at 100%.
- `meta.json` — every parameter used, including the outline points.

## Regenerate

```
python3 ../../scripts/make_tool.py <photo> hsc8-6-4a --length 174 --width 81 --offset 2.0 --outdir .
python3 ../../scripts/make_bin.py --meta meta.json --out . --stem bin
python3 ../../scripts/make_sheet.py meta.json
```
