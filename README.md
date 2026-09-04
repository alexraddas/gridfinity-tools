# gridfinity-tools

Gridfinity containers shaped to specific hand tools, generated from overhead photos.

Each tool ships three things: a **cutout** (a tool-shaped solid you subtract from a bin),
a **DXF** of its outline, and the finished **bin**. Organised by manufacturer.

## Layout

    <manufacturer>/<tool>/
        cutout.stl    tool-shaped cutting body, 20 mm deep
        cutout.dxf    2D outline, millimetres
        bin.stl       finished gridfinity container
        README.md     measurements and how to regenerate

## Conventions

| | |
|---|---|
| Pocket depth | 20 mm |
| Clearance | 1.5 mm radial offset around the traced outline |
| Finger slot | 25 mm wide, full depth, across the widest point of the tool |
| Slot length | `min(outline + 48 mm, bin width − 8 mm)` |
| Grid | 42 mm; bin is the smallest multiple that fits |

Bins follow the standard gridfinity profile: 4.75 mm base (0.8 chamfer / 1.8 vertical /
2.15 chamfer), solid pads with no magnet or screw holes, and a stacking lip.

## Accuracy

Outlines are traced from photographs and scaled to two hand measurements per tool
(overall length and maximum width). They are **not** derived from manufacturer drawings.
Expect them to be right to about a millimetre — good enough for a pocket with 1.5 mm of
clearance, not good enough for a press fit. Each tool's README records the measurements
used, so anything that looks wrong can be traced back.

The generator cross-checks the traced aspect ratio against the two measurements and
refuses to pass silently when they disagree by more than 4%.

## Regenerating

See [`scripts/README.md`](scripts/README.md). You need Autodesk Fusion running with its
MCP server enabled, plus numpy and OpenCV.

## Credits

Gridfinity is by [Zack Freedman](https://www.youtube.com/@ZackFreedman).
