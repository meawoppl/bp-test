#!/usr/bin/env python3
"""Historical display-bus construction; baseline guard prevents overwriting later layout.
After replay regenerate schematic, export netlist, run calibrator_sync and refill/DRC.
"""
import pcbnew as p,json,pathlib,math
import subprocess,sys,hashlib
if '--apply' not in sys.argv:raise SystemExit('Historical baseline-only reroute. Use --apply only on bd7a337 PCB state.')
base='bd7a337'; root=pathlib.Path(__file__).resolve().parents[2]
import os
os.chdir(root)
d=pathlib.Path('boards/gps-time-calibrator');t=pathlib.Path('tmp/calibrator-display-bus');t.mkdir(parents=True,exist_ok=True)
baseline=subprocess.check_output(['git','show',base+':'+str(d/'calibrator.kicad_pcb')])
assert (d/'calibrator.kicad_pcb').read_bytes()==baseline, 'Refusing to overwrite newer PCB edits'
for name in ['calibrator.kicad_pcb','calibrator.kicad_pro','calibrator.kicad_dru','docs/circuit.json','docs/display-map.json']:
 dest={'docs/circuit.json':'circuit-start.json','docs/display-map.json':'display-start.json'}.get(name,name.replace('calibrator.','start.'))
 (t/dest).write_bytes(subprocess.check_output(['git','show',base+':'+str(d/name)]))
D=pathlib.Path('boards/gps-time-calibrator');T=pathlib.Path('tmp/calibrator-display-bus');b=p.LoadBoard(str(T/'start.kicad_pcb'));parts=json.loads((T/'circuit-start.json').read_text());display=json.loads((T/'display-start.json').read_text());mm=p.FromMM
fps={f.GetReference():f for f in b.GetFootprints()};xy=lambda v:(p.ToMM(v.x),p.ToMM(v.y))
def pad(r,n):return next(q for q in fps[r].Pads() if q.GetNumber()==str(n))
def pt(r,n):return xy(pad(r,n).GetPosition())
def net(n):
 q=b.FindNet(n)
 if q is None or q.GetNetCode()<0:q=p.NETINFO_ITEM(b,n);b.Add(q)
 return q
def line(n,pts,w=.2,layer=p.F_Cu):
 for a,c in zip(pts,pts[1:]):
  if math.dist(a,c)<1e-6:continue
  t=p.PCB_TRACK(b);t.SetStart(p.VECTOR2I(*map(mm,a)));t.SetEnd(p.VECTOR2I(*map(mm,c)));t.SetLayer(layer);t.SetWidth(mm(w));t.SetNet(net(n));b.Add(t)
def via(n,at):
 t=p.PCB_VIA(b);t.SetPosition(p.VECTOR2I(*map(mm,at)));t.SetWidth(mm(.5));t.SetDrill(mm(.25));t.SetLayerPair(p.F_Cu,p.B_Cu);t.SetViaType(p.VIATYPE_THROUGH);t.SetNet(net(n));b.Add(t)
def move(r,x,y,ang):fps[r].SetPosition(p.VECTOR2I(mm(x),mm(y)));fps[r].SetOrientationDegrees(ang);parts[r]['position']=[x,y,ang]
oldnets={r['signal'] for r in display}|{f'DRIVE{i}' for i in range(16)}|{f'GATE{i}' for i in range(16)}
for t in list(b.GetTracks()):
 a,c=xy(t.GetStart()),xy(t.GetEnd());n=t.GetNetname()
 if n in oldnets or (n=='+3V3_LOGIC' and max(a[0],c[0])<130 and max(a[1],c[1])<32) or (n=='GND' and ((30<a[0]<126 and max(a[1],c[1])<17) or (48<a[0]<66 and 18<a[1]<31) or (96<a[0]<114 and 18<a[1]<31))):b.RemoveNative(t)
for i in range(141,156):b.RemoveNative(fps.pop(f'R{i}'));del parts[f'R{i}']
parts['R140'].update(value='10k',mpn='0805W8F1002T5E',lcsc='C17414',pins={'1':'+3V3_LOGIC','2':'FPGA_IOT_44B'})
fps['R140'].SetValue('10k');fps['R140'].SetField('MPN','0805W8F1002T5E');fps['R140'].SetField('LCSC','C17414')
move('R140',115,23,0)
for ref,cx in [('U3',53.65),('U4',101.65)]:
 move(ref,cx,24,270);parts[ref]['pins']['1']='FPGA_IOT_44B';parts[ref]['pins']['19']='GND'
move('C4',59.5,26.8625,0);move('C5',107.5,26.8625,0)
parts['J2']['pins']['9']='FPGA_IOT_37A';parts['J2']['pins']['24']=None;parts['J2']['pins']['33']='FPGA_IOT_44B'
contacts=[21,20,19,17,16,15,14,12,11,10,9,7,6,5,4,2]
# Lowest lane goes to the rightmost column; optical bit labels stay 15..0 left-to-right.
for i,contact in enumerate(contacts):
 ref='U4' if i<8 else 'U3';k=i%8;bit=i;sig=parts['J2']['pins'][str(contact)]
 parts[ref]['pins'][str(2+k)]=sig;parts[ref]['pins'][str(18-k)]=f'DRIVE{bit}'
 row=next(r for r in display if r['bit']==bit);row['signal']=sig;row['module_contact']=contact;row['buffer']=ref;row['buffer_input_pin']=2+k;row['buffer_output_pin']=18-k
for r,c in parts.items():
 for n,sig in c['pins'].items():
  q=pad(r,n)
  if sig is not None:q.SetNet(net(sig))
  elif r=='J2' and n=='24':q.SetNet(net('unconnected-(J2-Pad24)'))
# Output fanouts run on front copper, ordered directly toward the gate resistor row.
for bank,ref in enumerate(['U3','U4']):
 for col in range(8):
  pin=11+col;r=f'R{100+bank*8+col}';x,y=pt(ref,pin);xx,yy=pt(r,1);n=pad(ref,pin).GetNetname();assert n==pad(r,1).GetNetname()
  lane=27.9+.5*min(col,7-col)
  if xx<x:pts=[(x,y),(x,lane),(xx+1,lane),(xx,lane+1),(xx,yy)]
  else:pts=[(x,y),(x,lane),(xx-1,lane),(xx,lane+1),(xx,yy)]
  line(n,pts,.25)
# Preserve short local gate resistor / pulldown / MOSFET net intent with clean direct links.
for col in range(16):
 r=f'R{100+col}';q=f'Q{1+col}';rp=f'R{120+col}';x,y=pt(r,2);gx,gy=pt(q,1);move(rp,x+3,36.15,90)
 line(pad(r,2).GetNetname(),[(x,y),(x,35.2),(gx,36.15),(gx,gy),pt(rp,1)],.25)
# Top-side bus: parallel ordered turns, with no intermediate layer changes for 15 lanes.
for i,contact in enumerate(contacts):
 ref='U4' if i<8 else 'U3';pin=2+i%8;n=pad(ref,pin).GetNetname();tx,ty=pt(ref,pin);lane=18.5-.4*i
 x,y=pt('J2',contact)
 if contact==21:
  line(n,[(x,y),(x,51.4),(150.6,52.0)],.15);via(n,(150.6,52.0));via(n,(149.6,46.9));line(n,[(150.6,52.0),(149.6,51.0),(149.6,46.9)],.2,p.B_Cu);x=149.6;y=46.9
 # diagonal first, before the mounting-hole exclusion; common vertical corridor at x129..138
 line(n,[(x,y),(x,46.9),(x-20,26.9),(x-20,lane+1),(x-21,lane),(tx+1,lane),(tx,lane+1),(tx,ty)],.15 if contact!=21 else .2)
# Local supply cap immediately outside the VCC end, and plane tap.
for ref,c in [('U3','C4'),('U4','C5')]:
 line('+3V3_LOGIC',[pt(ref,20),pt(c,1)],.35);x,y=pt(c,1);line('+3V3_LOGIC',[(x,y),(x,y-1.5)],.35);via('+3V3_LOGIC',(x,y-1.5))
# Rebuild the logic supply trunk on the inner signal layer.
for t in list(b.GetTracks()):
 if t.GetNetname()=='+3V3_LOGIC' and t.GetLayer()==p.In2_Cu and xy(t.GetStart())[1]==18.3:b.RemoveNative(t)
line('+3V3_LOGIC',[(58.55,25.3625),(106.55,25.3625),(125.7625,25.3625),(132,31.6)],.5,p.In2_Cu)
line('+3V3_LOGIC',[pt('R140',1),(114.0875,25.3625)],.35);via('+3V3_LOGIC',(114.0875,25.3625))
# Shared active-low OE uses the back layer to leave the display bus uninterrupted.
for ref in ['U3','U4']:
 x,y=pt(ref,1);line('FPGA_IOT_44B',[(x,y),(x,19.85)],.2);via('FPGA_IOT_44B',(x,19.85))
 line('FPGA_IOT_44B',[(x,19.85),(x+2.15,22)],.2,p.B_Cu)
 gx,gy=pt(ref,19);line('GND',[(gx,gy),(gx,25.5),(gx+.9,24.6),(gx+1.575,24.6)],.2);via('GND',(gx+1.575,24.6))
 pad(ref,19).SetThermalSpokeAngleDegrees(45);pad(ref,19).SetThermalGap(mm(.15));pad(ref,19).SetLocalThermalSpokeWidthOverride(mm(.15))
line('FPGA_IOT_44B',[(58.725,22),(115.9125,22)],.2,p.B_Cu)
line('FPGA_IOT_44B',[pt('R140',2),(115.9125,21.5)],.2);via('FPGA_IOT_44B',(115.9125,21.5));line('FPGA_IOT_44B',[(115.9125,21.5),(115.9125,22),(144,22),(147,25),(147,54),(156.6,54),(156.6,52.2)],.2,p.B_Cu)
line('FPGA_IOT_44B',[pt('J2',33),(156,51.6),(156.6,52.2)],.15);via('FPGA_IOT_44B',(156.6,52.2))
(D/'docs/circuit.json').write_text(json.dumps(parts,indent=2)+'\n');(D/'docs/display-map.json').write_text(json.dumps(display,indent=2)+'\n');p.SaveBoard(str(D/'calibrator.kicad_pcb'),b)
