#!/usr/bin/env python3
"""Manual four-channel AUX input routing on the existing two-layer board.

Run after tesla_route_cst.py and tesla_route_power.py; own UUIDs make reruns safe.
"""
import json, uuid, math
from pathlib import Path
import pcbnew as p
ROOT=Path(__file__).resolve().parents[2]; D=ROOT/'boards/tesla-coil-controller'
b=p.LoadBoard(str(D/'controller.kicad_pcb')); assert b.GetCopperLayerCount()==2
fps={f.GetReference():f for f in b.GetFootprints()}; nets={n.GetNetname():n for n in b.GetNetInfo().NetsByNetcode().values()}
planfile=ROOT/'tools/hardware/tesla_placement.json'; plan=json.loads(planfile.read_text()); parts=json.loads((D/'docs/circuit.json').read_text())
uid=lambda i:str(uuid.uuid5(uuid.NAMESPACE_URL,f'bp-tesla-aux-routing/{i}')); owned={uid(i) for i in range(6000)}; retired=[]; counter=0
for t in list(b.GetTracks()):
 if t.m_Uuid.AsString() in owned: retired.append(t); b.Remove(t)
v=lambda pt:p.VECTOR2I(p.FromMM(pt[0]),p.FromMM(pt[1])); xy=lambda q:(round(p.ToMM(q.x),6),round(p.ToMM(q.y),6))
def move(r,x,y,a):
 f=fps[r]; f.SetOrientationDegrees(a); f.SetPosition(v((x,y))); plan['positions'][r]=[x,y,a]; parts[r]['position']=[x,y,a]
 if r in plan['reference_positions']: f.Reference().SetPosition(v(plan['reference_positions'][r]))
def pad(r,n): return next(q for q in fps[r].Pads() if q.GetNumber()==str(n))
def P(r,n): return xy(pad(r,n).GetPosition())
def wire(net,pts,w=.25,layer=p.F_Cu):
 global counter
 path=[]
 for pt in pts:
  pt=tuple(round(z,6) for z in pt)
  if path:
   a=path[-1]; dx=pt[0]-a[0]; dy=pt[1]-a[1]
   if abs(dx)>1e-6 and abs(dy)>1e-6 and abs(abs(dx)-abs(dy))>1e-6:
    step=min(abs(dx),abs(dy)); path.append((round(a[0]+math.copysign(step,dx),6),round(a[1]+math.copysign(step,dy),6)))
  path.append(pt)
 for a,z in zip(path,path[1:]):
  if math.dist(a,z)<1e-5: continue
  t=p.PCB_TRACK(b); t.SetStart(v(a)); t.SetEnd(v(z)); t.SetWidth(p.FromMM(w)); t.SetLayer(layer); t.SetNet(nets[net]); t.SetUuid(p.KIID(uid(counter))); counter+=1; b.Add(t)
def L(r,n,pts,w=.25,layer=p.F_Cu): wire(pad(r,n).GetNetname(),[P(r,n)]+pts,w,layer)
def via(net,pt):
 global counter
 t=p.PCB_VIA(b); t.SetPosition(v(pt)); t.SetWidth(p.FromMM(.6)); t.SetDrill(p.FromMM(.3)); t.SetViaType(p.VIATYPE_THROUGH); t.SetLayerPair(p.F_Cu,p.B_Cu); t.SetNet(nets[net]); t.SetUuid(p.KIID(uid(counter))); counter+=1; b.Add(t)
def G(r,n,pt): L(r,n,[pt],.3); via('GND',pt)
# Two matched pairs of cells. Raw shunt -> series resistor -> filtered shunt
# and clamp -> non-inverting input are a straight front-copper signal path.
for ch,dx,dy in [(1,0,0),(2,18,0),(3,0,18),(4,18,18)]:
 base=700+10*(ch-1); u=f'U{69+ch}'; clamp=f'D{69+ch}'
 raw=f'AUX{ch}_0_5V'; filt=f'AUX{ch}_FILTERED'; out=f'AUX{ch}_BUFFERED'
 cx=35+dx+(3 if ch in (2,4) else 0); rx=39.68+dx+(1.1 if ch in (2,4) else 0)
 move(f'C{base}',cx,83+dy,90); move(f'R{base+1}',cx,87+dy,270); move(f'R{base}',rx,83.95+dy,0)
 wire(raw,[P(f'C{base}',1),P(f'R{base}',1)])
 wire(raw,[P(f'C{base}',1),P(f'R{base+1}',1)])
 wire(filt,[P(f'R{base}',2),P(f'C{base+1}',1),P(u,3)])
 L(clamp,3,[(45.4+dx,87+dy),(45.4+dx,83.95+dy)])
 # V- bypass alongside the supply pin, outside the sensitive input route.
 move(f'C{base+3}',44.9+dx,80.1+dy,180)
 L(u,2,[(46.6+dx,83+dy),(46.3+dx,82.7+dy),(46.3+dx,80.55+dy),P(f'C{base+3}',1)],.3)
 nv=(45.85+dx,78.5+dy); L(f'C{base+3}',1,[nv],.3); via('-5V_CT',nv)
 G(f'C{base+3}',2,(42.35+dx,78.5+dy))
 # Short local feedback on bottom; both vias outside the amplifier body.
 ov=(47.7+dx,80.95+dy); fv=(51.8+dx,85.1+dy)
 L(u,1,[(47.7+dx,81.8475+dy),ov]); via(out,ov)
 L(u,4,[(51.8+dx,83.95+dy),fv]); via(out,fv)
 wire(out,[ov,(51.8+dx,85.05+dy),fv],.25,p.B_Cu)
# The left pair is direct; the right pair crosses the 12 V trunk once on bottom.
for conn,ch,dy in [('J3',1,0),('J9',3,18)]:
 L(conn,1,[(29.95,83.95+dy),P(f'C{700+10*(ch-1)}',1)])
for conn,ch,dy in [('J8',2,0),('J10',4,18)]:
 net=f'AUX{ch}_0_5V'; a=(53.2,89.5+dy); z=(55.8,89.5+dy)
 L(conn,1,[(30,91+dy),(31.5,89.5+dy),a]); via(net,a); via(net,z)
 wire(net,[a,z],.25,p.B_Cu)
 wire(net,[z,(57.5,89.5+dy),(57.5,85.45+dy),P(f'C{700+10*(ch-1)}',1)])
# Buffered signals cross the two analog supply spines together on the front.
for ch,dy in [(1,0),(3,18)]:
 net=f'AUX{ch}_BUFFERED'; a=(69,88.8) if ch==1 else (71.3,104.5); z=(75.3,a[1])
 trunk=[(51.8,85.1+dy),(53.2,86.5+dy)]+([(69,86.5)] if ch==1 else [])+[a]
 wire(net,trunk,.25,p.B_Cu)
 via(net,a); via(net,z); wire(net,[a,z])
for ch,dy in [(2,0),(4,18)]:
 net=f'AUX{ch}_BUFFERED'; q=(69.8,87.5+dy); a=(71.3,87.5+dy); z=(75.3,87.5+dy)
 if ch==2:
  wire(net,[(69.8,85.1),q,z])
 else:
  wire(net,[(69.8,85.1+dy),q]); via(net,q)
  wire(net,[q,a],.25,p.B_Cu); via(net,a); via(net,z); wire(net,[a,z])
for ch,points,end in [
 (1,[(75.3,88.8),(77,88.8),(78,89.8)],(78,95.2)),
 (2,[(75.3,87.5),(76.5,88.7)],(76.5,99)),
 (3,[(75.3,104.5),(77,104.5),(78,103.5)],(78,102.8)),
 (4,[(75.3,105.5)],(76.4,106.6))]:
 net=f'AUX{ch}_BUFFERED'; wire(net,points+[end],.25,p.F_Cu if ch==2 else p.B_Cu)
 if ch!=2:via(net,end)
 wire(net,[end,P(f'R{ch+4}',1)])
# ADC RC filters stay near the analog pin row. Bottom fan-in keeps the four
# front-pad escapes straight and avoids the intervening ADC ground pins.
for ch,y in [(5,95.2),(6,99),(7,102.8),(8,106.6)]:
 net=f'ADC_CH{ch}'; wire(net,[P(f'R{ch}',2),P(f'C{ch+10}',1)])
 via(net,(82,y)); iv=(85.65,96.25+ch-5); via(net,iv)
 paths={5:[(82,y),(84.6,y),iv],6:[(82,y),(83.75,97.25),iv],7:[(82,y),(83.2,101.6),(83.2,100.7),iv],8:[(82,y),(84.3,104.3),(84.3,100.6),iv]}
 wire(net,paths[ch],.25,p.B_Cu); wire(net,[iv,P('U1',57+2*(ch-5))],.2)
 G(f'C{ch+10}',2,(81.9,y+1.9))
# Complete the negative rail from the existing CST distribution. One front
# bridge crosses the +5 V CST supply below the AUX section.
for dy in [0,18]:
 if dy==0:wire('-5V_CT',[(45.85,77.4),(74.4,77.4)],.4,p.B_Cu)
 else:
  wire('-5V_CT',[(45.85,95.4),(71.3,95.4)],.4,p.B_Cu)
  via('-5V_CT',(71.3,95.4));via('-5V_CT',(73.3,95.4));wire('-5V_CT',[(71.3,95.4),(73.3,95.4)],.4)
  wire('-5V_CT',[(73.3,95.4),(74.4,95.4)],.4,p.B_Cu)
 for x in [45.85,63.85]:wire('-5V_CT',[(x,78.5+dy),(x,77.4+dy)],.4,p.B_Cu)
wire('-5V_CT',[(74.4,77.4),(74.4,82.8)],.4,p.B_Cu)
wire('-5V_CT',[(74.4,85.2),(74.4,116)],.4,p.B_Cu)
via('-5V_CT',(74.4,82.8)); via('-5V_CT',(74.4,85.2)); wire('-5V_CT',[(74.4,82.8),(74.4,85.2)],.4)
via('-5V_CT',(74.4,116)); via('-5V_CT',(74.4,124.5))
wire('-5V_CT',[(74.4,116),(74.4,124.5)],.4)
wire('-5V_CT',[(74.4,124.5),(76.7,126.8)],.4,p.B_Cu)
L('C741',1,[(68.05,113)],.4); via('-5V_CT',(68.05,113))
wire('-5V_CT',[(68.05,113),(70,114.95),(74.4,114.95)],.4,p.B_Cu)
p.ZONE_FILLER(b).Fill(b.Zones()); p.SaveBoard(str(D/'controller.kicad_pcb'),b)
planfile.write_text(json.dumps(plan,indent=2)+'\n'); (D/'docs/circuit.json').write_text(json.dumps(parts,indent=2)+'\n')
print('AUX routing created',counter,'items')
