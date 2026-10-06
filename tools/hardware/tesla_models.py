#!/usr/bin/env python3
"""Keep all fitted Tesla components on portable project-local STEP models.
KiCad SWIG returns model copies: reattach after editing, rather than mutating
iteration values and silently keeping the original system-library paths.
"""
from pathlib import Path
import json,re,shutil,hashlib
import pcbnew as p
D=Path(__file__).resolve().parents[2]/'boards/tesla-coil-controller'
def localize(f):
 models=list(f.Models())
 for m in models:
  src=Path(re.sub(r'\$\{KICAD\d+_3DMODEL_DIR\}','/usr/share/kicad/3dmodels',m.m_Filename).replace('${KIPRJMOD}',str(D)))
  if src.suffix.lower()=='.wrl' and src.with_suffix('.step').exists():src=src.with_suffix('.step')
  assert src.is_file(),(f.GetReference(),src)
  dst=D/'3dmodels'/src.name
  if src.resolve()!=dst.resolve():shutil.copy2(src,dst)
  m.m_Filename='${KIPRJMOD}/3dmodels/'+dst.name
 f.Models().clear()
 for m in models:f.Add3DModel(m)
def geometry(b):
 return sorted((f.GetReference(),str(f.GetFPID().GetLibNickname())+':'+str(f.GetFPID().GetLibItemName()),f.GetPosition().x,f.GetPosition().y,f.GetOrientationDegrees(),sorted((a.GetNumber(),a.GetPosition().x,a.GetPosition().y,a.GetNetname()) for a in f.Pads())) for f in b.GetFootprints())
def run():
 b=p.LoadBoard(str(D/'controller.kicad_pcb'));before=geometry(b)
 for path in sorted((D/'Tesla.pretty').glob('*.kicad_mod')):
  f=p.FootprintLoad(str(path.parent),path.stem)
  # Obsolete library-only footprints are not needed for current model coverage.
  if path.stem not in {str(q.GetFPID().GetLibItemName()) for q in b.GetFootprints()}:continue
  localize(f);p.PCB_IO_KICAD_SEXPR().FootprintSave(str(path.parent),f)
 for f in b.GetFootprints():localize(f)
 assert geometry(b)==before,'Model-only update changed copper/placement'
 p.SaveBoard(str(D/'controller.kicad_pcb'),b)
 rows=[]
 for f in sorted(b.GetFootprints(),key=lambda f:f.GetReference()):
  mods=[m.m_Filename for m in f.Models()]
  excluded=f.GetReference().startswith(('H','TP'))
  assert mods or excluded,('Missing component model',f.GetReference())
  assert all(x.endswith('.step') for x in mods),mods
  rows.append(dict(reference=f.GetReference(),footprint=str(f.GetFPID().GetLibNickname())+':'+str(f.GetFPID().GetLibItemName()),models=mods,status='bare PCB feature' if excluded else 'drawing-derived envelope' if any('envelope' in x for x in mods) else 'STEP package model'))
 report=dict(footprints=len(rows),modeled_components=sum(bool(x['models']) for x in rows),bare_pcb_features=sum(not x['models'] for x in rows),missing_components=[],rows=rows)
 (D/'docs/3d-model-audit.json').write_text(json.dumps(report,indent=2)+'\n')
 print({k:v for k,v in report.items() if k!='rows'})
if __name__=='__main__':run()
