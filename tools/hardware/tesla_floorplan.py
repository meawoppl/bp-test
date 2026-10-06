#!/usr/bin/env python3
"""Apply reviewed connector-led placement from tesla_placement.json.
No net changes. Refuses to move a routed board. Region silk explicitly requested.
"""
from pathlib import Path
import json,pcbnew as p
D=Path(__file__).resolve().parents[2]/'boards/tesla-coil-controller'
PLAN=Path(__file__).with_name('tesla_placement.json')
v=lambda x,y:p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def apply(b,parts):
 assert not b.GetTracks(),'Reconcile routing before changing placement'
 plan=json.loads(PLAN.read_text());fps={f.GetReference():f for f in b.GetFootprints()}
 assert set(fps)==set(plan['positions'])==set(parts),'Placement table must cover every footprint'
 for r,(x,y,a) in plan['positions'].items():
  f=fps[r];f.SetOrientationDegrees(a);f.SetPosition(v(x,y));parts[r]['position']=[x,y,a]
  ref=f.Reference();ref.SetVisible(r.startswith(('U','J')));ref.SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T))
  ref.SetTextSize(v(1,1));ref.SetTextThickness(p.FromMM(.15));ref.SetPosition(v(x,y-5))
 retired=list(b.GetDrawings())
 for d in retired:
  if d.GetLayer() in [p.F_SilkS,p.Dwgs_User,p.Edge_Cuts]:b.Remove(d)
 def line(a,z,layer=p.F_SilkS):
  d=p.PCB_SHAPE();d.SetShape(p.SHAPE_T_SEGMENT);d.SetStart(v(*a));d.SetEnd(v(*z));d.SetWidth(p.FromMM(.15));d.SetLayer(layer);b.Add(d)
 def text(s,x,y,layer=p.F_SilkS):
  t=p.PCB_TEXT(b);t.SetText(s);t.SetPosition(v(x,y));t.SetLayer(layer);t.SetTextSize(v(.9,.9));t.SetTextThickness(p.FromMM(.15));b.Add(t)
 x0,y0,x1,y1=plan.get('board_bounds',[20,20,252,200])
 for a,z in [((x0,y0),(x1,y0)),((x1,y0),(x1,y1)),((x1,y1),(x0,y1)),((x0,y1),(x0,y0))]:line(a,z,p.Edge_Cuts)
 for reg in plan['regions']:
  x0,y0,x1,y1=reg['bounds']
  points=reg.get('outline_points',[(x0,y0),(x1,y0),(x1,y1),(x0,y1),(x0,y0)])
  edges=list(zip(points,points[1:]))
  for a,z in ([] if reg.get('no_outline') else edges[1:] if reg.get('open_top') else edges):line(a,z)
  text(reg['name'],*reg.get('label_position',[(x0+x1)/2,y0+2]))
 for spec in plan.get('indicator_labels',[]):
  t=p.PCB_TEXT(b);t.SetText(spec['text']);t.SetTextAngle(p.EDA_ANGLE(spec.get('angle',0),p.DEGREES_T));t.SetPosition(v(*spec['position']));t.SetLayer(p.F_SilkS);size=spec.get('text_height_mm',.8);t.SetTextSize(v(size,size));t.SetTextThickness(p.FromMM(spec.get('text_thickness_mm',.12)));b.Add(t)
 x0,y0,x1,y1=plan['module_envelope']
 for a,z in [((x0,y0),(x1,y0)),((x1,y0),(x1,y1)),((x1,y1),(x0,y1)),((x0,y1),(x0,y0))]:line(a,z,p.Dwgs_User)
 text('MODULE v1 / 2 mm mating gap',(x0+x1)/2,y1+2.3,p.Dwgs_User)
 # Reference positions are independent of package rotation, outside dense support clusters.
 rp=plan['reference_positions'].copy()
 for r,(x,y) in rp.items():fps[r].Reference().SetPosition(v(x,y))
 (D/'docs/floorplan-regions.json').write_text(json.dumps(plan['regions'],indent=2)+'\n')
 return plan['regions']
if __name__=='__main__':
 b=p.LoadBoard(str(D/'controller.kicad_pcb'));parts=json.loads((D/'docs/circuit.json').read_text());apply(b,parts)
 p.SaveBoard(str(D/'controller.kicad_pcb'),b);(D/'docs/circuit.json').write_text(json.dumps(parts,indent=2)+'\n')
