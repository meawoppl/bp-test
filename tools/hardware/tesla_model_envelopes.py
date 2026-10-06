#!/usr/bin/env python3
"""STEP visual envelopes from local manufacturer drawings; not vendor-certified CAD.
Run with tmp/models/venv/bin/python. Coordinates mm, Y inverted from KiCad.
"""
from pathlib import Path
import cadquery as cq
D=Path(__file__).resolve().parents[2]/'boards/tesla-coil-controller/3dmodels'
def block(a,name,xyz,size,color):
 a.add(cq.Workplane('XY').box(*size).translate(xyz),name=name,color=cq.Color(*color))
black=(.10,.11,.13);silver=(.72,.74,.76)
a=cq.Assembly(name='LMZ14202H_NDW_drawing_envelope')
# TI NDW0007A: nominal 9.85x10.16 body, total 13.77 including leads, 4.57 high.
# This footprint has the lead row to the left. Pad 1 is top-left.
block(a,'molded_body',(0,0,2.485),(9.85,10.16,4.17),black)
block(a,'exposed_ground',(-.355,0,.2),(8.54,5.35,.4),silver)
for i in range(7):
 y=3.81-i*1.27
 block(a,f'lead_{i+1}',(-6.885,y,.135),(3.92,.69,.27),silver)
a.add(cq.Workplane('XY').center(-3.8,3.8).circle(.35).extrude(.02).translate((0,0,4.57)),name='pin1',color=cq.Color(.85,.85,.86))
a.export(str(D/'LMZ14202H_envelope.step'))
a=cq.Assembly(name='WCM4532F2SF_drawing_envelope')
# TAI-TECH p2 nominal overall 4.5x3.2x2.8; simplified ferrite and four terminals.
block(a,'ferrite',(0,0,1.5),(4.5,3.2,2.6),black)
for n,x,y in [(1,-1.75,1),(2,1.75,1),(3,1.75,-1),(4,-1.75,-1)]:
 block(a,f'terminal_{n}',(x,y,.1),(1,1.2,.2),silver)
a.add(cq.Workplane('XY').center(-1.7,1).circle(.14).extrude(.01).translate((0,0,2.8)),name='pin1',color=cq.Color(.85,.85,.86))
a.export(str(D/'WCM4532F2SF_envelope.step'))
print('Created two drawing-derived STEP envelopes')
