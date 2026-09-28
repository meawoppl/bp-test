#!/usr/bin/env python3
"""Illustrative HS OLED envelope, native KiCad axes; 3mm carrier standoff."""
from pathlib import Path
import cadquery as cq
D=Path(__file__).resolve().parents[2]/'boards/gps-time-calibrator/3dmodels'
a=cq.Assembly(name='HS96L03W2C03_envelope')
pcb=cq.Workplane('XY').box(27.3,27.8,1.2).translate((0,0,3.6))
for x in [-11.65,11.65]:
 for y in [-11.9,11.9]:pcb=pcb.cut(cq.Workplane('XY').center(x,y).circle(1.25).extrude(10))
for x in [-11.65,11.65]:
 for y in [-11.9,11.9]:
  a.add(cq.Workplane('XY').center(x,y).circle(2).circle(1.1).extrude(3),name=f'spacer_{x}_{y}',color=cq.Color(.08,.08,.08))
a.add(pcb,name='module_pcb',color=cq.Color(.04,.15,.32))
a.add(cq.Workplane('XY').box(24.744,16.9,1.45).translate((0,1.015,4.925)),name='glass',color=cq.Color(.045,.045,.05))
a.add(cq.Workplane('XY').box(21.744,10.864,.03).translate((0,3.598,5.665)),name='active_area',color=cq.Color(.12,.15,.18))
a.save(str(D/'HS96L03W2C03_envelope.step'))
# Separate header, centered on its own footprint; nominal untrimmed manufacturer geometry.
h=cq.Assembly(name='OLED_Header_1x04')
h.add(cq.Workplane('XY').box(10.16,2.54,2.54).translate((0,0,1.27)),name='insulator',color=cq.Color(.08,.08,.08))
for i in range(4):h.add(cq.Workplane('XY').box(.64,.64,11.54).translate((-3.81+i*2.54,0,2.77)),name='pin_'+str(i+1),color=cq.Color(.8,.7,.35))
h.save(str(D/'OLED_Header_1x04.step'))
