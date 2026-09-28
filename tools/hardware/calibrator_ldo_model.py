#!/usr/bin/env python3
"""Illustrative TI DCQ/SOT-223-6 envelope; drawing-derived, not vendor CAD.
Dimensions follow TPS7A45 DCQ package; footprint coordinates stay authoritative.
Run using tmp/models/venv/bin/python.
"""
from pathlib import Path
import cadquery as cq
D=Path(__file__).resolve().parents[2]/'boards/gps-time-calibrator/3dmodels'
a=cq.Assembly(name='DCQ_SOT223_6_drawing_derived')
a.add(cq.Workplane('XY').box(3.5,6.5,1.55).translate((0,0,.925)),name='body',color=cq.Color(.08,.08,.09))
for n,y in enumerate([2.54,1.27,0,-1.27,-2.54],1):
 a.add(cq.Workplane('XY').box(1.95,.45,.2).translate((-2.7,y,.1)),name=f'pin_{n}',color=cq.Color(.72,.73,.75))
a.add(cq.Workplane('XY').box(2.05,3,.2).translate((2.7,0,.1)),name='ground_tab',color=cq.Color(.72,.73,.75))
a.add(cq.Workplane('XY').center(-1,2.5).circle(.22).extrude(.01).translate((0,0,1.7)),name='pin1_dot',color=cq.Color(.8,.8,.8))
a.save(str(D/'SOT-223-6.step'))
