"""Extract a tool silhouette from an overhead photo on a warm wood background.

Discriminators, each measured against a locally-estimated background field so a
lighting gradient across the frame does not bias them:
    dB  wood is warm (high b*), steel is cool          -> polished/bare metal
    dL  wood is bright, blacked steel is dark          -> black oxide head
    dA  wood is neutral, grips are saturated           -> coloured handles

strict seed -> GC_FGD, mid mask -> GC_PR_FGD, far field -> GC_BGD, then GrabCut
settles the boundary.
"""
import cv2, numpy as np

K=lambda n: cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(n,n))

def fill_holes(m):
    h,w=m.shape
    ff=m.copy(); pad=np.zeros((h+2,w+2),np.uint8)
    cv2.floodFill(ff,pad,(0,0),255)
    return m|cv2.bitwise_not(ff)

def _bgfield(ch, mode, k=301, ds=4):
    sml=cv2.resize(ch,(ch.shape[1]//ds,ch.shape[0]//ds),interpolation=cv2.INTER_AREA)
    ker=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,((k//ds)|1,(k//ds)|1))
    o=cv2.GaussianBlur(cv2.morphologyEx(sml,mode,ker),(0,0),9)
    return cv2.resize(o,(ch.shape[1],ch.shape[0]),interpolation=cv2.INTER_LINEAR)

def _largest(m):
    n,lbl,st,_=cv2.connectedComponentsWithStats(m,8)
    if n<2: raise RuntimeError("empty mask")
    return (lbl==max(range(1,n),key=lambda i:st[i][4])).astype(np.uint8)*255

def backdrop_roi(sm, erode=9):
    """Mask of the shooting backdrop (sheet of paper, benchtop).

    A photo whose backdrop does not fill the frame leaves darker surroundings --
    carpet, a bag, a box -- which the darkness channel calls "tool", so the
    largest component ends up being the surround. Restricting the search to the
    backdrop fixes that. When the backdrop already fills the frame this returns
    all-ones and changes nothing.
    """
    L=cv2.cvtColor(sm,cv2.COLOR_BGR2LAB)[:,:,0]
    h,w=L.shape
    thr,_=cv2.threshold(cv2.GaussianBlur(L,(0,0),3),0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    m=(L>thr).astype(np.uint8)*255
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,K(31))
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,K(31))
    n,lbl,st,_=cv2.connectedComponentsWithStats(m,8)
    if n<2: return np.full((h,w),255,np.uint8)
    i=max(range(1,n),key=lambda j:st[j][4])
    if st[i][4] < 0.25*h*w: return np.full((h,w),255,np.uint8)
    roi=fill_holes((lbl==i).astype(np.uint8)*255)   # the tool is a hole in the backdrop
    if erode: roi=cv2.erode(roi,K(erode))
    return roi

def channels(sm):
    lab=cv2.cvtColor(cv2.bilateralFilter(sm,9,75,75),cv2.COLOR_BGR2LAB)
    L=lab[:,:,0].astype(np.float32);A=lab[:,:,1].astype(np.float32)-128;B=lab[:,:,2].astype(np.float32)-128
    # The b* background field uses a max filter, so a grip WARMER than the wood
    # (orange sits at b*~+38 against wood's ~+10) inflates the estimate and makes
    # ordinary wood look cool, i.e. metal. Neutralise saturated pixels first: the
    # background we are modelling is bare wood, which is close to neutral.
    chroma=np.hypot(A,B)
    Bn=B.copy()
    neutral=chroma<=20
    if neutral.any(): Bn[~neutral]=float(np.median(B[neutral]))
    return (_bgfield(Bn,cv2.MORPH_CLOSE)-B,
            A-_bgfield(A,cv2.MORPH_OPEN),
            _bgfield(L,cv2.MORPH_CLOSE)-L)

def segment(SRC, work=1400, iters=6, shrink=5,
            strict=(18,22,85), mid=(7.5,12,80), dbg=None):
    img=cv2.imread(SRC,cv2.IMREAD_COLOR)
    H0,W0=img.shape[:2]; s=float(work)/max(H0,W0)
    sm=cv2.resize(img,(int(W0*s),int(H0*s)),interpolation=cv2.INTER_AREA)
    h,w=sm.shape[:2]
    dB,dA,dL=channels(sm)
    roi=backdrop_roi(sm)

    def band(t,op,cl):
        m=(((dB>t[0])|(dA>t[1])|(dL>t[2])).astype(np.uint8))*255
        m=cv2.bitwise_and(m,roi)          # never look outside the backdrop
        m=cv2.morphologyEx(m,cv2.MORPH_OPEN,K(op))
        m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,K(cl))
        m[:6,:]=0;m[-6:,:]=0;m[:,:6]=0;m[:,-6:]=0
        return m

    sd  = fill_holes(_largest(band(strict,9,35)))
    md  = band(mid,7,25)
    md  = cv2.bitwise_or(md, sd)
    md  = fill_holes(_largest(md))

    gm=np.full((h,w),cv2.GC_PR_BGD,np.uint8)
    gm[cv2.dilate(md,K(85))==0]=cv2.GC_BGD
    gm[md>0]=cv2.GC_PR_FGD
    gm[cv2.erode(sd,K(21))>0]=cv2.GC_FGD
    cv2.grabCut(sm,gm,None,np.zeros((1,65),np.float64),np.zeros((1,65),np.float64),
                iters,cv2.GC_INIT_WITH_MASK)
    m=(((gm==cv2.GC_FGD)|(gm==cv2.GC_PR_FGD)).astype(np.uint8))*255
    m=cv2.bitwise_and(m,roi)

    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,K(9))
    m=fill_holes(_largest(m))
    if shrink: m=cv2.erode(m,K(shrink))
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,K(9))
    m=fill_holes(m)
    cs,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    c=max(cs,key=cv2.contourArea)
    if dbg:
        ov=sm.copy(); cv2.drawContours(ov,[c],-1,(0,255,0),3); cv2.imwrite(dbg,ov)
    return sm,m,c

def metrics(c):
    (_,_),(rw,rh),ang=cv2.minAreaRect(c)
    return max(rw,rh),min(rw,rh),ang

if __name__=="__main__":
    SRC="/Users/alexraddas/Desktop/tools/IMG_1805.jpeg"
    sm,m,c=segment(SRC,dbg="dbg_final.png")
    Lp,Wp,_=metrics(c)
    print("long=%.0f short=%.0f ratio=%.3f target=%.3f err=%+.1f%% area=%d pts=%d"
          %(Lp,Wp,Lp/Wp,246/51,100*((Lp/Wp)/(246/51)-1),cv2.contourArea(c),len(c)))
    ov=sm.copy(); cv2.drawContours(ov,[c],-1,(0,255,0),3)
    cv2.imwrite("dbg_head.png",cv2.resize(ov[100:470,420:680],None,fx=2.2,fy=2.2,interpolation=cv2.INTER_NEAREST))
    np.save("contour_px.npy",c.reshape(-1,2).astype(np.float64))
