"""photo -> gridfinity emboss/cutting body STL, via Fusion."""
import sys, os, json, argparse
import numpy as np, cv2
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from toolseg import segment, metrics
from contour import to_mm, resample, smooth
from fmcp import Fusion

# --- defaults agreed with the user ---
HEIGHT   = 20.0   # extrusion height, mm
OFFSET   = 1.5    # radial clearance offset, mm
SLOT_W   = 25.0   # finger slot width along the tool axis, mm
SLOT_OVER= 24.0   # slot overhang past each side of the outline, mm
GRID     = 42.0   # gridfinity unit, mm
GRID_M   = 8.0    # slot stops this far short of the bin width (4mm per side)
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

def build(name,P,height,slot_y,slot_len,slot_w,outdir,stem='cutout'):
    script='''
import adsk.core, adsk.fusion, os
PTS=%s
NAME=%r; OUT=%r; H=%r; SY=%r; SLEN=%r; SW=%r; STEM=%r

def run(_context: str):
    app=adsk.core.Application.get()
    app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
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
    if sk.saveAsDXF(dxf): print("exported:",dxf,os.path.getsize(dxf),"bytes")
    else: raise RuntimeError("DXF export failed")
''' % (json.dumps([[round(float(x),4),round(float(y),4)] for x,y in P]),
       name,outdir,float(height),float(slot_y),float(slot_len),float(slot_w),stem)
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
    ap.add_argument("--slot-y",type=float,default=None)
    ap.add_argument("--outdir",default=OUTDIR)
    ap.add_argument("--mirror",action="store_true",help="mirror across the long axis")
    ap.add_argument("--no-build",action="store_true")
    a=ap.parse_args()

    sm,mask,c=segment(a.image,dbg=f"chk_{a.name}_trace.png")
    Lp,Wp,_=metrics(c)
    print("traced: %.0f x %.0f px  ratio %.3f"%(Lp,Wp,Lp/Wp))
    if a.width:
        err=100*((Lp/Wp)/(a.length/a.width)-1)
        print("aspect vs measured %.1f x %.1f -> %+.1f%%"%(a.length,a.width,err))
        if abs(err)>4: print("  ** WARNING: aspect mismatch >4%%, check the trace overlay **")

    raw,_=to_mm(c.reshape(-1,2).astype(np.float64),a.length)
    off=polish(offset_polygon(raw,a.offset,res=40.0))
    if a.mirror:
        off=off[::-1].copy(); off[:,0]*=-1            # mirror across the long axis
        print("mirrored across the long axis")
    off-= [ (off[:,0].max()+off[:,0].min())/2, 0 ]     # centre X on the slot axis
    print("outline  raw %.2f x %.2f mm   offset+%.1f -> %.2f x %.2f mm"%(
        np.ptp(raw[:,0]),np.ptp(raw[:,1]),a.offset,np.ptp(off[:,0]),np.ptp(off[:,1])))

    # gap-closure check
    pr=width_profile(raw); po=width_profile(off)
    gr=max((s-m) for _,s,m in pr); go=max((s-m) for _,s,m in po)
    print("largest internal gap: raw %.2f mm -> offset %.2f mm"%(gr,go))
    if gr>0.5 and go<0.5: print("  ** WARNING: offset closed an internal gap entirely **")

    slot_y=a.slot_y
    if slot_y is None:
        slot_y=max(po,key=lambda r:r[1])[0]
    ow=float(np.ptp(off[:,0])); ol=float(np.ptp(off[:,1]))
    uw=a.units_w or int(np.ceil(ow/a.grid))
    ul=int(np.ceil(ol/a.grid))
    bin_w=uw*a.grid
    slot_len=min(ow+2*a.slot_over, bin_w-a.grid_margin)
    print("grid: needs %dx%d units (%.0f x %.0f mm) for outline %.2f x %.2f"%(uw,ul,bin_w,ul*a.grid,ow,ol))
    marg=(ul*a.grid-ol)/2
    if marg<3: print("  ** WARNING: only %.2f mm per end at %d units long -- likely needs %d **"%(marg,ul,ul+1))
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
        print(build(a.name,off,a.height,slot_y,slot_len,a.slot_w,a.outdir))

if __name__=="__main__": main()
