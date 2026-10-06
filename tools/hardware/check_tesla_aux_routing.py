#!/usr/bin/env python3
"""Native connectivity and geometry audit of the four AUX input channels."""
import pcbnew as p
import json,math,uuid,hashlib
from pathlib import Path
D=Path(__file__).resolve().parents[2]/'boards/tesla-coil-controller'
b=p.LoadBoard(str(D/'controller.kicad_pcb'));b.BuildConnectivity();conn=b.GetConnectivity();fps={f.GetReference():f for f in b.GetFootprints()}
def pad(ref,pin):return next(a for a in fps[ref].Pads() if a.GetNumber()==str(pin))
def cluster(a):return {x.m_Uuid.AsString() for x in conn.GetConnectedItems(a)}|{a.m_Uuid.AsString()}
xy=lambda a:(p.ToMM(a.x),p.ToMM(a.y))
rails=[];failures=[]
sources=[('-5V_CT','C423',1), ('+12V_AUX','R740',2), ('+5V_ADC','U1',1), ('GND','U30',4)]
for ch,connector in enumerate(['J3','J8','J9','J10'],1):
 sources += [(f'AUX{ch}_0_5V',connector,1),(f'AUX{ch}_FILTERED',f'U{69+ch}',3),(f'AUX{ch}_BUFFERED',f'U{69+ch}',1),(f'ADC_CH{ch}','U1',47+ch*2)]
for net,ref,pin in sources:
 source=pad(ref,pin);assert source.GetNetname()==net;ids=cluster(source)
 pp=[(f,a) for f in fps.values() for a in f.Pads() if a.GetNetname()==net]
 missing=[f.GetReference()+'.'+a.GetNumber() for f,a in pp if a.m_Uuid.AsString() not in ids]
 rails.append({'net':net,'source':f'{ref}.{pin}','pads':len(pp),'missing':missing,'all_connected':not missing})
 failures+=missing
# Verify the revised physical channel order and every RC-to-ADC connection.
channel_map=json.loads((D/'docs/adc-channel-map.json').read_text())
from tesla_dual_cst import ADC_INPUTS
assert [row['signal'] for row in channel_map]==ADC_INPUTS
for row in channel_map:
 ch=row['adc_channel']; rr=row['series_resistor']; cc=row['shunt_capacitor']; ip=row['adc_pin']
 assert pad(rr,1).GetNetname()==row['signal']
 assert {pad(rr,2).GetNetname(),pad(cc,1).GetNetname(),pad('U1',ip).GetNetname()}=={f'ADC_CH{ch}'}
 ids=cluster(pad('U1',ip))
 assert all(pad(r,n).m_Uuid.AsString() in ids for r,n in [(rr,2),(cc,1)])
 if row['signal'].startswith('AUX'):
  aux=int(row['signal'][3]);output=pad(f'U{69+aux}',1)
  assert pad(rr,1).m_Uuid.AsString() in cluster(output), f'AUX{aux}: buffer does not reach {rr}'
# AUX1..4 now reach ADC CH1..4 in order on front copper, without crossovers.
# Native KiCad DRC separately checks widths, endpoints, and pad clearances.
def orient(a,z,q):return (z[0]-a[0])*(q[1]-a[1])-(z[1]-a[1])*(q[0]-a[0])
aux_tracks=[t for t in b.GetTracks() if not isinstance(t,p.PCB_VIA) and t.GetNetname() in {f'AUX{i}_BUFFERED' for i in range(1,5)}]
crossovers=[];same_layer_crossovers=[]
for i,t in enumerate(aux_tracks):
 for u in aux_tracks[i+1:]:
  if t.GetNetCode()==u.GetNetCode():continue
  a,z=xy(t.GetStart()),xy(t.GetEnd());q,r=xy(u.GetStart()),xy(u.GetEnd())
  if orient(a,z,q)*orient(a,z,r)<-1e-12 and orient(q,r,a)*orient(q,r,z)<-1e-12:
   item={'tracks':[t.m_Uuid.AsString(),u.m_Uuid.AsString()],'nets':[t.GetNetname(),u.GetNetname()],'layers':[b.GetLayerName(t.GetLayer()),b.GetLayerName(u.GetLayer())]}
   crossovers.append(item)
   if t.GetLayer()==u.GetLayer():same_layer_crossovers.append(item)
assert not crossovers, crossovers
output_vias=[t.m_Uuid.AsString() for t in b.GetTracks() if isinstance(t,p.PCB_VIA) and t.GetNetname() in {f'AUX{i}_BUFFERED' for i in range(1,5)}]
assert not output_vias, output_vias
assert all(t.GetLayer()==p.F_Cu for t in aux_tracks), 'Buffered AUX routes must remain on front copper'
# Probe pads expose the unconditioned connector, buffered output, and ground.
probes=[]
for ch,connector in enumerate(['J3','J8','J9','J10'],1):
 k=700+10*(ch-1)
 for off,net,source in [(0,f'AUX{ch}_0_5V',pad(connector,1)),(1,f'AUX{ch}_BUFFERED',pad(f'U{69+ch}',1)),(2,'GND',pad(connector,2))]:
  ref=f'TP{k+off}';a=pad(ref,1)
  assert a.GetNetname()==net and a.m_Uuid.AsString() in cluster(source), ref
  assert fps[ref].GetAttributes() & p.FP_EXCLUDE_FROM_BOM
  assert fps[ref].GetAttributes() & p.FP_EXCLUDE_FROM_POS_FILES
  probes.append({'ref':ref,'net':net,'position_mm':xy(a.GetPosition()),'connected':True})
# The unity-feedback loops must reach pin 4 from pin 1 using front copper only.
for ch in range(1,5):
 graph={}
 for t in aux_tracks:
  if t.GetLayer()!=p.F_Cu or t.GetNetname()!=f'AUX{ch}_BUFFERED':continue
  a,z=xy(t.GetStart()),xy(t.GetEnd());graph.setdefault(a,set()).add(z);graph.setdefault(z,set()).add(a)
 source=xy(pad(f'U{69+ch}',1).GetPosition());target=xy(pad(f'U{69+ch}',4).GetPosition())
 seen={source};pending=[source]
 while pending:
  for q in graph.get(pending.pop(),set())-seen:seen.add(q);pending.append(q)
 assert target in seen, f'U{69+ch}: feedback requires a layer change'
# Each bypass in this power-routing scope has a conductive ground return.
ground=cluster(pad('U30',4));caps=[f'C{i}' for i in [700,701,702,703,710,711,712,713,720,721,722,723,730,731,732,733,740,741,11,12,13,14]]
missing_returns=[r+'.2' for r in caps if pad(r,2).m_Uuid.AsString() not in ground]
own={str(uuid.uuid5(uuid.NAMESPACE_URL,f'bp-tesla-aux-routing/{i}')) for i in range(6000)}
own|={str(uuid.uuid5(uuid.NAMESPACE_URL,f'{prefix}/{i}')) for prefix in ['bp-tesla-analog-tidy','bp-tesla-adc-swap','bp-tesla-aux-order','bp-tesla-aux-feedback','bp-tesla-aux-wedges','bp-tesla-adc-remux'] for i in range(1000)}
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
r={'pcb_sha256':hashlib.sha256((D/'controller.kicad_pcb').read_bytes()).hexdigest(),'copper_layers':b.GetCopperLayerCount(),'rails':rails,'testpoints':probes,'same_layer_output_crossings':same_layer_crossovers,'output_crossings_on_separate_layers':crossovers,'bypass_caps_with_ground_checked':len(caps),'missing_bypass_returns':missing_returns,'angle_errors':angle_errors,'overlapping_segments':overlaps,'via_holes_over_smd_pads':via_pad,'whole_board_unconnected':conn.GetUnconnectedCount(False),'new_track_count':len(local),'new_via_count':sum(t.m_Uuid.AsString() in own for t in vias)}
r.update(channel_map=channel_map, output_layers=['F.Cu'], output_vias=output_vias)
(D/'docs/aux-routing-audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
assert not failures and not missing_returns and not angle_errors and not overlaps and not via_pad and b.GetCopperLayerCount()==2
