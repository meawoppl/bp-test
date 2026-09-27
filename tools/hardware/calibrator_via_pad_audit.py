#!/usr/bin/env python3
"""Read-only native rotated-pad audit: kct currently misinterprets several rotations.
Requires pcbnew and shapely. A 0.05 mm margin around the drill is included.
"""
import json,hashlib
from pathlib import Path
D=Path(__file__).resolve().parents[2]/"boards/gps-time-calibrator"
findings=[]
import pcbnew as p
from shapely.geometry import Polygon,Point
b=p.LoadBoard(str(D/'calibrator.kicad_pcb'));xy=lambda v:(p.ToMM(v.x),p.ToMM(v.y))
ps=[]
for f in b.GetFootprints():
 for q in f.Pads():
  if q.GetAttribute()!=p.PAD_ATTRIB_SMD:continue
  z=q.GetEffectivePolygon(q.GetLayer());o=z.Outline(0)
  poly=Polygon([xy(o.CPoint(k)) for k in range(o.PointCount())]);ps.append((f.GetReference(),q.GetNumber(),q.GetNetname(),poly))
for t in b.GetTracks():
 if not isinstance(t,p.PCB_VIA):continue
 g=Point(xy(t.GetPosition())).buffer(p.ToMM(t.GetDrillValue())/2+.05)
 for ref,n,net,poly in ps:
  if g.intersects(poly):findings.append({'ref':ref,'pad':n,'pad_net':net,'via_mm':xy(t.GetPosition()),'via_net':t.GetNetname(),'uuid':t.m_Uuid.AsString()})

report={"pcb_sha256":hashlib.sha256((D/"calibrator.kicad_pcb").read_bytes()).hexdigest(),"drill_to_pad_margin_mm":0.05,"findings":findings}
(D/"fab/checks/native-via-pad.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2))
raise SystemExit(bool(findings))
