#!/usr/bin/env python3
"""Replay reviewed H-bridge geometry after the FPGA routing pass.

The sidecar records explicit copper/placement changes, including the gate-output
net correction. This is an idempotent replay, not an autoroute or a constructor.
Run the schematic generator, all routing audits and check_tesla_draft.py afterward.
"""
import json
from pathlib import Path
import pcbnew as p

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / 'boards/tesla-coil-controller'
recipe = json.loads(Path(__file__).with_name('tesla_hbridge_routing.json').read_text())
assert recipe['version'] == 1
board = p.LoadBoard(str(D / 'controller.kicad_pcb'))
assert board.GetCopperLayerCount() == 2
fps = {f.GetReference(): f for f in board.GetFootprints()}
nets = {n.GetNetname(): n for n in board.GetNetInfo().NetsByNetcode().values()}
for item in recipe['pad_nets']:
    name = item['net']
    if name not in nets:
        net = p.NETINFO_ITEM(board, name)
        board.Add(net)
        nets[name] = net

retired = []  # Keep removed SWIG wrappers alive through SaveBoard.
replace_ids = {item['uuid'] for item in recipe['copper']}
for t in list(board.GetTracks()):
    if t.m_Uuid.AsString() in replace_ids | set(recipe['retired_older_copper']):
        retired.append(t)
        board.Remove(t)

vec = lambda a: p.VECTOR2I(*a)
plan_path = ROOT / 'tools/hardware/tesla_placement.json'
plan = json.loads(plan_path.read_text())
parts = json.loads((D / 'docs/circuit.json').read_text())
for ref, item in recipe['placements'].items():
    f = fps[ref]
    f.SetOrientationDegrees(item['angle_deg'])
    f.SetPosition(vec(item['position_nm']))
    f.Reference().SetPosition(vec(item['reference_nm']))
    pos = [p.ToMM(v) for v in item['position_nm']] + [item['angle_deg']]
    plan['positions'][ref] = pos
    plan['reference_positions'][ref] = [p.ToMM(v) for v in item['reference_nm']]
    parts[ref]['position'] = pos
for item in recipe['pad_nets']:
    a = next(a for a in fps[item['ref']].Pads() if a.GetNumber() == item['pin'])
    a.SetNet(nets[item['net']])
    parts[item['ref']]['pins'][item['pin']] = item['net']
for item in recipe['thermal_spoke_angles']:
    a = next(a for a in fps[item['ref']].Pads() if a.GetNumber() == item['pin'])
    a.SetThermalSpokeAngle(p.EDA_ANGLE(item['angle_deg'], p.DEGREES_T))
drawings = {a.m_Uuid.AsString(): a for a in board.GetDrawings()}
for item in recipe['text_positions']:
    drawings[item['uuid']].SetPosition(vec(item['position_nm']))

created = []
for item in recipe['copper']:
    via = item['kind'] == 'via'
    t = p.PCB_VIA(board) if via else p.PCB_TRACK(board)
    t.SetNet(nets[item['net']])
    t.SetUuid(p.KIID(item['uuid']))
    t.SetWidth(item['width_nm'])
    if via:
        t.SetPosition(vec(item['start_nm']))
        t.SetDrill(item['drill_nm'])
        t.SetViaType(p.VIATYPE_THROUGH)
        t.SetLayerPair(p.F_Cu, p.B_Cu)
    else:
        t.SetStart(vec(item['start_nm']))
        t.SetEnd(vec(item['end_nm']))
        t.SetLayer({'F.Cu': p.F_Cu, 'B.Cu': p.B_Cu}[item['layer']])
    board.Add(t)
    created.append(t)
p.ZONE_FILLER(board).Fill(board.Zones())
p.SaveBoard(str(D / 'controller.kicad_pcb'), board)
plan_path.write_text(json.dumps(plan, indent=2) + '\n')
(D / 'docs/circuit.json').write_text(json.dumps(parts, indent=2) + '\n')
print(f'Replayed {len(created)} H-bridge/return copper objects; remaining board routing is still a draft.')
