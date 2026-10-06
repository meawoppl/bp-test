#!/usr/bin/env python3
"""Replay the current reviewed Tesla copper without resurrecting old ARM logic.

This fixed two-layer recipe supersedes the historical incremental routing passes.
It requires the matching circuit contract and existing footprints/ground zones;
it is not an autorouter, constructor, or a fabrication-release declaration.
"""
import hashlib
import json
from pathlib import Path
import pcbnew as p

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / 'boards/tesla-coil-controller'
recipe = json.loads(Path(__file__).with_name('tesla_reviewed_routing.json').read_text())
parts = json.loads((D / 'docs/circuit.json').read_text())
contract = json.dumps({r: c['pins'] for r, c in parts.items()}, sort_keys=True).encode()
assert hashlib.sha256(contract).hexdigest() == recipe['net_contract_sha256'], 'Circuit changed; review and refresh routing recipe first'
board = p.LoadBoard(str(D / 'controller.kicad_pcb'))
assert board.GetCopperLayerCount() == 2
project_bytes = (D / 'controller.kicad_pro').read_bytes()
retired = []
for f in list(board.GetFootprints()):
    if f.GetReference() not in parts:
        assert f.GetReference() in recipe['removed_footprints']
        retired.append(f)
        board.Remove(f)
fps = {f.GetReference(): f for f in board.GetFootprints()}
assert set(fps) == set(parts)
nets = {n.GetNetname(): n for n in board.GetNetInfo().NetsByNetcode().values()}
for name in {t['net'] for t in recipe['copper']} | {a['net'] for a in recipe['pads'] if a['net']}:
    if name not in nets:
        n = p.NETINFO_ITEM(board, name)
        board.Add(n)
        nets[name] = n
vec = lambda q: p.VECTOR2I(*q)
for ref, item in recipe['placements'].items():
    f = fps[ref]
    assert (str(f.GetFPID().GetLibNickname())+':'+str(f.GetFPID().GetLibItemName())) == item['footprint'], f'{ref}: footprint changed; review routing again'
    f.SetOrientationDegrees(item['angle_deg'])
    f.SetPosition(vec(item['position_nm']))
    f.Reference().SetPosition(vec(item['reference_nm']))
    if 'value' in item:
        f.SetValue(item['value'])
for item in recipe['pads']:
    # USB-C repeats shield pad S1 and some stacked contact numbers.
    pads = [a for a in fps[item['ref']].Pads() if a.GetNumber() == item['pin']]
    assert pads, f"Missing pad {item['ref']}.{item['pin']}"
    for a in pads:
        if item['net']:
            a.SetNet(nets[item['net']])
        else:
            a.SetNetCode(0)
        a.SetThermalSpokeAngle(p.EDA_ANGLE(item['thermal_angle_deg'], p.DEGREES_T))
for t in list(board.GetTracks()):
    retired.append(t)
    board.Remove(t)
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
(D / 'controller.kicad_pro').write_bytes(project_bytes)
print(f'Replayed {len(created)} reviewed copper objects. Board remains a routing draft.')
