#!/usr/bin/env python3
"""Reviewed hand-routed two-layer CST blocks. Only replaces this script's copper.
Coordinates describe channel 1; channel 2 is translated 23 mm down.
ADC and FPGA handoff ends intentionally stop short of their destinations.
"""
import json,uuid,math
from pathlib import Path
import pcbnew as p
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'boards/tesla-coil-controller'
b=p.LoadBoard(str(D/'controller.kicad_pcb'));b.SetCopperLayerCount(2)
fps={f.GetReference():f for f in b.GetFootprints()};parts=json.loads((D/'docs/circuit.json').read_text());planfile=ROOT/'tools/hardware/tesla_placement.json';plan=json.loads(planfile.read_text())
v=lambda xy:p.VECTOR2I(p.FromMM(xy[0]),p.FromMM(xy[1]));xy=lambda a:(round(p.ToMM(a.x),6),round(p.ToMM(a.y),6))
uid=lambda i:str(uuid.uuid5(uuid.NAMESPACE_URL,f'bp-tesla-cst-routing/{i}'));owned={uid(i) for i in range(6000)};retired=[]
for t in list(b.GetTracks())+list(b.Zones()):
 if t.m_Uuid.AsString() in owned:retired.append(t);b.Remove(t)
ni={n.GetNetname():n for n in b.GetNetInfo().NetsByNetcode().values()};count=0;records=[]
def move(r,x,y,a):
 f=fps[r];f.SetOrientationDegrees(a);f.SetPosition(v((x,y)));plan['positions'][r]=[x,y,a];parts[r]['position']=[x,y,a]
 if r in plan['reference_positions']:f.Reference().SetPosition(v(plan['reference_positions'][r]));f.Reference().SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T))
def ref2(r):
 import re
 m=re.fullmatch(r'([A-Z]+)(\d+)',r);return m[1]+str(int(m[2])+(200 if m[1] in ['R','C'] else 20))
for r,x,y,a in [('C427',36.5,127.8,90),('C428',36.5,137.3,270),('D43',100,132,180),('R411',97,129,270),('R422',97,135,270),('C413',109,132.95,0),('C425',90.5,132,0)]:
 move(r,x,y,a);move(ref2(r),x,y+23,a)
# Match bypass-pad centerlines to the amplifier supply pins; group feedback
# and the envelope RC by function instead of accommodating the old copper.
for r,x,y,a in [('C401',59.8625,135.7,270),('C402',65,132,0),
                ('C403',75.8625,135.7,270),('C404',81,132,0),
                ('R402',56.5,131.05,0),('R403',57.7,128.1,90),
                ('R406',70,132,0),('R407',76.775,128.4,0),
                ('R408',81,136.5,0),('C400',84,137.45,270),
                ('TP42',79.2,139.5,0),('TP43',84,133.5,0)]:
 move(r,x,y,a);move(ref2(r),x,y+23,a)
move('J4',27.5,39,270);move('J30',27.5,51,270)
for ref,x,y in [('U40',61.5,140.2),('U41',77,141.7),('U60',61.5,163.2),('U61',77,164.7)]:
 plan['reference_positions'][ref]=[x,y]
 fps[ref].Reference().SetPosition(v((x,y)))
# Compact the flying-capacitor/input/output current loops in the shared converter.
for args in [('U44',32,144,0),('C420',32,147,180),('C421',28,144,180),('C422',28.6,140.5,90),('R421',25.4,141.75,180),('C423',26,146,0)]:move(*args)
def pad(r,n):return next(a for a in fps[r].Pads() if a.GetNumber()==str(n))
def pos(r,n):return xy(pad(r,n).GetPosition())
def wire(net,points,width=.25,layer=p.F_Cu):
 global count
 # Each waypoint pair gets a deterministic straight/45 approach, no maze routing.
 pts=[]
 for end in points:
  end=tuple(round(z,6) for z in end)
  if pts:
   a=pts[-1];dx=end[0]-a[0];dy=end[1]-a[1]
   if abs(dx)>1e-6 and abs(dy)>1e-6 and abs(abs(dx)-abs(dy))>1e-6:
    step=min(abs(dx),abs(dy));pts.append((round(a[0]+math.copysign(step,dx),6),round(a[1]+math.copysign(step,dy),6)))
  pts.append(end)
 for a,z in zip(pts,pts[1:]):
  if math.dist(a,z)<1e-5:continue
  t=p.PCB_TRACK(b);t.SetStart(v(a));t.SetEnd(v(z));t.SetWidth(p.FromMM(width));t.SetLayer(layer);t.SetNet(ni[net]);t.SetUuid(p.KIID(uid(count)));b.Add(t);count+=1;records.append(dict(net=net,start=a,end=z,width=width,layer=b.GetLayerName(layer)))
def via(net,pt):
 global count
 t=p.PCB_VIA(b);t.SetPosition(v(pt));t.SetWidth(p.FromMM(.6));t.SetDrill(p.FromMM(.3));t.SetViaType(p.VIATYPE_THROUGH);t.SetLayerPair(p.F_Cu,p.B_Cu);t.SetNet(ni[net]);t.SetUuid(p.KIID(uid(count)));b.Add(t);count+=1
 records.append(dict(net=net,via=pt,diameter=.6,drill=.3))
def link(r,n,points,width=.25,layer=p.F_Cu):wire(pad(r,n).GetNetname(),[pos(r,n)]+points,width,layer)
def ground(r,n,pt):link(r,n,[pt],.3);via('GND',pt)
# Shared inverting charge pump: all switched/flying-capacitor copper stays on top.
link('U44',2,[pos('C421',1)],.4)
link('U44',1,[(30.3,143.05),pos('C422',1)],.4)
link('C422',1,[pos('R421',1)],.4)
link('R421',2,[(24,141.75),(24,144.95),pos('C423',1)],.35)
link('U44',3,[(30,144.95),(30,145.95),pos('C420',2)],.3)
link('U44',5,[(35,143.05),(35,145.8),(33.8,147),pos('C420',1)],.3)
for r,n,pt in [('U44',4,(34.1,144.95)),('C421',2,(25.7,144)),('C422',2,(28.6,138.05)),('C423',2,(26.95,147.5))]:ground(r,n,pt)
# Supply feeds run below signal loops on bottom; no inner-layer copper is used.
link('C421',1,[(28.95,145.5)],.4);via('+5V_ADC',(28.95,145.5))
link('C423',1,[(23,146)],.35);via('-5V_CT',(23,146))
for ch in range(2):
 off=23*ch
 rr=lambda r:ref2(r) if ch else r
 nn=lambda n:n.replace('CT1_','CT2_',1) if ch and n.startswith('CT1_') else n
 P=lambda r,n:pos(rr(r),n)
 T=lambda x,y:(x,y+off)
 def W(n,pts,w=.25,layer=p.F_Cu):wire(nn(n),[T(*a) for a in pts],w,layer)
 def V(n,x,y):via(nn(n),T(x,y))
 def L(r,n,pts,w=.25,layer=p.F_Cu):link(rr(r),n,[T(*a) for a in pts],w,layer)
 def G(r,n,x,y):ground(rr(r),n,T(x,y))
 # Cable pair -> common-mode choke -> permanent burden/TVS.
 L('J40',1,[(38.76,130),(40.175,131.415)],.65)
 L('J40',2,[(38.76,135.08),(40.175,133.665)],.65)
 L('C427',1,[(36.5,130)],.3);G('C427',2,36.5,125.35)
 L('C428',1,[(36.5,135.08)],.3);G('C428',2,36.5,139.65)
 L('R400',1,[(46.0375,134)],.8)
 L('L40',2,[(44.8,131.415),(46.0375,132.6525)],.65)
 L('R401',1,[(46.0375,139.1875),(46.85,140)],.8)
 L('D40',1,[(45,140),(45,142.5),(52.5,142.5),(54,141)],.5)
 L('TP40',1,[(55.05,140),(56.05,140)],.25)
 for r,n,x,y in [('L40',3,43.825,135.5),('R400',2,53.5,129),('R401',2,53.5,134),('D40',2,51.15,138.2),('C429',2,59.5,141)]:G(r,n,x,y)
 # Raw feed on bottom, outside the short rectifier feedback loops.
 L('R400',1,[(46.0375,126)],.5);V('CT1_RAW',46.0375,126)
 W('CT1_RAW',[(46.0375,126),(50.0375,122),(89.55,122),(89.55,130.4)],.3,p.B_Cu)
 L('R402',1,[(55.5875,129.45)]);V('CT1_RAW',55.5875,129.45);W('CT1_RAW',[(55.5875,129.45),(55.5875,122)],.3,p.B_Cu)
 L('R404',1,[(69.0875,124.4)]);V('CT1_RAW',69.0875,124.4);W('CT1_RAW',[(69.0875,124.4),(69.0875,122)],.3,p.B_Cu)
 L('C425',1,[(89.55,130.4)]);V('CT1_RAW',89.55,130.4)
 # Precision half-wave feedback, sum stage, and envelope.
 link(rr('U40'),4,[P('R402',2)])
 L('R403',1,[(57.7,131.05)])
 L('D41',1,[(61.35,127),(59.8,128.55),(59.8,129.85),(58.6,131.05)])
 L('D41',2,[(67.05,127),(67.05,136.6),(66.65,137)])
 L('U40',1,[(63.15,132.95),(63.8,133.6),(63.8,135.65),(65.15,137),(66.65,137)])
 L('D42',2,[(61.5,137)]);V('CT1_HALF',61.5,137)
 L('R403',2,[(57.7,125.6)]);V('CT1_HALF',57.7,125.6)
 W('CT1_HALF',[(57.7,125.6),(61.5,129.4),(61.5,137),(70.5,137),(72,138.5)],.25,p.B_Cu)
 L('R405',1,[(68,129),(68,130.5)]);L('R406',1,[(68,132),(68,130.5)]);V('CT1_HALF',68,130.5)
 W('CT1_HALF',[(68,130.5),(68,137)],.25,p.B_Cu)
 V('CT1_HALF',72,138.5);L('TP41',1,[(72,138.5)])
 L('R404',2,[(72.6,126),(72.6,131.05),(75.8625,131.05)])
 L('R405',2,[(72.6,129)]);L('R406',2,[(71.65,132),(72.6,131.05)])
 L('R407',1,[(75.8625,131.05)])
 L('U41',1,[(79.2,134.0125),(79.2,139.5)]);V('CT1_ABS',79.2,134.0125)
 L('R407',2,[(79.2,128.4)]);V('CT1_ABS',79.2,128.4);W('CT1_ABS',[(79.2,128.4),(79.2,134.0125)],.25,p.B_Cu)
 L('R408',1,[(79.2,136.5)])
 link(rr('R408'),2,[P('C400',1)])
 L('C400',1,[(84,133.5)]);G('C400',2,84,140)
 # Comparator input network and local reference.
 L('C425',2,[(93.0875,132)])
 L('R410',2,[(99.0625,132)])
 L('R411',2,[(97,132)]);L('R422',1,[(97,132)])
 L('R422',1,[(98.2,135.2875),(99.05,136.1375),(99.05,137)])
 W('CT1_PHASE',[(98,132),(98,133.5),(99.95,135.45),(101,135.45),(102,134.45),(102,133.75),(102.8,132.95),(103.8625,132.95)])
 L('R414',2,[(103.0875,125)])
 L('R415',1,[(103.0875,126.5),(104.95,128)])
 L('U42',1,[(102.8,131.05),(102.8,130),(104,128.8),(104.95,128.8),(104.95,128)])
 L('U42',5,[(107,132),(109.0875,129.9125),(109.0875,129.5)])
 L('R416',2,[(112,128.4125),(112,124)])
 for r,n,x,y in [('R422',2,95.5,135.9125),('C410',2,100.95,138.5),('D43',1,100.9375,133.95),('R415',2,106.5,125),('C412',2,101.7,127),('U42',2,102.4,132),('U42',6,106.1375,129.6),('C413',2,111.5,132.95),('C424',2,112.5,140)]:G(r,n,x,y)
 # Direct pin-to-decoupler links. Dedicated local returns connect both ground pours.
 for u,cp,cn in [('U40','C401','C402'),('U41','C403','C404')]:
  link(rr(u),5,[P(cp,1)],.3);link(rr(u),2,[P(cn,1)],.3)
  pu=P(cp,1);pv=(pu[0]-1.6,pu[1]);link(rr(cp),1,[pv],.35);via('+5V_ADC',pv)
  nv=P(cn,1);nv=(nv[0],nv[1]-1.5);link(rr(cn),1,[nv],.3);via('-5V_CT',nv)
  g=P(cp,2);ground(rr(cp),2,(g[0],g[1]+1.5));g=P(cn,2);ground(rr(cn),2,(g[0],g[1]+1.6))
  g=P(u,3);ground(rr(u),3,(g[0]+.3625,g[1]-1.05))
 L('U42',4,[(108.05,132.95)],.3)
 # Branches to bottom supply rails. The shared upstream feeds remain to be routed.
 W('+5V_ADC',[(58.2625,134.75),(58.2625,139.5),(74.2625,139.5),(74.2625,134.75)],.4,p.B_Cu)
 W('-5V_CT',[(64.05,130.5),(64.05,126.2),(80.05,126.2),(80.05,130.5)],.35,p.B_Cu)
 if not ch:W('-5V_CT',[(76.7,126.2),(76.7,143)],.35,p.B_Cu)
 for r,n,x,y in [('R414',1,98.0875,123.5),('R411',1,95.5,128.0875),('D43',2,100.9375,129.55),('C413',1,108.05,134.5),('C424',1,109.05,138.5)]:
  L(r,n,[(x,y)],.3);V('+3V3',x,y)
 W('+3V3',[(95.5,128.0875),(95.5,123.5),(108.05,123.5),(108.05,134.5),(109.05,135.5),(109.05,138.5)],.35,p.B_Cu)
 W('+3V3',[(100.9375,129.55),(100.9375,123.5)],.35,p.B_Cu)
# One +5 V entry from the ADC rail link above; independent short branches supply
# the two sensor rows and the charge pump. Front bridges only cross raw buses.
link('R20',2,[(110.5,85)],.5);via('+5V_ADC',(110.5,85))
wire('+5V_ADC',[(110.5,85),(110.5,116.5),(109,118),(57,118)],.5,p.B_Cu)
via('+5V_ADC',(57,118));wire('+5V_ADC',[(57,118),(57,124)],.5);via('+5V_ADC',(57,124))
wire('+5V_ADC',[(57,124),(57,141.8)],.5,p.B_Cu)
wire('+5V_ADC',[(57,139.5),(58.2625,139.5)],.4,p.B_Cu)
via('+5V_ADC',(57,141.8));wire('+5V_ADC',[(57,141.8),(57,147)],.5);via('+5V_ADC',(57,147))
wire('+5V_ADC',[(57,147),(57,162.5),(58.2625,162.5)],.5,p.B_Cu)
wire('+5V_ADC',[(57,141.2),(37,141.2)],.4,p.B_Cu)
via('+5V_ADC',(37,141.2));wire('+5V_ADC',[(37,141.2),(37,145.8)],.4);via('+5V_ADC',(37,145.8))
wire('+5V_ADC',[(37,145.8),(29.25,145.8),(28.95,145.5)],.4,p.B_Cu)
wire('-5V_CT',[(23,146),(23,143),(76.7,143)],.35,p.B_Cu)
wire('-5V_CT',[(76.7,143),(76.7,143.8)],.35,p.B_Cu);via('-5V_CT',(76.7,143.8));wire('-5V_CT',[(76.7,143.8),(76.7,146.2)],.35);via('-5V_CT',(76.7,146.2));wire('-5V_CT',[(76.7,146.2),(76.7,149.2)],.35,p.B_Cu)
wire('+3V3',[(108.05,123.5),(113.4,128.85),(113.4,141.15),(108.05,146.5)],.35,p.B_Cu)
# Four analog handoffs toward the ADC; deliberately unfinished, with no connector added.
via('CT1_RAW',(84,122));wire('CT1_RAW',[(84,122),(84,119.5)],.25)
wire('CT1_ENVELOPE',[(84,133.5),(85.5,132),(85.5,119.5)],.25)
via('CT2_RAW',(88.5,144.2));wire('CT2_RAW',[(88.5,145),(88.5,144.2)],.25,p.B_Cu);wire('CT2_RAW',[(88.5,144.2),(88.5,119.5)],.25)
wire('CT2_ENVELOPE',[(84,156.5),(85,155.5),(85,145.5),(87,143.5),(87,119.5)],.25)
# Miter isolated 90-degree bends; preserve pads, vias, and every branch/junction.
from collections import defaultdict
nodes=defaultdict(list)
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA) or t.m_Uuid.AsString() not in owned:continue
 for a in [t.GetStart(),t.GetEnd()]:nodes[(t.GetNetCode(),t.GetLayer(),a.x,a.y)].append(t)
allpads=[a for f in fps.values() for a in f.Pads()];vias=[t for t in b.GetTracks() if isinstance(t,p.PCB_VIA)]
miters=0
for (_,layer,nx,ny),tt in nodes.items():
 if len(tt)!=2:continue
 t1,t2=tt
 if t1.GetWidth()!=t2.GetWidth():continue
 node=p.VECTOR2I(nx,ny)
 if any(a.HitTest(node,p.FromMM(.4)) for a in allpads) or any((z.GetPosition()-node).EuclideanNorm()<p.FromMM(.45) for z in vias):continue
 a=t1.GetEnd() if t1.GetStart()==node else t1.GetStart();z=t2.GetEnd() if t2.GetStart()==node else t2.GetStart()
 d1=a-node;d2=z-node
 if not ((d1.x==0 and d2.y==0) or (d1.y==0 and d2.x==0)):continue
 if d1.EuclideanNorm()<p.FromMM(1) or d2.EuclideanNorm()<p.FromMM(1):continue
 # Interior tee intersections are also anchors, even if no segment was split there.
 def distance_to_track(t):
  aa=xy(t.GetStart());zz=xy(t.GetEnd());nn=(p.ToMM(nx),p.ToMM(ny));dx=zz[0]-aa[0];dy=zz[1]-aa[1];ll=dx*dx+dy*dy
  u=max(0,min(1,((nn[0]-aa[0])*dx+(nn[1]-aa[1])*dy)/ll)) if ll else 0
  return math.dist(nn,(aa[0]+u*dx,aa[1]+u*dy))
 if any(t.m_Uuid.AsString() not in [t1.m_Uuid.AsString(),t2.m_Uuid.AsString()] and not isinstance(t,p.PCB_VIA) and t.GetLayer()==layer and distance_to_track(t)<.01 for t in b.GetTracks()):continue
 cut=p.FromMM(.4);e1=node+p.VECTOR2I(int(math.copysign(cut,d1.x)) if d1.x else 0,int(math.copysign(cut,d1.y)) if d1.y else 0);e2=node+p.VECTOR2I(int(math.copysign(cut,d2.x)) if d2.x else 0,int(math.copysign(cut,d2.y)) if d2.y else 0)
 if t1.GetStart()==node:t1.SetStart(e1)
 else:t1.SetEnd(e1)
 if t2.GetStart()==node:t2.SetStart(e2)
 else:t2.SetEnd(e2)
 wire(t1.GetNetname(),[xy(e1),xy(e2)],p.ToMM(t1.GetWidth()),layer);miters+=1
print('Mitered',miters,'isolated corners')
# Local front/back analog ground. External supplies and ADC/FPGA routes remain open.
for layer in [p.F_Cu,p.B_Cu]:
 z=p.ZONE(b);z.SetLayer(layer);z.SetNet(ni['GND']);z.SetLocalClearance(p.FromMM(.2));z.SetPadConnection(p.ZONE_CONNECTION_THERMAL);z.SetThermalReliefGap(p.FromMM(.25));z.SetThermalReliefSpokeWidth(p.FromMM(.3));z.SetMinThickness(p.FromMM(.2));z.SetAssignedPriority(0);poly=z.Outline();poly.NewOutline()
 for pt in [(21,120),(114,120),(114,168.8),(21,168.8)]:poly.Append(*v(pt))
 z.SetUuid(p.KIID(uid(count)));count+=1;b.Add(z)
p.ZONE_FILLER(b).Fill(b.Zones())
p.SaveBoard(str(D/'controller.kicad_pcb'),b)
planfile.write_text(json.dumps(plan,indent=2)+'\n');(D/'docs/circuit.json').write_text(json.dumps(parts,indent=2)+'\n');(D/'docs/cst-routing.json').write_text(json.dumps({'stage':'CST local routing complete; six signal handoffs intentionally unfinished','copper_layers':2,'records':[dict(net=t.GetNetname(),via=xy(t.GetPosition()),diameter=p.ToMM(t.GetWidth()),drill=p.ToMM(t.GetDrillValue())) if isinstance(t,p.PCB_VIA) else dict(net=t.GetNetname(),start=xy(t.GetStart()),end=xy(t.GetEnd()),width=p.ToMM(t.GetWidth()),layer=b.GetLayerName(t.GetLayer())) for t in b.GetTracks() if t.m_Uuid.AsString() in owned]},indent=2)+'\n')
print('Created',count,'CST tracks/vias/zones')
