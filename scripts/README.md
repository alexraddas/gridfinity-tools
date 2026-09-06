# Pipeline

How the photo-to-STL pipeline works, and why it is built this way. The
operating rules -- how to verify a bin, how to diagnose a bad fit, which face
to photograph -- are in [`../CLAUDE.md`](../CLAUDE.md).

Turns an overhead photo of a tool into a gridfinity cutting body.

    python3 make_tool.py <photo> <name> --length <mm> --width <mm> [--mirror] --outdir <dir>

Emits `cutout.stl` and `cutout.dxf`, and writes `chk_<name>_trace.png` — the traced
outline drawn over the source photo. **Always look at that overlay.** It is the only
check that catches a segmentation error; the numbers alone will not.

## How segmentation works

Wood is warm, tools are not. Three signals, each measured against a *locally*
estimated background so a lighting gradient across the bench does not bias them:

| signal | catches | wood reads |
|---|---|---|
| `dB` b\* below local background | bare/polished steel (cool) | +9..+14 |
| `dL` luminance below local background | black-oxide heads | — |
| `dA` a\* above local background | coloured grips | ~0 |

A strict threshold seeds confident tool pixels; GrabCut then models the full colour
distributions and settles the boundary. Brightness alone does **not** work — polished
steel is as bright as the tabletop, which is why b\* carries the load.

The b\* background field is estimated with a max filter, which assumes the tool is
*cooler* than the wood. A grip that is **warmer** than wood breaks that assumption:
orange grips sit at b\* ≈ +38 against wood's ≈ +10, inflating the background estimate
until ordinary wood reads as metal — which bridged the gap between the handles on
IWISS IWD-12. Saturated pixels (chroma > 20) are therefore neutralised before the
field is estimated, since the background being modelled is bare, near-neutral wood.
Red grips (b\* ≈ +11) sit close enough to wood that they never triggered this.

## Edge bias

`segment()` used to end with `shrink=5`, an erosion by an ellipse of radius
2 px, and that erosion was a systematic inward bias on every side. Measured
against the photograph rather than by eye — b\* profiles sampled along the
outward normal at 600 contour points, at full sensor resolution, locating the
50% transition — the eroded contour sat a median **0.5 to 2.2 px inside the
true edge** depending on the photo (2.2 px, 0.38 mm, on `IMG_1812.jpeg`), and
`shrink=0` sits within ±1.1 px of it and errs *outside* rather than inside.
Inward bias is the one that costs a fit, so the default is now 0.

Because outlines are scaled by length alone, the erosion was largely
self-cancelling along the tool's axis — the rescale inflates everything by the
same amount it lost — and landed almost entirely in the width. Removing it
grows the offset outline by **+0.02 to +0.85 mm in width and less than
±0.1 mm in length**, and does not change the bin size of any tool in the repo.

Do not read this off the trace overlay. The overlay cannot resolve two pixels;
the only way to see it is to sample the image across the boundary.

## Requirements

`pip install -r ../requirements.txt` — numpy, OpenCV, and CadQuery.

Solids are built by `geom.py` on CadQuery/OCCT: rounded-rect wires, 45-degree
tapered extrudes for the base pads, a ruled loft for the lip, and boolean cuts
for the pocket. It replaced a dependency on Autodesk Fusion, which meant a
licensed GUI application had to be running and made CI impossible. Validated
against the Fusion output on all 13 tools: worst disagreement 0.25% by volume.

One deliberate difference: the tool outline is a polyline here where Fusion
fitted a spline through the same points. The spline bowed outward by up to
0.07 mm, so pockets came out fractionally larger than the computed outline.

`--engine fusion` still exists on `make_tool.py` and `make_bin.py` and needs
Fusion on `127.0.0.1:27182` (`fmcp.py` speaks to it; the session id must be sent
with every request *and* the `initialized` notification must follow
`initialize`, or `tools/list` returns empty).

## Backdrops

Backdrop polarity is detected per image: tools are normally darker than the
backdrop, but a bright tool on a dark one (polished blades on a grey desk)
flips the sign of the luminance test. Taking the max of both directions is
*not* safe -- it over-triggers badly on light backdrops -- so the direction is
chosen once per image from the backdrop's own brightness.

Wood and white paper both work. On wood the b\* channel does the heavy lifting
(wood is warm, metal is cool); on white paper b\* is near-neutral and darkness
carries it instead.

**The backdrop must be uncluttered, and the tool must sit well inside it.** A
sheet that does not fill the frame leaves carpet, bags and boxes around it,
which the darkness channel calls "tool" -- one photo traced the entire image
border. `backdrop_roi()` finds the sheet and confines the search to it, but it
cannot help when the tool runs to the very edge of the sheet.

## Photographing a tool

- Shoot straight down, tool flat, whole tool in frame.
- **Open a spring-loaded tool to its rest position and hold it there.** A
  squeezed handle is not just a narrow silhouette: it swings the handle tip
  away from the head, so the photographed pose is *longer* than the tool at
  rest, and scaling that pose to the measured length shrinks the entire model.
  On the Baomain HSC8 the handles sat 12.3 mm short of their 81 mm spread,
  which made the photo 172.4-173.6 mm long against a 171 mm tool and shrank
  the pocket by 0.8-1.5% all over — a median 0.36 mm per side, up to 1.21 mm
  at the head. It reads as a pocket that grips everywhere at once, and no
  amount of staring at the trace overlay will show it.
- **Avoid hard directional light.** A sharp cast shadow beside a tool can be
  darker than the tool itself (measured L=11 against a black body's L=28) and
  neutral in hue where the body is cool, so neither the darkness nor the
  warm/cool channel can reject it. Diffuse light, or none.
- Leave a wide margin of bare wood on all sides. Too tight and the background
  estimate starves — this mangles jaws and dark heads. Too wide and a differently-lit
  plank can bridge into the tool. Roughly a tool-width of wood each side works.
- Include a ruler if you can; otherwise measure length and max width by hand.

## Low-contrast tools

The default luminance thresholds (85/80) suit dark tools on wood. **Bare or
polished steel on a pale backdrop is much lower contrast** and needs them
lowered — `--dl-strict 50 --dl-mid 35` for the Milwaukee scissors. Symptom: the
contour runs *inside* the tool, following an internal dark line and shaving off
a bright edge, rather than failing outright. Check the trace overlay against
the real outline; the aspect ratio can look fine while a third of a blade is
missing.

## Tools with crossed jaws

Pliers, cutters and crimpers are 180-degree rotationally symmetric, not mirror
symmetric: the heel of the upper jaw stands proud on one side of the head and
the lower jaw's on the other. A pocket cut from the photographed face therefore
**rejects the tool laid in the other way up** -- on the Doyle cutters the
flipped silhouette fouled the pocket at 38 of 134 vertices, worst case 2.73 mm.
It reads as a jammed head at one corner and an unexplained empty crescent at
the opposite one, and it is easy to misdiagnose as a bad trace: the trace is
fine, it just only describes one face.

Pass `--symmetric` on any such tool. It unions the outline with its mirror
before the offset, so either face drops in. It cannot change the bin size --
the outline is centred on its bounding box, so mirroring leaves the width
alone -- and costs only the slop where the two silhouettes disagree (640 mm2
on the Doyle). Not needed for a tool that really is mirror symmetric about its
long axis, such as a straight screwdriver or a wire stripper whose jaws close
in plane.

It is worth checking rather than assuming. The Baomain HSC8 has no crossed
jaws at all — its die closes concentrically — but its moving handle is a lever
riveted to one face of the frame, and that was enough to foul the flipped tool
at 50 of 106 vertices, worst case 4.98 mm. Measured on that tool, `--symmetric`
also cost nothing in location: free play stayed at ±1.9 mm in both axes,
because the union adds material only where the pocket was already slack.

## Flat edges and the notch that isn't there

`--symmetric` has a side effect worth knowing about. Wherever the original
outline has an off-centre extremum, the union with its mirror leaves a horn at
that point *and* at its reflection, with the original profile sagging between
them. On the Doyle cutters the head's peak sits 7 mm off centre, so the union
produced peaks at +-7 mm with a 1.30 mm dip between -- on a tool whose top is
flat. The segmentation was innocent: sampled against the photograph it tracked
the true edge to within 0.5 mm across the whole top.

`--fill-notches MM` bridges any concavity shallower than MM with its
convex-hull chord. Depth is the right discriminator, not width: on the Doyle
the convexity defects run 0.03 and 0.04 mm (raster noise), 1.25 mm (the dip),
3.34 and 4.71 mm twice over (real steps at the jaw and shoulder), then
146.69 mm (the gap between the handles), so a 2 mm threshold is unambiguous.
The outline can only grow, so it cannot stop a tool fitting.

This is the kind of defect only the paper sheet catches. It is invisible in the
trace overlay, because the trace is correct -- the error is introduced after
segmentation.

## Measuring length

By default `length` is the tool's bounding extent along its long axis. On a
bent tool -- offset scissors -- the blade-tip-to-handle-tip distance is longer
than that, by 4.2% on the Milwaukee 48-22-4047. Pass `--length-mode tip` when
the figure was taken tip-to-tip. For straight tools the two agree to within
half a percent and the flag makes no difference.

## Spring-loaded tools

On a tool with sprung handles the traced width is set by how far the handles
sat apart in the photograph. Three photographs of the HSC8 6-4A traced 73.9,
74.8 and 74.8 mm at the same length against a hand-measured 81 mm -- consistent
between photographs, so the disagreement is with the measurement rather than
the segmentation. `CLAUDE.md` covers what to do about it.

## Validation sheets

`make_sheet.py <meta.json>` writes `outline_sheet.pdf` and `outline_sheet.jpg`
next to it: a dimensioned 1:1 drawing of the tool, with the traced silhouette
solid, the pocket dashed, overall length and width dimensioned, and a panel
carrying the tool, pocket and bin numbers.

**Print it and lay the tool on the solid line before you print a bin.** The
trace overlay only proves the contour matches the *photograph*. It cannot prove
the photograph was scaled correctly -- a wrong scale looks perfect at any size,
because the overlay scales with it. The paper sheet is the only check that
catches a scale error, and it costs a sheet of paper instead of a six-hour
print. The L-shaped ruler in the corner is there because "Fit to page" is the
default in too many print dialogs; if both legs do not measure 50 mm, nothing
else on the sheet means anything.

The PDF is authoritative -- it carries real physical units. The JPG is written
at 300 dpi with a correct JFIF density, which most viewers honour, but a PDF
cannot be silently resampled the way an image can. Both render from one display
list, so they cannot drift apart.

Every outline in the repo fits A4 portrait; `--page letter` is available and
warns on the sheet itself if the outline does not fit.

## Rebuilding

`build-all.sh` rebuilds every tool from its photo, then writes its sheet.
`NO_BUILD=1 bash scripts/build-all.sh` refreshes `meta.json` and the sheets
from the photos without touching Fusion -- worth running after a segmentation
change to see what moved before spending 26 Fusion round-trips on STLs.

## Conventions

| | |
|---|---|
| Depth | 20 mm |
| Clearance | 1.5 mm radial offset (`--offset`; 2.0 on the Baomain HSC8) |
| Finger slot | 25 mm wide, stadium in plan, vertical walls, full depth |
| Slot length | `min(outline + 48, bin_width - 8)` |
| Slot position | widest point of the outline |
| Grid | 42 mm; bin = smallest multiple that fits the offset outline |

## Fusion documents

Both scripts create a scratch Fusion document, export, then close it. Pass
`--keep-open` to leave it open for inspection. Without that they would pile up
one document per run.

## Fusion MCP gotchas

- **No line in the generated script may exceed ~4 KB.** The server accepts an
  oversized line, returns success, and silently never runs the script. Outline
  data is therefore emitted as adjacent string literals across many lines.
- **Paths must be absolute.** The script executes inside Fusion, whose working
  directory is elsewhere and read-only.
- **The session id must be sent on every request**, and the `initialized`
  notification must follow `initialize`, or `tools/list` returns empty.
