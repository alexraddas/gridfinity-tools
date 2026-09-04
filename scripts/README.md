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

## Requirements

- `numpy`, `opencv-python`
- Autodesk Fusion running, with its MCP server on `127.0.0.1:27182`
  (`fmcp.py` speaks to it; note the session id must be sent with every request
  *and* the `initialized` notification must follow `initialize`, or `tools/list`
  returns empty)

## Photographing a tool

- Shoot straight down, tool flat, whole tool in frame.
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
