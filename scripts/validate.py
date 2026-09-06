"""Ask Claude to look at a trace overlay and say whether it is any good.

The overlay is the one artefact that catches a segmentation error, and reading
it is a visual judgement no assertion in this repo can make. Every defect this
project has shipped was obvious in the overlay to anyone who looked -- a
contour running inside a bright blade, a gap bridged between two handles, a
clipped tip. So the check is: hand Claude the overlay and the numbers, and ask
the questions a person would ask.

    export ANTHROPIC_API_KEY=...
    python3 validate.py <tool-dir>            # trace.png + meta.json
    python3 validate.py <tool-dir> --markdown # report for a PR/issue comment

Exit status is 0 when Claude finds no blocking issue, 1 when it does, and 2 if
the check could not run -- so CI can tell "the tool is wrong" apart from "the
validator broke", which are different problems.
"""
import argparse
import base64
import json
import os
import sys
from typing import List, Literal

import anthropic
import cv2
import numpy as np
from pydantic import BaseModel, Field

MODEL = "claude-opus-5"
MAX_EDGE = 2000          # px; Opus 5 accepts 2576 on the long edge


class Issue(BaseModel):
    region: str = Field(description="Where on the tool, in plain words: "
                                    "'top of the head', 'left handle tip'.")
    observation: str = Field(description="What is visibly wrong in the image.")
    severity: Literal["blocking", "worth_checking", "cosmetic"] = Field(
        description="blocking = the pocket would be wrong and the bin should "
                    "not be printed. worth_checking = suspicious but might be "
                    "real geometry. cosmetic = does not affect fit.")


class Verdict(BaseModel):
    outline_follows_tool: bool = Field(
        description="True if the green contour follows the real edge of the "
                    "tool all the way round.")
    issues: List[Issue] = Field(description="Empty if nothing is wrong.")
    summary: str = Field(description="Two sentences at most, for a human "
                                     "deciding whether to print.")


PROMPT = """\
This is a traced outline (green) drawn over an overhead photograph of a hand \
tool. The outline becomes a pocket milled into a 3D-printed tray, with {offset} \
mm of clearance added around it, so it has to follow the real silhouette of \
the tool.

Judge only what you can see. These are the failure modes this pipeline actually \
produces, in rough order of how often they bite:

1. The contour runs INSIDE the tool, following an internal dark line or a shadow \
   and shaving off a bright edge. Polished steel against a pale background is \
   where this happens -- the aspect ratio still looks fine while a third of a \
   blade is missing.
2. A gap that should be open is bridged -- most often between two handles, where \
   the background between them got included in the tool.
3. A tip, jaw, or handle end is cut short.
4. Background included as tool: a cast shadow, a wood-grain line, or the edge of \
   the sheet the tool sits on.

Two things that are NOT faults, and that you should not report:

- Asymmetry. Pliers and cutters are 180-degree rotationally symmetric, not \
  mirror symmetric, so one side genuinely sticks out further than the other. \
  Only flag a difference between the two sides if you can see the outline \
  departing from the metal.
- The contour sitting a hair inside a bright specular rim. Under a millimetre \
  is expected and is absorbed by the clearance.

Reference numbers for this trace, which may help you spot a scale problem but \
are not themselves what you are judging:

  measured by hand   {length} mm long
  traced             {traced_l:.2f} x {traced_w:.2f} mm
{aspect}

An aspect disagreement of a few percent is normal here and is usually the hand \
measurement, not the trace. Do not report it as an issue unless the image \
shows the outline actually missing part of the tool.
"""


def load_image(path: str) -> tuple:
    """Return (base64 png, media type). Downscaled if oversized -- a 4000 px
    overlay costs three times the tokens and shows nothing more."""
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        raise SystemExit("cannot read image: %s" % path)
    h, w = img.shape[:2]
    if max(h, w) > MAX_EDGE:
        s = MAX_EDGE / float(max(h, w))
        img = cv2.resize(img, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)
    # JPEG, not PNG: the overlay is a photograph with a line on it, and PNG
    # makes it ten times the bytes for no visible gain. Token cost is set by
    # dimensions, not file size, so this only buys upload time -- but on a
    # 20 MB photo that is the difference between a fast check and a timeout.
    ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 92])
    if not ok:
        raise SystemExit("failed to encode %s" % path)
    return base64.standard_b64encode(buf.tobytes()).decode("ascii"), "image/jpeg"


def validate(tool_dir: str) -> Verdict:
    meta = json.load(open(os.path.join(tool_dir, "meta.json")))
    raw = np.array(meta["outline_raw"]) if "outline_raw" in meta else None
    traced_l = float(np.ptp(raw[:, 1])) if raw is not None else meta["outline_l"]
    traced_w = float(np.ptp(raw[:, 0])) if raw is not None else meta["outline_w"]
    aspect = (100 * ((traced_l / traced_w) / (meta["length_mm"] / meta["width_mm"]) - 1)
              if meta.get("width_mm") else None)

    data, media_type = load_image(os.path.join(tool_dir, "trace.png"))
    client = anthropic.Anthropic()
    response = client.messages.parse(
        model=MODEL,
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image",
                 "source": {"type": "base64", "media_type": media_type, "data": data}},
                {"type": "text", "text": PROMPT.format(
                    offset=meta["offset_mm"], length=meta["length_mm"],
                    traced_l=traced_l, traced_w=traced_w,
                    aspect=("  aspect disagreement %+.1f%%" % aspect) if aspect
                            is not None else "  (no width was given to compare against)")},
            ],
        }],
        output_format=Verdict,
    )
    if response.stop_reason == "refusal":
        raise SystemExit("the model declined to answer (%s)" %
                         getattr(response.stop_details, "category", "no category"))
    if response.parsed_output is None:
        raise SystemExit("no structured output returned")
    return response.parsed_output


BADGE = {"blocking": "**BLOCKING**", "worth_checking": "worth checking",
         "cosmetic": "cosmetic"}


def render(v: Verdict, tool_dir: str, markdown: bool) -> str:
    blocking = [i for i in v.issues if i.severity == "blocking"]
    if markdown:
        out = ["### Trace check — `%s`" % tool_dir, "", v.summary, ""]
        if not v.issues:
            out.append("No issues found. The outline follows the tool.")
        else:
            out.append("| Severity | Region | Observation |")
            out.append("|---|---|---|")
            for i in v.issues:
                out.append("| %s | %s | %s |" % (BADGE[i.severity], i.region,
                                                 i.observation.replace("|", "\\|")))
        out += ["", "_Reviewed by %s from the trace overlay. It reads the "
                    "overlay, not the tool — print `outline_sheet.pdf` and lay "
                    "the real tool on it before printing a bin._" % MODEL]
        return "\n".join(out)
    lines = ["%s: %s" % (tool_dir, v.summary)]
    for i in v.issues:
        lines.append("  [%s] %s: %s" % (i.severity, i.region, i.observation))
    lines.append("  -> %s" % ("BLOCKED, %d issue(s)" % len(blocking) if blocking
                              else "no blocking issues"))
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tool_dir", help="directory holding trace.png and meta.json")
    ap.add_argument("--markdown", action="store_true",
                    help="emit a comment body instead of terminal text")
    ap.add_argument("--out", default=None, help="write the report here as well")
    a = ap.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY is not set; skipping the trace check.",
              file=sys.stderr)
        return 2
    try:
        verdict = validate(a.tool_dir)
    except anthropic.APIStatusError as e:
        print("Claude API error %s: %s" % (e.status_code, e.message), file=sys.stderr)
        return 2
    except anthropic.APIConnectionError:
        print("could not reach the Claude API", file=sys.stderr)
        return 2

    report = render(verdict, a.tool_dir, a.markdown)
    print(report)
    if a.out:
        open(a.out, "w").write(report + "\n")
    return 1 if any(i.severity == "blocking" for i in verdict.issues) else 0


if __name__ == "__main__":
    sys.exit(main())
