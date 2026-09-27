#!/usr/bin/env python3
"""Measure connected ESD-to-module USB paths, not total branched net copper."""
from pathlib import Path
D=Path(__file__).resolve().parents[2]/"boards/gps-time-calibrator"
import pcbnew as p,collections,heapq,math,json
b=p.LoadBoard(str(D/'calibrator.kicad_pcb'));xy=lambda v:(round(p.ToMM(v.x),6),round(p.ToMM(v.y),6));out={}
for net,ep,cp in [('USB_D+',6,7),('USB_D-',4,8)]:
 g=collections.defaultdict(list);vs=[]
 for t in b.GetTracks():
  if t.GetNetname()!=net:continue
  if isinstance(t,p.PCB_VIA):vs.append(xy(t.GetPosition()));continue
  a=(*xy(t.GetStart()),t.GetLayer());c=(*xy(t.GetEnd()),t.GetLayer());d=math.dist(a[:2],c[:2]);g[a].append((c,d));g[c].append((a,d))
 for v in vs:
  nodes=[a for a in g if a[:2]==v]
  for a in nodes:
   for c in nodes:
    if a!=c:g[a].append((c,0))
 def pad(ref,n):return next(q for q in b.FindFootprintByReference(ref).Pads() if q.GetNumber()==str(n))
 a=(*xy(pad('U1',ep).GetPosition()),p.F_Cu);end=(*xy(pad('J1',cp).GetPosition()),p.F_Cu);q=[(0,a)];dist={a:0}
 while q:
  d,a=heapq.heappop(q)
  if d!=dist[a]:continue
  for c,w in g[a]:
   nd=d+w
   if nd<dist.get(c,1e9):dist[c]=nd;heapq.heappush(q,(nd,c))
 out[net]={'esd_to_module_track_length_mm':dist[end]}
out['skew_mm']=abs(out['USB_D+']['esd_to_module_track_length_mm']-out['USB_D-']['esd_to_module_track_length_mm']);out['scope']='Shortest routed copper path from ESD IC board-side pins to J1, excludes package and via barrel lengths. Both paths use two through vias.'
print(json.dumps(out,indent=2));(D/'docs/usb-route-lengths.json').open('w').write(json.dumps(out,indent=2)+'\n')
