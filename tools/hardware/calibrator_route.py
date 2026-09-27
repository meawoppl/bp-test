#!/usr/bin/env python3
"""Deterministic local optical/power routing; preserve continuous inner ground plane."""
import sys
if '--rebuild-unrouted' not in sys.argv:
 raise SystemExit('Historical construction step: requires --rebuild-unrouted; will overwrite routed work. Use calibrator_export.py for deliverables.')

from pathlib import Path
import pcbnew as p,json,math
R=Path(__file__).resolve().parents[2];D=R/'boards/gps-time-calibrator';b=p.LoadBoard(str(D/'calibrator.kicad_pcb'));fp={f.GetReference():f for f in b.GetFootprints()};mm=p.FromMM;v=lambda x,y:p.VECTOR2I(mm(x),mm(y));xy=lambda a:(p.ToMM(a.x),p.ToMM(a.y))
def pad(r,n):return next(a for a in fp[r].Pads() if a.GetNumber()==str(n))
def pos(r,n):return xy(pad(r,n).GetPosition())
def route(n,pts,layer=p.F_Cu,width=.25):
 for a,z in zip(pts,pts[1:]):
  if math.dist(a,z)<1e-6:continue
  t=p.PCB_TRACK(b);t.SetNet(b.FindNet(n));t.SetStart(v(*a));t.SetEnd(v(*z));t.SetLayer(layer);t.SetWidth(mm(width));b.Add(t)
def via(n,a):
 t=p.PCB_VIA(b);t.SetPosition(v(*a));t.SetWidth(mm(.5));t.SetDrill(mm(.25));t.SetViaType(p.VIATYPE_THROUGH);t.SetLayerPair(p.F_Cu,p.B_Cu);t.SetNet(b.FindNet(n));b.Add(t)
def stub(r,n,dx,dy,w=.25):
 a=pos(r,n);z=(a[0]+dx,a[1]+dy);nn=pad(r,n).GetNetname();route(nn,[a,z],width=w);via(nn,z);return z
for t in list(b.GetTracks()):b.RemoveNative(t)
for z in list(b.Zones()):b.RemoveNative(z)
for col in range(16):
 x=32+6*col;bit=15-col;nn=f'LED_K{bit}';q='Q'+str(col+1);rg='R'+str(100+col);rp='R'+str(120+col)
 # One continuous cathode spine per column with equal short branch stubs.
 a=pos(q,3);busx=x-2.2;route(nn,[a,(x,40),(busx,42.2),(busx,82.5)],width=.4)
 for row in range(4):
  idx=row*16+col;dd='D'+str(10+idx);rr='R'+str(10+idx)
  z=pos(dd,1);route(nn,[(busx,z[1]),z],width=.3)
  route(pad(dd,2).GetNetname(),[pos(dd,2),pos(rr,2)],width=.3)
  stub(rr,1,0,1.2,.3)
 # Local decoupling connects directly to planes, not through long narrow daisy-chain traces.
 for cr in ['C'+str(20+col),'C'+str(40+col)]:
  stub(cr,1,1.25 if int(cr[1:])<40 else 0,0 if int(cr[1:])<40 else 1.25,.3);stub(cr,2,1.25 if int(cr[1:])<40 else 0,0 if int(cr[1:])<40 else 1.25,.3)
 stub(q,2,0,-1.25,.3)
 a=pos(rg,2);z=pos(q,1);route(f'GATE{bit}',[a,(a[0],z[1]-.95),z],width=.25)
 a=pos(rp,1);route(f'GATE{bit}',[z,(a[0],z[1]),a],width=.25)
 stub(rp,2,1.1,0)
 # Gate drive endpoints and FPGA input bias endpoints for residual routing.
 stub(rg,1,0,-1.2)
 stub('R'+str(140+col),1,0,1.2)
 stub('R'+str(140+col),2,0,-1.2)
# Each buffer VCC and ground pad has a local escape; capacitor within ~2 mm of package.
for ref,cap in [('U3','C4'),('U4','C5')]:
 for n in [1,19,10,20]:
  a=pos(ref,n);center=xy(fp[ref].GetPosition());dy=1.2 if a[1]>center[1] else -1.2;stub(ref,n,0,dy,.2)
 for n in [1,2]:stub(cap,n,1.3,0)
# Ground and VIN plane connections for remaining power passives and ICs.
for ref,f in fp.items():
 if ref in ['U3','U4'] or ref.startswith('Q') or (ref.startswith('C') and 20<=int(ref[1:])<56) or (ref.startswith('R') and 10<=int(ref[1:])<156):continue
 # These remaining local connections are deliberately left for detailed fanout next.
# Planes: ground immediately below every signal layer; inner 5 V supplies the repeated loads.
for layer,n in [(p.F_Cu,'GND'),(p.In1_Cu,'GND'),(p.In2_Cu,'VIN_5V'),(p.B_Cu,'GND')]:
 z=p.ZONE(b);z.SetLayer(layer);z.SetNet(b.FindNet(n));z.SetLocalClearance(mm(.2));z.SetThermalReliefGap(mm(.2));z.SetThermalReliefSpokeWidth(mm(.3));z.SetPadConnection(p.ZONE_CONNECTION_THERMAL);z.SetMinThickness(mm(.15));z.Outline().NewOutline()
 for a in [(20.5,10.5),(199.5,10.5),(199.5,109.5),(20.5,109.5)]:z.Outline().Append(*v(*a))
 b.Add(z)
p.SaveBoard(str(D/'calibrator.kicad_pcb'),b)
print('Optical branches and local decoupling routed')
