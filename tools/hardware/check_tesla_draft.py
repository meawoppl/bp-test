#!/usr/bin/env python3
"""Regenerate development schematic PDF and checks; never fabricate an unrouted draft."""
import subprocess,json,hashlib
from pathlib import Path
D=Path(__file__).resolve().parents[2]/'boards/tesla-coil-controller';out=D/'fab/checks';out.mkdir(parents=True,exist_ok=True)
def run(*args):subprocess.run(['kicad-cli',*map(str,args)],check=True)
run('sch','erc','--format','json','-o',out/'erc.json',D/'controller.kicad_sch')
run('pcb','drc','--schematic-parity','--format','json','-o',out/'drc.json',D/'controller.kicad_pcb')
e=json.loads((out/'erc.json').read_text());d=json.loads((out/'drc.json').read_text())
r={'stage':'Development routing: CST/AUX inputs connected to ADC, supply distribution, FPGA signals and H-bridge drivers; remaining controller routing incomplete','erc':sum(len(s.get('violations',[])) for s in e.get('sheets',[])),'physical_drc':len(d['violations']),'schematic_parity':len(d['schematic_parity']),'unconnected_items':len(d['unconnected_items']),'fabrication_ready':False,'sha256':{f:hashlib.sha256((D/f).read_bytes()).hexdigest() for f in ['controller.kicad_sch','controller.kicad_pcb','controller.kicad_pro']}}
(D/'docs/validation.json').write_text(json.dumps(r,indent=2)+'\n')
intent=D/'docs/routing-intent.json'
if intent.exists():
 import pcbnew as pcb
 board=pcb.LoadBoard(str(D/'controller.kicad_pcb'));board.BuildConnectivity();tracks={t.m_Uuid.AsString():t for t in board.GetTracks()};expected=json.loads(intent.read_text())['open_route_ends'];accepted=[]
 for violation in d['violations']:
  if violation['type']!='track_dangling' or len(violation['items'])!=1:continue
  t=tracks.get(violation['items'][0]['uuid'])
  if t is None or t.GetNetname() not in expected:continue
  xy=expected[t.GetNetname()]
  if any(abs(pcb.ToMM(pt.x)-xy[0])<1e-5 and abs(pcb.ToMM(pt.y)-xy[1])<1e-5 for pt in [t.GetStart(),t.GetEnd()]):accepted.append(t.GetNetname())
 r['native_drc_findings']=len(d['violations']);r['intentional_open_route_ends']=accepted;r['physical_drc']=len(d['violations'])-len(accepted);r['native_whole_board_unconnected']=board.GetConnectivity().GetUnconnectedCount(False)
 (D/'docs/validation.json').write_text(json.dumps(r,indent=2)+'\n')
assert not any(r[k] for k in ['erc','physical_drc','schematic_parity']),r
run('sch','export','pdf','-o',D/'docs/controller-schematic.pdf',D/'controller.kicad_sch')
print(json.dumps(r,indent=2))
