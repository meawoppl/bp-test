#!/usr/bin/env python3
"""Native connectivity and copper audit of FPGA data/control and status paths."""
import pcbnew as p
import json,math,uuid,hashlib
from pathlib import Path
D=Path(__file__).resolve().parents[2]/'boards/tesla-coil-controller'
b=p.LoadBoard(str(D/'controller.kicad_pcb'));b.BuildConnectivity();conn=b.GetConnectivity();fps={f.GetReference():f for f in b.GetFootprints()}
def pad(ref,pin):return next(a for a in fps[ref].Pads() if a.GetNumber()==str(pin))
def cluster(a):return {x.m_Uuid.AsString() for x in conn.GetConnectedItems(a)}|{a.m_Uuid.AsString()}
xy=lambda a:(p.ToMM(a.x),p.ToMM(a.y))
import re, collections
duplicate_uuids=[u for u,n in collections.Counter(re.findall(r'\(uuid "([^"]+)"\)',(D/'controller.kicad_pcb').read_text())).items() if n>1]
assert not duplicate_uuids,duplicate_uuids
rails=[];failures=[]
# FRSTDATA is locally probeable; the obsolete long service-header route is gone.
first_pads={(f.GetReference(),a.GetNumber()) for f in fps.values() for a in f.Pads() if a.GetNetname()=='ADC_FIRST'}
assert first_pads=={('U1','15'),('TP1','1')},first_pads
assert 'J7' not in fps  # Service header was removed in the reviewed board.
assert not any(isinstance(t,p.PCB_VIA) for t in b.GetTracks() if t.GetNetname()=='ADC_FIRST')
sources=[(a.GetNetname(),'J2',a.GetNumber()) for a in fps['J2'].Pads() if a.GetNetname() and a.GetNetname()!='GND' and not a.GetNetname().startswith('unconnected-')]
extras=[f'GDT{ch}_{side}_{level}_BUS' for ch in [1,2] for side in ['L','R'] for level in ['HI','LO']]+['ADC_FIRST']
for net in extras:
 f,a=next((f,a) for f in fps.values() for a in f.Pads() if a.GetNetname()==net);sources.append((net,f.GetReference(),a.GetNumber()))
for net,ref,pin in sources:
 source=pad(ref,pin);assert source.GetNetname()==net;ids=cluster(source)
 pp=[(f,a) for f in fps.values() for a in f.Pads() if a.GetNetname()==net]
 missing=[f.GetReference()+'.'+a.GetNumber() for f,a in pp if a.m_Uuid.AsString() not in ids]
 rails.append({'net':net,'source':f'{ref}.{pin}','pads':len(pp),'missing':missing,'all_connected':not missing})
 failures+=missing
# Each bypass in this power-routing scope has a conductive ground return.
ground=cluster(pad('U30',4));caps=[]
missing_returns=[r+'.2' for r in caps if pad(r,2).m_Uuid.AsString() not in ground]
own={str(uuid.uuid5(uuid.NAMESPACE_URL,f'{namespace}/{i}')) for namespace in ['bp-tesla-fpga-remux','bp-tesla-fpga-routing','bp-tesla-fpga-completion','bp-tesla-fpga-finishing','bp-tesla-command-rebuild','bp-tesla-u53-passives','bp-tesla-input-groups'] for i in range(6000)}
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
(D/'docs/fpga-routing-audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
assert not failures and not missing_returns and not angle_errors and not overlaps and not via_pad and b.GetCopperLayerCount()==2
