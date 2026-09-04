"""Generate a gridfinity bin, optionally subtracting a tool cutout.

Constants reverse-engineered from a gridfinitygenerator.com bin so these
interlock with bins already printed from that generator.

    footprint   42n - 0.62, corner r 3.75
    base pad    35.48 r0.8 -[0.8 chamfer]- 37.08 r1.6 -[1.8]- -[2.15 chamfer]- 41.38 r3.75
    wall        1.2
    lip         mirrors the base outer profile, so a bin above nests into it
"""
import sys, os, json, argparse
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fmcp import Fusion

GRID, CLEAR, WALL, BASE_H = 42.0, 0.62, 1.2, 4.75
CELL = [(0.00, 35.48, 0.80), (0.80, 37.08, 1.60),
        (2.60, 37.08, 1.60), (4.75, 41.38, 3.75)]
# inner void, as (depth below rim, half-width inset from footprint/2, corner r)
LIP  = [(0.000, 0.00, 3.75), (1.909, 2.15, 1.60),
        (3.709, 2.15, 1.60), (4.509, 2.95, 0.80),
        (5.709, 2.95, 0.80), (7.459, 1.20, 2.55)]

SCRIPT = r'''
import adsk.core, adsk.fusion, os, json
P = json.loads(%r)   # parse, don't paste: JSON true/false/null are not Python literals
KEEP_OPEN = bool(P["keep_open"])

def run(_context: str):
    app = adsk.core.Application.get()
    _doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    des = adsk.fusion.Design.cast(app.activeProduct)
    des.designType = adsk.fusion.DesignTypes.DirectDesignType
    des.unitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
    root = des.rootComponent
    ex   = root.features.extrudeFeatures
    C    = lambda v: v / 10.0
    NEW  = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    JOIN = adsk.fusion.FeatureOperations.JoinFeatureOperation
    CUT  = adsk.fusion.FeatureOperations.CutFeatureOperation

    def rrect(sk, cx, cy, w, h, r):
        L = sk.sketchCurves.sketchLines; A = sk.sketchCurves.sketchArcs
        x0, x1 = cx - w/2.0, cx + w/2.0
        y0, y1 = cy - h/2.0, cy + h/2.0
        p = lambda x, y: adsk.core.Point3D.create(C(x), C(y), 0)
        L.addByTwoPoints(p(x0+r, y0), p(x1-r, y0))
        L.addByTwoPoints(p(x1, y0+r), p(x1, y1-r))
        L.addByTwoPoints(p(x1-r, y1), p(x0+r, y1))
        L.addByTwoPoints(p(x0, y1-r), p(x0, y0+r))
        s = r * (2**0.5) / 2.0
        A.addByThreePoints(p(x1-r, y0), p(x1-r+s, y0+r-s), p(x1, y0+r))
        A.addByThreePoints(p(x1, y1-r), p(x1-r+s, y1-r+s), p(x1-r, y1))
        A.addByThreePoints(p(x0+r, y1), p(x0+r-s, y1-r+s), p(x0, y1-r))
        A.addByThreePoints(p(x0, y0+r), p(x0+r-s, y0+r-s), p(x0+r, y0))

    planes = {}
    def plane(z):
        k = round(z, 4)
        if k in planes: return planes[k]
        if abs(z) < 1e-9:
            planes[k] = root.xYConstructionPlane
        else:
            i = root.constructionPlanes.createInput()
            i.setByOffset(root.xYConstructionPlane, adsk.core.ValueInput.createByReal(C(z)))
            planes[k] = root.constructionPlanes.add(i)
        return planes[k]

    def sketch_rrect(z, cx, cy, w, h, r):
        sk = root.sketches.add(plane(z)); sk.isComputeDeferred = True
        rrect(sk, cx, cy, w, h, r); sk.isComputeDeferred = False
        return sk, max([sk.profiles.item(i) for i in range(sk.profiles.count)],
                       key=lambda q: q.areaProperties().area)

    def extrude(prof, h, op, taper=0.0, bodies=None):
        ei = ex.createInput(prof, op)
        ext = adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(C(h)))
        ei.setOneSideExtent(ext, adsk.fusion.ExtentDirections.PositiveExtentDirection,
                            adsk.core.ValueInput.createByString("%%.6f deg" %% taper))
        if bodies: ei.participantBodies = bodies
        return ex.add(ei)

    NX, NY, H = P["nx"], P["ny"], P["height"]
    FW = 42.0*NX - P["clear"]; FH = 42.0*NY - P["clear"]
    CELL = P["cell"]

    # 1. base pads, one per grid cell, 45-degree chamfers via tapered extrude
    body = None
    for i in range(NX):
        for j in range(NY):
            cx = (i - (NX-1)/2.0) * 42.0
            cy = (j - (NY-1)/2.0) * 42.0
            for k in range(len(CELL)-1):
                z0, w0, r0 = CELL[k]; z1, w1, r1 = CELL[k+1]
                taper = 45.0 if abs(w1-w0) > 1e-6 else 0.0
                _, pr = sketch_rrect(z0, cx, cy, w0, w0, r0)
                f = extrude(pr, z1-z0, NEW if body is None else JOIN,
                            taper, None if body is None else [body])
                if body is None: body = f.bodies.item(0)
    print("base pads:", root.bRepBodies.count, "body")

    # 2. main block from the top of the base to the rim
    _, pr = sketch_rrect(P["base_h"], 0, 0, FW, FH, 3.75)
    extrude(pr, H - P["base_h"], JOIN, 0.0, [body])
    print("block joined, bbox check follows")

    # 3. inner void: loft through the lip + cavity profiles, then cut
    lofts = root.features.loftFeatures
    li = lofts.createInput(CUT)
    li.participantBodies = [body]
    order = sorted(P["lip"], key=lambda t: -t[0])          # bottom-most first
    floor = P["cavity_floor"]
    _, base_pr = sketch_rrect(floor, 0, 0, FW-2*P["wall"], FH-2*P["wall"], 3.75-P["wall"])
    li.loftSections.add(base_pr)
    for depth, inset, r in order:
        z = H - depth
        if z <= floor + 1e-6: continue
        _, pr = sketch_rrect(z, 0, 0, FW-2*inset, FH-2*inset, r)
        li.loftSections.add(pr)
    lofts.add(li)

    # 4. subtract the tool cutout: top flush with the rim, extending DEPTH down
    T = P.get("tool")
    if T:
        z0 = H - T["depth"]
        sk = root.sketches.add(plane(z0)); sk.isComputeDeferred = True
        coll = adsk.core.ObjectCollection.create()
        for x, y in T["outline"]: coll.add(adsk.core.Point3D.create(C(x), C(y), 0))
        sk.sketchCurves.sketchFittedSplines.add(coll).isClosed = True
        sk.isComputeDeferred = False
        pr = max([sk.profiles.item(i) for i in range(sk.profiles.count)],
                 key=lambda q: q.areaProperties().area)
        extrude(pr, T["depth"], CUT, 0.0, [body])
        r = T["slot_w"] / 2.0; half = T["slot_len"] / 2.0 - r
        sy = T["slot_y"]
        sk2 = root.sketches.add(plane(z0)); sk2.isComputeDeferred = True
        L = sk2.sketchCurves.sketchLines; A = sk2.sketchCurves.sketchArcs
        p = lambda x, y: adsk.core.Point3D.create(C(x), C(y), 0)
        L.addByTwoPoints(p(-half, sy-r), p(half, sy-r))
        L.addByTwoPoints(p(-half, sy+r), p(half, sy+r))
        A.addByThreePoints(p(half, sy-r), p(half+r, sy), p(half, sy+r))
        A.addByThreePoints(p(-half, sy-r), p(-half-r, sy), p(-half, sy+r))
        sk2.isComputeDeferred = False
        pr2 = max([sk2.profiles.item(i) for i in range(sk2.profiles.count)],
                  key=lambda q: q.areaProperties().area)
        extrude(pr2, T["depth"], CUT, 0.0, [body])
        print("cutout subtracted, depth", T["depth"], "top at rim", H)

    b = root.bRepBodies.item(0); b.name = P["name"]
    bb = b.boundingBox
    print("bbox mm: %%.3f x %%.3f x %%.3f" %% ((bb.maxPoint.x-bb.minPoint.x)*10,
        (bb.maxPoint.y-bb.minPoint.y)*10, (bb.maxPoint.z-bb.minPoint.z)*10))
    print("volume mm3: %%.1f" %% (b.volume*1000.0))

    os.makedirs(P["out"], exist_ok=True)
    path = os.path.join(P["out"], P["stem"] + ".stl")
    em = des.exportManager
    o = em.createSTLExportOptions(b, path)
    o.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
    o.isBinaryFormat = True
    em.execute(o)
    print("exported:", path, os.path.getsize(path), "bytes")
    if not KEEP_OPEN:
        _doc.close(False)   # scratch doc; artefacts are on disk
        print("document closed")
'''

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nx", type=int, default=0)
    ap.add_argument("--ny", type=int, default=0)
    ap.add_argument("--height", type=float, default=25.754)
    ap.add_argument("--cavity-floor", type=float, default=14.0)
    ap.add_argument("--out", default=".")
    ap.add_argument("--stem", default="bin")
    ap.add_argument("--name", default="bin")
    ap.add_argument("--meta", default=None, help="tool meta.json to subtract")
    ap.add_argument("--keep-open", action="store_true", help="leave the Fusion document open")
    a = ap.parse_args()
    tool=None
    if a.meta:
        m=json.load(open(a.meta))
        tool=dict(outline=m["outline"], depth=m["depth_mm"],
                  slot_y=m["slot"]["y"], slot_w=m["slot"]["width"], slot_len=m["slot"]["length"])
        if not a.nx: a.nx, a.ny = m["grid_units"]
    P = dict(keep_open=int(a.keep_open), tool=tool, nx=a.nx, ny=a.ny, height=a.height, clear=CLEAR, cell=CELL, wall=WALL,
             lip=LIP, base_h=BASE_H, cavity_floor=a.cavity_floor,
             out=os.path.abspath(a.out), stem=a.stem, name=a.name)
    print(Fusion().call("fusion_mcp_execute",
        {"featureType": "script", "object": {"script": SCRIPT % json.dumps(P)}}))

if __name__ == "__main__":
    main()
