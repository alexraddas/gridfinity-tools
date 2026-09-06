"""Write a tool's README.md from its meta.json.

Hand-written READMEs carry the interesting part -- why a tool needed a lower
threshold, why a bin was packed tight. A generated one covers the numbers, and
says plainly that it was generated so nobody mistakes the absence of notes for
the absence of caveats.

    python3 tool_readme.py <tool-dir> --title "Klein Tools D228-8" [--issue 42]
"""
import argparse
import json
import os

import numpy as np

TEMPLATE = """\
# {title}

{intro}

| | |
|---|---|
| Measured length | {length:.0f} mm |
| Measured width | {width:.0f} mm |
| Traced (raw) | {traced_l:.2f} x {traced_w:.2f} mm |
| Pocket | {pocket_l:.2f} x {pocket_w:.2f} mm |
| Cutout depth | {depth:.0f} mm |
| Bin size | {uw}x{ul} units ({fw:.2f} x {fl:.2f} mm) |
| Clearance | {offset:.1f} mm radial |
| Lip margin | {margin:.2f} mm per end |
{notes}
## Files

- `bin.stl` — finished gridfinity container, pocket already subtracted.
- `cutout.stl` — tool-shaped cutting body, to subtract from your own bin.
- `cutout.dxf` — 2D outline in millimetres, for CAD.
- `outline_sheet.pdf` / `.jpg` — dimensioned 1:1 drawing. Print at 100%.
- `meta.json` — every parameter used, including the outline points.

## Accuracy

The outline is traced from a photograph and scaled to the measured length, so
the whole model rests on that one number. Print `outline_sheet.pdf` at 100% and
lay the tool on it before printing a bin: a bin that grips or rattles
*uniformly* is a mis-measured length, not a bad trace.

## Regenerate

```
python3 ../../scripts/make_tool.py <photo> {name} --length {length:.0f} --width {width:.0f}{flags} --outdir .
python3 ../../scripts/make_bin.py --meta meta.json --out . --stem bin
python3 ../../scripts/make_sheet.py meta.json
```
"""


def build(tool_dir: str, title: str, issue=None, aspect_note=True) -> str:
    m = json.load(open(os.path.join(tool_dir, "meta.json")))
    raw = np.array(m["outline_raw"])
    traced_l, traced_w = float(np.ptp(raw[:, 1])), float(np.ptp(raw[:, 0]))
    uw, ul = m["grid_units"]
    lip = ul * 42.0 - 6.52

    intro = ("Generated automatically from a submitted photograph"
             + (" ([#%s](../../issues/%s))" % (issue, issue) if issue else "")
             + ". Nobody has written notes on this tool yet, so treat anything "
               "unusual about it as undocumented rather than absent.")

    notes = []
    if m.get("width_mm"):
        err = 100 * ((traced_l / traced_w) / (m["length_mm"] / m["width_mm"]) - 1)
        if aspect_note and abs(err) > 4:
            notes.append(
                "\n**Traced aspect is %+.1f%% off the measurement.** Outlines are "
                "scaled by length alone, so the disagreement lands in the width. "
                "On a tool with sprung handles this usually means the handles sat "
                "differently when measured than when photographed, rather than a "
                "bad trace — the paper sheet settles it.\n" % err)
    flags = ""
    if m.get("symmetric"):
        flags += " --symmetric"
        notes.append(
            "\n**The pocket takes the tool either face up.** Crossed jaws are "
            "180-degree rotationally symmetric rather than mirror symmetric, so "
            "a pocket cut from one photographed face otherwise rejects the "
            "other. Built with `--symmetric`.\n")
    if m.get("fill_notches"):
        flags += " --fill-notches %g" % m["fill_notches"]

    return TEMPLATE.format(
        title=title, intro=intro, name=m["name"],
        length=m["length_mm"], width=m["width_mm"] or 0,
        traced_l=traced_l, traced_w=traced_w,
        pocket_l=m["outline_l"], pocket_w=m["outline_w"],
        depth=m["depth_mm"], offset=m["offset_mm"],
        uw=uw, ul=ul, fw=uw * 42.0 - 0.62, fl=ul * 42.0 - 0.62,
        margin=(lip - m["outline_l"]) / 2.0,
        notes="".join(notes), flags=flags)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tool_dir")
    ap.add_argument("--title", required=True)
    ap.add_argument("--issue", default=None)
    a = ap.parse_args()
    text = build(a.tool_dir, a.title, a.issue)
    open(os.path.join(a.tool_dir, "README.md"), "w").write(text)
    print("wrote %s/README.md" % a.tool_dir)


if __name__ == "__main__":
    main()
