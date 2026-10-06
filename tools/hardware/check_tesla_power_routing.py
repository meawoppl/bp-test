#!/usr/bin/env python3
"""Native source-to-load, bypass-return and copper-geometry audit of positive rails."""
import pcbnew as p
import json,math,uuid,hashlib
from pathlib import Path
D=Path(__file__).resolve().parents[2]/'boards/tesla-coil-controller'
b=p.LoadBoard(str(D/'controller.kicad_pcb'));b.BuildConnectivity();conn=b.GetConnectivity();fps={f.GetReference():f for f in b.GetFootprints()}
def pad(ref,pin):return next(a for a in fps[ref].Pads() if a.GetNumber()==str(pin))
def cluster(a):return {x.m_Uuid.AsString() for x in conn.GetConnectedItems(a)}|{a.m_Uuid.AsString()}
xy=lambda a:(p.ToMM(a.x),p.ToMM(a.y))
rails=[];failures=[]
for net,ref,pin in [('VIN_5V','U31',7),('+5V_ADC','R20',2),('+12V_BIAS','U30',7),('+12V_AUX','R740',2),('+3V3','U2',5)]:
 source=pad(ref,pin);assert source.GetNetname()==net;ids=cluster(source)
 pp=[(f,a) for f in fps.values() for a in f.Pads() if a.GetNetname()==net]
 missing=[f.GetReference()+'.'+a.GetNumber() for f,a in pp if a.m_Uuid.AsString() not in ids]
 rails.append({'net':net,'source':f'{ref}.{pin}','pads':len(pp),'missing':missing,'all_connected':not missing})
 failures+=missing
# Each bypass in this power-routing scope has a conductive ground return.
ground=cluster(pad('U30',4));caps=[f'C{i}' for i in [304,305,306,314,315,316,521,522,524,525,561,562,564,565,1,2,3,4,10,20,702,712,722,732,740]]
missing_returns=[r+'.2' for r in caps if pad(r,2).m_Uuid.AsString() not in ground]
own={str(uuid.uuid5(uuid.NAMESPACE_URL,f'bp-tesla-power-routing/{i}')) for i in range(6000)}
own|={str(uuid.uuid5(uuid.NAMESPACE_URL,f'bp-tesla-3v3-direct/{i}')) for i in range(100)}
own|={str(uuid.uuid5(uuid.NAMESPACE_URL,f'bp-tesla-3v3-front/{i}')) for i in range(100)}
own|={str(uuid.uuid5(uuid.NAMESPACE_URL,f'bp-tesla-adc-3v3-direct/{i}')) for i in range(100)}
own|={str(uuid.uuid5(uuid.NAMESPACE_URL,f'bp-tesla-cst-front/{i}')) for i in range(100)}
own|={str(uuid.uuid5(uuid.NAMESPACE_URL,f'bp-tesla-regulator-cleanup/{i}')) for i in range(100)}
tracks=[t for t in b.GetTracks() if not isinstance(t,p.PCB_VIA)];local=[t for t in tracks if t.m_Uuid.AsString() in own];vias=[t for t in b.GetTracks() if isinstance(t,p.PCB_VIA)]
angle_errors=[];overlaps=[];via_pad=[]
for t in local:
 a,z=t.GetStart(),t.GetEnd();dx=abs(a.x-z.x);dy=abs(a.y-z.y)
 if min(dx,dy)>2 and abs(dx-dy)>2:angle_errors.append(t.m_Uuid.AsString())
for i,t in enumerate(tracks):
 a,z=xy(t.GetStart()),xy(t.GetEnd());dx=z[0]-a[0];dy=z[1]-a[1];length=math.hypot(dx,dy)
 for u in tracks[i+1:]:
  if t.m_Uuid.AsString() not in own and u.m_Uuid.AsString() not in own:continue
  if t.GetNetCode()!=u.GetNetCode() or t.GetLayer()!=u.GetLayer():continue
  ends=[xy(u.GetStart()),xy(u.GetEnd())]
  if any(abs((q[0]-a[0])*dy-(q[1]-a[1])*dx)/length>.002 for q in ends):continue
  interval=sorted(((q[0]-a[0])*dx+(q[1]-a[1])*dy)/length for q in ends)
  overlap=min(length,interval[1])-max(0,interval[0])
  if overlap>.005:overlaps.append({'net':t.GetNetname(),'overlap_mm':overlap,'a':a,'z':z})
for t in vias:
 if t.m_Uuid.AsString() not in own:continue
 for f in fps.values():
  for a in f.Pads():
   if a.GetAttribute()==p.PAD_ATTRIB_SMD and a.HitTest(t.GetPosition(),t.GetDrillValue()//2):via_pad.append({'via':xy(t.GetPosition()),'pad':f'{f.GetReference()}.{a.GetNumber()}'})
r={'pcb_sha256':hashlib.sha256((D/'controller.kicad_pcb').read_bytes()).hexdigest(),'copper_layers':b.GetCopperLayerCount(),'rails':rails,'bypass_caps_with_ground_checked':len(caps),'missing_bypass_returns':missing_returns,'angle_errors':angle_errors,'overlapping_segments':overlaps,'via_holes_over_smd_pads':via_pad,'whole_board_unconnected':conn.GetUnconnectedCount(False),'new_track_count':len(local),'new_via_count':sum(t.m_Uuid.AsString() in own for t in vias)}
(D/'docs/power-routing-audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
assert not failures and not missing_returns and not angle_errors and not overlaps and not via_pad and b.GetCopperLayerCount()==2
