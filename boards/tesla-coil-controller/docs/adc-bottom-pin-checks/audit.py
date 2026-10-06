"""Read-only datasheet pin-role and physical connectivity audit.

KCT sch info reports zero pins for this generated symbol. Its sync and
net-status checks are retained; native pin/cluster queries supply the
per-pin and isolated regulator/reference-output evidence.
"""
import csv, hashlib, json
from pathlib import Path
import pcbnew as p

D = Path('boards/tesla-coil-controller')
T = Path('tmp/tesla-adc-power-pin-review')
files = [D/'controller.kicad_pcb', D/'controller.kicad_sch', D/'controller.kicad_pro',
         D/'Tesla.kicad_sym', D/'docs/circuit.json', Path('tools/hardware/tesla_reviewed_routing.json')]
hashes = {str(f): hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
b = p.LoadBoard(str(D/'controller.kicad_pcb'))
b.BuildConnectivity()
c = b.GetConnectivity()
fps = {f.GetReference(): f for f in b.GetFootprints()}
pads = {(f.GetReference(), a.GetNumber()): a for f in b.GetFootprints() for a in f.Pads()}
keys = {a.m_Uuid.AsString(): k for k, a in pads.items()}
def cluster(ref, pin):
    a = pads[ref, str(pin)]
    return {keys[t.m_Uuid.AsString()] for t in c.GetConnectedItems(a)
            if t.m_Uuid.AsString() in keys} | {(ref, str(pin))}
checks = []
def check(name, ok):
    checks.append({'check': name, 'pass': bool(ok)})
contract = json.loads((D/'docs/circuit.json').read_text())
for pin, net in contract['U1']['pins'].items():
    a = pads['U1', pin]
    check(f'U1.{pin} matches source net contract',
          a.GetNetname() == net if net else a.GetNetname().startswith('unconnected-'))

rows = []
functions = {1:'AVCC', 2:'AGND', 3:'OS0', 4:'OS1', 5:'OS2', 6:'PAR/SER SEL',
             7:'STBY', 8:'RANGE', 9:'CONVST', 10:'WR', 11:'RESET', 12:'RD/SCLK',
             13:'CS', 14:'BUSY', 15:'FRSTDATA', 16:'DB0'}
for pin in range(1,17):
    a = pads['U1',str(pin)]
    role = ('analog supply' if pin == 1 else 'ground' if pin == 2 else
            'configuration strap HIGH' if pin in [3,4,5,6,7,10] else
            'configuration strap LOW' if pin == 8 else
            'unused parallel data: grounded' if pin == 16 else 'interface signal')
    rows.append({'pin':pin, 'datasheet_name':functions[pin], 'role':role,
                 'net':a.GetNetname(), 'x_mm':p.ToMM(a.GetPosition().x),
                 'y_mm':p.ToMM(a.GetPosition().y)})
for pin in [3,4,5,6,7,10,23,34]:
    check(f'U1.{pin} is on 3.3V and physically reaches U2.5',
          pads['U1',str(pin)].GetNetname()=='+3V3' and ('U2','5') in cluster('U1',pin))
for pin in [1,37,38,48]:
    check(f'U1.{pin} is on +5V_ADC and physically reaches R20.2',
          pads['U1',str(pin)].GetNetname()=='+5V_ADC' and ('R20','2') in cluster('U1',pin))
for pin in [2,8,16,17,18,26,30,31,32,33,35,40,41,43,46,47,*range(50,65,2)]:
    check(f'U1.{pin} is grounded and physically reaches J2.1',
          pads['U1',str(pin)].GetNetname()=='GND' and ('J2','1') in cluster('U1',pin))
decoupling = [('C1','100nF',1),('C2','100nF',37),('C3','100nF',38),('C4','100nF',48),
              ('C5','100nF',23),('C6','1uF',36),('C7','1uF',39),
              ('C8','100nF',42),('C9','10uF',44),('C10','10uF',1)]
for ref, value, pin in decoupling:
    check(ref+' expected capacitance', fps[ref].GetValue()==value)
    check(ref+' reaches U1 pin and ground', ('U1',str(pin)) in cluster(ref,1) and ('J2','1') in cluster(ref,2))
for pin, ref in [(36,'C6'),(39,'C7'),(42,'C8')]:
    check(f'U1.{pin} output is isolated to its own capacitor', cluster('U1',pin)=={('U1',str(pin)),(ref,'1')})
check('REFCAPA/B shorted only to C9', cluster('U1',44)=={('U1','44'),('U1','45'),('C9','1')})
drc=json.loads(json.loads((T/'drc.json').read_text())['report'])
erc=json.loads(json.loads((T/'erc.json').read_text())['report'])
sync=json.loads(json.loads((T/'sync.json').read_text())['stdout'])
kct=json.loads(json.loads((T/'3v3-connectivity.json').read_text())['stdout'])
check('DRC zero violations/opens/parity issues', not any(drc[k] for k in ['violations','unconnected_items','schematic_parity']))
check('ERC zero violations', all(not s['violations'] for s in erc['sheets']))
check('schematic in sync', sync['in_sync'])
check('KCT +3V3 physically complete', kct['summary']['complete']==1 and kct['summary']['incomplete']==0)
check('native whole board has zero opens', c.GetUnconnectedCount(False)==0)
check('design files unchanged', hashes=={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in files})
out={'scope':'U1 bottom-pin datasheet investigation; no board/schematic edits',
     'annotation_revision':'a6725f560b3aebf86e6d', 'reviewed_portal_revision':'7f950fdc4e6d7c96dfa8',
     'sources_sha256':hashes,
     'datasheet':'https://www.analog.com/media/en/technical-documentation/data-sheets/ad7606c-16.pdf',
     'datasheet_revision':'A, August 2025', 'datasheet_sections':['Table 9 pp15-17','Table 14 p36','Table 23 p43','Figure 123 p59','layout p60'],
     'bottom_pins':rows,'checks':checks,'failures':[v for v in checks if not v['pass']],
     'limitations':'Connectivity and documented configuration only; no powered hardware or firmware timing test. Layout was not altered.'}
(T/'verification.json').write_text(json.dumps(out,indent=2)+'\n')
with (T/'bottom-pins.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
print(json.dumps({'checks':len(checks),'failures':out['failures'],'sources_sha256':hashes},indent=2))
assert not out['failures']
