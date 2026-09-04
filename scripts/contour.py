"""Turn a pixel contour into a smoothed, scaled, mm-space closed outline."""
import cv2, numpy as np

def resample(P, n):
    """Uniform resample of a closed polygon by arc length."""
    Q=np.vstack([P,P[:1]])
    seg=np.linalg.norm(np.diff(Q,axis=0),axis=1)
    s=np.concatenate([[0],np.cumsum(seg)])
    t=np.linspace(0,s[-1],n,endpoint=False)
    return np.column_stack([np.interp(t,s,Q[:,0]), np.interp(t,s,Q[:,1])])

def smooth(P, win):
    """Circular moving average; removes pixel stair-stepping."""
    if win<3: return P
    k=np.ones(win)/win
    ext=np.vstack([P[-win:],P,P[:win]])
    out=np.column_stack([np.convolve(ext[:,0],k,'same'),np.convolve(ext[:,1],k,'same')])
    return out[win:-win]

def to_mm(P_px, length_mm, n=520, win=9, simplify_mm=0.12):
    P=resample(P_px,n*3)
    P=smooth(P,win)
    # align long axis to +Y using the minimum-area rectangle
    rect=cv2.minAreaRect(P.astype(np.float32))
    (cx,cy),(rw,rh),ang=rect
    if rw>rh: ang+=90.0
    th=np.deg2rad(-ang)
    R=np.array([[np.cos(th),-np.sin(th)],[np.sin(th),np.cos(th)]])
    P=(P-[cx,cy])@R.T
    Lpx=max(rw,rh)
    mm_per_px=length_mm/Lpx
    P*=mm_per_px
    P[:,1]*=-1                      # image y grows down; flip to a right-handed sketch
    P=resample(P,n)
    if simplify_mm:
        P=cv2.approxPolyDP(P.astype(np.float32).reshape(-1,1,2),simplify_mm,True).reshape(-1,2).astype(np.float64)
    P-=P.mean(axis=0)
    return P, mm_per_px

def report(P):
    w=P[:,0].max()-P[:,0].min(); h=P[:,1].max()-P[:,1].min()
    a=0.5*abs(np.dot(P[:,0],np.roll(P[:,1],-1))-np.dot(P[:,1],np.roll(P[:,0],-1)))
    return w,h,a

if __name__=="__main__":
    px=np.load("contour_px.npy")
    P,mmpp=to_mm(px,246.0)
    w,h,a=report(P)
    print("points: %d   mm/px: %.4f"%(len(P),mmpp))
    print("bbox  : %.2f mm wide  x  %.2f mm tall   (target 51 x 246)"%(w,h))
    print("area  : %.1f mm^2"%a)
    np.save("outline_mm.npy",P)
    # preview
    S=4.0; pad=20
    img=np.full((int(h*S)+2*pad,int(w*S)+2*pad,3),255,np.uint8)
    Q=((P-[P[:,0].min(),P[:,1].min()])*S+pad).astype(np.int32)
    Q[:,1]=img.shape[0]-Q[:,1]
    cv2.fillPoly(img,[Q],(215,225,240)); cv2.polylines(img,[Q],True,(20,20,20),2)
    cv2.imwrite("preview_outline.png",img)
    print("preview_outline.png written", img.shape)
