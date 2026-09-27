#!/usr/bin/env python3
"""Clearance-checked residual route search; all resulting geometry gets native DRC."""
from pathlib import Path
import pcbnew as p,numpy as np,math,json,subprocess
from shapely.geometry import Point,LineString,box,Polygon
from shapely import contains_xy
R=Path(__file__).resolve().parents[2];D=R/'boards/gps-time-calibrator';O=R/'tmp/calibrator/grid';O.mkdir(parents=True,exist_ok=True);b=p.LoadBoard(str(D/'calibrator.kicad_pcb'));layers=[p.F_Cu,p.In2_Cu,p.B_Cu]+([p.In1_Cu] if __import__("os").environ.get("ALLOW_IN1") else []);step=.05;clear=.137;width=.2;vr=.25;mm=p.FromMM
xy=lambda pos:(p.ToMM(pos.x),p.ToMM(pos.y))
def run(n,start,end):
 global W,H,A,V,x0,y0
 x0=max(20.5,math.floor(min(start[0],end[0])-12));y0=max(10.5,math.floor(min(start[1],end[1])-12));x1=min(199.5,math.ceil(max(start[0],end[0])+12));y1=min(109.5,math.ceil(max(start[1],end[1])+12));W=round((x1-x0)/step)+1;H=round((y1-y0)/step)+1;A=np.zeros((len(layers),H,W),np.uint8);V=np.zeros((H,W),np.uint8)
 def paint(arr,g):
  a,c,d,e=g.bounds;ix0=max(0,math.floor((a-x0)/step));iy0=max(0,math.floor((c-y0)/step));ix1=min(W-1,math.ceil((d-x0)/step));iy1=min(H-1,math.ceil((e-y0)/step))
  if ix1<ix0 or iy1<iy0:return
  xx,yy=np.meshgrid(x0+np.arange(ix0,ix1+1)*step,y0+np.arange(iy0,iy1+1)*step);mask=contains_xy(g,xx,yy);arr[iy0:iy1+1,ix0:ix1+1][mask]=1
 for f in b.GetFootprints():
  for pad in f.Pads():
   px,py=xy(pad.GetPosition());sx,sy=xy(pad.GetSize());ang=pad.GetOrientationDegrees()%180
   if abs(ang-90)<1:sx,sy=sy,sx
   g=box(px-sx/2,py-sy/2,px+sx/2,py+sy/2)
   paint(V,g.buffer(vr+clear))
   if pad.GetNetname()!=n:
    for z,ly in enumerate(layers):
     if pad.IsOnLayer(ly):paint(A[z],g.buffer(clear+width/2))
 for t in b.GetTracks():
  if t.GetNetname()==n:continue
  if isinstance(t,p.PCB_VIA):
   g=Point(*xy(t.GetPosition())).buffer(p.ToMM(t.GetWidth(p.F_Cu))/2)
   for a in A:paint(a,g.buffer(clear+width/2))
  else:
   g=LineString([xy(t.GetStart()),xy(t.GetEnd())]).buffer(p.ToMM(t.GetWidth())/2)
   if t.GetLayer() in layers:paint(A[layers.index(t.GetLayer())],g.buffer(clear+width/2))
  paint(V,g.buffer(clear+vr))
 for ref in ['U3','U4','U11','U14']:
  f=b.FindFootprintByReference(ref);bb=f.GetBoundingBox(False,False);g=box(p.ToMM(bb.GetX()),p.ToMM(bb.GetY()),p.ToMM(bb.GetRight()),p.ToMM(bb.GetBottom()))
  paint(V,g.buffer(vr))
 for ref in ['H1','H2','H3','H4','H5']:
  f=b.FindFootprintByReference(ref);g=Point(*xy(f.GetPosition())).buffer(3.5)
  for a in A:paint(a,g.buffer(width/2))
  paint(V,g.buffer(vr))
 def index(pt,z):return z*W*H+round((pt[1]-y0)/step)*W+round((pt[0]-x0)/step)
 endpoint_layers=[0] if __import__("os").environ.get("ENDPOINTS_F") else range(len(layers))
 ss=[index(start,z) for z in endpoint_layers];tt=[index(end,z) for z in endpoint_layers]
 if __import__('os').environ.get('CANDIDATES'):
  cand=[]
  for yy in range(H):
   for xx in range(W):
    pt=(x0+xx*step,y0+yy*step)
    if math.dist(pt,start)<3 and not V[yy,xx] and not any(A[:,yy,xx]):cand.append((math.dist(pt,start),pt))
  print(sorted(cand)[:20]);return
 ss=[k for k in ss if not A.flat[k]];tt=[k for k in tt if not A.flat[k]]
 assert ss and tt,(n,'blocked endpoints')
 with (O/'search.bin').open('wb') as f:
  np.array([W,H,len(layers),len(ss),len(tt)],np.int32).tofile(f);A.tofile(f);V.tofile(f);np.array(ss,np.int32).tofile(f);np.array(tt,np.int32).tofile(f)
 subprocess.run([str(R/'tmp/carrier/grid_route'),str(O)],check=True)
 path=[tuple(map(int,l.split())) for l in (O/'path.txt').read_text().splitlines()];pts=[]
 for i,a in enumerate(path):
  if i==0 or i==len(path)-1 or tuple(a[k]-path[i-1][k] for k in range(3))!=tuple(path[i+1][k]-a[k] for k in range(3)):pts.append(a)
 def xyz(a):return (x0+a[0]*step,y0+a[1]*step,a[2])
 pts=list(map(xyz,pts));pts=[(*start,pts[0][2])]+pts+[(*end,pts[-1][2])]
 for a,c in zip(pts,pts[1:]):
  if a[2]!=c[2]:
   t=p.PCB_VIA(b);t.SetPosition(p.VECTOR2I(mm(a[0]),mm(a[1])));t.SetWidth(mm(.5));t.SetDrill(mm(.25));t.SetLayerPair(p.F_Cu,p.B_Cu);t.SetViaType(p.VIATYPE_THROUGH)
  else:
   if math.dist(a[:2],c[:2])<.00001:continue
   t=p.PCB_TRACK(b);t.SetStart(p.VECTOR2I(mm(a[0]),mm(a[1])));t.SetEnd(p.VECTOR2I(mm(c[0]),mm(c[1])));t.SetLayer(layers[a[2]]);t.SetWidth(mm(width))
  t.SetNet(b.FindNet(n));b.Add(t)
 print(n,'routed',len(pts),'vertices',flush=True)
 p.SaveBoard(str(D/'calibrator.kicad_pcb'),b)
if __name__=='__main__':
 import sys
 n=sys.argv[1];vs=[xy(t.GetPosition()) for t in b.GetTracks() if isinstance(t,p.PCB_VIA) and t.GetNetname()==n];print(n,vs)
 # Manual endpoint selection is explicit in command line.
 run(n,tuple(map(float,sys.argv[2:4])),tuple(map(float,sys.argv[4:6])))
