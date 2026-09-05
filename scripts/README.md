# Pipeline

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

## Requirements

- `numpy`, `opencv-python`
- Autodesk Fusion running, with its MCP server on `127.0.0.1:27182`
  (`fmcp.py` speaks to it; note the session id must be sent with every request
  *and* the `initialized` notification must follow `initialize`, or `tools/list`
  returns empty)

## Backdrops

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
- **Avoid hard directional light.** A sharp cast shadow beside a tool can be
  darker than the tool itself (measured L=11 against a black body's L=28) and
  neutral in hue where the body is cool, so neither the darkness nor the
  warm/cool channel can reject it. Diffuse light, or none.
- Leave a wide margin of bare wood on all sides. Too tight and the background
  estimate starves — this mangles jaws and dark heads. Too wide and a differently-lit
  plank can bridge into the tool. Roughly a tool-width of wood each side works.
- Include a ruler if you can; otherwise measure length and max width by hand.

## Conventions

| | |
|---|---|
| Depth | 20 mm |
| Clearance | 1.5 mm radial offset |
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
