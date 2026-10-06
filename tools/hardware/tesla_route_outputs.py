#!/usr/bin/env python3
"""Manual wide front-copper switch-node/output links for the compact draft.
Only replaces tracks owned by this script. Control, power feeds and planes remain unrouted.
"""
import json,uuid,math
from pathlib import Path
import pcbnew as p
D=Path(__file__).resolve().parents[2]/'boards/tesla-coil-controller'
b=p.LoadBoard(str(D/'controller.kicad_pcb'));nets={n.GetNetname():n for n in b.GetNetInfo().NetsByNetcode().values()}
uid=lambda i:str(uuid.uuid5(uuid.NAMESPACE_URL,f'bp-tesla-output-copper/{i}'))
owned={uid(i) for i in range(200)};removed=[]
for t in list(b.GetTracks()):
 if t.m_Uuid.AsString() in owned:removed.append(t);b.Remove(t)
rows=[];count=0
v=lambda xy:p.VECTOR2I(p.FromMM(xy[0]),p.FromMM(xy[1]))
def path(net,width,pts,off):
 global count
 pts=[(x+3,y+off+12) for x,y in pts]
 for a,z in zip(pts,pts[1:]):
  if a==z:continue
  dx=abs(a[0]-z[0]);dy=abs(a[1]-z[1]);assert min(dx,dy)<1e-5 or abs(dx-dy)<1e-5,(net,a,z)
  t=p.PCB_TRACK(b);t.SetStart(v(a));t.SetEnd(v(z));t.SetWidth(p.FromMM(width));t.SetLayer(p.F_Cu);t.SetNet(nets[net]);t.SetUuid(p.KIID(uid(count)));b.Add(t);count+=1
  rows.append(dict(net=net,width_mm=width,length_mm=math.dist(a,z),start=a,end=z))
for ch in range(2):
 off=55*ch;pre=f'GDT{ch+1}_'
 for leg,x in [('L',142),('R',160)]:
  path(pre+leg+'_SW',2.5,[(x+2.28,57.04),(x+2.28,67.46),(x,69.74)],off)
 path(pre+'L_SW',2.5,[(142,69.74),(142,79),(143,80),(164.0375,80),(167.525,76.5125),(167.525,72)],off)
 path(pre+'R_SW',2.5,[(162.28,57.04),(171.12,57.04),(174,59.92)],off)
 path(pre+'OUT_P',2.5,[(170.475,72),(174,68.475),(174,65)],off)
 path(pre+'OUT_P',1,[(175.475,80),(177,80),(177,68.475),(174,68.475)],off)
 path(pre+'SNUB',1,[(169.9625,80),(172.525,80)],off)
p.SaveBoard(str(D/'controller.kicad_pcb'),b)
(D/'docs/output-copper.json').write_text(json.dumps(dict(stage='Local output links only; remainder unrouted',layer='F.Cu',segments=rows),indent=2)+'\n')
print(len(rows),'manual output segments')
