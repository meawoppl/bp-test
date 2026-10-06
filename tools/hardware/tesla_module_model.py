"""Illustrative TO-PMOD envelope from TI NDW dimensions; not vendor mechanical CAD."""
from pathlib import Path
D=Path(__file__).resolve().parents[2]/'boards/tesla-coil-controller/3dmodels'
s=['#VRML V2.0 utf8']
def box(x,y,z,dx,dy,dz,color):
 # KiCad VRML uses 0.1-inch units.
 vals=[v/2.54 for v in [x,y,z,dx,dy,dz]]
 s.append('Transform { translation %g %g %g children [ Shape { appearance Appearance { material Material { diffuseColor %s } } geometry Box { size %g %g %g } } ] }'%(*vals[:3],color,*vals[3:]))
box(0,0,2.42,9.85,10.16,4.3,'.12 .12 .14')
for i in range(7):box(-6.885,3.81-i*1.27,.135,3.92,.69,.27,'.75 .76 .78')
box(-3.8,3.8,4.58,.65,.65,.02,'.9 .9 .9')
(D/'LMZ14202H_envelope.wrl').write_text('\n'.join(s)+'\n')
