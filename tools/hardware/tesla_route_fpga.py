#!/usr/bin/env python3
"""Replay the reviewed FPGA copper after CST, power and AUX routing.

The sidecar contains fixed, validated geometry rather than a fresh autoroute.
Only this step's owned copper and explicitly recorded placements/overrides change.
Run check_tesla_fpga_routing.py and check_tesla_draft.py after replaying.
"""
import json
import uuid
from pathlib import Path
import pcbnew as p

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / 'boards/tesla-coil-controller'
recipe = json.loads(Path(__file__).with_name('tesla_fpga_routing.json').read_text())
assert recipe['version'] == 1
board = p.LoadBoard(str(D / 'controller.kicad_pcb'))
assert board.GetCopperLayerCount() == 2
assert board.FindFootprintByReference('U80'), 'Historical buffer-era recipe; use tesla_route_reviewed.py on the current board'
fps = {f.GetReference(): f for f in board.GetFootprints()}
nets = {n.GetNetname(): n for n in board.GetNetInfo().NetsByNetcode().values()}
layers = {'F.Cu': p.F_Cu, 'B.Cu': p.B_Cu}
owned = {str(uuid.uuid5(uuid.NAMESPACE_URL, f'{namespace}/{i}'))
         for namespace in ('bp-tesla-fpga-routing', 'bp-tesla-fpga-completion', 'bp-tesla-fpga-finishing')
         for i in range(8000)}
retired = []  # Keep SWIG wrappers alive through SaveBoard.
for t in list(board.GetTracks()):
    if t.m_Uuid.AsString() in owned | set(recipe['retired_older_copper']):
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
for a in fps['J2'].Pads():
    if a.GetNumber() in recipe['j2_pin_nets']:
        name = recipe['j2_pin_nets'][a.GetNumber()]
        a.SetNet(nets[name])
        parts['J2']['pins'][a.GetNumber()] = name
for item in recipe['thermal_spoke_angles']:
    pad = next(a for a in fps[item['ref']].Pads() if a.GetNumber() == item['pin'])
    pad.SetThermalSpokeAngle(p.EDA_ANGLE(item['angle_deg'], p.DEGREES_T))

def configure(t, item):
    t.SetNet(nets[item['net']])
    t.SetUuid(p.KIID(item['uuid']))
    t.SetWidth(item['width_nm'])
    if item['kind'] == 'via':
        t.SetPosition(vec(item['start_nm']))
        t.SetDrill(item['drill_nm'])
        t.SetViaType(p.VIATYPE_THROUGH)
        t.SetLayerPair(p.F_Cu, p.B_Cu)
    else:
        t.SetStart(vec(item['start_nm']))
        t.SetEnd(vec(item['end_nm']))
        t.SetLayer(layers[item['layer']])

existing = {t.m_Uuid.AsString(): t for t in board.GetTracks()}
for item in recipe['existing_copper_overrides']:
    assert item['uuid'] in existing, 'Apply the CST/power routing passes first'
    configure(existing[item['uuid']], item)
created = []
for item in recipe['copper']:
    t = p.PCB_VIA(board) if item['kind'] == 'via' else p.PCB_TRACK(board)
    configure(t, item)
    board.Add(t)
    created.append(t)
p.ZONE_FILLER(board).Fill(board.Zones())
p.SaveBoard(str(D / 'controller.kicad_pcb'), board)
plan_path.write_text(json.dumps(plan, indent=2) + '\n')
(D / 'docs/circuit.json').write_text(json.dumps(parts, indent=2) + '\n')
print(f'Replayed {len(created)} FPGA copper objects; board remains a routing draft.')
