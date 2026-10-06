#!/usr/bin/env python3
"""Check bridge connectivity, driver voltage-domain separation and geometry."""
import json,uuid,math,hashlib,re,collections
from pathlib import Path
import pcbnew as p
D=Path(__file__).resolve().parents[2]/'boards/tesla-coil-controller';b=p.LoadBoard(str(D/'controller.kicad_pcb'));b.BuildConnectivity();conn=b.GetConnectivity();fs={f.GetReference():f for f in b.GetFootprints()}
padrefs={a.m_Uuid.AsString():f.GetReference()+'.'+a.GetNumber() for f in fs.values() for a in f.Pads()}
def pad(r,n):return next(a for a in fs[r].Pads() if a.GetNumber()==str(n))
def same(expected,*targets):
 actual={f'{r}.{n}':pad(r,n).GetNetname() for r,n in targets}
 assert set(actual.values())=={expected},(expected,actual)
 return {'net':expected,'pads':list(actual)}
contracts=[]
removed={'U50','U55','C500','C501','R504','J6','D85','R805','R821'}
assert removed.isdisjoint(fs), 'Obsolete command enable circuitry returned'
assert not any(a.GetNetname()=='DRIVE_ARM' or (a.GetNetname().startswith('GDT') and a.GetNetname().endswith('_EN')) for f in fs.values() for a in f.Pads()), 'Obsolete enable net remains'
assert pad('J1',14).GetNetname()=='unconnected-(J1-NC-Pad14)'
assert pad('J2',25).GetNetname()=='unconnected-(J2-NC-Pad25)'
assert pad('J2',30).GetNetname()=='unconnected-(J2-NC-Pad30)'
assert pad('J2',31).GetNetname()=='unconnected-(J2-NC-Pad31)'
assert {'U80','C80','R820','R822','R823','R824'}.isdisjoint(fs), 'Obsolete LED buffer remains'
assert not any(a.GetNetname()=='LED_ARM' for f in fs.values() for a in f.Pads()), 'ARM indicator is removed'
for ch,contacts in enumerate([[37,38,39,40],[33,34,35,36]]):
 for i,contact in enumerate(contacts):
  stem=f'GDT{ch+1}_{"L" if i<2 else "R"}_{"HI" if i%2==0 else "LO"}'
  rr=f'R{(505 if ch==0 else 513)+i}'
  rp=f'R{(500 if ch==0 else 509)+i}'
  driver=f'U{51+ch*2+i//2}'
  contracts.append(same(stem,('J2',contact),(rr,1),(rp,1)))
  contracts.append(same(stem+'_BUS',(rr,2),(driver,5+i%2)))
  contracts.append(same('GND',(rp,2)))
for ch in [1,2]:
 for leg,k in [('L',0),('R',1)]:
  pre=f'GDT{ch}_{leg}_';u=f'U{51+(ch-1)*2+k}';qh=f'Q{50+(ch-1)*4+k*2}';ql=f'Q{51+(ch-1)*4+k*2}';rr=520+(ch-1)*40+k*4;cc=520+(ch-1)*40+k*3
  for expected,pins in [(pre+'LO_DRV',[(u,8),(f'R{rr+2}',1)]),(pre+'HO',[(u,3),(f'R{rr}',1)]),(pre+'HG',[(qh,1),(f'R{rr}',2),(f'R{rr+1}',1)]),(pre+'LG',[(ql,1),(f'R{rr+2}',2),(f'R{rr+3}',1)]),(pre+'SW',[(u,4),(qh,3),(ql,2),(f'C{cc}',2),(f'R{rr+1}',2)]),(pre+'HB',[(u,2),(f'C{cc}',1)]),('VBAT_24V',[(qh,2)]),('GND',[(u,7),(ql,3),(f'R{rr+3}',2)]),('+12V_BIAS',[(u,1)]),(pre+'HI_BUS',[(u,5)]),(pre+'LO_BUS',[(u,6)])]:contracts.append(same(expected,*pins))
  # A passive daughterboard connector cannot make ERC detect accidental sharing
  # of a 12V output net with a 3V3 FPGA command. Assert the domains explicitly.
  logic={a.GetNetname() for a in fs['J2'].Pads()}
  assert pad(u,8).GetNetname() not in logic and pad(u,3).GetNetname() not in logic
names=sorted({a.GetNetname() for f in fs.values() for a in f.Pads() if a.GetNetname().startswith('GDT')})+['VBAT_24V','+12V_BIAS','+3V3']
results=[]
for name in names:
 pp=[a for f in fs.values() for a in f.Pads() if a.GetNetname()==name];source=pp[0];ids={a.m_Uuid.AsString() for a in conn.GetConnectedItems(source)}|{source.m_Uuid.AsString()}
 missing=[padrefs[a.m_Uuid.AsString()] for a in pp if a.m_Uuid.AsString() not in ids];results.append(dict(net=name,pads=len(pp),missing=missing))
own={str(uuid.uuid5(uuid.NAMESPACE_URL,f'bp-tesla-hbridge-routing/{i}')) for i in range(8000)}
own|={str(uuid.uuid5(uuid.NAMESPACE_URL,f'bp-tesla-direct-drive/{i}')) for i in range(1000)}
own|={str(uuid.uuid5(uuid.NAMESPACE_URL,f'bp-tesla-command-rebuild/{i}')) for i in range(5000)}
own|={str(uuid.uuid5(uuid.NAMESPACE_URL,f'bp-tesla-gate-pairs/{i}')) for i in range(100)}
own|={str(uuid.uuid5(uuid.NAMESPACE_URL,f'bp-tesla-ho-direct/{i}')) for i in range(100)}
own|={str(uuid.uuid5(uuid.NAMESPACE_URL,f'bp-tesla-input-groups/{i}')) for i in range(200)}
tracks=[t for t in b.GetTracks() if not isinstance(t,p.PCB_VIA)];angle_errors=[];via_pad=[];overlaps=[]
for t in tracks:
 if t.m_Uuid.AsString() not in own:continue
 dx=abs(t.GetEnd().x-t.GetStart().x);dy=abs(t.GetEnd().y-t.GetStart().y)
 if min(dx,dy)>2 and abs(dx-dy)>2:angle_errors.append(t.m_Uuid.AsString())
for t in b.GetTracks():
 if not isinstance(t,p.PCB_VIA) or t.m_Uuid.AsString() not in own:continue
 for f in fs.values():
  for a in f.Pads():
   if a.GetAttribute()==p.PAD_ATTRIB_SMD and a.HitTest(t.GetPosition(),t.GetDrillValue()//2):via_pad.append(dict(via=t.m_Uuid.AsString(),pad=f.GetReference()+'.'+a.GetNumber()))
xy=lambda a:(p.ToMM(a.x),p.ToMM(a.y))
for i,t in enumerate(tracks):
 a,z=xy(t.GetStart()),xy(t.GetEnd());dx=z[0]-a[0];dy=z[1]-a[1];ll=math.hypot(dx,dy)
 for u in tracks[i+1:]:
  if t.m_Uuid.AsString() not in own and u.m_Uuid.AsString() not in own:continue
  if t.GetNetname()!=u.GetNetname() or t.GetLayer()!=u.GetLayer():continue
  pts=[xy(u.GetStart()),xy(u.GetEnd())]
  if any(abs((q[0]-a[0])*dy-(q[1]-a[1])*dx)/ll>.002 for q in pts):continue
  v=sorted(((q[0]-a[0])*dx+(q[1]-a[1])*dy)/ll for q in pts);overlap=min(ll,v[1])-max(0,v[0])
  if overlap>.005:overlaps.append(dict(net=t.GetNetname(),mm=overlap,ids=[t.m_Uuid.AsString(),u.m_Uuid.AsString()]))
duplicates=[u for u,n in collections.Counter(re.findall(r'\(uuid "([^"]+)"\)',(D/'controller.kicad_pcb').read_text())).items() if n>1]
# Native DRC distinguishes disconnected fill islands inside one zone object.
# GetConnectedItems alone can report those pads through the shared zone object.
native=json.loads((D/'fab/checks/drc.json').read_text())
validation=json.loads((D/'docs/validation.json').read_text())
assert validation['sha256']['controller.kicad_pcb']==hashlib.sha256((D/'controller.kicad_pcb').read_bytes()).hexdigest(), 'Run check_tesla_draft.py on this board before the bridge audit'
scope=set(names)|{'GND'}
return_failures=[v for v in native['unconnected_items'] if any(any('['+name+']' in a['description'] for name in scope) for a in v['items'])]
r=dict(pcb_sha256=hashlib.sha256((D/'controller.kicad_pcb').read_bytes()).hexdigest(),layers=b.GetCopperLayerCount(),whole_board_unconnected=conn.GetUnconnectedCount(False),driver_contracts=contracts,connectivity=results,native_scope_unconnected=return_failures,off_angle=angle_errors,via_drill_over_pad=via_pad,overlapping_tracks=overlaps,duplicate_uuids=duplicates)
(D/'docs/hbridge-routing-audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
assert not return_failures and not any(v['missing'] for v in results) and not angle_errors and not via_pad and not overlaps and not duplicates and b.GetCopperLayerCount()==2
