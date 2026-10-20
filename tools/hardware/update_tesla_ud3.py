#!/usr/bin/env python3
"""Synchronize independent GDT commands / CT cable filter into the unrouted draft."""
import ast,json,uuid,re,shutil,csv
from pathlib import Path
import pcbnew as p
from tesla_output import populate as output,CONTACTS
from tesla_cst import populate as cst
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'boards/tesla-coil-controller';C=ROOT/'third_party/gumstick/programming-carrier'
b=p.LoadBoard(str(D/'controller.kicad_pcb'));assert not b.GetTracks(),'Reconcile routing first'
parts=json.loads((D/'docs/circuit.json').read_text());fps={f.GetReference():f for f in b.GetFootprints()};nets={n.GetNetname():n for n in b.GetNetInfo().NetsByNetcode().values()}
v=lambda x,y:p.VECTOR2I(p.FromMM(x),p.FromMM(y));uid=lambda s:str(uuid.uuid5(uuid.NAMESPACE_URL,'bp-tesla-controller/'+s))
tree=ast.parse((ROOT/'tools/hardware/build_tesla_controller.py').read_text())
for n in tree.body:
 if isinstance(n,ast.FunctionDef) and n.name in ['net','add','cap','res']:exec(compile(ast.Module(body=[n],type_ignores=[]),'<constructor adapter>','exec'))
original_add=add
def add(ref,value,lib,name,pins,x,y,a=0,kind='ic',mpn='',lcsc='',names=None,types=None):
 if ref not in parts:return original_add(ref,value,lib,name,pins,x,y,a,kind,mpn,lcsc,names,types)
 parts[ref].update(value=value,pins=pins,mpn=mpn,lcsc=lcsc,names=names or {},types=types or {})
 f=fps[ref];f.SetValue(value)
 for pad in f.Pads():
  nn=pins.get(pad.GetNumber())
  if nn:pad.SetNet(net(nn))
 return f
output(add,res,cap);cst(add,res,cap)
parts['J2']['pins'].update(CONTACTS)
for pin,nn in {'1':CONTACTS['25'],'3':CONTACTS['30'],'7':CONTACTS['34'],'9':CONTACTS['35']}.items():parts['J6']['pins'][pin]=nn
for r in ['J2','J6']:
 for pad in fps[r].Pads():
  nn=parts[r]['pins'].get(pad.GetNumber())
  if nn:pad.SetNet(net(nn))
from tesla_floorplan import apply
apply(b,parts)
p.SaveBoard(str(D/'controller.kicad_pcb'),b);(D/'docs/circuit.json').write_text(json.dumps(parts,indent=2)+'\n')
pth=D/'docs/daughterboard-pinout.csv';rows=list(csv.DictReader(pth.open()))
for row in rows:row['controller_net']=parts[row['connector']]['pins'][row['contact']] or 'UNUSED'
with pth.open('w') as f:
 w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
print(len(parts),'parts')
