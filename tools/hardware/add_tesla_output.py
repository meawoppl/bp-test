#!/usr/bin/env python3
"""Incremental output-stage integration; preserve unrelated draft geometry."""
import ast,json,uuid,re,shutil,csv
from pathlib import Path
import pcbnew as p
from tesla_output import populate,REMOVED_CST,CONTACTS,finish_placement
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'boards/tesla-coil-controller';C=ROOT/'third_party/gumstick/programming-carrier'
b=p.LoadBoard(str(D/'controller.kicad_pcb'));parts=json.loads((D/'docs/circuit.json').read_text());nets={n.GetNetname():n for n in b.GetNetInfo().NetsByNetcode().values()};fps={f.GetReference():f for f in b.GetFootprints()}
v=lambda x,y:p.VECTOR2I(p.FromMM(x),p.FromMM(y));uid=lambda s:str(uuid.uuid5(uuid.NAMESPACE_URL,'bp-tesla-controller/'+s))
assert not b.GetTracks(), 'Routing exists; integration needs explicit reconciliation.'
removed=[]
for r in REMOVED_CST:
 if r in fps:
  removed.append(fps.pop(r));b.Remove(removed[-1]);parts.pop(r)
fps={f.GetReference():f for f in b.GetFootprints()}
assert 'U50' not in parts,'Output stage already present'
tree=ast.parse((ROOT/'tools/hardware/build_tesla_controller.py').read_text())
for n in tree.body:
 if isinstance(n,ast.FunctionDef) and n.name in ['net','add','cap','res']:exec(compile(ast.Module(body=[n],type_ignores=[]),'<constructor adapter>','exec'))
for pin,nn in CONTACTS.items():parts['J2']['pins'][pin]=nn
parts['J6']['pins'].update({'1':CONTACTS['25'],'3':CONTACTS['30'],'7':CONTACTS['34'],'9':CONTACTS['35']})
for ref in ['J2','J6']:
 for pad in fps[ref].Pads():
  nn=parts[ref]['pins'].get(pad.GetNumber())
  if nn:pad.SetNet(net(nn))
populate(add,res,cap)
finish_placement(fps,parts,p,v)
# Room for two independently decoupled bridges and film coupling capacitors.
for o in b.GetDrawings():
 if isinstance(o,p.PCB_SHAPE) and o.GetLayer()==p.Edge_Cuts:
  for get,setter in [(o.GetStart,o.SetStart),(o.GetEnd,o.SetEnd)]:
   pos=get()
   if abs(p.ToMM(pos.x)-180)<.01:setter(v(252,p.ToMM(pos.y)))
for ref in ['H3','H5']:
 xy=fps[ref].GetPosition();fps[ref].SetPosition(v(248,p.ToMM(xy.y)));parts[ref]['position'][0]=248
for o in list(b.GetDrawings()):
 if isinstance(o,p.PCB_TEXT) and any(t in o.GetText() for t in ['RESERVED:','Independent shutdown','UD2.7-derived','Rectifier + hardwired']):b.Remove(o)
p.SaveBoard(str(D/'controller.kicad_pcb'),b);(D/'docs/circuit.json').write_text(json.dumps(parts,indent=2)+'\n')
pth=D/'docs/daughterboard-pinout.csv';rows=list(csv.DictReader(pth.open()))
for row in rows:
 if row['connector']=='J2' and row['contact'] in CONTACTS:row['controller_net']=CONTACTS[row['contact']]
with pth.open('w') as f:
 w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
print('Removed',len(REMOVED_CST),'OC parts; total',len(parts),'parts. Unrouted.')
