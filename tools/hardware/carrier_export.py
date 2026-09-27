#!/usr/bin/env python3
"""Checked, repeatable carrier fabrication and assembly export."""
from pathlib import Path
import csv, subprocess, tempfile, zipfile, shutil, hashlib, json, math, re
R=Path(__file__).resolve().parents[2];D=R/'boards/programming-carrier';F=D/'fab';P=D/'carrier.kicad_pcb';S=D/'carrier.kicad_sch'
def run(*args): subprocess.run(list(map(str,args)),check=True)
def part_corrections(pcb):
 """JLCPCB corrections from footprint fields (footprint-local frame, KiCad +Y down).

 Returns ref -> (CPL rotation delta, CPL dx, CPL dy). A local offset maps to the
 board like a pad offset: bottom-side parts mirror local Y, then the footprint
 rotation applies; CPL Y is up. Bottom-side rotation deltas are mirrored."""
 out={}
 for block in re.split(r'\n\t\(footprint ',pcb.read_text())[1:]:
  field=lambda name:(m:=re.search(r'\(property "%s" "([^"]*)"'%name,block)) and m[1].strip()
  rot,pos=field('JLCPCB Rotation Offset'),field('JLCPCB Position Offset')
  if not rot and not pos:continue
  ref=field('Reference');at=re.search(r'\n\t\t\(at (\S+) (\S+?)(?: (\S+))?\)',block)
  theta=math.radians(float(at[3] or 0));bottom='\n\t\t(layer "B.Cu")' in block
  lx,ly=(float(v.strip().removesuffix('mm')) for v in pos.strip('()').split(',')) if pos else (0.0,0.0)
  if bottom:ly=-ly
  bx,by=lx*math.cos(theta)+ly*math.sin(theta),-lx*math.sin(theta)+ly*math.cos(theta)
  delta=float(rot.removesuffix('°')) if rot else 0.0
  out[ref]=(-delta if bottom else delta,round(bx,9)+0,round(-by,9)+0)
 return out
for sub in ['checks','gerbers','jlcpcb','bom']:(F/sub).mkdir(parents=True,exist_ok=True)
run('kicad-cli','sch','erc','--format','json','--exit-code-violations','-o',F/'checks/erc.json',S)
run('kicad-cli','pcb','drc','--schematic-parity','--refill-zones','--format','json','--exit-code-violations','-o',F/'checks/drc.json',P)
run('python3',R/'tools/hardware/carrier_bom.py')
with tempfile.TemporaryDirectory() as td:
 stage=Path(td)
 run('kicad-cli','pcb','export','gerbers','--layers','F.Cu,In1.Cu,In2.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,F.Paste,B.Paste,Edge.Cuts','--subtract-soldermask','--use-drill-file-origin','-o',str(stage)+'/',P)
 run('kicad-cli','pcb','export','drill','--format','excellon','--drill-origin','plot','--excellon-units','mm','--excellon-separate-th','-o',str(stage)+'/',P)
 files=sorted(x for x in stage.iterdir() if x.suffix in {'.gtl','.gbl','.g1','.g2','.gts','.gbs','.gto','.gbo','.gtp','.gbp','.gm1','.drl','.gbrjob'})
 assert any(x.suffix=='.g1' for x in files) and any(x.suffix=='.g2' for x in files)
 with zipfile.ZipFile(F/'gerbers/carrier-gerbers.zip','w',zipfile.ZIP_DEFLATED) as z:
  for f in files:
   shutil.copy2(f,F/'gerbers'/f.name);z.write(f,f.name)
run('kicad-cli','pcb','export','pos','--format','csv','--units','mm','--side','both','--exclude-dnp','--use-drill-file-origin','-o',F/'bom/carrier-native-positions.csv',P)
with (F/'jlcpcb/BOM_carrier.csv').open() as f:bom=list(csv.DictReader(f))
refs={r.strip() for row in bom for r in row['Designator'].split(',')}
part_by_ref={r.strip():row['LCSC Part #'] for row in bom for r in row['Designator'].split(',')}
corrections=part_corrections(P)
with (F/'bom/carrier-native-positions.csv').open() as f:positions=[r for r in csv.DictReader(f) if r['Ref'] in refs]
assert {r['Ref'] for r in positions}==refs and len(positions)==len(refs)
with (F/'jlcpcb/CPL_carrier.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['Designator','Mid X','Mid Y','Layer','Rotation'])
 for r in positions:
  correction,dx,dy=corrections.get(r['Ref'],(0,0,0))
  rotation=round((float(r['Rot'])+correction)%360,9)%360
  w.writerow([r['Ref'],f"{round(float(r['PosX'])+dx,9)+0:.6f}",f"{round(float(r['PosY'])+dy,9)+0:.6f}",{'top':'T','bottom':'B'}[r['Side']],f'{rotation:.6f}'])
(F/'EXPORT.json').write_text(json.dumps({'pcb_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'assembly_components':len(refs),'bom_groups':len(bom),'coordinate_convention':'mm, board drill/place origin; native KiCad Y preserved; part-level JLCPCB Rotation/Position Offset fields applied (footprint-local frame); T/B layers'},indent=2)+'\n')
print('Exported Gerber ZIP, BOM and CPL:',len(refs),'placements')
