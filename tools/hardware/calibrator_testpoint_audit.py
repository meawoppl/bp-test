#!/usr/bin/env python3
"""Read-only native audit of probe access, labels and circuit/PCB agreement.
The general kct checks do not know the assembled module and OLED envelopes.
Run with the layout venv (pcbnew + shapely).
"""
import json,hashlib
from pathlib import Path
import pcbnew as p
from shapely.geometry import Point,box,Polygon
D=Path(__file__).resolve().parents[2]/'boards/gps-time-calibrator'
b=p.LoadBoard(str(D/'calibrator.kicad_pcb'));parts=json.loads((D/'docs/circuit.json').read_text());spec=json.loads((D/'docs/testpoints.json').read_text());findings=[]
xy=lambda v:(p.ToMM(v.x),p.ToMM(v.y))
def bbox(f):
 q=f.GetBoundingBox(False,False) if isinstance(f,p.FOOTPRINT) else f.GetBoundingBox()
 return box(p.ToMM(q.GetX()),p.ToMM(q.GetY()),p.ToMM(q.GetRight()),p.ToMM(q.GetBottom()))
def padshape(q):
 a=q.GetEffectivePolygon(q.GetLayer()).Outline(0)
 return Polygon([xy(a.CPoint(i)) for i in range(a.PointCount())])
fps={f.GetReference():f for f in b.GetFootprints()}
mechanics={'assembled_module':box(145,10,165,55),'assembled_OLED':box(133.35,74.1,160.65,102)}
for ref,f in fps.items():
 if not ref.startswith('TP'):mechanics[ref]=bbox(f)
rows=[]
assert not spec['missing']
assert len(spec['testpoints'])==31
assert not any(s['group'] in ['led','ground'] for s in spec['testpoints'])
for s in spec['testpoints']:
 f=fps[s['ref']];qs=list(f.Pads());assert len(qs)==1;q=qs[0]
 assert q.GetNetname()==s['net']==parts[s['ref']]['pins']['1']
 assert f.IsExcludedFromBOM() and f.IsExcludedFromPosFiles() and not parts[s['ref']]['bom']
 assert q.IsOnLayer(p.F_Cu) and q.IsOnLayer(p.F_Mask) and not q.IsOnLayer(p.F_Paste)
 assert f.Value().IsVisible() and f.Value().GetLayer()==p.F_SilkS and f.GetValue()==s['label']
 assert s['net'] not in ['USB_D+','USB_D-','GNSS_RF','USB_ILIM']
 pad=padshape(q);text=bbox(f.Value())
 for name,geom in mechanics.items():
  for kind,g in [('pad',pad),('label',text)]:
   if g.intersects(geom):findings.append({'ref':s['ref'],'kind':kind,'obstructed_by':name})
 rows.append({'ref':s['ref'],'label':s['label'],'net':s['net'],'position_mm':xy(q.GetPosition()),'diameter_mm':p.ToMM(q.GetSizeX()),'nearest_body_mm':round(min(pad.distance(g) for g in mechanics.values()),3)})
report={'pcb_sha256':hashlib.sha256((D/'calibrator.kicad_pcb').read_bytes()).hexdigest(),'count':len(rows),'findings':findings,'probe_points':rows,'notes':['Component courtyard/bounding rectangles and complete assembled module/OLED envelopes checked.','Native DRC separately checks mask/silkscreen and electrical clearances.','Bare copper only: no paste and no purchased or populated testpoint parts.']}
(D/'docs/testpoint-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'count':len(rows),'findings':findings},indent=2));raise SystemExit(bool(findings))
