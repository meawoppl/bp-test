#!/usr/bin/env python3
"""Normalize downloaded HRO CAD and construct drawing-derived AOC97 10 MHz model."""
from pathlib import Path
import cadquery as cq
D=Path(__file__).resolve().parents[2]/'boards/gps-time-calibrator/3dmodels'
# Original has X 0..8.94 and insertion axis -Z. Pegs become (+/-2.89,+2.6)
# in model axes, corresponding to footprint (+/-2.89,-2.6).
u=cq.importers.importStep(str(D/'vendor/HRO_TYPE-C-31-M-12_original.step'))
u=u.rotate((0,0,0),(1,0,0),90).translate((-4.47,-3.65,0))
a=cq.Assembly(name='HRO_TYPE_C_31_M_12');a.add(u,name='connector',color=cq.Color(.7,.72,.75));a.save(str(D/'HRO_TYPE-C-31-M-12.step'))
# Abracon AOC97 drawing p4: 10 MHz variant, 9.7 x 7.5 x 3.9 mm,
# pad centers 6 x 4 mm, terminal diameter 1.5. Cosmetic seam/radii/text are
# illustrative; model is not vendor STEP nor an enclosure tolerance authority.
a=cq.Assembly(name='AOC97_10MHz_drawing_derived')
base=cq.Workplane('XY').box(9.7,7.5,.2).translate((0,0,.3))
a.add(base,name='base',color=cq.Color(.24,.25,.27))
can=cq.Workplane('XY').box(9.7,7.5,3.5).edges('|Z').fillet(.45).translate((0,0,2.15))
a.add(can,name='can',color=cq.Color(.68,.7,.73))
for i,(x,y) in enumerate([(-3,-2),(3,-2),(3,2),(-3,2)],1):
 a.add(cq.Workplane('XY').center(x,y).circle(.75).extrude(.2),name=f'terminal_{i}',color=cq.Color(.8,.72,.4))
a.add(cq.Workplane('XY').center(-3.7,-2.6).circle(.22).extrude(.015).translate((0,0,3.9)),name='pin1',color=cq.Color(.08,.08,.08))
for text,y,size in [('ABRACON',.8,1.0),('10.000',-.8,.85)]:
 a.add(cq.Workplane('XY').text(text,size,.012).translate((0,y,3.9)),name=text,color=cq.Color(.12,.12,.12))
a.save(str(D/'AOC97_10MHz_drawing_derived.step'))
