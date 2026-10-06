#!/usr/bin/env python3
"""Incrementally add CST parts using the constructor's exact footprint/library adapter."""
import ast,json,uuid,re,shutil,csv,sys
from pathlib import Path
import pcbnew as p
from tesla_cst import populate
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'boards/tesla-coil-controller';C=ROOT/'boards/programming-carrier'
b=p.LoadBoard(str(D/'controller.kicad_pcb'));parts=json.loads((D/'docs/circuit.json').read_text())
if 'U40' in parts and '--update' not in sys.argv:raise SystemExit('CST already present; refusing to replace placed parts.')
nets={n.GetNetname():n for n in b.GetNetInfo().NetsByNetcode().values()};fps={f.GetReference():f for f in b.GetFootprints()}
v=lambda x,y:p.VECTOR2I(p.FromMM(x),p.FromMM(y));uid=lambda s:str(uuid.uuid5(uuid.NAMESPACE_URL,'bp-tesla-controller/'+s))
tree=ast.parse((ROOT/'tools/hardware/build_tesla_controller.py').read_text())
for node in tree.body:
 if isinstance(node,ast.FunctionDef) and node.name in ['net','add','cap','res']:exec(compile(ast.Module(body=[node],type_ignores=[]),'<constructor adapter>','exec'))
base_add=add
def add(ref,value,lib,name,pins,x,y,a=0,**kw):
 if ref not in parts:return base_add(ref,value,lib,name,pins,x,y,a,**kw)
 c=parts[ref];assert c['footprint']=='Tesla:'+name
 c.update(value=value,pins=pins,names=kw.get('names',{}),types=kw.get('types',{}));fps[ref].SetValue(value)
 for pad in fps[ref].Pads():
  n=pins.get(pad.GetNumber())
  if n:pad.SetNet(net(n))
 return fps[ref]
populate(add,res,cap)
from tesla_cst import finish_placement
finish_placement(fps,parts,p,v)
parts['J3']['value']='Auxiliary inputs / CT monitor outputs';fps['J3'].SetValue(parts['J3']['value'])
p.SaveBoard(str(D/'controller.kicad_pcb'),b);(D/'docs/circuit.json').write_text(json.dumps(parts,indent=2)+'\n')
print('CST added; prior footprints and all tracks retained.')
