#!/usr/bin/env python3
"""Add AUX buffers without disturbing existing placement/routing."""
import ast,json,uuid,re,shutil
from pathlib import Path
import pcbnew as p
from tesla_aux import populate
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'boards/tesla-coil-controller';C=ROOT/'boards/programming-carrier'
b=p.LoadBoard(str(D/'controller.kicad_pcb'));parts=json.loads((D/'docs/circuit.json').read_text());fps={f.GetReference():f for f in b.GetFootprints()};nets={n.GetNetname():n for n in b.GetNetInfo().NetsByNetcode().values()}
v=lambda x,y:p.VECTOR2I(p.FromMM(x),p.FromMM(y));uid=lambda s:str(uuid.uuid5(uuid.NAMESPACE_URL,'bp-tesla-controller/'+s))
for n in ast.parse((ROOT/'tools/hardware/build_tesla_controller.py').read_text()).body:
 if isinstance(n,ast.FunctionDef) and n.name in ['net','add']:exec(compile(ast.Module(body=[n],type_ignores=[]),'<adapter>','exec'))
assert 'U70' not in parts,'Already integrated; edit existing objects rather than replace routed footprints'
before=set(parts);populate(add)
planpath=ROOT/'tools/hardware/tesla_placement.json';plan=json.loads(planpath.read_text())
for r in set(parts)-before:
 plan['positions'][r]=parts[r]['position']
 fps[r].Reference().SetVisible(r.startswith('U'))
 if r.startswith('U'):
  xx,yy,_=parts[r]['position'];plan['reference_positions'][r]=[xx,yy+4];fps[r].Reference().SetPosition(v(xx,yy+4))
for ch in range(5,9):
 r=f'R{ch}';nn=f'AUX{ch-4}_BUFFERED';parts[r]['pins']['1']=nn
 for pad in fps[r].Pads():
  if pad.GetNumber()=='1':pad.SetNet(net(nn))
for r in ['J3','J8']:
 xx,_,a=plan['positions'][r];plan['positions'][r]=[xx,145,a];parts[r]['position']=[xx,145,a];fps[r].SetPosition(v(xx,145));plan['reference_positions'][r]=[xx,138];fps[r].Reference().SetPosition(v(xx,138))
for reg in plan['regions']:
 if reg['name']=='AUX 1-4':reg['bounds']=[88,136,133,153];reg['label_position']=[114,140]
plan['regions'].append(dict(name='AUX UNITY BUFFERS',bounds=[23,150,90,169],references=sorted(set(parts)-before),label_position=[56,167],no_outline=True))
for d in b.GetDrawings():
 if isinstance(d,p.PCB_TEXT) and d.GetText()=='AUX 1-4':d.SetPosition(v(114,140))
t=p.PCB_TEXT(b);t.SetText('AUX UNITY BUFFERS');t.SetPosition(v(56,167));t.SetLayer(p.F_SilkS);t.SetTextSize(v(.9,.9));t.SetTextThickness(p.FromMM(.15));b.Add(t)
p.SaveBoard(str(D/'controller.kicad_pcb'),b);(D/'docs/circuit.json').write_text(json.dumps(parts,indent=2)+'\n');planpath.write_text(json.dumps(plan,indent=2)+'\n');(D/'docs/floorplan-regions.json').write_text(json.dumps(plan['regions'],indent=2)+'\n')
