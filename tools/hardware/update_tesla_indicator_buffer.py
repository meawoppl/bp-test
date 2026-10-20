"""One-time replacement of discrete indicator drivers with the carrier's octal buffer."""
import ast,json,uuid,re,shutil
from pathlib import Path
import pcbnew as p
from tesla_indicators import populate
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'boards/tesla-coil-controller';C=ROOT/'third_party/gumstick/programming-carrier'
b=p.LoadBoard(str(D/'controller.kicad_pcb'));parts=json.loads((D/'docs/circuit.json').read_text());fps={f.GetReference():f for f in b.GetFootprints()};nets={n.GetNetname():n for n in b.GetNetInfo().NetsByNetcode().values()}
assert 'U80' not in parts
v=lambda x,y:p.VECTOR2I(p.FromMM(x),p.FromMM(y));uid=lambda s:str(uuid.uuid5(uuid.NAMESPACE_URL,'bp-tesla-controller/'+s))
for n in ast.parse((ROOT/'tools/hardware/build_tesla_controller.py').read_text()).body:
 if isinstance(n,ast.FunctionDef) and n.name in ['net','add']:exec(compile(ast.Module(body=[n],type_ignores=[]),'<adapter>','exec'))
pp=ROOT/'tools/hardware/tesla_placement.json';plan=json.loads(pp.read_text())
remove=[f'D{80+i}' for i in range(9)]+[f'R{800+i}' for i in range(9)]+[f'Q{80+i}' for i in range(5)]+[f'R{810+i}' for i in range(5)]+[f'R{820+i}' for i in range(5)]
retired=[]
for r in remove:
 retired.append(fps.pop(r));b.Remove(retired[-1]);parts.pop(r);plan['positions'].pop(r);plan['reference_positions'].pop(r,None)
for r,f in fps.items():
 x,y,a=plan['positions'][r]
 if x>=116.5 and 34<=y<=146 and not r.startswith('H'):
  f.Move(v(0,12));plan['positions'][r][1]+=12;parts[r]['position'][1]+=12
  if r in plan['reference_positions']:plan['reference_positions'][r][1]+=12
for t in b.GetTracks():t.Move(v(0,12))
for reg in plan['regions']:
 if reg['name'] in ['GDT 1','GDT 2','DRIVE ARM','SERVICE']:
  reg['bounds'][1]+=12;reg['bounds'][3]+=12
  if 'label_position' in reg:reg['label_position'][1]+=12
before=set(parts);populate(add)
for pad in fps['U80'].Pads():
 n=pad.GetNumber()
 if n in ['11','12','13']:pad.SetNet(net(f'unconnected-(U80-Y{19-int(n)}-Pad{n})'))
for r in set(parts)-before:
 plan['positions'][r]=parts[r]['position'];plan['reference_positions'][r]=parts[r]['position'][:2];fps[r].Reference().SetVisible(r=='U80')
fps['U80'].Reference().SetPosition(v(147,38));plan['reference_positions']['U80']=[147,38]
p.SaveBoard(str(D/'controller.kicad_pcb'),b);(D/'docs/circuit.json').write_text(json.dumps(parts,indent=2)+'\n');pp.write_text(json.dumps(plan,indent=2)+'\n')
q=ROOT/'tools/hardware/tesla_route_outputs.py';q.write_text(q.read_text().replace('(x+3,y+off)','(x+3,y+off+12)'))
