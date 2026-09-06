"""Headless solid modelling for cutouts and bins, on CadQuery/OCCT.

The original pipeline drove Autodesk Fusion over its MCP server, which meant a
licensed GUI application had to be running on the machine. That is fine on a
desk and impossible in CI. This module builds the same solids with OCCT through
CadQuery, so `build-all.sh` runs anywhere Python does.

The constants are unchanged -- they were reverse-engineered from a
gridfinitygenerator.com bin so these interlock with bins printed from that
tool, and that compatibility is the whole point.

One deliberate difference from the Fusion path: the tool outline is a polyline
here, where Fusion fitted a spline through the same points. The spline bowed
outward by up to 0.07 mm, so pockets came out fractionally larger than the
computed outline. A polyline gives exactly the clearance the outline asks for.
"""
import numpy as np
import cadquery as cq
from cadquery.occ_impl.shapes import Solid

GRID, CLEAR, WALL, BASE_H = 42.0, 0.62, 1.2, 4.75
# base pad profile, as (z, width across flats, corner radius). A step that
# changes width is a 45-degree draft: the width grows by exactly the step
# height per side, and so does the corner radius, which is what a uniform
# 2D offset does -- so a tapered extrude reproduces it exactly.
CELL = [(0.00, 35.48, 0.80), (0.80, 37.08, 1.60),
        (2.60, 37.08, 1.60), (4.75, 41.38, 3.75)]
# inner void, as (depth below rim, inset from footprint/2, corner radius).
# Every section is a uniform offset of the footprint, so the radii follow the
# insets: 3.75 - inset.
LIP = [(0.000, 0.00, 3.75), (1.909, 2.15, 1.60),
       (3.709, 2.15, 1.60), (4.509, 2.95, 0.80),
       (5.709, 2.95, 0.80), (7.459, 1.20, 2.55)]
HEIGHT_DEFAULT = 25.754
FLOOR_DEFAULT = 14.0


def rrect_wire(w, h, r, z=0.0, cx=0.0, cy=0.0):
    """A rounded-rectangle wire, as a closed 8-edge loop."""
    sk = cq.Sketch().rect(w, h)
    if r > 1e-9:
        sk = sk.vertices().fillet(r)
    wire = sk._faces.Faces()[0].outerWire()
    return wire.moved(cq.Location(cq.Vector(cx, cy, z)))


def polygon_solid(pts, z0, height):
    """Straight prism through a closed polygon given as (N,2) millimetres."""
    P = np.asarray(pts, float)
    if np.allclose(P[0], P[-1]):
        P = P[:-1]
    return (cq.Workplane("XY", origin=(0, 0, z0))
            .polyline([tuple(p) for p in P]).close()
            .extrude(height).val())


def stadium_solid(y, length, width, z0, height):
    """The finger slot: a stadium in plan, vertical walls, full depth.

    A rectangle filleted by half its height *is* a stadium, which saves
    constructing the two arcs by hand."""
    sk = cq.Sketch().rect(length, width).vertices().fillet(width / 2.0)
    return (cq.Workplane("XY", origin=(0, 0, z0)).placeSketch(sk)
            .extrude(height).val().moved(cq.Location(cq.Vector(0, y, 0))))


def cutout_solid(outline, height=20.0, slot_y=0.0, slot_len=None, slot_w=25.0):
    """The tool-shaped cutting body: outline prism joined to the finger slot."""
    body = polygon_solid(outline, 0.0, height)
    if slot_len:
        body = body.fuse(stadium_solid(slot_y, slot_len, slot_w, 0.0, height))
        body = body.clean()
    return body


def bin_solid(nx, ny, height=HEIGHT_DEFAULT, cavity_floor=FLOOR_DEFAULT,
              tool=None):
    """A gridfinity bin, with the tool pocket already subtracted.

    tool is None or a dict of outline / depth / slot_y / slot_w / slot_len,
    matching the fields make_tool.py writes into meta.json.
    """
    FW, FH = GRID * nx - CLEAR, GRID * ny - CLEAR

    # 1. base pads, one per grid cell, 45-degree drafts as tapered extrudes
    body = None
    for i in range(nx):
        for j in range(ny):
            cx = (i - (nx - 1) / 2.0) * GRID
            cy = (j - (ny - 1) / 2.0) * GRID
            for k in range(len(CELL) - 1):
                z0, w0, r0 = CELL[k]
                z1, w1, _ = CELL[k + 1]
                sk = cq.Sketch().rect(w0, w0).vertices().fillet(r0)
                # negative taper drafts outward, one millimetre per millimetre
                # of height at 45 degrees
                taper = -45.0 if abs(w1 - w0) > 1e-6 else 0.0
                pad = (cq.Workplane("XY", origin=(cx, cy, z0))
                       .placeSketch(sk).extrude(z1 - z0, taper=taper).val())
                body = pad if body is None else body.fuse(pad)
    body = body.clean()

    # 2. main block, top of the base pads up to the rim
    block = (cq.Workplane("XY").add(rrect_wire(FW, FH, 3.75, BASE_H))
             .toPending().extrude(height - BASE_H).val())
    body = body.fuse(block).clean()

    # 3. inner void: loft the lip profiles down to the cavity floor, then cut.
    #    Ruled, not smooth: these sections describe straight chamfers, and a
    #    smooth loft would bulge them.
    wires = [rrect_wire(FW - 2 * WALL, FH - 2 * WALL, 3.75 - WALL, cavity_floor)]
    for depth, inset, r in sorted(LIP, key=lambda t: -t[0]):
        z = height - depth
        if z <= cavity_floor + 1e-6:
            continue
        wires.append(rrect_wire(FW - 2 * inset, FH - 2 * inset, r, z))
    body = body.cut(Solid.makeLoft(wires, ruled=True)).clean()

    # 4. the tool pocket, top flush with the rim
    if tool:
        z0 = height - tool["depth"]
        body = body.cut(cutout_solid(tool["outline"], tool["depth"],
                                     tool.get("slot_y", 0.0),
                                     tool.get("slot_len"),
                                     tool.get("slot_w", 25.0))
                        .moved(cq.Location(cq.Vector(0, 0, z0)))).clean()
    return body


def export_stl(solid, path, tolerance=0.01, angular_tolerance=0.1):
    cq.exporters.export(cq.Workplane("XY").add(solid), path, exportType="STL",
                        tolerance=tolerance, angularTolerance=angular_tolerance)
    return path


def export_dxf(outline, path):
    """The outline only, in millimetres. No finger slot, matching the old
    Fusion export."""
    P = np.asarray(outline, float)
    if np.allclose(P[0], P[-1]):
        P = P[:-1]
    wp = cq.Workplane("XY").polyline([tuple(p) for p in P]).close()
    cq.exporters.export(wp.wires(), path, exportType="DXF")
    return path


def describe(solid):
    bb = solid.BoundingBox()
    return dict(volume=solid.Volume(),
                bbox=(bb.xlen, bb.ylen, bb.zlen))
