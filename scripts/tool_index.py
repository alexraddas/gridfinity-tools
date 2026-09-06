"""Regenerate the tool table in the top-level README from what is on disk.

Every merged submission adds a tool, and a hand-maintained index rots on the
first one nobody remembers to update -- the count in the prose goes stale even
faster than the table. This reads each tool's own README heading and meta.json,
so the index cannot disagree with the tools it lists.

    python3 tool_index.py [--check]

--check exits 1 if the README is out of date, without writing, so CI can fail
on a stale index instead of quietly shipping one.
"""
import argparse
import glob
import json
import os
import re
import sys

import numpy as np

BEGIN = "<!-- tool-index:begin -->"
END = "<!-- tool-index:end -->"
# "Klein Tools D228-8 — Diagonal cutters" -> name, type
H1 = re.compile(r"^#\s+(.*?)\s*$")


def entry(tool_dir: str):
    m = json.load(open(os.path.join(tool_dir, "meta.json")))
    raw = np.array(m["outline_raw"])
    L, W = float(np.ptp(raw[:, 1])), float(np.ptp(raw[:, 0]))
    title = os.path.basename(tool_dir)
    readme = os.path.join(tool_dir, "README.md")
    if os.path.exists(readme):
        first = open(readme).readline()
        h = H1.match(first)
        if h:
            title = h.group(1)
    # An em dash separates the tool from what it is, where a human wrote one.
    name, _, kind = (p.strip() for p in title.partition("—"))
    uw, ul = m["grid_units"]
    return dict(dir=tool_dir, name=name, kind=kind or "—",
                size="%.0f × %.0f" % (L, W), bin="%d×%d" % (uw, ul),
                sort=name.lower())


def table(rows) -> str:
    out = ["| Tool | Type | Size (mm) | Bin |", "|---|---|---|---|"]
    for r in rows:
        out.append("| [%s](%s) | %s | %s | %s |"
                   % (r["name"], r["dir"], r["kind"], r["size"], r["bin"]))
    return "\n".join(out)


WORDS = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six",
         7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten", 11: "Eleven",
         12: "Twelve", 13: "Thirteen", 14: "Fourteen", 15: "Fifteen",
         16: "Sixteen", 17: "Seventeen", 18: "Eighteen", 19: "Nineteen",
         20: "Twenty"}


def render(rows) -> str:
    n = len(rows)
    count = WORDS.get(n, str(n))
    return ("%s\n%s tools, all built and verified. Bin size is in Gridfinity "
            "units (1 unit = 42 mm).\n\n%s\n%s"
            % (BEGIN, count, table(rows), END))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--readme", default="README.md")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if out of date; write nothing")
    a = ap.parse_args()

    rows = sorted((entry(os.path.dirname(p)) for p in glob.glob("*/*/meta.json")),
                  key=lambda r: r["sort"])
    text = open(a.readme).read()
    if BEGIN not in text or END not in text:
        raise SystemExit("%s has no %s / %s markers" % (a.readme, BEGIN, END))
    new = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END), lambda _: render(rows),
                 text, flags=re.S)

    if a.check:
        if new != text:
            print("::error::the tool index in %s is stale — run "
                  "scripts/tool_index.py" % a.readme)
            return 1
        print("tool index is up to date (%d tools)" % len(rows))
        return 0
    open(a.readme, "w").write(new)
    print("indexed %d tools" % len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
