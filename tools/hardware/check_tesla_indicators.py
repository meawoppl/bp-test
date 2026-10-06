#!/usr/bin/env python3
"""Verify local indicator topology, copper continuity and absence of retired logic."""
from pathlib import Path
import hashlib,json,uuid
import pcbnew as p
from tesla_indicators import ROWS,PROTECT
D=Path(__file__).resolve().parents[2]/'boards/tesla-coil-controller'
b=p.LoadBoard(str(D/'controller.kicad_pcb'));b.BuildConnectivity();conn=b.GetConnectivity();fs={f.GetReference():f for f in b.GetFootprints()}
parts=json.loads((D/'docs/circuit.json').read_text());plan=json.loads((Path(__file__).with_name('tesla_placement.json')).read_text())
def pad(r,n):return next(a for a in fs[r].Pads() if a.GetNumber()==str(n))
def cluster(a):return {x.m_Uuid.AsString() for x in conn.GetConnectedItems(a)}|{a.m_Uuid.AsString()}
retired={'U80','C80','R820','R822','R823','R824','D85','R805','R821'}
assert retired.isdisjoint(fs) and retired.isdisjoint(parts)
assert not any(a.GetNetname().startswith('LED_BUF_') or a.GetNetname() in ['LED_READY','LED_GDT1_ACTIVE','LED_GDT2_ACTIVE','LED_FAULT','LED_ARM'] for f in fs.values() for a in f.Pads())
for n in ['15','16','17','19']:assert parts['J2']['pins'][n] is None and pad('J2',n).GetNetname().startswith('unconnected-')
rows=[];ground=cluster(pad('J30',2));env=plan['module_envelope']
for i,(label,_,_,signal,value) in ROWS.items():
 r=f'R{800+i}';d=f'D{80+i}';an=f'LED_{80+i}_A'
 assert pad(r,1).GetNetname()==signal and pad(r,2).GetNetname()==pad(d,2).GetNetname()==an
 assert parts[r]['value']==value and pad(d,1).GetNetname()=='GND'
 assert pad(d,2).m_Uuid.AsString() in cluster(pad(r,2))
 assert pad(d,1).m_Uuid.AsString() in ground
 sources=[a for f in fs.values() if f.GetReference()!=r for a in f.Pads() if a.GetNetname()==signal]
 assert sources and any(a.m_Uuid.AsString() in cluster(pad(r,1)) for a in sources)
 x,y=p.ToMM(fs[d].GetPosition().x),p.ToMM(fs[d].GetPosition().y)
 assert not (env[0]<=x<=env[2] and env[1]<=y<=env[3]),f'{d}: concealed by daughterboard'
 if i in PROTECT:
  dd=PROTECT[i];assert pad(dd,1).GetNetname()==an and pad(dd,2).GetNetname()=='GND'
  assert pad(dd,1).m_Uuid.AsString() in cluster(pad(d,2)) and pad(dd,2).m_Uuid.AsString() in ground
 rows.append(dict(label=label,led=d,resistor=r,sensed_net=signal,reverse_clamp=PROTECT.get(i),all_connected=True))
# Check native unconnected findings too: one zone object can have isolated islands.
native=json.loads((D/'fab/checks/drc.json').read_text());ids={a.m_Uuid.AsString() for i in ROWS for r in [f'R{800+i}',f'D{80+i}']+([PROTECT[i]] if i in PROTECT else []) for a in fs[r].Pads()}
missing=[v for v in native['unconnected_items'] if any(a['uuid'] in ids for a in v['items'])];assert not missing,missing
own={str(uuid.uuid5(uuid.NAMESPACE_URL,f'bp-tesla-direct-leds/{i}')) for i in range(200)};tracks=[t for t in b.GetTracks() if t.m_Uuid.AsString() in own]
for t in tracks:
 if isinstance(t,p.PCB_VIA):
  assert not any(a.GetAttribute()==p.PAD_ATTRIB_SMD and a.HitTest(t.GetPosition(),t.GetDrillValue()//2) for f in fs.values() for a in f.Pads())
 else:
  dx,dy=abs(t.GetEnd().x-t.GetStart().x),abs(t.GetEnd().y-t.GetStart().y)
  assert min(dx,dy)<=2 or abs(dx-dy)<=2, (t.GetNetname(),dx,dy)
r=dict(pcb_sha256=hashlib.sha256((D/'controller.kicad_pcb').read_bytes()).hexdigest(),indicators=rows,removed=sorted(retired),freed_J2_contacts=[15,16,17,19],local_copper_items=len(tracks),new_vias=sum(isinstance(t,p.PCB_VIA) for t in tracks),native_indicator_unconnected=missing)
(D/'docs/indicator-routing-audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
