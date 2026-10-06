#!/usr/bin/env python3
"""Native connectivity and geometry audit for the routed CST subset."""
import json,math,hashlib,uuid
from pathlib import Path
import pcbnew as p
D=Path(__file__).resolve().parents[2]/'boards/tesla-coil-controller';b=p.LoadBoard(str(D/'controller.kicad_pcb'));b.BuildConnectivity();c=b.GetConnectivity()
plan=json.loads((D.parents[1]/'tools/hardware/tesla_placement.json').read_text());refs=set(next(r['references'] for r in plan['regions'] if r['name'].startswith('CST 1')))
pads={};allpads={}
for f in b.GetFootprints():
 for a in f.Pads():
  if a.GetNetCode():allpads.setdefault(a.GetNetname(),[]).append(a)
  if f.GetReference() in refs and a.GetNetCode():pads.setdefault(a.GetNetname(),[]).append(a)
results=[];errors=[]
for net,pp in sorted(pads.items()):
 connected={a.m_Uuid.AsString() for a in c.GetConnectedItems(pp[0])}|{pp[0].m_Uuid.AsString()}
 missing=[a.GetParent().GetReference()+'.'+a.GetNumber() for a in pp if a.m_Uuid.AsString() not in connected]
 results.append(dict(net=net,local_pad_count=len(pp),all_local_pads_connected=not missing,missing=missing,external_pad_count=len(allpads[net])-len(pp)))
 if missing:errors.append({'net':net,'missing':missing})
via_pad=[]
footprints=list(b.GetFootprints());smd=[(f.GetReference(),a) for f in footprints for a in f.Pads() if a.GetAttribute()==p.PAD_ATTRIB_SMD]
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA):
  for ref,a in smd:
   if a.HitTest(t.GetPosition(),t.GetDrillValue()//2):via_pad.append({'ref':ref,'pad':a.GetNumber(),'via':[p.ToMM(t.GetPosition().x),p.ToMM(t.GetPosition().y)]})
tr=[]
for t in b.GetTracks():
 if not isinstance(t,p.PCB_VIA):
  a=t.GetStart();z=t.GetEnd();dx=abs(a.x-z.x);dy=abs(a.y-z.y)
  if min(dx,dy)>2 and abs(dx-dy)>2:tr.append(t.m_Uuid.AsString())
# Same-net overlapping segments can conceal a dangling tail from native DRC.
owned={str(uuid.uuid5(uuid.NAMESPACE_URL,f'bp-tesla-cst-routing/{i}')) for i in range(6000)}
owned|={str(uuid.uuid5(uuid.NAMESPACE_URL,f'bp-tesla-cst-adc/{i}')) for i in range(100)}
owned|={str(uuid.uuid5(uuid.NAMESPACE_URL,f'bp-tesla-cst-front/{i}')) for i in range(100)}
owned.add(str(uuid.uuid5(uuid.NAMESPACE_URL,'bp-tesla-r416-align/0')))
owned|={str(uuid.uuid5(uuid.NAMESPACE_URL,f'bp-tesla-cst-condense/{i}')) for i in range(6000)}
owned|={str(uuid.uuid5(uuid.NAMESPACE_URL,'bp-tesla-cst-condense/'+name)) for name in ['3v3-top','5v-branch']}
local_tracks=[t for t in b.GetTracks() if t.m_Uuid.AsString() in owned and not isinstance(t,p.PCB_VIA)]
overlaps=[]
xy=lambda a:(p.ToMM(a.x),p.ToMM(a.y))
for i,t in enumerate(local_tracks):
 a,z=xy(t.GetStart()),xy(t.GetEnd());dx=z[0]-a[0];dy=z[1]-a[1];length=math.hypot(dx,dy)
 for u in local_tracks[i+1:]:
  if t.GetNetCode()!=u.GetNetCode() or t.GetLayer()!=u.GetLayer():continue
  ends=[xy(u.GetStart()),xy(u.GetEnd())]
  if any(abs((q[0]-a[0])*dy-(q[1]-a[1])*dx)/length>.002 for q in ends):continue
  intervals=sorted(((q[0]-a[0])*dx+(q[1]-a[1])*dy)/length for q in ends)
  overlap=min(length,intervals[1])-max(0,intervals[0])
  if overlap>.005:overlaps.append({'net':t.GetNetname(),'length_mm':overlap,'tracks':[t.m_Uuid.AsString(),u.m_Uuid.AsString()]})
fps={f.GetReference():f for f in footprints}
getpad=lambda ref,n:next(a for a in fps[ref].Pads() if a.GetNumber()==str(n))
adc_links=[]
for net,ref,ch in [('CT1_RAW','R400',5),('CT1_ENVELOPE','C400',6),('CT2_RAW','R600',7),('CT2_ENVELOPE','C600',8)]:
 source=getpad(ref,1);rr='R'+str(ch);cc='C'+str(ch+10);adc_pin=47+2*ch
 assert source.GetNetname()==getpad(rr,1).GetNetname()==net
 ids={a.m_Uuid.AsString() for a in c.GetConnectedItems(source)}|{source.m_Uuid.AsString()}
 assert getpad(rr,1).m_Uuid.AsString() in ids,(net,'source-to-filter open')
 adc=getpad('U1',adc_pin);ids={a.m_Uuid.AsString() for a in c.GetConnectedItems(adc)}|{adc.m_Uuid.AsString()}
 assert {getpad(rr,2).GetNetname(),getpad(cc,1).GetNetname(),adc.GetNetname()}=={f'ADC_CH{ch}'}
 assert all(getpad(r,n).m_Uuid.AsString() in ids for r,n in [(rr,2),(cc,1)]),(net,'filter-to-ADC open')
 adc_links.append(dict(signal=net,source=f'{ref}.1',filter=rr+'/'+cc,adc_channel=ch,adc_pin=adc_pin,all_connected=True))
source=getpad('R20',2);connected={a.m_Uuid.AsString() for a in c.GetConnectedItems(source)}|{source.m_Uuid.AsString()}
source_missing=[a.GetParent().GetReference()+'.'+a.GetNumber() for a in pads['+5V_ADC'] if a.m_Uuid.AsString() not in connected]
bypass=[]
for u,cp,cn in [('U40','C401','C402'),('U41','C403','C404'),('U60','C601','C602'),('U61','C603','C604')]:
 for pin,ref in [(5,cp),(2,cn)]:
  a,z=xy(getpad(u,pin).GetPosition()),xy(getpad(ref,1).GetPosition())
  bypass.append({'ic':u,'pin':pin,'capacitor':ref,'pin_to_pad_mm':round(math.dist(a,z),4),'aligned':min(abs(a[0]-z[0]),abs(a[1]-z[1]))<.00001})
connectors_aligned=fps['J4'].GetPosition().x==fps['J30'].GetPosition().x and abs(fps['J4'].GetOrientationDegrees()-fps['J30'].GetOrientationDegrees())<.001
r={'copper_layers':b.GetCopperLayerCount(),'native_whole_board_unconnected':c.GetUnconnectedCount(False),'local_connectivity':results,'local_connectivity_failures':errors,'non_octilinear_tracks':tr,'via_hole_over_smd_pad':via_pad,'overlapping_local_tracks':overlaps,'five_volt_entry':'R20.2','five_volt_entry_missing_connections':source_missing,'amplifier_bypass_placement':bypass,'J4_J30_aligned':connectors_aligned,'pcb_sha256':hashlib.sha256((D/'controller.kicad_pcb').read_bytes()).hexdigest()}
r['adc_links']=adc_links
(D/'docs/cst-routing-audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['copper_layers','native_whole_board_unconnected','local_connectivity_failures','non_octilinear_tracks','via_hole_over_smd_pad','overlapping_local_tracks','five_volt_entry_missing_connections','amplifier_bypass_placement','J4_J30_aligned','adc_links']},indent=2))
assert not errors and not tr and not via_pad and not overlaps and not source_missing and connectors_aligned and r['copper_layers']==2
assert all(row['aligned'] and row['pin_to_pad_mm']<=2.0 for row in bypass)
