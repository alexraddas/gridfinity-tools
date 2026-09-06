"""Parse one slash command out of a pull-request comment.

Comments on these PRs come from the person who submitted the tool, and they are
untrusted text. Nothing here is evaluated: a comment either matches one of the
patterns below exactly, with an in-range value, or it is ignored. Free text --
including anything shaped like an instruction to a model -- is never acted on
and never forwarded anywhere.

    python3 pr_command.py --body-file comment.md \\
        --author octocat --allow octocat --out cmd.json
"""
import argparse
import json
import re
import sys

# Anchored to the start of a line so a command quoted inside a reply does not
# fire. One command per comment; the first match wins.
PATTERNS = [
    ("length",    re.compile(r"^/length\s+([0-9]*\.?[0-9]+)\s*(?:mm)?\s*$",  re.I | re.M)),
    ("width",     re.compile(r"^/width\s+([0-9]*\.?[0-9]+)\s*(?:mm)?\s*$",   re.I | re.M)),
    ("notches",   re.compile(r"^/notches\s+([0-9]*\.?[0-9]+)\s*(?:mm)?\s*$", re.I | re.M)),
    ("symmetric", re.compile(r"^/symmetric\s+(on|off)\s*$",                  re.I | re.M)),
    ("bin",       re.compile(r"^/bin\s+([1-9])\s*[x×]\s*([1-9][0-9]?)\s*$",  re.I | re.M)),
    ("approve",   re.compile(r"^/approve\s*$",                               re.I | re.M)),
    ("close",     re.compile(r"^/close\s*$",                                 re.I | re.M)),
]

RANGE = {"length": (20.0, 600.0), "width": (5.0, 400.0), "notches": (0.0, 10.0)}

HELP = """\
| Command | Effect |
|---|---|
| `/length 240` | Re-measure and rebuild at a new overall length |
| `/width 51` | New width (a cross-check; it does not rescale the model) |
| `/symmetric on` | Make the pocket accept the tool either face up |
| `/notches 2.0` | Bridge concavities shallower than this, to flatten an edge |
| `/bin 2x7` | Force a bin size in grid units |
| `/approve` | You are happy with it — merge the tool into the repository |
| `/close` | Abandon this submission |
"""


def parse(body: str):
    for name, rx in PATTERNS:
        m = rx.search(body)
        if not m:
            continue
        if name in RANGE:
            v = float(m.group(1))
            lo, hi = RANGE[name]
            if not lo <= v <= hi:
                return {"command": "error",
                        "message": "`/%s %s` is outside the accepted range "
                                   "(%g-%g mm)." % (name, m.group(1), lo, hi)}
            return {"command": name, "value": v}
        if name == "symmetric":
            return {"command": name, "value": m.group(1).lower() == "on"}
        if name == "bin":
            return {"command": name, "units_w": int(m.group(1)),
                    "units_l": int(m.group(2))}
        return {"command": name}
    return {"command": "none"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--body-file", required=True)
    ap.add_argument("--author", required=True, help="who wrote the comment")
    ap.add_argument("--allow", required=True,
                    help="the only login whose commands are honoured")
    ap.add_argument("--out", default="cmd.json")
    a = ap.parse_args()

    body = open(a.body_file).read()
    cmd = parse(body)

    # Authorisation last, so an unauthorised comment that isn't a command at
    # all stays silent rather than producing a "you may not do that" reply to
    # ordinary conversation.
    if cmd["command"] != "none" and a.author.lower() != a.allow.lower():
        cmd = {"command": "denied",
               "message": "Only @%s can change or approve this submission." % a.allow}

    json.dump(cmd, open(a.out, "w"), indent=1)
    print(json.dumps(cmd))
    return 0


if __name__ == "__main__":
    sys.exit(main())
