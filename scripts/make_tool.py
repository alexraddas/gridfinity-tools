"""photo -> gridfinity emboss/cutting body STL, via Fusion."""
import sys, os, json, argparse
import numpy as np, cv2
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from toolseg import segment, metrics
from contour import to_mm, resample, smooth
from fmcp import Fusion

def _chunk(s, width=180):
    """Emit a long string as adjacent literals on separate lines.

    Fusion's MCP server silently drops a script containing any single line
    longer than roughly 4 KB -- it returns success and never runs it. Long
    outline data must therefore be wrapped."""
    return "\n".join(repr(s[i:i+width]) for i in range(0, len(s), width))

# --- defaults agreed with the user ---
HEIGHT   = 20.0   # extrusion height, mm
OFFSET   = 1.5    # radial clearance offset, mm
SLOT_W   = 25.0   # finger slot width along the tool axis, mm
SLOT_OVER= 24.0   # slot overhang past each side of the outline, mm
GRID     = 42.0   # gridfinity unit, mm
GRID_M   = 8.0    # slot stops this far short of the bin width (4mm per side)
BIN_CLR  = 0.62   # bin footprint = GRID*n - BIN_CLR
LIP_IN   = 2.95   # lip narrows the opening by this much per side
MARGIN   = 5.0    # minimum clearance per end between outline and lip opening
USABLE   = lambda n, g=42.0: g*n - BIN_CLR - 2*LIP_IN
OUTDIR   = "/Users/alexraddas/Desktop/tools/stl"

def offset_polygon(P, delta, res=20.0):
    """Raster-based polygon offset. Handles self-intersection and gap closure
    the same way Fusion's sketch offset does."""
    pad=abs(delta)+3.0
    mn=P.min(0)-pad; mx=P.max(0)+pad
    size=((mx-mn)*res).astype(int)+1
    img=np.zeros((size[1],size[0]),np.uint8)
    cv2.fillPoly(img,[((P-mn)*res).astype(np.int32)],255)
    r=int(round(abs(delta)*res))
    k=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*r+1,2*r+1))
    img=cv2.dilate(img,k) if delta>0 else cv2.erode(img,k)
    cs,_=cv2.findContours(img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    c=max(cs,key=cv2.contourArea).reshape(-1,2).astype(np.float64)
    return c/res+mn

def polish(P,n=520,win=5,simplify=0.06):
    P=smooth(resample(P,n*3),win)
    P=resample(P,n)
    return cv2.approxPolyDP(P.astype(np.float32).reshape(-1,1,2),simplify,True).reshape(-1,2).astype(np.float64)

def width_profile(P,res=8.0):
    mn=P.min(0); size=((P.max(0)-mn)*res).astype(int)+3
    img=np.zeros((size[1],size[0]),np.uint8)
    cv2.fillPoly(img,[((P-mn)*res+1).astype(np.int32)],255)
    rows=[]
    for r in range(img.shape[0]):
        xs=np.where(img[r]>0)[0]
        if len(xs)==0: continue
        rows.append(((r-1)/res+mn[1], (xs.max()-xs.min())/res, len(xs)/res))
    return rows   # (y, outer span, material)

def build(name,P,height,slot_y,slot_len,slot_w,outdir,stem='cutout',keep_open=False):
    script='''
import adsk.core, adsk.fusion, os, json
PTS=json.loads(
%s
)
NAME=%r; OUT=%r; H=%r; SY=%r; SLEN=%r; SW=%r; STEM=%r; KEEP_OPEN=%r

def run(_context: str):
    app=adsk.core.Application.get()
    _doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    des=adsk.fusion.Design.cast(app.activeProduct)
    des.designType=adsk.fusion.DesignTypes.DirectDesignType
    des.unitsManager.distanceDisplayUnits=adsk.fusion.DistanceUnits.MillimeterDistanceUnits
    root=des.rootComponent
    C=lambda v: v/10.0

    sk=root.sketches.add(root.xYConstructionPlane); sk.name=NAME+"_outline"
    sk.isComputeDeferred=True
    coll=adsk.core.ObjectCollection.create()
    for x,y in PTS: coll.add(adsk.core.Point3D.create(C(x),C(y),0.0))
    sk.sketchCurves.sketchFittedSplines.add(coll).isClosed=True
    sk.isComputeDeferred=False
    if sk.profiles.count==0: raise RuntimeError("no closed profile")
    prof=max([sk.profiles.item(i) for i in range(sk.profiles.count)],
             key=lambda p:p.areaProperties().area)
    ext=root.features.extrudeFeatures.addSimple(prof,
        adsk.core.ValueInput.createByReal(C(H)),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    body=ext.bodies.item(0); body.name=NAME

    # finger slot: stadium in plan, vertical walls, full depth
    sk2=root.sketches.add(root.xYConstructionPlane); sk2.name=NAME+"_fingerslot"
    r=SW/2.0; half=SLEN/2.0-r
    y0,y1=SY-r,SY+r
    L=sk2.sketchCurves.sketchLines
    L.addByTwoPoints(adsk.core.Point3D.create(C(-half),C(y0),0),
                     adsk.core.Point3D.create(C( half),C(y0),0))
    L.addByTwoPoints(adsk.core.Point3D.create(C(-half),C(y1),0),
                     adsk.core.Point3D.create(C( half),C(y1),0))
    A=sk2.sketchCurves.sketchArcs
    A.addByThreePoints(adsk.core.Point3D.create(C(half),C(y0),0),
                       adsk.core.Point3D.create(C(half+r),C(SY),0),
                       adsk.core.Point3D.create(C(half),C(y1),0))
    A.addByThreePoints(adsk.core.Point3D.create(C(-half),C(y0),0),
                       adsk.core.Point3D.create(C(-half-r),C(SY),0),
                       adsk.core.Point3D.create(C(-half),C(y1),0))
    if sk2.profiles.count==0: raise RuntimeError("slot profile failed")
    sp=max([sk2.profiles.item(i) for i in range(sk2.profiles.count)],
           key=lambda p:p.areaProperties().area)
    ei=root.features.extrudeFeatures.createInput(sp,
        adsk.fusion.FeatureOperations.JoinFeatureOperation)
    ei.setDistanceExtent(False,adsk.core.ValueInput.createByReal(C(H)))
    ei.participantBodies=[body]
    root.features.extrudeFeatures.add(ei)

    body=root.bRepBodies.item(0)
    bb=body.boundingBox
    print("bodies:",root.bRepBodies.count)
    print("bbox mm: %%.2f x %%.2f x %%.2f"%%((bb.maxPoint.x-bb.minPoint.x)*10,
        (bb.maxPoint.y-bb.minPoint.y)*10,(bb.maxPoint.z-bb.minPoint.z)*10))
    print("volume mm3: %%.1f"%%(body.volume*1000.0))
    os.makedirs(OUT,exist_ok=True)
    path=os.path.join(OUT,STEM+".stl")
    em=des.exportManager
    o=em.createSTLExportOptions(body,path)
    o.meshRefinement=adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
    o.isBinaryFormat=True
    em.execute(o)
    print("exported:",path,os.path.getsize(path),"bytes")
    dxf=os.path.join(OUT,STEM+".dxf")
    if not sk.saveAsDXF(dxf): raise RuntimeError("DXF export failed")
    if not os.path.exists(dxf): raise RuntimeError("DXF reported success but no file at "+dxf)
    print("exported:",dxf,os.path.getsize(dxf),"bytes")
    if not KEEP_OPEN:
        _doc.close(False)   # close only after every export has landed
        print("document closed")
''' % (_chunk(json.dumps([[round(float(x),4),round(float(y),4)] for x,y in P])),
       name,outdir,float(height),float(slot_y),float(slot_len),float(slot_w),stem,keep_open)
    return Fusion().call("fusion_mcp_execute",{"featureType":"script","object":{"script":script}})

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("image"); ap.add_argument("name")
    ap.add_argument("--length",type=float,required=True)
    ap.add_argument("--width",type=float)
    ap.add_argument("--height",type=float,default=HEIGHT)
    ap.add_argument("--offset",type=float,default=OFFSET)
    ap.add_argument("--slot-w",type=float,default=SLOT_W)
    ap.add_argument("--slot-over",type=float,default=SLOT_OVER)
    ap.add_argument("--grid",type=float,default=GRID)
    ap.add_argument("--grid-margin",type=float,default=GRID_M)
    ap.add_argument("--units-w",type=int,default=None)
    ap.add_argument("--units-l",type=int,default=None)
    ap.add_argument("--margin",type=float,default=MARGIN,help="min mm per end (0 = pack tight)")
    ap.add_argument("--slot-y",type=float,default=None)
    ap.add_argument("--outdir",default=OUTDIR)
    ap.add_argument("--keep-open",action="store_true",help="leave the Fusion document open")
    ap.add_argument("--dl-strict",type=float,default=85.0,
                    help="luminance threshold for the confident seed (default 85)")
    ap.add_argument("--dl-mid",type=float,default=80.0,
                    help="luminance threshold for the probable-foreground band (default 80).\n"
                         "Lower both for a low-contrast tool, e.g. bare steel on a pale backdrop")
    ap.add_argument("--length-mode",choices=("rect","tip"),default="rect",
                    help="rect: length is the bounding extent (default). tip: length is the\n"
                         "max tip-to-tip distance, for bent tools such as scissors")
    ap.add_argument("--mirror",action="store_true",help="mirror across the long axis")
    ap.add_argument("--no-build",action="store_true")
    a=ap.parse_args()
    a.outdir=os.path.abspath(a.outdir)

    sm,mask,c=segment(a.image,dbg=f"chk_{a.name}_trace.png",
                      strict=(18,22,a.dl_strict), mid=(7.5,12,a.dl_mid))
    Lp,Wp,_=metrics(c)
    print("traced: %.0f x %.0f px  ratio %.3f"%(Lp,Wp,Lp/Wp))
    if a.width:
        err=100*((Lp/Wp)/(a.length/a.width)-1)
        print("aspect vs measured %.1f x %.1f -> %+.1f%%"%(a.length,a.width,err))
        if abs(err)>4: print("  ** WARNING: aspect mismatch >4%%, check the trace overlay **")

    raw,_=to_mm(c.reshape(-1,2).astype(np.float64),a.length)
    if a.length_mode=="tip":
        # "length" was measured tip-to-tip, not as a bounding extent. On a bent
        # tool (scissors with offset handles) the two differ by several percent.
        hull=cv2.convexHull(raw.astype(np.float32)).reshape(-1,2).astype(np.float64)
        diam=max(np.hypot(*(hull-p).T).max() for p in hull)
        k=a.length/diam
        raw*=k
        print("length mode 'tip': rescaled by %.4f (bounding %.2f -> tip-to-tip %.2f mm)"%(
            k,np.ptp(raw[:,1])/k,a.length))
    off=polish(offset_polygon(raw,a.offset,res=40.0))
    if a.mirror:
        off=off[::-1].copy(); off[:,0]*=-1            # mirror across the long axis
        print("mirrored across the long axis")
    # centre on the bounding box in both axes. Centring on the centroid instead
    # shifts an asymmetric tool toward its heavy end and overhangs the bin.
    off-= [ (off[:,0].max()+off[:,0].min())/2, (off[:,1].max()+off[:,1].min())/2 ]
    print("outline  raw %.2f x %.2f mm   offset+%.1f -> %.2f x %.2f mm"%(
        np.ptp(raw[:,0]),np.ptp(raw[:,1]),a.offset,np.ptp(off[:,0]),np.ptp(off[:,1])))

    # gap-closure check
    pr=width_profile(raw); po=width_profile(off)
    gr=max((s-m) for _,s,m in pr); go=max((s-m) for _,s,m in po)
    print("largest internal gap: raw %.2f mm -> offset %.2f mm"%(gr,go))
    if gr>0.5 and go<0.5: print("  ** WARNING: offset closed an internal gap entirely **")

    # mid-length by default: the outline is centred on its bounding box, so 0
    # is the middle of the tool. On short tools the widest point sits at the
    # handle tips and the slot would overhang the end of the outline.
    slot_y=0.0 if a.slot_y is None else a.slot_y
    ow=float(np.ptp(off[:,0])); ol=float(np.ptp(off[:,1]))
    # the tool must fit the lip opening (42n - 6.52), not the outer footprint
    fit=lambda d: int(np.ceil((d+2*a.margin+BIN_CLR+2*LIP_IN)/a.grid))
    uw=a.units_w or fit(ow)
    ul=a.units_l or fit(ol)
    bin_w=uw*a.grid
    slot_len=min(ow+2*a.slot_over, bin_w-a.grid_margin)
    print("grid: needs %dx%d units (%.0f x %.0f mm) for outline %.2f x %.2f"%(uw,ul,bin_w,ul*a.grid,ow,ol))
    marg=(USABLE(ul,a.grid)-ol)/2
    print("  fits lip opening %.2f mm with %.2f mm per end"%(USABLE(ul,a.grid),marg))
    if marg<0: print("  ** ERROR: tool overhangs the lip by %.2f mm per end **"%(-marg))
    elif marg<a.margin: print("  ** NOTE: %.2f mm per end is below the %.1f mm minimum (overridden) **"%(marg,a.margin))
    print("slot: y=%.2f  width %.1f  length %.1f mm (capped by %.0f mm bin - %.0f)"%(
        slot_y,a.slot_w,slot_len,bin_w,a.grid_margin))
    if slot_len < ow+8:
        print("  ** WARNING: slot only %.1f mm wider than the tool -- little finger access **"%(slot_len-ow))

    np.save(f"outline_{a.name}.npy",off)
    meta=dict(name=a.name,source=os.path.basename(a.image),
              length_mm=a.length,width_mm=a.width,mirrored=bool(a.mirror),
              depth_mm=a.height,offset_mm=a.offset,
              outline_w=round(ow,3),outline_l=round(ol,3),
              grid_units=[uw,ul],bin_mm=[uw*a.grid,ul*a.grid],
              slot=dict(y=round(float(slot_y),3),width=a.slot_w,length=round(slot_len,3)),
              outline=[[round(float(x),4),round(float(y),4)] for x,y in off])
    os.makedirs(a.outdir,exist_ok=True)
    json.dump(meta,open(os.path.join(a.outdir,"meta.json"),"w"),indent=1)
    print("wrote",os.path.join(a.outdir,"meta.json"))
    if not a.no_build:
        print(build(a.name,off,a.height,slot_y,slot_len,a.slot_w,a.outdir,keep_open=a.keep_open))

if __name__=="__main__": main()
