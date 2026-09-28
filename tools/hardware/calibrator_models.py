#!/usr/bin/env python3
"""Attach installed KiCad STEP models and the audited Hirose mating models."""
from pathlib import Path
import pcbnew as p,re,shutil
R=Path(__file__).resolve().parents[2];D=R/'boards/gps-time-calibrator';b=p.LoadBoard(str(D/'calibrator.kicad_pcb'))
for f in b.GetFootprints():
 name=str(f.GetFPID().GetLibItemName());lib=p.FootprintLoad(str(D/'Calibrator.pretty'),name)
 if len(list(lib.Models()))==0:
  matches=list(Path('/usr/share/kicad/footprints').glob('*.pretty/'+name+'.kicad_mod'))
  if matches:
   src=p.FootprintLoad(str(matches[0].parent),name)
   for old in src.Models():
    path=Path(re.sub(r'\$\{KICAD\d+_3DMODEL_DIR\}','/usr/share/kicad/3dmodels',old.m_Filename)).with_suffix('.step')
    if path.exists():
     shutil.copy2(path,D/'3dmodels'/path.name);m=p.FP_3DMODEL();m.m_Filename='${KIPRJMOD}/3dmodels/'+path.name;m.m_Offset=old.m_Offset;m.m_Rotation=old.m_Rotation;m.m_Scale=old.m_Scale;lib.Add3DModel(m)
 if f.GetReference()=='J3' and (D/'3dmodels/HRO_TYPE-C-31-M-12.step').exists():
  lib.Models().clear();m=p.FP_3DMODEL();m.m_Filename='${KIPRJMOD}/3dmodels/HRO_TYPE-C-31-M-12.step';lib.Add3DModel(m)
 if f.GetReference()=='SW1' and (D/'3dmodels/CK_JS102011SAQN_envelope.step').exists():
  lib.Models().clear();m=p.FP_3DMODEL();m.m_Filename='${KIPRJMOD}/3dmodels/CK_JS102011SAQN_envelope.step';lib.Add3DModel(m)
 if f.GetReference()=='Y1' and (D/'3dmodels/AOC97_10MHz_drawing_derived.step').exists():
  lib.Models().clear();m=p.FP_3DMODEL();m.m_Filename='${KIPRJMOD}/3dmodels/AOC97_10MHz_drawing_derived.step';lib.Add3DModel(m)
 envelopes={'U11':'HUSB238_DFN10_envelope','U14':'TPS2595_WSON_envelope','L1':'Coilcraft_0805CS_envelope'}
 if f.GetReference() in envelopes:
  path=D/'3dmodels'/(envelopes[f.GetReference()]+'.step')
  if path.exists():
   lib.Models().clear();m=p.FP_3DMODEL();m.m_Filename='${KIPRJMOD}/3dmodels/'+path.name;lib.Add3DModel(m)
 # New standard footprints already have model entries; localize those as well.
 models=list(lib.Models())
 lib.Models().clear()
 for m in models:
  path=Path(re.sub(r'\$\{KICAD\d+_3DMODEL_DIR\}','/usr/share/kicad/3dmodels',m.m_Filename)).with_suffix('.step')
  if path.is_absolute() and path.exists():
   shutil.copy2(path,D/'3dmodels'/path.name)
   m.m_Filename='${KIPRJMOD}/3dmodels/'+path.name
  lib.Add3DModel(m)
 f.Models().clear()
 for m in lib.Models():f.Add3DModel(m)
 p.PCB_IO_KICAD_SEXPR().FootprintSave(str(D/'Calibrator.pretty'),lib)
p.SaveBoard(str(D/'calibrator.kicad_pcb'),b)
print('Missing models:',[(f.GetReference(),str(f.GetFPID().GetLibItemName())) for f in b.GetFootprints() if not list(f.Models()) and not f.GetReference().startswith('H')])
