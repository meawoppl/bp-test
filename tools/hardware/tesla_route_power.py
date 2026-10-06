#!/usr/bin/env python3
"""Manual two-layer +5 V/+12 V distribution, preserving existing CST/GDT copper."""
import json,uuid,math
from pathlib import Path
import pcbnew as p
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'boards/tesla-coil-controller'
b=p.LoadBoard(str(D/'controller.kicad_pcb'));assert b.GetCopperLayerCount()==2
fps={f.GetReference():f for f in b.GetFootprints()};nets={n.GetNetname():n for n in b.GetNetInfo().NetsByNetcode().values()}
planfile=ROOT/'tools/hardware/tesla_placement.json';plan=json.loads(planfile.read_text());parts=json.loads((D/'docs/circuit.json').read_text())
uid=lambda i:str(uuid.uuid5(uuid.NAMESPACE_URL,f'bp-tesla-power-routing/{i}'));owned={uid(i) for i in range(6000)};retired=[];counter=0
for t in list(b.GetTracks())+list(b.Zones()):
 if t.m_Uuid.AsString() in owned:retired.append(t);b.Remove(t)
v=lambda pt:p.VECTOR2I(p.FromMM(pt[0]),p.FromMM(pt[1]));xy=lambda q:(round(p.ToMM(q.x),6),round(p.ToMM(q.y),6))
def move(r,x,y,a):
 f=fps[r];f.SetOrientationDegrees(a);f.SetPosition(v((x,y)));plan['positions'][r]=[x,y,a];parts[r]['position']=[x,y,a]
 if r in plan['reference_positions']:f.Reference().SetPosition(v(plan['reference_positions'][r]))
def pad(r,n):return next(q for q in fps[r].Pads() if q.GetNumber()==str(n))
def P(r,n):return xy(pad(r,n).GetPosition())
def wire(net,pts,w=.4,layer=p.F_Cu):
 global counter
 path=[]
 for pt in pts:
  pt=tuple(round(z,6) for z in pt)
  if path:
   a=path[-1];dx=pt[0]-a[0];dy=pt[1]-a[1]
   if abs(dx)>1e-6 and abs(dy)>1e-6 and abs(abs(dx)-abs(dy))>1e-6:
    step=min(abs(dx),abs(dy));path.append((round(a[0]+math.copysign(step,dx),6),round(a[1]+math.copysign(step,dy),6)))
  path.append(pt)
 for a,z in zip(path,path[1:]):
  if math.dist(a,z)<1e-5:continue
  t=p.PCB_TRACK(b);t.SetStart(v(a));t.SetEnd(v(z));t.SetWidth(p.FromMM(w));t.SetLayer(layer);t.SetNet(nets[net]);t.SetUuid(p.KIID(uid(counter)));counter+=1;b.Add(t)
def L(r,n,pts,w=.4,layer=p.F_Cu):wire(pad(r,n).GetNetname(),[P(r,n)]+pts,w,layer)
def via(net,pt):
 global counter
 t=p.PCB_VIA(b);t.SetPosition(v(pt));t.SetWidth(p.FromMM(.6));t.SetDrill(p.FromMM(.3));t.SetViaType(p.VIATYPE_THROUGH);t.SetLayerPair(p.F_Cu,p.B_Cu);t.SetNet(nets[net]);t.SetUuid(p.KIID(uid(counter)));counter+=1;b.Add(t)
def G(r,n,pt,w=.4):L(r,n,[pt],w);via('GND',pt)
# Output banks below their regulators. Short wide rail joins each bank before
# leaving the supply block; feedback components keep their original netlist.
for idx,off,net in [(30,0,'+12V_BIAS'),(31,33,'VIN_5V')]:
 for k,x in enumerate([38.7,43.2,47.7]):move(f'C{idx*10+4+k}',x+off,70.5,270)
 L(f'U{idx}',7,[(35.34+off,67.3),(37.065+off,69.025),(47.7+off,69.025)],1.0)
 for k,x in enumerate([38.7,43.2,47.7]):
  r=f'C{idx*10+4+k}';G(r,2,(x+off,73.575) if k==2 else (x+off+2.15,71.975),.6)
 L(f'C{idx*10+1}',1,[(34.05+off,68.59),(35.34+off,67.3)],.3)
 L(f'R{idx*10}',1,[(28.5+off,70),(28.5+off,68.59),(34.05+off,68.59)],.3)
# +12 V front trunk crosses the board below the supply and daughterboard blocks.
wire('+12V_BIAS',[(47.7,69.025),(50,69.025),(50,74.5),(51,75.5),(115,75.5),(116,74.5)],.8);via('+12V_BIAS',(116,74.5))
wire('+12V_BIAS',[(116,64),(116,119),(154.2,119)],.8,p.B_Cu)
wire('+12V_BIAS',[(116,64),(154.2,64)],.8,p.B_Cu)
# Input resistance keeps analog buffer supply branch separate from gate drivers.
wire('+12V_BIAS',[(54.5,75.5),(54.5,110),P('R740',1)],.5)
# Driver bypasses: aligned VDD pads, two caps in parallel, local return vias.
for u,cp,bulk,dx,dy in [('U51','C521','C522',0,0),('U52','C524','C525',18,0),('U53','C561','C562',0,55),('U54','C564','C565',18,55)]:
 move(cp,138.75+dx,71.025+dy,0);move(bulk,138.75+dx,67.5+dy,0)
 L(u,1,[P(cp,1)],.5);L(cp,1,[P(bulk,1)],.5)
 feed=(136.2+dx,67.5+dy);L(bulk,1,[feed],.5);via('+12V_BIAS',feed)
 wire('+12V_BIAS',[feed,(136.2+dx,64+dy)],.6,p.B_Cu)
 G(cp,2,(141.3+dx,71.025+dy));G(bulk,2,(141.3+dx,67.5+dy));G(u,7,(134.635+dx,77.6+dy),.5)
# Rail indicator, picked off the driver-side distribution spine.
L('R801',1,[(147,39.9),(146,40.9),(146,41.1)],.3);via('+12V_BIAS',(146,41.1))
wire('+12V_BIAS',[(116,64),(116,44.3),(117,43.3),(145,43.3),(146,42.3),(146,41.1)],.5,p.B_Cu)
# +5 V bank -> module, USB service header, status indicator and ADC regulator.
wire('VIN_5V',[(80.7,69.025),(84,69.025),(84,73.5)],1.0);via('VIN_5V',(84,73.5))
wire('VIN_5V',[(84,73.5),(90,67.5),(90,40.5),(91,39.5),(150,39.5),(150,40.5)],1.0,p.B_Cu)
for n in [1,2,3,4]:L('J1',n,[(P('J1',n)[0],39.5)],.18)
wire('VIN_5V',[(105.6,39.5),(109,39.5)],.5);via('VIN_5V',(109,39.5))
# J5 is now self-powered USB-C; never connect USB VBUS to VIN_5V.
# Current USB copper is replayed by tesla_route_reviewed.py.
L('R802',1,[(150,40.5)],.3);via('VIN_5V',(150,40.5))
wire('VIN_5V',[(84,73.5),(89,78.5),(104,78.5),(107.0875,81.5875),(107.0875,83.0)],.8,p.B_Cu)
via('VIN_5V',(107.0875,83.0));L('R20',1,[(107.0875,83.0)],.5)
move('C20',104,90.05,180)
L('R20',1,[(105.2,85),(105.2,90.05)],.5)
L('U2',1,[P('C20',1)],.4)
L('U2',3,[(104.95,91.95),P('C20',1)],.3)
G('C20',2,(101.45,90.05));G('U2',2,(105.8,91),.3)
# ADC local bypass row, leaving room for reference and internal regulator caps.
for r,x,y,a in [('C4',89.25,87.4,90),('C9',91.25,82.5,90),('C8',91.5,87.4,90),('C7',93.75,82.5,90),('C2',94.5,87.4,90),('C3',96.75,87.4,90),('C6',99,87.4,90),('C1',89.25,104.6,270)]:move(r,x,y,a)
wire('+5V_ADC',[(110.5,85),(109.5,84),(86.4,84),(86.4,83.75)],.6,p.B_Cu)
L('C10',1,[(86.4,83.75)],.5);via('+5V_ADC',(86.4,83.75));G('C10',2,(88,80.25))
for cap,icpin,end in [('C4',48,(89.25,89.15)),('C1',1,(89.25,102.85))]:
 L('U1',icpin,[end],.2);L(cap,1,[end],.3)
 q=P(cap,1);pt=(q[0]-1.6,q[1]);L(cap,1,[pt],.4);via('+5V_ADC',pt)
 g=P(cap,2);G(cap,2,(g[0],g[1]-1.6) if cap=='C4' else (g[0]-1.6,g[1]))
wire('+5V_ADC',[(87.65,103.65),(87.65,84)],.5,p.B_Cu)
for pin in [37,38]:
 x,y=P('U1',pin);L('U1',pin,[(x,89.6),(94.5,89.35)],.2)
L('C2',1,[(94.5,89.35)],.3);L('C3',1,[P('C2',1)],.4)
L('C2',1,[(92.9,88.35)],.4);via('+5V_ADC',(92.9,88.35));wire('+5V_ADC',[(92.9,88.35),(92.9,84)],.5,p.B_Cu)
for r in ['C2','C3']:
 x,y=P(r,2);G(r,2,(x,y-1.6))
# Four AUX rail clamps. Buses are on bottom, with one straight front bridge
# between rows so the filtered +12 V branch can cross on the back.
for r,dy in [('D70',0),('D71',0),('D72',18),('D73',18)]:
 x,y=P(r,2);pt=(x-1.6,y);L(r,2,[pt],.3);via('+5V_ADC',pt);wire('+5V_ADC',[pt,(pt[0],90.5+dy)],.4,p.B_Cu)
wire('+5V_ADC',[(41.0425,90.5),(70.5,90.5),(70.5,84),(86.4,84)],.5,p.B_Cu)
wire('+5V_ADC',[(41.0425,108.5),(70.5,108.5)],.5,p.B_Cu)
for y in [90.5,108.5]:via('+5V_ADC',(70.5,y))
wire('+5V_ADC',[(70.5,90.5),(70.5,108.5)],.5)
# Filtered 12 V rail: local cap at each amplifier's V+ pin, and branch bulk cap.
L('R740',2,[P('C740',1)],.4);L('C740',1,[(62.05,111.6)],.4);via('+12V_AUX',(62.05,111.6));G('C740',2,(65.55,110))
wire('+12V_AUX',[(62.05,111.6),(71,111.6),(72,110.6),(72,85.2)],.5,p.B_Cu)
via('+12V_AUX',(72,85.2));wire('+12V_AUX',[(72,85.2),(72,82.8)],.5);via('+12V_AUX',(72,82.8))
wire('+12V_AUX',[(72,82.8),(72,80.25),(48.5775,80.25)],.5,p.B_Cu)
wire('+12V_AUX',[(72,98.25),(48.5775,98.25)],.5,p.B_Cu)
for u,cap in [('U70','C702'),('U71','C712'),('U72','C722'),('U73','C732')]:
 x,y=P(u,5);move(cap,x,y-2.75,90);L(u,5,[P(cap,1)],.3)
 q=P(cap,1);pt=(q[0]-1.6,q[1]);L(cap,1,[pt],.4);via('+12V_AUX',pt)
 g=P(cap,2);G(cap,2,(g[0]+1.6,g[1]))
# Miter only simple bends. Pads, vias and interior branch points are anchors.
from collections import defaultdict
nodes=defaultdict(list)
local=[t for t in b.GetTracks() if t.m_Uuid.AsString() in owned and not isinstance(t,p.PCB_VIA)]
allpads=[a for f in fps.values() for a in f.Pads()];allvias=[t for t in b.GetTracks() if isinstance(t,p.PCB_VIA)]
for t in local:
 for q in [t.GetStart(),t.GetEnd()]:nodes[(t.GetNetCode(),t.GetLayer(),q.x,q.y)].append(t)
for (_,layer,nx,ny),tt in nodes.items():
 if len(tt)!=2 or tt[0].GetWidth()!=tt[1].GetWidth():continue
 node=p.VECTOR2I(nx,ny)
 if any(a.HitTest(node,p.FromMM(.6)) for a in allpads) or any((a.GetPosition()-node).EuclideanNorm()<p.FromMM(.65) for a in allvias):continue
 t1,t2=tt;a=t1.GetEnd() if t1.GetStart()==node else t1.GetStart();z=t2.GetEnd() if t2.GetStart()==node else t2.GetStart();d1=a-node;d2=z-node
 if not ((d1.x==0 and d2.y==0) or (d1.y==0 and d2.x==0)):continue
 if min(d1.EuclideanNorm(),d2.EuclideanNorm())<p.FromMM(1.5):continue
 def hits(t):
  aa,zz=xy(t.GetStart()),xy(t.GetEnd());q=xy(node);dx=zz[0]-aa[0];dy=zz[1]-aa[1];ll=dx*dx+dy*dy
  u=max(0,min(1,((q[0]-aa[0])*dx+(q[1]-aa[1])*dy)/ll)) if ll else 0
  return math.dist(q,(aa[0]+u*dx,aa[1]+u*dy))<.01
 if any(t.m_Uuid.AsString() not in [t1.m_Uuid.AsString(),t2.m_Uuid.AsString()] and not isinstance(t,p.PCB_VIA) and t.GetLayer()==layer and hits(t) for t in b.GetTracks()):continue
 cut=p.FromMM(.5);e1=node+p.VECTOR2I(int(math.copysign(cut,d1.x)) if d1.x else 0,int(math.copysign(cut,d1.y)) if d1.y else 0);e2=node+p.VECTOR2I(int(math.copysign(cut,d2.x)) if d2.x else 0,int(math.copysign(cut,d2.y)) if d2.y else 0)
 if t1.GetStart()==node:t1.SetStart(e1)
 else:t1.SetEnd(e1)
 if t2.GetStart()==node:t2.SetStart(e2)
 else:t2.SetEnd(e2)
 wire(t1.GetNetname(),[xy(e1),xy(e2)],p.ToMM(t1.GetWidth()),layer)
# Extend the original ground zones to provide continuous board-wide returns.
# Re-run this after the CST generator, which restores its local-only outlines.
for layer in [p.F_Cu,p.B_Cu]:
 z=next(z for z in b.Zones() if z.GetLayer()==layer and z.GetNetname()=='GND');poly=z.Outline();poly.RemoveAllContours();poly.NewOutline()
 for q in [(20.75,27.95),(183.05,27.95),(183.05,169.05),(20.75,169.05)]:poly.Append(*v(q))
p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(D/'controller.kicad_pcb'),b)
planfile.write_text(json.dumps(plan,indent=2)+'\n');(D/'docs/circuit.json').write_text(json.dumps(parts,indent=2)+'\n')
print('Power routing created',counter,'items')
