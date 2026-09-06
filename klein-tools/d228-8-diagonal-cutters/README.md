# Klein Tools D228-8 — Diagonal cutters

Source photo: `IMG_1804.jpeg` (two tools in frame; cropped to x < 2100 px — see `photos/IMG_1804_crop_d228-8.jpg`)

| | |
|---|---|
| Part number | D228-8 |
| Measured length | 206 mm |
| Measured width | 49 mm |
| Cutout depth | 20 mm |
| Bin size | 2x6 units (83.38 x 251.38 mm) |
| Clearance | 1.5 mm radial |

## Files

- `cutout.stl` — cutting body. Subtract from a bin to produce the pocket.
- `cutout.dxf` — 2D outline in mm (outline only; the finger slot is not included).
- `bin.stl` — finished gridfinity container, pocket already subtracted.
- `meta.json` — every parameter used, including the outline points.

## Regenerate

```
python3 ../../scripts/make_tool.py <photo> klein-d228-8 --length 206 --width 49 \
    --dl-strict 70 --dl-mid 60 --outdir .
```

Regenerate the bin from `meta.json`:

```
python3 ../../scripts/make_bin.py --meta meta.json --out . --stem bin
```

## Why this one needs `--dl-strict 70 --dl-mid 60`

The polished face of the head is covered in specular highlights that are
*brighter than the wood*, so at the default 85/80 the luminance channel reads
zero or negative right across it — measured along one scanline: L 225 giving
dL 0, L 242 giving dL -8, L 229 giving dL -17. The warmth channel only reaches
5-11 there against a strict threshold of 18. So the head contributed nothing to
the strict seed and was left entirely as probable-foreground.

That is what broke it. GrabCut trains its foreground colour model on the strict
seed, which here held the red grips and no metal at all. The black outer face of
the far jaw reads dL 211 — far above any threshold, unambiguously tool — but it
resembles nothing in that foreground model, so GrabCut discarded it. The mask
had the wedge; GrabCut threw it away. The default also punched a hole clean
through the closed jaws, which would have left a post standing in the pocket.

Dropping the thresholds to 70/60 puts metal into the seed and both faults go.
Traced width lands at 49.04 mm against 49 mm measured, +0.1%.

Do not push them lower to "improve" it. At 40/30 the contour crosses into the
cast shadow along the right-hand edge and the trace comes out 51.44 mm wide,
tripping the aspect warning at -4.8%.
