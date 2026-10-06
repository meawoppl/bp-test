#!/usr/bin/env python3
"""Run with KiCad library tools root + src on PYTHONPATH.
TAI-TECH PDF pp2–3: pad envelope 4.8 x 3.8, gaps 2.5 x 0.7 mm;
pads 1.15 x 1.55 at (+/-1.825,+/-1.125). 1–2 and 4–3 are windings.
"""
from pathlib import Path
from KicadModTree import Footprint,FootprintType,Pad,Rectangle,Property,Line,Model,KicadFileHandler
D=Path(__file__).resolve().parents[2]/'boards/tesla-coil-controller'
name='CMC_TAI-TECH_WCM4532F2SF';f=Footprint(name,FootprintType.SMD)
f.setDescription('TAI-TECH WCM4532F2SF recommended land pattern, datasheet pp2-3; 1-2 and 4-3 windings; dots at 1/4')
f.append(Property('Reference','L',at=[0,-3],layer='F.SilkS'))
f.append(Property('Value',name,at=[0,3],layer='F.Fab'))
for n,x,y in [('1',-1.825,-1.125),('2',1.825,-1.125),('3',1.825,1.125),('4',-1.825,1.125)]:
 f.append(Pad(number=n,type=Pad.TYPE_SMT,shape=Pad.SHAPE_RECT,at=[x,y],size=[1.15,1.55],layers=Pad.LAYERS_SMT))
f.append(Rectangle(layer='F.Fab',width=.1,center=[0,0],size=[4.5,3.2]))
f.append(Rectangle(layer='F.CrtYd',width=.05,center=[0,0],size=[5.5,4.4]))
for y in [-2.1,2.1]:f.append(Line(start=[-2.25,y],end=[2.25,y],layer='F.SilkS',width=.12))
f.append(Line(start=[-2.65,-1.5],end=[-2.65,-.75],layer='F.SilkS',width=.12))
f.append(Model(filename='${KIPRJMOD}/3dmodels/WCM4532F2SF_envelope.step'))
KicadFileHandler(f).writeFile(str(D/'Tesla.pretty'/f'{name}.kicad_mod'))
(D/'3dmodels/WCM4532F2SF_envelope.wrl').write_text('#VRML V2.0 utf8\n# Nominal package envelope, not manufacturer CAD; millimetres / 2.54.\nTransform { scale 0.393700787 0.393700787 0.393700787 children [ Transform { translation 0 0 1.4 children [ Shape { appearance Appearance { material Material { diffuseColor 0.13 0.13 0.15 } } geometry Box { size 4.5 3.2 2.8 } } ] } ] }\n')
