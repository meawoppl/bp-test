#!/usr/bin/env python3
"""Construct the acquisition-first Tesla controller draft. Never overwrites a board without --replace-draft."""
from pathlib import Path
import pcbnew as p,json,uuid,re,shutil,sys,csv
ROOT=Path(__file__).resolve().parents[2]; D=ROOT/'boards/tesla-coil-controller'; C=ROOT/'boards/programming-carrier'
if (D/'controller.kicad_pcb').exists() and '--replace-draft' not in sys.argv:raise SystemExit('Existing board: use --replace-draft explicitly; this discards routing.')
for dn in ['Tesla.pretty','3dmodels','docs','fab/checks']:(D/dn).mkdir(parents=True,exist_ok=True)
b=p.BOARD();b.SetCopperLayerCount(2);b.GetDesignSettings().SetBoardThickness(p.FromMM(1.6))
v=lambda x,y:p.VECTOR2I(p.FromMM(x),p.FromMM(y));uid=lambda s:str(uuid.uuid5(uuid.NAMESPACE_URL,'bp-tesla-controller/'+s))
parts={};nets={};fps={}
def net(n):
 if n not in nets:nets[n]=p.NETINFO_ITEM(b,n);b.Add(nets[n])
 return nets[n]
def add(ref,value,lib,name,pins,x,y,a=0,kind='ic',mpn='',lcsc='',names=None,types=None):
 # ADC support parts use 0603; power, CST and AUX parts retain their rated packages.
 if ref in {f'R{i}' for i in list(range(1,9))+list(range(20,24))} | {f'C{i}' for i in list(range(1,19))+[20,21]}:
  lib='Resistor_SMD' if kind=='r' else 'Capacitor_SMD';name=('R' if kind=='r' else 'C')+'_0603_1608Metric'
 libpath=C/'Carrier.pretty' if lib=='Carrier' else D/'Tesla.pretty' if lib=='Tesla' else Path('/usr/share/kicad/footprints')/(lib+'.pretty')
 f=p.FootprintLoad(str(libpath),name);assert f,(lib,name)
 for m in list(f.Models()):
  src=Path(re.sub(r'\$\{KICAD\d+_3DMODEL_DIR\}','/usr/share/kicad/3dmodels',m.m_Filename).replace('${KIPRJMOD}',str(C)))
  if src.suffix=='.wrl' and src.with_suffix('.step').exists():src=src.with_suffix('.step')
  if src.exists():shutil.copy2(src,D/'3dmodels'/src.name);m.m_Filename='${KIPRJMOD}/3dmodels/'+src.name
 from tesla_models import localize
 localize(f)
 f.SetFPID(p.LIB_ID('Tesla',name))
 p.PCB_IO_KICAD_SEXPR().FootprintSave(str(D/'Tesla.pretty'),f)
 f.SetReference(ref);f.SetValue(value);f.SetPosition(v(x,y));f.SetOrientationDegrees(a);f.SetPath(p.KIID_PATH('/'+uid('root')+'/'+uid(ref)))
 for pad in f.Pads():
  n=pins.get(pad.GetNumber())
  if n:pad.SetNet(net(n))
 f.Reference().SetVisible(kind not in ['r','c','hole','testpoint']);f.Reference().SetTextSize(v(1,1));f.Reference().SetTextThickness(p.FromMM(.15));f.Reference().SetPosition(v(x,y-9 if ref=='U1' else y-7 if ref in ['J4','J30'] else y-5));f.Value().SetVisible(False)
 if ref=='J4':f.Reference().SetPosition(v(x-7,y))
 for k,val in [('MPN',mpn),('LCSC',lcsc),('Design status','Acquisition draft / not for fabrication')]:f.SetField(k,val);f.GetField(k).SetVisible(False)
 b.Add(f);fps[ref]=f;parts[ref]=dict(value=value,mpn=mpn,lcsc=lcsc,footprint='Tesla:'+name,pins=pins,kind=kind,names=names or {},types=types or {},position=[x,y,a])
 return f
def cap(ref,val,n,x,y,a=0):return add(ref,val,'Capacitor_SMD','C_0805_2012Metric',{'1':n,'2':'GND'},x,y,a,kind='c')
def res(ref,val,n1,n2,x,y,a=0):return add(ref,val,'Resistor_SMD','R_0805_2012Metric',{'1':n1,'2':n2},x,y,a,kind='r')
def line(a,z,layer=p.Edge_Cuts,width=.05):
 o=p.PCB_SHAPE();o.SetShape(p.SHAPE_T_SEGMENT);o.SetStart(v(*a));o.SetEnd(v(*z));o.SetWidth(p.FromMM(width));o.SetLayer(layer);b.Add(o)
def txt(s,x,y,layer=p.Dwgs_User):
 t=p.PCB_TEXT(b);t.SetText(s);t.SetPosition(v(x,y));t.SetLayer(layer);t.SetTextSize(v(1.5,1.5));t.SetTextThickness(p.FromMM(.2));b.Add(t)
# Roomy 232 x 180 mm draft; acquisition left, two GDT bridges right.
for a,z in [((20,20),(252,20)),((252,20),(252,200)),((252,200),(20,200)),((20,200),(20,20))]:line(a,z)
contract=json.loads((C/'docs/circuit.json').read_text())
from tesla_fpga_pinmap import CONTACTS as FPGA_CONTACTS
fpga={int(k):v for k,v in FPGA_CONTACTS.items()}
from tesla_output import CONTACTS
fpga.update({int(k):v for k,v in CONTACTS.items()})
from tesla_indicators import CONTACTS as INDICATOR_CONTACTS
fpga.update({int(k):v for k,v in INDICATOR_CONTACTS.items()})
pinout=[]
for ref,y in [('J1',39.3),('J2',64.3)]:
 c=contract[ref];pinmap={}
 for n,signal in c['pins'].items():
  target=signal if signal in ['GND','VIN_5V','USB_D+','USB_D-'] else None
  if ref=='J2':target='GND' if signal=='GND' else fpga.get(int(n))
  if ref=='J1' and n in ['13','14','15','16']:target=None
  if ref=='J1' and n=='20':target='USB_VBUS_PRESENT'
  pinmap[n]=target
  pinout.append(dict(connector=ref,contact=n,module_signal=signal,controller_net=target or 'UNUSED'))
 connector_names=dict(c['names'])
 if ref=='J2':connector_names['31']='FPGA_IOT_49A'
 add(ref,c['value'],'Carrier',ref+'_Module_v1_Mate',pinmap,100,y,kind='connector',mpn=c['mpn'],lcsc=c['lcsc'],names=connector_names)
add('H1','M3 module mounting','MountingHole','MountingHole_3.2mm_M3',{},100,51.8,kind='hole')
for ref,x,y in [('H2',24,24),('H3',248,24),('H4',24,196),('H5',248,196)]:add(ref,'M3','MountingHole','MountingHole_3.2mm_M3',{},x,y,kind='hole')
# Correct frozen v1 envelope relative to the connector midpoint.
for a,z in [((90,25),(110,25)),((110,25),(110,70)),((110,70),(90,70)),((90,70),(90,25))]:line(a,z,p.Dwgs_User,.15)
txt('MODULE v1 / 2 mm mating gap',100,73)
# Exact AD7606C-16 pin map, datasheet Table 9; software serial mode, internal reference.
ap={str(i):None for i in range(1,65)};names={};types={}
for i in [1,37,38,48]:ap[str(i)]='+5V_ADC';names[str(i)]='AVCC';types[str(i)]='power_in'
for i in [2,26,35,40,41,47,43,46]:ap[str(i)]='GND';names[str(i)]='AGND';types[str(i)]='power_in'
for i,n in {3:'OS0',4:'OS1',5:'OS2',6:'PAR_SER',7:'STBY_N',10:'WR_N',34:'REFSEL'}.items():ap[str(i)]='+3V3';names[str(i)]=n;types[str(i)]='input'
ap['8']='GND';names['8']='RANGE';types['8']='input'
for i,n in {9:'ADC_CONVST',11:'ADC_RESET',12:'ADC_SCLK',13:'ADC_CS_N',14:'ADC_BUSY',15:'ADC_FIRST',24:'ADC_DOUT_A',25:'ADC_DOUT_B',27:'ADC_DOUT_C',28:'ADC_DOUT_D',29:'ADC_SDI'}.items():ap[str(i)]=n;names[str(i)]=n;types[str(i)]='output' if i in [14,15,24,25,27,28] else 'input'
for i in [16,17,18,30,31,32,33]:ap[str(i)]='GND';names[str(i)]='UNUSED_DB';types[str(i)]='passive'
for i in [19,20,21,22]:names[str(i)]='UNUSED_DOUT';types[str(i)]='output'
for i,n in {23:'+3V3',36:'REGCAP_A',39:'REGCAP_D',42:'ADC_REF_2V5',44:'ADC_REFCAP',45:'ADC_REFCAP'}.items():ap[str(i)]=n;names[str(i)]=n;types[str(i)]='power_in' if i==23 else 'passive' if i==45 else 'power_out'
for ch in range(1,9):
 ap[str(47+2*ch)]=f'ADC_CH{ch}';ap[str(48+2*ch)]='GND';names[str(47+2*ch)]=f'V{ch}+';names[str(48+2*ch)]=f'V{ch}-';types[str(47+2*ch)]='input';types[str(48+2*ch)]='input'
add('U1','AD7606C-16BSTZ','Package_QFP','LQFP-64_10x10mm_P0.5mm',ap,60,62,mpn='AD7606C-16BSTZ',lcsc='C5371769',names=names,types=types)
add('TP1','ADC_FIRST','TestPoint','TestPoint_Pad_D1.0mm',{'1':'ADC_FIRST'},98.5,103.5,kind='testpoint',names={'1':'FRSTDATA'})
# Decouplers deliberately grouped next to their physical supply/reference pad side.
for ref,val,n,x,y,a in [('C1','100nF','+5V_ADC',51,57,90),('C2','100nF','+5V_ADC',69,65.75,90),('C3','100nF','+5V_ADC',72,68.5,90),('C4','100nF','+5V_ADC',69,57,90),('C5','100nF','+3V3',58,71,0),('C6','1uF','REGCAP_A',76,68.5,90),('C7','1uF','REGCAP_D',72,64.5,90),('C8','100nF','ADC_REF_2V5',72,60.5,90),('C9','10uF','ADC_REFCAP',73,56,90),('C10','10uF','+5V_ADC',51,67,90)]:cap(ref,val,n,x,y,a)
# Four buffered JST AUX inputs occupy CH1..4; two CST raw/envelope pairs use CH5..8.
from tesla_dual_cst import ADC_INPUTS,populate_aux,populate_second
populate_aux(add)
from tesla_aux import populate as populate_aux_buffers
populate_aux_buffers(add)
jp={str(2*i+1):nn for i,nn in enumerate(ADC_INPUTS)}
for ch in range(1,9):
 res('R'+str(ch),'100R',jp[str(ch*2-1)],f'ADC_CH{ch}',43,42+ch*3.5)
 cap('C'+str(ch+10),'1nF',f'ADC_CH{ch}',48,42+ch*3.5)
# Series battery input; direct GDT power, on-board 12 V and 5 V conversion.
add('J4','12V BATTERY / UPPER','TerminalBlock_Phoenix','TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal',{'1':'VBAT_24V','2':'BAT_MID_12V'},160,27,kind='connector',names={'1':'+','2':'-'})
res('R20','0R','VIN_5V','+5V_ADC',42,27)
c=contract['U1'];pp={n:{'VIN_5V':'VIN_5V','+3V3_TEST':'+3V3'}.get(nn,nn) for n,nn in c['pins'].items()}
add('U2',c['value'],'Carrier','SOT-23-5',pp,55,30,mpn=c['mpn'],lcsc=c['lcsc'],names=c['names'],types=c['types'])
cap('C20','1uF','VIN_5V',50,30,90);cap('C21','1uF','+3V3',60,30,90)
res('R21','10k','GND','ADC_CONVST',79,61,90);res('R22','10k','+3V3','ADC_CS_N',79,56,90);res('R23','10k','+3V3','ADC_RESET',79,51,90)
# USB programming is self-powered; host VBUS never joins the board 5 V rail.
from tesla_usb import populate as populate_usb
populate_usb(add)
# Logic service boundary; actual GDT output stages are J50/J51.
txt('8 x CM600HA-24H / 1:1 GDTs',151,125)
txt('CT burden / clamp / comparator',62,94);txt('ACQUISITION DRAFT - UNROUTED',91,119)
from tesla_power import populate
populate(add,res,cap)
from tesla_cst import populate as populate_cst
populate_cst(add,res,cap)
populate_second(add)
from tesla_cst import finish_placement
finish_placement(fps,parts,p,v)
from tesla_output import populate as populate_output, finish_placement as place_output
populate_output(add,res,cap)
place_output(fps,parts,p,v)
from tesla_indicators import populate as populate_indicators
populate_indicators(add)
from tesla_floorplan import apply as apply_floorplan
apply_floorplan(b,parts)
# No fabricated routes or planes yet: review connector & ADC choices first.
p.SaveBoard(str(D/'controller.kicad_pcb'),b)
project=json.loads((C/'carrier.kicad_pro').read_text()) if (C/'carrier.kicad_pro').exists() else {}
project['schematic']={'drawing':{'default_line_thickness':6.0,'default_wire_thickness':6.0,'junction_size_choice':3}}
project['net_settings']={'classes':[{'name':'Default','clearance':.15,'track_width':.25,'via_diameter':.5,'via_drill':.25,'microvia_diameter':.3,'microvia_drill':.1,'diff_pair_width':.2,'diff_pair_gap':.2,'diff_pair_via_gap':.25}]}
(D/'controller.kicad_pro').write_text(json.dumps(project,indent=2)+'\n')
(D/'fp-lib-table').write_text('(fp_lib_table (lib (name "Tesla") (type "KiCad") (uri "${KIPRJMOD}/Tesla.pretty") (options "") (descr "Project-local Tesla controller")))\n')
(D/'sym-lib-table').write_text('(sym_lib_table (lib (name "Tesla") (type "KiCad") (uri "${KIPRJMOD}/Tesla.kicad_sym") (options "") (descr "Project-local Tesla controller")))\n')
(D/'docs/circuit.json').write_text(json.dumps(parts,indent=2)+'\n')
with (D/'docs/daughterboard-pinout.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(pinout[0]));w.writeheader();w.writerows(pinout)
print('Created',len(parts),'footprints; routing intentionally not yet started.')
