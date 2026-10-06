#!/usr/bin/env python3
"""Apply dual CSTs and terminal auxiliary inputs without replacing existing board."""
import ast,json,uuid,re,shutil,csv
from pathlib import Path
import pcbnew as p
from tesla_dual_cst import populate_second,populate_aux,ADC_INPUTS
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'boards/tesla-coil-controller';C=ROOT/'boards/programming-carrier'
b=p.LoadBoard(str(D/'controller.kicad_pcb'));assert not b.GetTracks(),'Reconcile routing first'
parts=json.loads((D/'docs/circuit.json').read_text());fps={f.GetReference():f for f in b.GetFootprints()};nets={n.GetNetname():n for n in b.GetNetInfo().NetsByNetcode().values()}
v=lambda x,y:p.VECTOR2I(p.FromMM(x),p.FromMM(y));uid=lambda s:str(uuid.uuid5(uuid.NAMESPACE_URL,'bp-tesla-controller/'+s))
tree=ast.parse((ROOT/'tools/hardware/build_tesla_controller.py').read_text())
for n in tree.body:
 if isinstance(n,ast.FunctionDef) and n.name in ['net','add','cap','res']:exec(compile(ast.Module(body=[n],type_ignores=[]),'<constructor adapter>','exec'))
original_add=add;removed=[]
def add(ref,*a,**kw):
 if ref in fps:
  old=fps.pop(ref);removed.append(old);b.Remove(old);parts.pop(ref)
 return original_add(ref,*a,**kw)
populate_second(add);populate_aux(add)
for ch,nn in enumerate(ADC_INPUTS,1):parts[f'R{ch}']['pins']['1']=nn
parts['J2']['pins'].update({'24':'CT2_ZERO','33':'FAULT_N'})
for r in ['J2']+[f'R{i}' for i in range(1,9)]:
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
