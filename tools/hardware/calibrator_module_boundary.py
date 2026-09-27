#!/usr/bin/env python3
"""Keep the module-v1 mechanical envelope attached to its mating interface.
J1-relative ordered module geometry: body x +/-10, y -14.3..30.7;
J2 is +25 mm Y and H1 +12.5 mm Y. No copper/footprint placement changes.
"""
from pathlib import Path
import pcbnew as p
D=Path(__file__).resolve().parents[2]/'boards/gps-time-calibrator'
b=p.LoadBoard(str(D/'calibrator.kicad_pcb'));fps={f.GetReference():f for f in b.GetFootprints()}
x,y=(p.ToMM(v) for v in [fps['J1'].GetPosition().x,fps['J1'].GetPosition().y])
for ref,dy in [('J2',25),('H1',12.5)]:
 q=fps[ref].GetPosition();assert abs(p.ToMM(q.x)-x)<.001 and abs(p.ToMM(q.y)-y-dy)<.001,(ref,'module interface spacing mismatch')
name='Module v1 mating interface (J1 J2 H1 + body)'
old=next((g for g in b.Groups() if g.GetName()==name),None)
if old:
 for item in list(old.GetItems()):
  old.RemoveItem(item)
  if isinstance(item,p.PCB_SHAPE):b.RemoveNative(item)
 b.RemoveNative(old)
else:
 for item in list(b.GetDrawings()):
  if not isinstance(item,p.PCB_SHAPE) or item.GetLayer()!=p.F_Fab:continue
  a,z=item.GetStart(),item.GetEnd()
  pts=[(p.ToMM(t.x),p.ToMM(t.y)) for t in [a,z]]
  if all(any(abs(xx-k)<.001 for k in [145,165]) and any(abs(yy-k)<.001 for k in [29.7,74.7]) for xx,yy in pts):b.RemoveNative(item)
g=p.PCB_GROUP(b);g.SetName(name);b.Add(g)
for ref in ['J1','J2','H1']:g.AddItem(fps[ref])
pts=[(x-10,y-14.3),(x+10,y-14.3),(x+10,y+30.7),(x-10,y+30.7)]
for a,z in zip(pts,pts[1:]+pts[:1]):
 s=p.PCB_SHAPE(b);s.SetShape(p.SHAPE_T_SEGMENT);s.SetStart(p.VECTOR2I(*[p.FromMM(v) for v in a]));s.SetEnd(p.VECTOR2I(*[p.FromMM(v) for v in z]));s.SetLayer(p.F_Fab);s.SetWidth(p.FromMM(.12));b.Add(s);g.AddItem(s)
# Visible side/bottom outline; top is flush with carrier edge, so omit top silk.
silk=[(x-10,y-13.5),(x-10,y+30.7),(x+10,y+30.7),(x+10,y-13.5)]
segments=list(zip(silk,silk[1:]))[:2]+[((x+10,y+30.7),(x+10,y-4.8)),((x+10,y-7.8),(x+10,y-13.5))]
# Leave a 3 mm silk break around the run-mode pull-up R4 at the right edge.
for a,z in segments:
 s=p.PCB_SHAPE(b);s.SetShape(p.SHAPE_T_SEGMENT);s.SetStart(p.VECTOR2I(*[p.FromMM(v) for v in a]));s.SetEnd(p.VECTOR2I(*[p.FromMM(v) for v in z]));s.SetLayer(p.F_SilkS);s.SetWidth(p.FromMM(.12));b.Add(s);g.AddItem(s)
p.SaveBoard(str(D/'calibrator.kicad_pcb'),b)
print('Module body:',pts,'; J1/J2/H1 grouped with outline; no placements changed.')
