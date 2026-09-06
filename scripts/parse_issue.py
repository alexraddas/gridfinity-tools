"""Turn a `new-tool` issue body into build arguments.

GitHub Issue Forms render to markdown: a `### Field label` heading followed by
the value. That is the only contract available -- there is no structured
payload -- so this parser is deliberately forgiving about whitespace and case,
and strict about the two numbers that matter.

    python3 parse_issue.py --body-file issue.md --out build.json
"""
import argparse
import json
import re
import sys

FIELDS = {
    "manufacturer": "manufacturer",
    "part number": "part_number",
    "length (mm)": "length",
    "width (mm)": "width",
    "does it have crossed jaws?": "crossed_jaws",
    "photo": "photo",
    "anything unusual?": "notes",
}
# Only GitHub's own upload hosts, in both the markdown-image and bare-URL forms
# (dragging and pasting produce different text). An arbitrary URL here would have the runner
# fetch whatever a stranger names, and a photo that is not a GitHub upload did
# not come from dragging it into the issue -- which is what we asked for.
HOST = r"https://(?:github\.com/user-attachments/assets|user-images\.githubusercontent\.com)/[^\s)\"']+"
IMAGE = re.compile(r"!\[[^\]]*\]\((?P<md>" + HOST + r")\)|(?P<bare>" + HOST + r")")
SLUG = re.compile(r"[^a-z0-9]+")


def split_sections(body: str) -> dict:
    out, key, buf = {}, None, []
    for line in body.replace("\r\n", "\n").split("\n"):
        m = re.match(r"^#{1,6}\s+(.*?)\s*$", line)
        if m:
            if key:
                out[key] = "\n".join(buf).strip()
            key, buf = m.group(1).strip().lower(), []
        elif key:
            buf.append(line)
    if key:
        out[key] = "\n".join(buf).strip()
    return out


def slug(*parts) -> str:
    s = SLUG.sub("-", "-".join(p.lower() for p in parts if p)).strip("-")
    return re.sub(r"-+", "-", s)


def number(raw: str, field: str) -> float:
    """Accept '206', '206 mm', '206mm', '20.6 cm'. Reject anything else loudly:
    a silently mis-parsed length scales the entire model."""
    t = raw.strip().lower().replace(",", ".")
    m = re.match(r"^([0-9]*\.?[0-9]+)\s*(mm|cm|millimet(?:er|re)s?|centimet(?:er|re)s?)?$", t)
    if not m:
        raise ValueError("%s: cannot read a measurement from %r" % (field, raw))
    v = float(m.group(1))
    if (m.group(2) or "mm").startswith(("cm", "centi")):
        v *= 10.0
    if not 20.0 <= v <= 600.0:
        raise ValueError("%s: %.1f mm is outside the range this pipeline handles "
                         "(20-600 mm). Check the units." % (field, v))
    return v


def parse(body: str) -> dict:
    sec = split_sections(body)
    got = {}
    for label, name in FIELDS.items():
        for k, v in sec.items():
            if k == label:
                got[name] = v
                break
    # Width is optional: nothing is scaled from it, and the printed sheet is a
    # better width check than a number typed into a form.
    missing = [l for l, n in FIELDS.items()
               if n not in ("notes", "width") and not got.get(n)]
    if missing:
        raise ValueError("the issue is missing: %s" % ", ".join(sorted(missing)))

    m = IMAGE.search(got["photo"])
    if not m:
        raise ValueError("no image found in the Photo field — drag the photo "
                         "into the issue rather than linking to it elsewhere")

    answer = got["crossed_jaws"].lower()
    symmetric = "either way up" in answer

    name = slug(got["manufacturer"], got["part_number"])
    return {
        "name": name,
        "dir": "%s/%s" % (slug(got["manufacturer"]), slug(got["part_number"])),
        "photo_url": m.group("md") or m.group("bare"),
        "length": number(got["length"], "length"),
        "width": number(got["width"], "width") if got.get("width", "").strip()
                 not in ("", "_No response_") else None,
        "symmetric": symmetric,
        # GitHub writes this placeholder into empty optional fields
        "notes": "" if got.get("notes", "").strip() == "_No response_"
                 else got.get("notes", "").strip(),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--body-file", required=True)
    ap.add_argument("--out", default="build.json")
    a = ap.parse_args()
    try:
        spec = parse(open(a.body_file).read())
    except ValueError as e:
        print("::error::%s" % e)
        return 1
    json.dump(spec, open(a.out, "w"), indent=1)
    for k, v in spec.items():
        print("%-10s %s" % (k, v))
    return 0


if __name__ == "__main__":
    sys.exit(main())
