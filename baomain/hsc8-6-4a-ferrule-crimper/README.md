# Baomain HSC8 6-4A — Self-adjusting ferrule crimper

Source photo: `IMG_1812.jpeg`

HSC8 6-4A is a model designation sold by many vendors. Nothing is marked on
the tool itself — the body is plain black with only crimp-size marks on the
hex die — so the manufacturer is recorded from the owner rather than read off
the tool.

| | |
|---|---|
| Model | HSC8 6-4A |
| Manufacturer | Baomain |
| Measured length | 171 mm |
| Measured width | 81 mm at the handle ends (see note) |
| Traced (raw) | 170.93 mm long, 71.35 mm wide |
| Pocket | 174.87 x 75.30 mm |
| Cutout depth | 20 mm |
| Bin size | 3x5 units (125.38 x 209.38 mm) |
| Clearance | 2.0 mm radial (the repo default is 1.5) |

**The pocket is symmetric, and has to be.** The frame of this crimper is a
single plate carrying the fixed handle; the moving handle is a separate lever
riveted on one face, and it stands proud of the frame in plan view. Laid in
the other face up the tool presents the mirror of the photographed silhouette,
which fouled the previous pocket at **50 of 106 vertices, worst case 4.98 mm** —
spread over all four regions of the outline (head 10/28, body 16/38, upper
handles 6/12, handle tips 18/28), not concentrated at one corner. That is
enough interference that the tool cannot enter at all; it sits proud and rocks.
Built with `--symmetric`, which unions the outline with its mirror before the
offset. Both faces now clear by at least 1.86 mm. It costs 950 mm2 of extra
pocket area, nothing in bin size, and — measured — nothing in location: the
tool's free play inside the pocket is +-1.9 mm in both axes whether the pocket
is symmetric or not, because the union adds material only where the pocket was
already slack.

About half of that mirror mismatch is not a real 3D feature but a 3.25-degree
skew: because only one handle moves and it sat squeezed, the silhouette's
minimum-area-rectangle axis is tilted about 1.6 degrees off the tool's own
symmetry axis. Rotating the mirrored silhouette by 3.25 degrees recovers the
interference from 4.98 mm to 2.09 mm. The pocket cannot rotate, so the full
4.98 mm is what the tool would have met.

**Clearance is 2.0 mm here, not the repo's usual 1.5.** The extra 0.5 mm pays
for a scale error that cannot be removed without a reshoot. The handles are
spring-loaded and sat squeezed in the photo, and squeezing them swings the
moving handle's tip *away* from the head: measured about the pivot at
(10.2, 30.4) mm with a tip radius of 117.3 mm, opening the handles from the
traced 68.7 mm spread to the measured 81 mm retracts that tip by 2.6 mm. The
photographed pose is therefore 172.4–173.6 mm long where the tool at rest is
171 mm, so scaling the trace to 171 mm shrinks the whole model by 0.8–1.5% —
a median 0.36 mm per side and up to 1.21 mm at the head. That is a uniform,
all-around loss, and it is what made the first pocket grip everywhere: against
the real tool it delivered only **+0.30 to +0.73 mm** of clearance at its
tightest point, not the 1.5 mm it nominally carried. At 2.0 mm the worst case
is +0.62 mm even on the most pessimistic pose correction, and +1.88 mm on the
least. 3.0 mm was rejected: free play would rise to about +-2.9 mm and the
pocket would stop locating the tool.

**Built as photographed; the handle spread is still short.** The traced handle
ends span 68.7 mm against 81 mm measured — 12.3 mm, or 6.15 mm per side. The
pocket matches the photo, so the tool still seats with the handles squeezed
inward rather than at full rest. The spring takes that up easily and it is not
what made the bin feel tight; the *rigid* head is what binds. Reshoot with the
handles held open at their measured spread and rebuild if you want it to drop
in without pinching the grips — that would also remove the scale error above
and let the clearance go back to 1.5 mm.

**`make_tool.py` prints an aspect warning for this tool, and it is expected.**
The traced 994 x 418 px silhouette is 12.7% off the measured 171 x 81 aspect,
for exactly the handle-spread reason above. The trace overlay is correct; check
it rather than the number.

## Files

- `cutout.stl` — cutting body. Subtract from a bin to produce the pocket.
- `cutout.dxf` — 2D outline in mm (outline only; the finger slot is not included).
- `bin.stl` — finished gridfinity container, pocket already subtracted.
- `meta.json` — every parameter used, including the outline points.

## Regenerate

```
python3 ../../scripts/make_tool.py <photo> hsc8-6-4a --length 171 --width 81 \
    --symmetric --offset 2.0 --outdir .
python3 ../../scripts/make_bin.py --meta meta.json --out . --stem bin
```
