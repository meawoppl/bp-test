#!/usr/bin/env python3
"""Generate grouped carrier BOMs from native KiCad schematic export."""
import csv
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
BOARD = ROOT / 'boards/gps-time-calibrator'
# Reviewed assembly-equivalent footprint variants. U12's custom artwork/name
# differs, but its pad numbers, positions, sizes, shapes and layers are identical.
# Keep the actual schematic/PCB footprint; normalize only the BOM grouping label.
ASSEMBLY_FOOTPRINT_ALIASES = {
    'Calibrator:SOT-23-5_U12': 'Calibrator:SOT-23-5',
}
def refkey(ref):
    return (re.sub(r'\d+', '', ref), int(re.search(r'\d+', ref).group()))
def main():
    with tempfile.TemporaryDirectory() as td:
        xml = Path(td) / 'netlist.xml'
        subprocess.run(['kicad-cli', 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', str(xml), str(BOARD / 'calibrator.kicad_sch')], check=True)
        root = ET.parse(xml)
    groups = defaultdict(list)
    manual = []
    excluded = []
    for comp in root.findall('./components/comp'):
        ref = comp.get('ref')
        props = {p.get('name') for p in comp.findall('property')}
        if props & {'exclude_from_bom', 'dnp'}:
            excluded.append(ref)
            continue
        fields = {f.get('name'): f.text or '' for f in comp.findall('./fields/field')}
        mpn, lcsc = fields.get('MPN', ''), fields.get('LCSC', '')
        if fields.get('Assembly') == 'Manual':
            assert mpn and fields.get('Supplier URL'), (ref, 'Manual part must have purchasing source')
            manual.append({'Comment':comp.findtext('value'),'Designator':ref,'Quantity':1,'Footprint':comp.findtext('footprint'),'MPN':mpn,'LCSC Part #':'','Supplier URL':fields['Supplier URL']})
            continue
        assert mpn and re.fullmatch(r'C\d+', lcsc), (ref, 'Missing exact purchasing fields')
        footprint = comp.findtext('footprint')
        footprint = ASSEMBLY_FOOTPRINT_ALIASES.get(footprint, footprint)
        groups[(mpn, lcsc, footprint)].append((ref, comp.findtext('value')))
    rows = []
    for (mpn, lcsc, footprint), items in groups.items():
        items.sort(key=lambda x: refkey(x[0]))
        values = list(dict.fromkeys(v for _, v in items))
        rows.append({'Comment': ' / '.join(values), 'Designator': ','.join(r for r, _ in items), 'Footprint': footprint, 'LCSC Part #': lcsc, 'Quantity': len(items), 'MPN': mpn, 'Supplier URL': f'https://www.lcsc.com/product-detail/{lcsc}.html'})
    rows.sort(key=lambda r: refkey(r['Designator'].split(',')[0]))
    for relative, columns in [
        ('fab/bom/calibrator-bom.csv', ['Comment','Designator','Quantity','Footprint','MPN','LCSC Part #','Supplier URL']),
        ('fab/jlcpcb/BOM_calibrator.csv', ['Comment','Designator','Footprint','LCSC Part #']),
    ]:
        output = BOARD / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=columns, extrasaction='ignore', lineterminator='\n')
            writer.writeheader(); writer.writerows(rows + (manual if relative.startswith('fab/bom/') else []))
    if manual:
        output=BOARD/'fab/bom/manual-assembly.csv'
        with output.open('w',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(manual[0]),lineterminator='\n');writer.writeheader();writer.writerows(manual)
    print(f'{len(rows)} BOM groups; {sum(r["Quantity"] for r in rows)} populated parts; excluded {", ".join(sorted(excluded, key=refkey))}')
if __name__ == '__main__':
    main()
