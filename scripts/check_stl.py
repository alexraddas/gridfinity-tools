import struct, numpy as np, cv2, sys, os
def check(path, meta_json=None, png=None):
    """meta_json, when given, overlays that tool's pocket outline on the plan view."""
    d=open(path,'rb').read(); n=struct.unpack('<I',d[80:84])[0]
    tris=np.frombuffer(d[84:84+50*n],dtype=np.dtype([('n','<3f4'),('v','<3,3f4'),('a','<u2')]))
    V=tris['v'].reshape(-1,3)
    print("%s: %d tris  %.2f x %.2f x %.2f mm"%(os.path.basename(path),n,*(V.max(0)-V.min(0))))
    E={}
    for t in tris['v']:
        k=[tuple(np.round(x,4)) for x in t]
        for a,b in ((0,1),(1,2),(2,0)):
            e=tuple(sorted((k[a],k[b]))); E[e]=E.get(e,0)+1
    bad=sum(1 for v in E.values() if v!=2)
    print("   watertight: %s (%d bad edges)"%(bad==0,bad))
    if png:
        S=5.0; mn=np.array([V[:,0].min(),V[:,1].min()]); pad=18
        sz=(((V.max(0)-V.min(0))[:2])*S+2*pad).astype(int)
        m=np.zeros((sz[1],sz[0]),np.uint8)
        for t in tris['v']:
            q=((t[:,:2]-mn)*S+pad).astype(np.int32); q[:,1]=m.shape[0]-q[:,1]
            cv2.fillConvexPoly(m,q,255)
        vis=np.full((sz[1],sz[0],3),255,np.uint8); vis[m>0]=(205,220,238)
        cs,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        cv2.drawContours(vis,cs,-1,(40,60,90),2)
        if meta_json is not None:
            import json
            P=np.array(json.load(open(meta_json))["outline"])
            P=P-[(P[:,0].max()+P[:,0].min())/2,0]
            Q=((P-mn)*S+pad).astype(np.int32); Q[:,1]=vis.shape[0]-Q[:,1]
            cv2.polylines(vis,[Q],True,(40,40,200),2)
        cv2.imwrite(png,vis); print("   wrote",png)
if __name__=="__main__":
    check(sys.argv[1], sys.argv[2] if len(sys.argv)>2 else None, sys.argv[3] if len(sys.argv)>3 else None)
