"""Read-only scope/connectivity audit for the series-battery annotation.

Native DRC checks clearance; this audit checks pad membership and change scope,
which KCT's whole-board check does not report. Run from the workspace root.
"""
from pathlib import Path
import hashlib, json, math
import pcbnew as p

D = Path('boards/tesla-coil-controller')
T = Path('tmp/tesla-series-battery')
B = T / 'before'
xy = lambda v: [v.x, v.y]
load = lambda f: json.loads(Path(f).read_text())
boards = [p.LoadBoard(str(f)) for f in [B/D/'controller.kicad_pcb', D/'controller.kicad_pcb']]

def copper(b):
    rows = {}
    for t in b.GetTracks():
        v = dict(uuid=t.m_Uuid.AsString(), net=t.GetNetname(), start_nm=xy(t.GetStart()), end_nm=xy(t.GetEnd()), layer=b.GetLayerName(t.GetLayer()))
        v.update(dict(kind='via', width_nm=t.GetWidth(p.F_Cu), drill_nm=t.GetDrillValue()) if isinstance(t, p.PCB_VIA) else dict(kind='track', width_nm=t.GetWidth()))
        rows[v['uuid']] = v
    return rows

def clusters(b):
    b.BuildConnectivity()
    c = b.GetConnectivity()
    pads = {a.m_Uuid.AsString(): (f.GetReference()+'.'+a.GetNumber(), a) for f in b.GetFootprints() for a in f.Pads() if a.GetNetname()}
    pending = set(pads)
    result = {}
    while pending:
        u = next(iter(pending))
        members = ({a.m_Uuid.AsString() for a in c.GetConnectedItems(pads[u][1])} | {u}) & pads.keys()
        pending -= members
        net = pads[u][1].GetNetname()
        assert {pads[v][1].GetNetname() for v in members} == {net}
        result.setdefault(net, set()).add(tuple(sorted(pads[v][0] for v in members)))
    return result

old, new = map(copper, boards)
removed = {u:v for u,v in old.items() if u not in new}
added = {u:v for u,v in new.items() if u not in old}
assert len(removed) == 3 and len(added) == 4
assert all(old[u] == new[u] for u in old.keys() & new.keys())
assert {v['net'] for v in removed.values()} == {'VBAT_24V'}
assert {v['net'] for v in added.values()} == {'VBAT_24V', 'BAT_MID_12V'}
assert all(v['kind'] == 'track' and v['layer'] == 'F.Cu' for v in added.values())
mid = [v for v in new.values() if v['net'] == 'BAT_MID_12V']
assert len(mid) == 1 and mid[0]['width_nm'] == 2500000
assert {tuple(mid[0][k]) for k in ['start_nm','end_nm']} == {(27500000,44080000),(27500000,51000000)}
for t in added.values():
    dx, dy = [abs(a-b) for a,b in zip(t['start_nm'],t['end_nm'])]
    assert max(dx,dy)>0 and (min(dx,dy)<2 or abs(dx-dy)<2)

def pads(b):
    return {f.GetReference()+'.'+a.GetNumber(): (a.GetNetname(), xy(a.GetPosition()), xy(a.GetSize()), xy(a.GetDrillSize()), a.GetOrientationDegrees(), str(a.GetLayerSet().FmtHex()), str(a.GetShape()), a.GetThermalSpokeAngle().AsDegrees()) for f in b.GetFootprints() for a in f.Pads()}
op,np = map(pads, boards)
changed = {k for k in op if op[k]!=np[k]}
assert changed == {'J4.2','J30.1'}
assert all(op[k][1:-1] == np[k][1:-1] for k in changed)
assert op['J4.2'][0] == 'GND' and op['J30.1'][0] == 'VBAT_24V'
assert all(np[k][0]=='BAT_MID_12V' for k in changed)

def placements(b):
    return {f.GetReference(): [xy(f.GetPosition()), f.GetOrientationDegrees(), xy(f.Reference().GetPosition()), f.Reference().IsVisible(), str(f.GetFPID().GetLibNickname())+":"+str(f.GetFPID().GetLibItemName())] for f in b.GetFootprints()}
assert placements(boards[0]) == placements(boards[1])
values = [{f.GetReference():f.GetValue() for f in b.GetFootprints()} for b in boards]
assert {k for k in values[0] if values[0][k]!=values[1][k]} == {'J4','J30'}
assert values[1]['J4']=='12V BATTERY / UPPER' and values[1]['J30']=='12V BATTERY / LOWER'
assert (B/D/'controller.kicad_pro').read_bytes() == (D/'controller.kicad_pro').read_bytes()

bc,ac = map(clusters,boards)
assert all(b.GetConnectivity().GetUnconnectedCount(False)==0 for b in boards)
assert ac['BAT_MID_12V'] == {('J30.1','J4.2')}
for n in ['GND','VBAT_24V']:
    assert len(bc[n])==len(ac[n])==1
    expected = set(next(iter(bc[n]))) - ({'J4.2'} if n=='GND' else {'J30.1'})
    assert set(next(iter(ac[n])))==expected
assert 'R304.1' in next(iter(ac['VBAT_24V']))
assert {k:v for k,v in bc.items() if k not in ['GND','VBAT_24V']} == {k:v for k,v in ac.items() if k not in ['GND','VBAT_24V','BAT_MID_12V']}

before,after = [load(f) for f in [B/D/'docs/circuit.json',D/'docs/circuit.json']]
assert {r for r in before if before[r]!=after[r]} == {'J4','J30'}
assert after['J4']['pins']=={'1':'VBAT_24V','2':'BAT_MID_12V'}
assert after['J30']['pins']=={'1':'BAT_MID_12V','2':'GND'}
for r,c in after.items():
    actual = {a.GetNumber(): (None if not a.GetNetname() or a.GetNetname().startswith('unconnected-') else a.GetNetname()) for f in boards[1].GetFootprints() if f.GetReference()==r for a in f.Pads() if a.GetNumber()}
    assert actual == c['pins'], r
recipe=load('tools/hardware/tesla_reviewed_routing.json')
assert {t['uuid']:t for t in recipe['copper']}==new
assert recipe['net_contract_sha256']==hashlib.sha256(json.dumps({r:c['pins'] for r,c in after.items()},sort_keys=True).encode()).hexdigest()

erc=json.loads(load(T/'erc-after.json')['report'])
drc=json.loads(load(T/'drc-after.json')['report'])
assert all(not s['violations'] for s in erc['sheets'])
assert all(not drc[k] for k in ['violations','unconnected_items','schematic_parity'])
assert json.loads(load(T/'sync-after.json')['stdout'])['in_sync']
for f in ['midpoint-status','rail-status']:
    assert json.loads(load(T/(f+'.json'))['stdout'])['summary']['incomplete']==0
qd=load(T/'quality-delta.json')
assert not any(v['severity']=='error' for v in qd['added'])
assert all(v['type'] in ['mistake.bom_health.component_missing_manufacturer_part_number','optimize_traces.mergeable_segments'] for v in qd['added'])
assert {v['items'][0]['description'] for v in qd['added'] if v['severity']=='warning'}=={'J4','J30'}
quality=json.loads(load(T/'quality-after.json')['report'])['summary']
report=dict(annotation_created_at='2026-09-30T18:44:41.307Z',source_revision='7f950fdc4e6d7c96dfa8',
    midpoint_pads=['J4.2','J30.1'],midpoint_length_mm=6.92,midpoint_width_mm=2.5,midpoint_layer='F.Cu',
    exactly_two_pad_nets_changed=True,all_other_net_memberships_identical=True,all_placements_identical=True,
    all_unrelated_copper_identical=True,all_other_component_contracts_identical=True,project_rules_identical=True,
    uvlo_R304_remains_on_24V=True,recipe_matches_board=True,copper_removed=list(removed.values()),copper_added=list(added.values()),
    erc_violations=0,drc_violations=0,unconnected_items=0,schematic_parity_issues=0,schematic_in_sync=True,
    quality=quality,quality_new_errors=0,quality_existing_warnings_renamed=['J4','J30'],quality_warning_count_change=-6,
    visual_review=['Final battery schematic block','Native PCB copper: J4/J30 midpoint and R304 supply feed'],
    sha256={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in [D/'controller.kicad_sch',D/'controller.kicad_pcb',D/'controller.kicad_pro']})
(T/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS: series topology, isolation, UVLO feed, scope, contract, sync, ERC, DRC and quality delta')
