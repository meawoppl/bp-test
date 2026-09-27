#!/usr/bin/env python3
"""HS96L03W2C03 module land pattern; run in KiCad Library Tools environment.
Dimensions: manufacturer drawing p6, body 27.30 x 27.80, 23.30 x23.80 hole grid.
Header centered, 4x2.54 pitch, 1.32 from top. Module mounted 3 mm above carrier.
"""
from pathlib import Path
from KicadModTree import Footprint,FootprintType,Property,Pad,Rectangle,Model,KicadFileHandler
D=Path(__file__).resolve().parents[2]/'boards/gps-time-calibrator'
f=Footprint('HS96L03W2C03_27.3x27.8mm',FootprintType.THT)
f.setDescription('HS OLED C5248080, 4-pin GND/VCC/SCL/SDA, manual assembly on 3mm spacers; vendor drawing p6')
f.append(Property(name='Reference',text='DS1',at=[0,15.4],layer='F.SilkS',size=[1,1],thickness=.15))
f.append(Property(name='Value',text='HS96L03W2C03',at=[0,16.9],layer='F.Fab',size=[1,1],thickness=.15))
for layer,margin,width in [('F.Fab',0,.1),('F.SilkS',.15,.12),('F.CrtYd',.5,.05)]:
 f.append(Rectangle(layer=layer,width=width,start=[-13.65-margin,-13.9-margin],end=[13.65+margin,13.9+margin]))
# Four signal holes use 1.1 mm drills for nominal 0.64 mm square header pins.
for n in range(1,5):f.append(Pad(number=n,type=Pad.TYPE_THT,shape=Pad.SHAPE_RECT if n==1 else Pad.SHAPE_CIRCLE,at=[-3.81+(n-1)*2.54,-12.58],size=[1.8,1.8],drill=1.1,layers=Pad.LAYERS_THT))
# Carrier holes: 2.7mm for M2 screws through module's 2.5mm holes; washers/spacers.
for x in [-11.65,11.65]:
 for y in [-11.9,11.9]:f.append(Pad(number='',type=Pad.TYPE_NPTH,shape=Pad.SHAPE_CIRCLE,at=[x,y],size=[2.7,2.7],drill=2.7,layers=Pad.LAYERS_NPTH))
f.append(Model('${KIPRJMOD}/3dmodels/HS96L03W2C03_envelope.step'))
KicadFileHandler(f).writeFile(str(D/'Calibrator.pretty/HS96L03W2C03_27.3x27.8mm.kicad_mod'))
