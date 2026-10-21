"""Integrate indicators into current board without replacing existing geometry."""
import ast,json,uuid,re,shutil
from pathlib import Path
import pcbnew as p
from tesla_indicators import populate,CONTACTS,ROWS
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'boards/tesla-coil-controller';C=ROOT/'third_party/gumstick/programming-carrier'
b=p.LoadBoard(str(D/'controller.kicad_pcb'));parts=json.loads((D/'docs/circuit.json').read_text());fps={f.GetReference():f for f in b.GetFootprints()};nets={n.GetNetname():n for n in b.GetNetInfo().NetsByNetcode().values()}
v=lambda x,y:p.VECTOR2I(p.FromMM(x),p.FromMM(y));uid=lambda s:str(uuid.uuid5(uuid.NAMESPACE_URL,'bp-tesla-controller/'+s))
for n in ast.parse((ROOT/'tools/hardware/build_tesla_controller.py').read_text()).body:
 if isinstance(n,ast.FunctionDef) and n.name in ['net','add']:exec(compile(ast.Module(body=[n],type_ignores=[]),'<adapter>','exec'))
assert 'D80' not in parts,'Indicators already integrated'
before=set(parts);populate(add)
planpath=ROOT/'tools/hardware/tesla_placement.json';plan=json.loads(planpath.read_text())
for r in set(parts)-before:
 plan['positions'][r]=parts[r]['position'];plan['reference_positions'][r]=parts[r]['position'][:2];fps[r].Reference().SetVisible(False)
for pin,nn in CONTACTS.items():
 assert parts['J2']['pins'][pin] is None
 parts['J2']['pins'][pin]=nn
 for pad in fps['J2'].Pads():
  if pad.GetNumber()==pin:pad.SetNet(net(nn))
for r,pos in [('J5',[117,26,90]),('J7',[128,26,90])]:
 plan['positions'][r]=pos;parts[r]['position']=pos;fps[r].SetPosition(v(*pos[:2]));fps[r].SetOrientationDegrees(pos[2]);plan['reference_positions'][r]=[pos[0]+3,29]
for reg in plan['regions']:
 if reg['name']=='USB / SERVICE':reg.update(bounds=[115,21,138,32],label_position=[126,31.5])
plan['indicator_labels']=[{'text':a,'position':[144+i*3,23],'angle':90} for i,(a,_,_,_,_) in enumerate(ROWS)]
p.SaveBoard(str(D/'controller.kicad_pcb'),b);(D/'docs/circuit.json').write_text(json.dumps(parts,indent=2)+'\n');planpath.write_text(json.dumps(plan,indent=2)+'\n')
