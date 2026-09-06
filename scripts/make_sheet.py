"""meta.json -> a dimensioned 1:1 drawing of the tool outline.

One sheet per tool showing the traced silhouette, the pocket that gets cut for
it, and the measurements that set the bin size. Printed at 100% it is also a
gauge: lay the real tool on the solid line and the fit is either right or
obviously not. The trace overlay proves the contour matches the *photograph*;
it cannot prove the photograph was scaled correctly, because a wrong scale
looks perfect at any size. This closes that loop for the price of a sheet of
paper instead of a six-hour print.

    python3 make_sheet.py <meta.json> [--page a4|letter] [--out DIR]

Emits a PDF -- real physical units, so it is the authoritative one -- and a JPG
carrying a correct JFIF density so it prints 1:1 too. Both are drawn from one
display list, so they cannot drift apart.

No dependency beyond numpy and OpenCV: the PDF is written by hand, which is
less alarming than it sounds for a document that is two polylines, a handful of
dimension lines and a ruler.
"""
import sys, os, json, argparse
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_tool import offset_polygon

MM     = 72.0 / 25.4        # PostScript points per millimetre
PAGE   = {"a4": (210.0, 297.0), "letter": (215.9, 279.4)}
MARGIN = 10.0               # mm kept clear of the paper edge
COL    = 58.0               # mm reserved at the left for the legend and ruler
RULER  = 50.0               # mm per leg of the L-shaped scale check
DIM    = 9.0                # mm from the outline bbox out to a dimension line


# ---------------------------------------------------------------- display list
# Primitives are (kind, ...) in millimetres, origin bottom-left, y up. Both
# renderers consume this, so the PDF and the JPG cannot disagree.

def poly(P, w=0.4, g=0.0, dash=None):   return ("poly", np.asarray(P, float), w, g, dash)
def line(x0, y0, x1, y1, w=0.4, g=0.0): return ("line", x0, y0, x1, y1, w, g)
def tri(pts, g=0.0):                    return ("tri", np.asarray(pts, float), g)
def text(x, y, s, size=8.0, g=0.0, rot=False, mid=False):
    return ("text", x, y, s, size, g, rot, mid)


def arrowhead(x, y, ux, uy, size=2.2):
    """Solid triangle at (x,y) pointing along the unit vector (ux,uy)."""
    px, py = -uy, ux
    return tri([(x, y),
                (x - ux * size + px * size * 0.34, y - uy * size + py * size * 0.34),
                (x - ux * size - px * size * 0.34, y - uy * size - py * size * 0.34)])


def dim_v(ops, x, y0, y1, label, ext_from=None):
    """Vertical dimension: extension lines, arrows turned inward, text on top."""
    if ext_from is not None:
        ops += [line(ext_from, y0, x + 2.0, y0, 0.2, 0.45),
                line(ext_from, y1, x + 2.0, y1, 0.2, 0.45)]
    ops += [line(x, y0, x, y1, 0.3),
            arrowhead(x, y0, 0, 1), arrowhead(x, y1, 0, -1),
            text(x + 1.6, (y0 + y1) / 2.0, label, 7.5, rot=True, mid=True)]


def dim_h(ops, y, x0, x1, label, ext_from=None):
    if ext_from is not None:
        ops += [line(x0, ext_from, x0, y - 2.0, 0.2, 0.45),
                line(x1, ext_from, x1, y - 2.0, 0.2, 0.45)]
    ops += [line(x0, y, x1, y, 0.3),
            arrowhead(x0, y, 1, 0), arrowhead(x1, y, -1, 0),
            text((x0 + x1) / 2.0, y - 4.2, label, 7.5, mid=True)]


# --------------------------------------------------------------------- the page

def raw_outline(meta):
    """The traced silhouette. Stored since 2026-09-06; older meta.json files
    predate the field, so fall back to shrinking the pocket back down. That
    recovers the silhouette everywhere except sharp concave corners, which the
    outward offset rounded off and no inward offset can restore."""
    if "outline_raw" in meta:
        return np.array(meta["outline_raw"]), True
    return offset_polygon(np.array(meta["outline"]), -float(meta["offset_mm"]), res=40.0), False


def build(meta, page="a4"):
    W, H = PAGE[page]
    off = np.array(meta["outline"])
    raw, exact = raw_outline(meta)

    rw, rl = float(np.ptp(raw[:, 0])), float(np.ptp(raw[:, 1]))
    ow, ol = float(np.ptp(off[:, 0])), float(np.ptp(off[:, 1]))
    # the drawing needs room for the outline plus a dimension line on two sides
    need_w, need_h = ow + DIM + 9.0, ol + DIM + 9.0
    avail_w, avail_h = W - 2 * MARGIN - COL, H - 2 * MARGIN
    fits = need_w <= avail_w and need_h <= avail_h

    # centre the outline-plus-dimensions block, then place the outline inside it
    cx = MARGIN + COL + (avail_w - need_w) / 2.0 + ow / 2.0
    cy = MARGIN + (avail_h - need_h) / 2.0 + DIM + 9.0 + ol / 2.0
    ops = []

    ops.append(poly(off + [cx, cy], w=0.35, g=0.55, dash=(3, 2)))
    ops.append(poly(raw + [cx, cy], w=0.7, g=0.0))

    l, r = cx - ow / 2.0, cx + ow / 2.0
    b, t = cy - ol / 2.0, cy + ol / 2.0
    dim_v(ops, r + DIM, cy - rl / 2.0, cy + rl / 2.0, "%.1f" % rl, ext_from=cx + rw / 2.0)
    dim_h(ops, b - DIM, cx - rw / 2.0, cx + rw / 2.0, "%.1f" % rw, ext_from=cy - rl / 2.0)

    # scale check, bottom-left, clear of everything
    x0, y0 = MARGIN, MARGIN
    ops += [line(x0, y0, x0 + RULER, y0, 0.6), line(x0, y0, x0, y0 + RULER, 0.6)]
    for k in range(0, int(RULER) + 1, 10):
        h = 4.0 if k % 50 == 0 else 2.5
        ops += [line(x0 + k, y0, x0 + k, y0 + h, 0.35),
                line(x0, y0 + k, x0 + h, y0 + k, 0.35)]
    ops += [text(x0 + RULER / 2.0, y0 + 5.5, "%d mm" % RULER, 7, mid=True),
            text(x0 + 5.5, y0 + RULER / 2.0, "%d mm" % RULER, 7, rot=True, mid=True)]

    uw, ul = meta["grid_units"]
    legend = [
        (meta["name"], 11, 0.0),
        ("", 0, 0),
        ("PRINT AT 100% / ACTUAL SIZE", 8, 0.0),
        ('not "fit to page", not "shrink to fit"', 6.8, 0.3),
        ("both ruler legs must read %d mm" % RULER, 6.8, 0.3),
        ("", 0, 0),
        ("TOOL", 7.5, 0.0),
        ("  measured    %.0f x %.0f mm" % (meta["length_mm"], meta["width_mm"] or 0), 7, 0.15),
        ("  traced      %.2f x %.2f mm" % (rl, rw), 7, 0.15),
        ("", 0, 0),
        ("POCKET", 7.5, 0.0),
        ("  outline     %.2f x %.2f mm" % (ol, ow), 7, 0.15),
        ("  clearance   %.1f mm radial" % meta["offset_mm"], 7, 0.15),
        ("  depth       %.0f mm" % meta["depth_mm"], 7, 0.15),
        ("", 0, 0),
        ("BIN", 7.5, 0.0),
        ("  %d x %d units" % (uw, ul), 7, 0.15),
        ("  %.2f x %.2f mm" % (uw * 42.0 - 0.62, ul * 42.0 - 0.62), 7, 0.15),
        ("  lip opening %.2f mm" % (ul * 42.0 - 6.52), 7, 0.15),
        ("  margin      %.2f mm per end" % ((ul * 42.0 - 6.52 - ol) / 2.0), 7, 0.15),
        ("", 0, 0),
        ("solid   tool silhouette", 6.8, 0.15),
        ("dashed  pocket", 6.8, 0.15),
        ("", 0, 0),
        ("photo   %s" % meta["source"], 6.5, 0.35),
    ]
    if meta.get("mirrored"):
        legend.append(("mirrored across the long axis", 6.5, 0.35))
    if not exact:
        legend += [("", 0, 0), ("silhouette reconstructed from the pocket;", 6.3, 0.4),
                   ("rebuild the tool for an exact one", 6.3, 0.4)]
    if not fits:
        legend += [("", 0, 0), ("** DOES NOT FIT %s **" % page.upper(), 8, 0.0),
                   ("needs %.1f x %.1f, have %.1f x %.1f mm"
                    % (need_w, need_h, avail_w, avail_h), 6.3, 0.0)]

    y = H - MARGIN - 5
    for s, size, g in legend:
        if s:
            ops.append(text(MARGIN, y, s, size, g))
        y -= (size + 1.5) if s else 2.6
    return ops, W, H, fits


# ----------------------------------------------------------------- PDF renderer

def _esc(t):
    return t.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")


def _wid(s, size):
    """Helvetica is ~0.52 em average over this character set; good enough to
    centre a dimension figure without embedding metrics."""
    return len(s) * size * 0.52


def to_pdf(ops, W, H):
    out_ops = []
    for op in ops:
        k = op[0]
        if k == "poly":
            _, P, w, g, dash = op
            out_ops.append("q %.3f G %.2f w [%s] 0 d" %
                           (g, w, " ".join("%.1f" % d for d in dash) if dash else ""))
            for i, (x, y) in enumerate(P):
                out_ops.append("%.3f %.3f %s" % (x * MM, y * MM, "m" if i == 0 else "l"))
            out_ops.append("h S Q")
        elif k == "line":
            _, x0, y0, x1, y1, w, g = op
            out_ops.append("q %.3f G %.2f w %.3f %.3f m %.3f %.3f l S Q"
                           % (g, w, x0 * MM, y0 * MM, x1 * MM, y1 * MM))
        elif k == "tri":
            _, P, g = op
            out_ops.append("q %.3f g %.3f %.3f m %.3f %.3f l %.3f %.3f l h f Q"
                           % (g, *(v * MM for p in P for v in p)))
        elif k == "text":
            _, x, y, s, size, g, rot, mid = op
            if mid:                       # _wid is in points; x,y are in mm
                half = _wid(s, size) / 2.0 / MM
                if rot: y -= half
                else:   x -= half
            tm = ("0 1 -1 0 %.3f %.3f Tm" if rot else "1 0 0 1 %.3f %.3f Tm") % (x * MM, y * MM)
            out_ops.append("q BT %.3f g /F1 %.2f Tf %s (%s) Tj ET Q" % (g, size, tm, _esc(s)))
    stream = "\n".join(out_ops).encode("latin-1")
    objs = [
        b"<</Type/Catalog/Pages 2 0 R>>",
        b"<</Type/Pages/Kids[3 0 R]/Count 1>>",
        ("<</Type/Page/Parent 2 0 R/MediaBox[0 0 %.3f %.3f]"
         "/Resources<</Font<</F1 5 0 R>>>>/Contents 4 0 R>>" % (W * MM, H * MM)).encode(),
        b"<</Length " + str(len(stream)).encode() + b">>\nstream\n" + stream + b"\nendstream",
        b"<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>",
    ]
    out, offs = bytearray(b"%PDF-1.4\n"), []
    for i, body in enumerate(objs, 1):
        offs.append(len(out))
        out += b"%d 0 obj\n" % i + body + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n" % (len(objs) + 1) + b"0000000000 65535 f \n"
    for o in offs:
        out += b"%010d 00000 n \n" % o
    out += b"trailer\n<</Size %d/Root 1 0 R>>\nstartxref\n%d\n%%%%EOF\n" % (len(objs) + 1, xref)
    return bytes(out)


# -------------------------------------------------------------- raster renderer

def _dashes(P, dash):
    """Walk a closed polygon by arc length, emitting the on-segments of a dash
    pattern. cv2.polylines has no dash support, and a solid grey line would
    contradict the legend."""
    Q = np.vstack([P, P[:1]])
    on, off = float(dash[0]), float(dash[1])
    pos, drawing, out = 0.0, True, []
    for a, b in zip(Q[:-1], Q[1:]):
        seg = float(np.hypot(*(b - a)))
        if seg <= 1e-9:
            continue
        t = 0.0
        while t < seg:
            span = (on if drawing else off) - pos
            step = min(span, seg - t)
            if drawing:
                out.append((a + (b - a) * (t / seg), a + (b - a) * ((t + step) / seg)))
            t += step
            pos += step
            if pos >= (on if drawing else off) - 1e-9:
                drawing, pos = not drawing, 0.0
    return out


def to_jpg(ops, W, H, dpi=300.0):
    px = dpi / 25.4
    img = np.full((int(round(H * px)), int(round(W * px)), 3), 255, np.uint8)
    Y = img.shape[0]
    pt = lambda x, y: (int(round(x * px)), int(round(Y - y * px)))
    gray = lambda g: tuple([int(round(255 * g))] * 3)
    lw = lambda w: max(1, int(round(w * px)))
    FT, TH = cv2.FONT_HERSHEY_SIMPLEX, cv2.LINE_AA
    for op in ops:
        k = op[0]
        if k == "poly":
            _, P, w, g, dash = op
            if dash:
                for A, B in _dashes(P, dash):
                    cv2.line(img, pt(*A), pt(*B), gray(g), lw(w), TH)
            else:
                Q = np.array([pt(x, y) for x, y in P], np.int32)
                cv2.polylines(img, [Q], True, gray(g), lw(w), TH)
        elif k == "line":
            _, x0, y0, x1, y1, w, g = op
            cv2.line(img, pt(x0, y0), pt(x1, y1), gray(g), lw(w), TH)
        elif k == "tri":
            _, P, g = op
            cv2.fillConvexPoly(img, np.array([pt(x, y) for x, y in P], np.int32), gray(g), TH)
        elif k == "text":
            _, x, y, s, size, g, rot, mid = op
            sc = size / 11.0
            (tw, th), _ = cv2.getTextSize(s, FT, sc, max(1, int(round(px * 0.09))))
            if rot:                      # render upright, then rotate the patch
                pad = np.full((th + 8, tw + 8, 3), 255, np.uint8)
                cv2.putText(pad, s, (2, th + 2), FT, sc, gray(g),
                            max(1, int(round(px * 0.09))), TH)
                pad = cv2.rotate(pad, cv2.ROTATE_90_COUNTERCLOCKWISE)
                ox, oy = pt(x, y)
                oy -= pad.shape[0] if not mid else pad.shape[0] // 2
                h2, w2 = pad.shape[:2]
                if 0 <= oy and oy + h2 <= Y and 0 <= ox and ox + w2 <= img.shape[1]:
                    roi = img[oy:oy + h2, ox:ox + w2]
                    img[oy:oy + h2, ox:ox + w2] = np.minimum(roi, pad)
            else:
                ox, oy = pt(x, y)
                if mid:
                    ox -= tw // 2
                cv2.putText(img, s, (ox, oy), FT, sc, gray(g),
                            max(1, int(round(px * 0.09))), TH)
    ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 92])
    if not ok:
        raise RuntimeError("JPEG encode failed")
    return _set_jfif_dpi(bytearray(buf.tobytes()), dpi)


def _set_jfif_dpi(b, dpi):
    """Patch the APP0/JFIF density fields. OpenCV writes a 1:1 aspect ratio,
    which tells a print dialog nothing about physical size."""
    i = b.find(b"\xff\xe0")
    if i < 0 or b[i + 4:i + 9] != b"JFIF\x00":
        return bytes(b)          # no JFIF segment; the PDF is authoritative anyway
    b[i + 11] = 1                # density units: pixels per inch
    b[i + 12:i + 14] = int(dpi).to_bytes(2, "big")
    b[i + 14:i + 16] = int(dpi).to_bytes(2, "big")
    return bytes(b)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("meta")
    ap.add_argument("--page", choices=sorted(PAGE), default="a4")
    ap.add_argument("--dpi", type=float, default=300.0)
    ap.add_argument("--out", default=None, help="output dir (default: alongside meta.json)")
    ap.add_argument("--stem", default="outline_sheet")
    a = ap.parse_args()

    meta = json.load(open(a.meta))
    outdir = a.out or os.path.dirname(os.path.abspath(a.meta))
    os.makedirs(outdir, exist_ok=True)
    ops, W, H, fits = build(meta, a.page)
    open(os.path.join(outdir, a.stem + ".pdf"), "wb").write(to_pdf(ops, W, H))
    open(os.path.join(outdir, a.stem + ".jpg"), "wb").write(to_jpg(ops, W, H, a.dpi))

    raw, exact = raw_outline(meta)
    print("%-22s %-6s silhouette %7.2f x %6.2f mm  %s%s" % (
        meta["name"], a.page.upper(), np.ptp(raw[:, 1]), np.ptp(raw[:, 0]),
        "" if exact else "(reconstructed) ", "" if fits else "** DOES NOT FIT **"))


if __name__ == "__main__":
    main()
