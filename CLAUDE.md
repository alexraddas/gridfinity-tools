# CLAUDE.md

Working rules for this repository. `README.md` describes the project for
people who want to print the bins; `scripts/README.md` explains how the
pipeline works and why. This file is the operating procedure — the things that
have gone wrong before and how to not repeat them.

## The pipeline

    python3 scripts/make_tool.py <photo> <name> --length <mm> --width <mm> --outdir <dir>
    python3 scripts/make_bin.py --meta <dir>/meta.json --out <dir> --stem bin
    python3 scripts/make_sheet.py <dir>/meta.json

`bash scripts/build-all.sh` rebuilds every tool and writes its sheet.
`NO_BUILD=1 bash scripts/build-all.sh` refreshes `meta.json` and the sheets
without building solids — use it after a segmentation change to see what moved
before spending the geometry time.

Solids are built headlessly by `scripts/geom.py` on CadQuery/OCCT, so the whole
pipeline runs anywhere Python does. `--engine fusion` still drives Autodesk
Fusion over its MCP server on `127.0.0.1:27182`; the two agree to within 0.25%
by volume across all 13 tools, and CadQuery is the default because CI cannot run
a licensed GUI application. Artefacts land in the tool's own folder;
**nothing should ever be written to the repository root.**

## Verifying a bin

**A trace that matches the photograph is not a working pocket.** The overlay
only proves the contour follows the image. It cannot catch a wrong scale (a
mis-scaled outline looks perfect at any size), a mirrored pocket, or a defect
introduced after segmentation. Three separate faults have shipped past a
correct-looking overlay.

So: after any rebuild, **print `outline_sheet.pdf` at 100% and lay the tool on
it.** The L-shaped ruler must read 50 mm on both legs or the print was scaled.

The sheet is also a measuring instrument. The PDF dash array is 3-on 2-off *in
points*, a **1.764 mm period**, so photographing a tool lying on the sheet
calibrates the photograph with no ruler in frame — count dashes to get mm/px,
then measure the gap between the tool's edge and the printed line.

## Diagnosing a bad fit

| Symptom | Cause to check first |
|---|---|
| Tight or loose **uniformly**, all the way round | The length measurement. Scale comes from that one number. |
| Tight at a few **specific** places, gap at others | The tool is going in the other face up. |
| A **flat edge** that sags in the middle | `--symmetric` horns; use `--fill-notches`. |
| Contour runs **inside** a bright tool | Lower `--dl-strict` / `--dl-mid`. |

**Never absorb a scale error into the clearance.** The HSC8 6-4A cost three
rebuilds proving this: built at an assumed 171 mm it printed tight everywhere,
which was nearly "fixed" by raising the clearance to 2.0 mm. The real length is
174 mm; once corrected, the 2.0 mm printed loose and the 1.5 mm default was
right all along. Using the clearance as a fudge hides the error and then gets
the value wrong in *both* directions once the scale is fixed. Every tool in the
repo is on 1.5 mm and there should be no exceptions.

**Do not chase a 2–3% aspect warning as a segmentation fault.** On
spring-loaded tools the traced width is set by how far the handles sat apart in
the photograph, not by the segmentation. Three photographs of the HSC8 traced
73.9, 74.8 and 74.8 mm against a hand-measured 81 — consistent between photos,
so the disagreement is with the measurement.

## Which face is up

Pliers, cutters and crimpers are 180-degree rotationally symmetric, not mirror
symmetric, so the two faces present different silhouettes. A pocket cut from
one photographed face can reject the tool laid the other way up — measured at
2.73 mm of interference on the Doyle, 4.70 mm on the Milwaukee 48-22-3079,
4.98 mm on the HSC8.

Two valid answers, and it is the owner's call, not a default:

- `--symmetric` unions the outline with its mirror, so either face drops in. It
  cannot change bin size. It costs slop wherever the two silhouettes disagree —
  about 6 mm locally on the tools measured here — so it is only worth it when
  the tool genuinely has no obvious right way up.
- Otherwise photograph the face that will be uppermost in the drawer (the one
  with the label) and record the right way up in that tool's README.

`--symmetric` has a side effect: wherever the outline has an off-centre
extremum, the union leaves a horn there *and* at its reflection, with the
profile sagging between them. On the Doyle that put a 1.30 mm dip in a top edge
that is dead flat. `--fill-notches MM` bridges concavities shallower than MM
with their hull chord; depth discriminates cleanly where width would not.

## Bin sizing

The rule in `make_tool.py` wants 5 mm of lip clearance per end. Override it
with `--units-l` when a tool only just crosses a boundary and would otherwise
waste a whole 42 mm row — but **not below about 2 mm per end.** A 2x6 Doyle at
1.37 mm per end was printed and rejected; the lip shelf was too thin to grip.
2.29 mm was accepted. Always state the per-end margin out loud so it can be
judged rather than discovered after a print.

## Photographing a tool

- Straight down, tool flat, whole tool in frame, on an uncluttered backdrop.
- **Diffuse light.** A hard cast shadow beside a tool can be darker than the
  tool itself and neutral in hue, which defeats both discriminating channels.
- Leave roughly a tool-width of clear backdrop on every side.
- Spring-loaded handles: let them rest, and note where they sat.
- Shoot the face that should be uppermost in the drawer.

## Automated intake from issues

`.github/` accepts tool submissions from strangers. The whole design turns on
one decision: **a submitted photograph is never committed.** Only traced
geometry reaches a branch, so no image a stranger uploads can enter this
repository's history — where it would be effectively permanent. `trace.png` is
gitignored for the same reason, and the sheet rendered into the PR is vector
output from the outline, carrying no pixels from the photo.

The rest of the trust boundary:

- **A maintainer is the content gate.** Every submission opens as a *draft*
  PR and only a maintainer can merge it. `/approve` from the submitter means
  "it fits the sheet" — it marks the PR ready and requests review, nothing
  more. This is the one check that cannot be prompt-injected or fooled by a
  classifier-evading image.
- **`scripts/gate.py` is an optional pre-filter**, enabled by setting
  `ANTHROPIC_API_KEY`. With no key the step is skipped. With a key it fails
  closed — exit 2 (API unreachable) counts as rejection, never as permission —
  and re-runs on every rebuild, because issues are editable and the image
  behind a URL can change after it passed. It only ever *adds* a rejection
  path; it never grants approval.
- **Model output is never trusted with authority.** `gate.py` and
  `validate.py` return structured verdicts that the workflow branches on; no
  model output is executed, interpolated into a shell, or committed.
- **Untrusted text never reaches a model.** The issue's free-text notes are
  parsed and stored but never sent to Claude, so there is nothing for a prompt
  injection to ride in on. Only images and derived numbers go into a request.
- **Issue and comment bodies are regex-matched, never evaluated**, and passed
  through the environment rather than interpolated into shell commands.
- **Photos may only come from GitHub's own upload hosts**, so an issue cannot
  point the runner at an arbitrary URL.
- **Commands are gated to the submitter**, resolved from the PR body that only
  this pipeline writes — not from the comment.

**Nothing merges without a human.** That is deliberate and is the property to
preserve if this is ever changed: an automated approval path would put the
whole design at the mercy of a classifier, and classifiers can be evaded.
Belt and braces, add a branch-protection rule on `main` requiring one approving
review — then even a workflow bug cannot merge on its own.

## Housekeeping

- Stage by naming paths. `git add -A` has twice swept scratch files into
  commits.
- `meta.json` is the single source of truth for an outline — it carries both
  `outline` (the pocket) and `outline_raw` (the traced silhouette). Do not
  write parallel `.npy` dumps.
- Regenerated artefacts are committed deliberately; `.git` is already large, so
  avoid gratuitous full rebuilds.
