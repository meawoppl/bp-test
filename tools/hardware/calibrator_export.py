#!/usr/bin/env python3
"""Checked, repeatable calibrator fabrication and assembly export."""
from pathlib import Path
import csv, subprocess, tempfile, zipfile, shutil, hashlib, json
R=Path(__file__).resolve().parents[2];D=R/'boards/gps-time-calibrator';F=D/'fab';P=D/'calibrator.kicad_pcb';S=D/'calibrator.kicad_sch'
def run(*args): subprocess.run(list(map(str,args)),check=True)
# Publish native outputs through the plugin, then apply this carrier's assembly policy.
# --published finalizes an already published, source-matching build without rerunning it.
import sys, time, urllib.request
base='http://127.0.0.1:49022/api/build/'
def api(endpoint, post=False):
 req=urllib.request.Request(base+endpoint+'?project=gps-time-calibrator',method='POST' if post else 'GET')
 with urllib.request.urlopen(req,timeout=60) as response:return json.load(response)
if '--published' not in sys.argv:
 api('run',True)
 for attempt in range(900):
  status=api('status')
  if not status['busy']:break
  time.sleep(1)
 else:raise RuntimeError('Build did not complete')
 api('publish',True)
manifest=json.loads((F/'.kicad-pcb-build.json').read_text())
for name in ['calibrator.kicad_pcb','calibrator.kicad_sch']:
 assert hashlib.sha256((D/name).read_bytes()).hexdigest()==manifest['source_files'][name], 'Publish current sources first'
drc=json.loads((F/'checks/drc.json').read_text())
# The plugin may wrap the native report.
if 'report' in drc:drc=json.loads(drc['report']) if isinstance(drc['report'],str) else drc['report']
assert not any(drc.get(k) for k in ['violations','unconnected_items','schematic_parity']), 'Resolve DRC before export'
run('python3',R/'tools/hardware/calibrator_bom.py')
# Retain only manufacturing layers in the fabrication ZIP; do not ship drawing layers.
allowed={'.gtl','.gbl','.g1','.g2','.gts','.gbs','.gto','.gbo','.gtp','.gbp','.gm1','.drl'}
with zipfile.ZipFile(F/'gerbers/calibrator-gerbers.zip') as z:
 gerbers={n:z.read(n) for n in z.namelist() if Path(n).suffix in allowed}
assert 'calibrator-In1_Cu.g1' in gerbers and 'calibrator-In2_Cu.g2' in gerbers
# Discard publisher drawing exports from manufacturing directories.
for sub in ['gerbers','jlcpcb']:
 for f in (F/sub).glob('calibrator-*'):
  if f.suffix in {'.gbr','.gba','.gta'}:f.unlink()
with zipfile.ZipFile(F/'gerbers/calibrator-gerbers.zip','w',zipfile.ZIP_DEFLATED) as z:
 for name,data in sorted(gerbers.items()):z.writestr(name,data)
# Remove obsolete split drills from the prior origin convention, now replaced by merged drill.
if 'calibrator.drl' in gerbers:
 for name in ['calibrator-PTH.drl','calibrator-NPTH.drl']:
  (F/'gerbers'/name).unlink(missing_ok=True)
with tempfile.TemporaryDirectory() as td:
 raw=Path(td)/'positions.csv'
 run('kicad-cli','pcb','export','pos','--format','csv','--units','mm','--side','both','--exclude-dnp','-o',raw,P)
 shutil.copy2(raw,F/'bom/calibrator-native-positions.csv')
with (F/'jlcpcb/BOM_calibrator.csv').open() as f:bom=list(csv.DictReader(f))
refs={r.strip() for row in bom for r in row['Designator'].split(',')}
part_by_ref={r.strip():row['LCSC Part #'] for row in bom for r in row['Designator'].split(',')}
offsets=json.loads((D/'docs/jlcpcb-placement-offsets.json').read_text())
with (F/'bom/calibrator-native-positions.csv').open() as f:positions=[r for r in csv.DictReader(f) if r['Ref'] in refs]
assert {r['Ref'] for r in positions}==refs and len(positions)==len(refs)
with (F/'jlcpcb/CPL_calibrator.csv').open('w',newline='') as f:
 w=csv.writer(f,lineterminator="\n");w.writerow(['Designator','Mid X','Mid Y','Layer','Rotation'])
 for r in positions:
  adjustment=offsets.get(part_by_ref[r['Ref']],{})
  correction=adjustment.get('rotation_offset_degrees',0)
  dx=adjustment.get('cpl_offset_x_mm',0);dy=adjustment.get('cpl_offset_y_mm',0)
  if dx or dy:
   assert r['Side']=='top' and float(r['Rot'])%360==adjustment['verified_native_rotation_degrees'], 'Reverify translation for changed placement rotation'
  if correction:assert r['Side']=='top', 'Bottom-side offsets need separate verification'
  rotation=(float(r['Rot'])+correction)%360
  w.writerow([r['Ref'],f"{float(r['PosX'])+dx:.6f}",f"{float(r['PosY'])+dy:.6f}",{'top':'T','bottom':'B'}[r['Side']],f'{rotation:.6f}'])
(F/'EXPORT.json').write_text(json.dumps({'pcb_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'assembly_components':len(refs),'bom_groups':len(bom),'coordinate_convention':'mm, absolute KiCad origin to match plugin Gerbers; native negative Y preserved; part-specific JLCPCB rotation offsets applied from docs/jlcpcb-placement-offsets.json; T/B layers'},indent=2)+'\n')
print('Exported Gerber ZIP, BOM and CPL:',len(refs),'placements')

# Keep the combined assembly archive consistent with the corrected standalone files.
with zipfile.ZipFile(F/'jlcpcb/calibrator-jlcpcb.zip','w',zipfile.ZIP_DEFLATED) as z:
 for name,data in sorted(gerbers.items()):z.writestr(name,data)
 for name in ['BOM_calibrator.csv','CPL_calibrator.csv']:z.write(F/'jlcpcb'/name,name)
for src,dst in [('calibrator-schematic.pdf','docs/calibrator-schematic.pdf'),('calibrator.glb','docs/3d/calibrator.glb')]:shutil.copy2(F/src,D/dst)
# Separate manifest records intentional post-publish assembly policy, without falsifying the plugin manifest.
paths=['gerbers/calibrator-gerbers.zip','jlcpcb/calibrator-jlcpcb.zip','jlcpcb/BOM_calibrator.csv','jlcpcb/CPL_calibrator.csv','bom/calibrator-native-positions.csv','bom/calibrator-bom.csv','bom/manual-assembly.csv']
(F/'assembly-finalization.json').write_text(json.dumps({'base_publish_revision':manifest['hashes']['revision'],'pcb_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'policy':'Manual parts excluded; grouped BOM; saved JLCPCB rotation/position corrections; fabrication-only ZIP','files':{p:hashlib.sha256((F/p).read_bytes()).hexdigest() for p in paths}},indent=2)+'\n')
