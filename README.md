# Gridfinity Tool Bins — 3D-printable STL organisers for hand tools

Free, printable **Gridfinity** bins with pockets cut to the exact silhouette of
specific pliers, cutters, crimpers and wire strippers. Each tool drops into its
own shadow-board pocket, so a drawer stays sorted and a missing tool is obvious
at a glance.

Every bin here was generated from an overhead photograph of the real tool, then
printed and checked against it. Ready-to-slice `bin.stl` files, `cutout.stl`
bodies for cutting your own pockets, `cutout.dxf` outlines for CAD, and a
printable 1:1 drawing per tool.

**Keywords:** gridfinity, gridfinity bins, STL, 3D printing, tool organiser,
tool organizer, shadow board, foam insert alternative, toolbox drawer
organiser, pliers, crimper, wire stripper, cable cutter, Klein Tools,
Milwaukee, IWISS, Pressmaster, Knipex-style ferrule crimper, 42 mm grid.

---

## Tools in this repository

Thirteen tools, all built and verified. Bin size is in Gridfinity units
(1 unit = 42 mm).

| Tool | Type | Size (mm) | Bin |
|---|---|---|---|
| [Baomain HSC8 6-4A](baomain/hsc8-6-4a-ferrule-crimper) | Self-adjusting ferrule crimper | 174 × 81 | 3×5 |
| [Doyle cable cutters](doyle/cable-cutters) | Cable cutters | 240 × 51 | 2×7 |
| [Heschen HS-07FL](heschen/hs-07fl-crimper) | Crimper | 226 × 71 | 2×6 |
| [HKS ratcheting crimper](hks/ratcheting-crimper-6-35mm2) | Ratcheting crimper, 6–35 mm² | 235 × 79 | 3×7 |
| [IWISS IWD-12](iwiss/iwd-12-deutsch-crimper) | Deutsch connector crimper | 160 × 103 | 3×5 |
| [Klein Tools 1005](klein-tools/1005-crimper) | Crimper / cutter | 246 × 51 | 2×7 |
| [Klein Tools 1019](klein-tools/1019-wire-stripper) | Wire stripper, multi-tool | 196 × 55 | 2×6 |
| [Klein Tools D228-8](klein-tools/d228-8-diagonal-cutters) | Diagonal cutters | 206 × 49 | 2×6 |
| [Klein Tools D275-5](klein-tools/d2755-flush-cutter) | Flush cutter | 131 × 81 | 3×4 |
| [Milwaukee 48-22-3079](milwaukee/48-22-3079-wire-stripper) | 6-in-1 wire stripper | 196 × 54 | 2×5 |
| [Milwaukee 48-22-4047](milwaukee/48-22-4047-scissors) | Offset electrician's scissors | 253 × 96 | 3×7 |
| [Pressmaster KRB 0560](pressmaster/krb-0560-crimper) | Crimper | 253 × 73 | 3×7 |
| [Tool Aid 18880](tool-aid/18880-deutsch-crimper) | Deutsch connector crimper | 155 × 103 | 3×4 |

## What each folder contains

    <manufacturer>/<tool>/
        bin.stl             finished Gridfinity bin, pocket already subtracted
        cutout.stl          tool-shaped solid, 20 mm deep, to subtract yourself
        cutout.dxf          2D outline in millimetres, for CAD
        outline_sheet.pdf   dimensioned 1:1 drawing — print and check the fit
        outline_sheet.jpg   the same drawing at 300 dpi
        meta.json           every parameter used, including the outline points
        README.md           measurements, and anything unusual about this tool

A `trace.png` — the traced outline drawn over the source photograph — is also
written into each folder when you rebuild. It is deliberately not committed;
it is a working check, and thirteen of them is 22 MB of regenerable pixels.

## Printing

`bin.stl` is ready to slice. No supports needed — the pocket has vertical walls
and the bin's own geometry is self-supporting.

Print **`outline_sheet.pdf` at 100% first** and lay the real tool on it. It
takes a minute and a sheet of paper, and it is the only check that catches a
scale error before you commit six hours of filament. The L-shaped ruler in the
corner exists because "Fit to page" is the default in too many print dialogs;
if both legs do not measure 50 mm, nothing else on the sheet is trustworthy.

## Compatibility

These interlock with bins from
[gridfinitygenerator.com](https://gridfinitygenerator.com) — the outer profile
was reverse-engineered from one and matches it at every height. Standard 42 mm
Gridfinity grid, so they sit in any Gridfinity baseplate.

| | |
|---|---|
| Grid | 42 mm |
| Footprint | 42n − 0.62 mm, corner radius 3.75 |
| Height | 25.754 mm (6 units of 4.75 mm base + block) |
| Pocket depth | 20 mm |
| Clearance | 1.5 mm radial around the traced outline |
| Finger slot | 25 mm wide, full depth, across the middle |
| Walls | 1.2 mm, solid base pads, no magnet or screw holes |

## Accuracy

Outlines are traced from photographs and scaled to two hand measurements per
tool — overall length and maximum width. They are **not** derived from
manufacturer drawings. Expect them to be right to about a millimetre: good
enough for a pocket with 1.5 mm of clearance, not good enough for a press fit.
Each tool's README records the measurements used, so anything that looks wrong
can be traced back.

Scale comes entirely from the length measurement, so a bin that grips or
rattles *uniformly* is almost always a mis-measured length rather than a bad
trace. The 1:1 sheet settles it.

## Adding a tool

Open an issue with a photo and two measurements, and a bin is built for you
automatically. You review it against a printed drawing, adjust it by commenting,
and a maintainer merges it. No account setup, no software to install.

### 1. Photograph the tool

This is the part that decides whether any of it works.

- Shoot **straight down**, tool **flat**, whole tool in frame.
- **Diffuse light.** A hard shadow beside a tool can be darker than the tool
  itself, and gets traced as part of it. Overcast daylight or open shade is ideal.
- Leave roughly **a tool-width of plain background** on every side. Wood or
  white paper both work; a cluttered bench does not.
- If the tool has a label face, shoot **that** face — pockets are cut from the
  face you photograph.
- Spring-loaded handles: let them **rest**, don't hold them.

### 2. Measure it

| | |
|---|---|
| **Length** | Overall, along the long axis. **The entire model is scaled from this one number** — get it right and everything else follows; get it wrong and the bin is uniformly tight or loose. |
| **Width** | Widest point, with the tool lying as photographed. A cross-check only; it does not rescale anything, and a few percent of disagreement is normal. |

### 3. Submit

**[Open the form →](../../issues/new?template=new-tool.yml)** Fill in the
manufacturer, part number, both measurements, whether the jaws cross, and drag
the photo in. Submit.

```mermaid
sequenceDiagram
    actor You
    participant Issue
    participant CI as GitHub Actions
    participant PR as Draft PR
    actor Maintainer

    You->>Issue: photo + length + width
    Issue->>CI: new-tool label fires the build
    CI->>CI: trace outline, build STL/DXF/sheet
    CI->>PR: open draft (geometry only, no photo)
    CI-->>You: link to outline_sheet.pdf

    loop until it fits
        You->>You: print sheet at 100%, lay tool on it
        You->>PR: /length 240
        PR->>CI: rebuild
        CI-->>You: new sheet
    end

    You->>PR: /approve
    PR->>Maintainer: marked ready, review requested
    Maintainer->>PR: merge
```

### 4. Check it before it merges

Within a few minutes you get a **draft pull request** with a comment linking to
`outline_sheet.pdf`. Print that at 100% — *not* "fit to page" — and lay the real
tool on it.

**Check both ruler legs measure 50 mm first.** If they don't, your printer
scaled the page and nothing else on the sheet means anything.

Then look at the outline: the tool should sit on the solid line with an even gap
out to the dashed one. A bin that would grip or rattle *uniformly* is a
mis-measured length, not a bad trace.

### 5. Adjust it by commenting

Comment on the pull request. Only you — the person who opened the issue — can
run these, and each one rebuilds and posts a fresh sheet:

| Command | Effect |
|---|---|
| `/length 240` | Rebuild at a corrected overall length |
| `/width 51` | Update the width cross-check |
| `/symmetric on` | Make the pocket accept the tool either face up |
| `/notches 2.0` | Bridge shallow dips, to flatten an edge that should be straight |
| `/bin 2x7` | Force a bin size in grid units |
| `/approve` | You're happy — hand it to a maintainer to merge |
| `/close` | Abandon the submission |

Go round as many times as you need. Nothing is merged until you say `/approve`
**and** a maintainer reviews it.

### What happens to your photo

It is used to trace the outline and is **never committed to this repository** —
only the resulting geometry is. The drawing posted to the pull request is drawn
from the outline and contains no pixels from your photo.

A submission with no activity for 30 days is closed automatically and its branch
deleted, so unconfirmed bins don't sit around looking ready to merge.

## Making a bin for your own tool

See [`scripts/README.md`](scripts/README.md). You will need a photograph, two
measurements, Python with numpy and OpenCV, and Autodesk Fusion running with
its MCP server enabled.

    python3 scripts/make_tool.py <photo> <name> --length <mm> --width <mm> --outdir <dir>
    python3 scripts/make_bin.py --meta <dir>/meta.json --out <dir> --stem bin
    python3 scripts/make_sheet.py <dir>/meta.json

## Licence

[MIT](LICENSE). Print them, sell them, remix them.
