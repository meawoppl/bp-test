#!/usr/bin/env python3
"""Visible exterior pin-1 dots for every carrier IC and MOSFET. Layout venv."""
import pcbnew as p,json,math
from pathlib import Path
from shapely.geometry import Point,box
from shapely.ops import unary_union
from shapely.prepared import prep
D=Path(__file__).resolve().parents[2]/'boards/gps-time-calibrator';b=p.LoadBoard(str(D/'calibrator.kicad_pcb'));out=D/'docs/pin1-markers.json'
old=json.loads(out.read_text()) if out.exists() else []
uuids={s['uuid'] for s in old}
for g in list(b.GetDrawings()):
 if g.m_Uuid.AsString() in uuids:b.RemoveNative(g)
xy=lambda q:(q.x/1e6,q.y/1e6);v=lambda x,y:p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def bb(obj):
 q=obj.GetBoundingBox(False,False) if isinstance(obj,p.FOOTPRINT) else obj.GetBoundingBox()
 return box(q.GetX()/1e6,q.GetY()/1e6,q.GetRight()/1e6,q.GetBottom()/1e6)
fps=list(b.GetFootprints());obstacles=[bb(f) for f in fps]
for f in fps:
 for a in f.GetFields():
  if a.IsVisible() and a.GetLayer()==p.F_SilkS:obstacles.append(bb(a))
for g in b.GetDrawings():
 if g.GetLayer()==p.F_SilkS:obstacles.append(bb(g))
obstacle_union=unary_union(obstacles).buffer(.42)
rows=[]
for f in sorted(fps,key=lambda f:f.GetReference()):
 if not f.GetReference().startswith(('U','Q')):continue
 blocked=prep(obstacle_union)
 pad=next(a for a in f.Pads() if a.GetNumber()=='1');px,py=xy(pad.GetPosition());cx,cy=xy(f.GetPosition());candidates=[]
 for i in range(-35,36):
  for j in range(-35,36):
   x=round(px+i*.1,4);y=round(py+j*.1,4)
   if (x-cx)*(px-cx)+(y-cy)*(py-cy)<0:continue
   dot=Point(x,y)
   if blocked.intersects(dot):continue
   candidates.append((math.hypot(x-px,y-py),x,y))
 assert candidates,f.GetReference()
 _,x,y=min(candidates);g=p.PCB_SHAPE(b);g.SetShape(p.SHAPE_T_CIRCLE);g.SetCenter(v(x,y));g.SetEnd(v(x+.2,y));g.SetWidth(p.FromMM(.12));g.SetFilled(True);g.SetLayer(p.F_SilkS);b.Add(g);obstacles.append(Point(x,y).buffer(.2))
 obstacle_union=obstacle_union.union(Point(x,y).buffer(.6))
 rows.append({'ref':f.GetReference(),'pad1_mm':[px,py],'marker_mm':[x,y],'uuid':g.m_Uuid.AsString()})
p.SaveBoard(str(D/'calibrator.kicad_pcb'),b);out.write_text(json.dumps(rows,indent=2)+'\n');print('Added',len(rows),'exterior pin-1 markers')
