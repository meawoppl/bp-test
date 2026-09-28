#!/usr/bin/env python3
"""Drawing-derived HUSB238 DFN-10 envelope; run with tmp/models/venv/bin/python."""
from pathlib import Path
import cadquery as cq
D=Path(__file__).resolve().parents[2]/'boards/gps-time-calibrator/3dmodels'
a=cq.Assembly(name='HUSB238_DFN10_drawing_derived')
a.add(cq.Workplane('XY').box(3,3,.7).translate((0,0,.4)),name='body',color=cq.Color(.08,.08,.09))
for x in [-1.3,1.3]:
 for y in [-1,-.5,0,.5,1]:a.add(cq.Workplane('XY').box(.4,.25,.1).translate((x,y,.05)),name=f'lead_{x}_{y}',color=cq.Color(.75,.75,.77))
a.add(cq.Workplane('XY').box(1.7,2.4,.1).translate((0,0,.05)),name='EP',color=cq.Color(.75,.75,.77))
a.add(cq.Workplane('XY').center(-1,1).circle(.18).extrude(.01).translate((0,0,.75)),name='pin1',color=cq.Color(.75,.75,.75))
a.save(str(D/'HUSB238_DFN10_envelope.step'))
