#!/usr/bin/env python3
"""Acquisition draft schematic. Circuit contract and footprint UUIDs shared with constructor."""
from pathlib import Path
import json,uuid,re,math
R=Path(__file__).resolve().parents[2];D=R/'boards/tesla-coil-controller';parts=json.loads((D/'docs/circuit.json').read_text())
uid=lambda s:str(uuid.uuid5(uuid.NAMESPACE_URL,'bp-tesla-controller/'+s));q=lambda s:json.dumps(str(s));items=[];symbols={};count=0
E=lambda z=1.27,just='':f'(effects (font (size {z} {z}))'+(f' (justify {just})' if just else '')+')'
def prop(k,val,x,y,hide=False):return f'(property {q(k)} {q(val)} (at {x} {y} 0) {E()}'+(' (hide yes)' if hide else '')+')'
def wire(a,b):
 global count
 count+=1;items.append(f'(wire (pts (xy {a[0]} {a[1]}) (xy {b[0]} {b[1]})) (stroke (width 0.1524) (type default)) (uuid "{uid("w"+str(count))}"))')
def label(n,x,y,side=0):
 global count
 count+=1;items.append(f'(global_label {q(n)} (shape passive) (at {x} {y} {side}) {E(1.27,"right" if side==180 else "left")} (uuid "{uid("l"+str(count))}"))')
def note(s,x,y,size=1.5):items.append(f'(text {q(s)} (at {x} {y} 0) {E(size,"left")} (uuid "{uid(s+str(x)+str(y))}"))')
def box(s,x,y,w,h):
 items.append(f'(rectangle (start {x} {y}) (end {x+w} {y+h}) (stroke (width 0.254) (type dash)) (fill (type none)) (uuid "{uid(s)}"))');note(s,x+3,y+5,2)

PIN_LAYOUTS={}
def ic_layout(ref,left,right):
 h=math.ceil((max(len(left),len(right))*3.81+2.54)/2.54)*2.54;w=17.78
 pm={}
 for side,nums in [(-1,left),(1,right)]:
  for i,n in enumerate(nums):pm[str(n)]=(side*(w+5.08),h-5.08-i*7.62,0 if side==-1 else 180)
 PIN_LAYOUTS[ref]=(pm,w,h)
for ref in ['U30','U31']:
 ic_layout(ref,[1,2,3,5,4,8],[7,6])
ic_layout('U2',[1,3,2],[5,4])
ic_layout('U42',[3,1,6],[5,4,2])
ic_layout('U43',[1,2,3,4],[7,6,8,5])
ic_layout('U44',[2,4],[5,3,1])
ic_layout('U45',[1,2,3],[4,5])
ic_layout('J40',[],[1,2])
ic_layout('J60',[],[1,2])
for ref in ['J4','J30']:ic_layout(ref,[],[1,2])
ic_layout('U62',[3,1,6],[5,4,2])
for ref in ['U51','U52','U53','U54']:
 ic_layout(ref,[1,5,6,7],[2,3,4,8])
 pm,w,h=PIN_LAYOUTS[ref]
 for n,yy in [('2',25.4),('3',12.7),('4',-2.54),('8',-17.78)]:pm[n]=(22.86,yy,180)
 PIN_LAYOUTS[ref]=(pm,w,30.48)
for ref in ['J50','J51']:ic_layout(ref,[1,2],[])
PIN_LAYOUTS['U44'][0]['5']=(22.86,10.16,180)
PIN_LAYOUTS['U44'][0]['3']=(22.86,0,180)
PIN_LAYOUTS['U44'][0]['1']=(22.86,-12.7,180)
PIN_LAYOUTS['U3']=({'1':(-17.78,-5.08,0),'3':(-17.78,5.08,0),
 '6':(17.78,-5.08,180),'4':(17.78,5.08,180),
 '5':(0,15.24,270),'2':(0,-15.24,90)},12.7,10.16)

def symdef(ref):
 c=parts[ref];kind=c['kind'];shapes=[];pmap={};pins=[]
 if kind in ['r','c']:
  pmap={'1':(-5.08,0,0),'2':(5.08,0,180)};h=0;length=2.54 if kind=='r' else 4.445
  shapes=['(polyline (pts (xy -2.54 0) (xy -1.905 1.016) (xy -0.635 -1.016) (xy 0.635 1.016) (xy 1.905 -1.016) (xy 2.54 0)) (stroke (width 0.254) (type default)) (fill (type none)))'] if kind=='r' else ['(polyline (pts (xy -0.635 -2.032) (xy -0.635 2.032)) (stroke (width 0.254) (type default)) (fill (type none)))','(polyline (pts (xy 0.635 -2.032) (xy 0.635 2.032)) (stroke (width 0.254) (type default)) (fill (type none)))']
 elif ref in ['U40','U41','U60','U61','U70','U71','U72','U73']:
  pmap={'1':(17.78,0,180),'2':(-2.54,-12.7,90),'3':(-12.7,-5.08,0),'4':(-12.7,5.08,0),'5':(-2.54,12.7,270)};h=10.16;length=5.08
  shapes=['(polyline (pts (xy -7.62 10.16) (xy 12.7 0) (xy -7.62 -10.16) (xy -7.62 10.16)) (stroke (width 0.254) (type default)) (fill (type background)))']
 elif ref=='D43':
  # BAT54S series pair: A1 -> K1/A2 -> K2. Keep the existing pin
  # names/numbers, with the supply cathode above and ground anode below.
  pmap={'1':(0,-10.16,90),'2':(0,10.16,270),'3':(10.16,0,180)};h=7.62;length=5.08
  paths=[[(0,-5.08),(0,5.08)],[(0,0),(5.08,0)]]
  for cy in [-2.54,5.08]:
   paths.extend([
    [(-1.905,cy-2.54),(1.905,cy-2.54),(0,cy),(-1.905,cy-2.54)],
    [(-1.27,cy-.635),(-1.905,cy-.635),(-1.905,cy),(1.905,cy),(1.905,cy+.635),(1.27,cy+.635)],
   ])
  shapes=['(polyline (pts '+ ' '.join(f'(xy {x:g} {y:g})' for x,y in pts)+') (stroke (width 0.254) (type default)) (fill (type none)))' for pts in paths]
  shapes.append('(circle (center 0 0) (radius 0.381) (stroke (width 0.254) (type default)) (fill (type outline)))')
 elif ref in ['D70','D71','D72','D73']:
  pmap={'1':(0,-10.16,90),'2':(0,10.16,270),'3':(-10.16,0,0)};h=5.08;length=5.08
  shapes=['(rectangle (start -5.08 5.08) (end 5.08 -5.08) (stroke (width 0.254) (type default)) (fill (type background)))']
 elif kind=='cmc':
  pmap={'1':(-10.16,10.16,0),'2':(10.16,10.16,180),'4':(-10.16,-10.16,0),'3':(10.16,-10.16,180)};h=12.7;length=5.08
  shapes=[]
  for yy in [10.16,-10.16]:
   pts=[(-5.08,yy),(-3.81,yy+1.27),(-2.54,yy),(-1.27,yy+1.27),(0,yy),(1.27,yy+1.27),(2.54,yy),(3.81,yy+1.27),(5.08,yy)]
   shapes.append('(polyline (pts '+ ' '.join(f'(xy {x} {y})' for x,y in pts)+') (stroke (width 0.254) (type default)) (fill (type none)))')
   shapes.append(f'(circle (center -5.08 {yy+2.54}) (radius 0.5) (stroke (width 0.254) (type default)) (fill (type outline)))')
  for yy in [-1.27,1.27]:shapes.append(f'(polyline (pts (xy -5.08 {yy}) (xy 5.08 {yy})) (stroke (width 0.254) (type default)) (fill (type none)))')
 elif kind=='testpoint':
  pmap={'1':(0,0,90)};h=2.54;length=0
  # TP1 shares its attachment with the ADC_FIRST label. Give it a visible
  # vertical pin so the probe circle is distinct from the label and wire.
  if ref=='TP1':length=5.08
  shapes=[f'(circle (center 0 {length+1.27:g}) (radius 1.27) (stroke (width 0.254) (type default)) (fill (type none)))']
 elif kind=='tvs':
  pmap={'1':(-5.08,0,0),'2':(5.08,0,180)};h=0;length=2.54
  shapes=['(polyline (pts (xy -2.54 -1.8) (xy -2.54 1.8) (xy 0 0) (xy 2.54 1.8) (xy 2.54 -1.8) (xy 0 0) (xy -2.54 -1.8)) (stroke (width 0.254) (type default)) (fill (type none)))']
 elif ref=='J5':
  # Parallel USB-C contacts are stacked, as in KiCad's USB2 receptacle symbol.
  pmap={};h=33.02;length=5.08
  for nums,xy in [(('A4','A9','B4','B9'),(20.32,25.4,180)),
   (('A6','B6'),(20.32,2.54,180)),(('A7','B7'),(20.32,10.16,180)),
   (('A5',),(20.32,-10.16,180)),(('B5',),(20.32,-17.78,180)),
   (('A8',),(-20.32,-10.16,0)),(('B8',),(-20.32,-17.78,0)),
   (('A1','A12','B1','B12'),(0,-38.1,90)),(('S1',),(-10.16,-38.1,90))]:
   for n in nums:pmap[n]=xy
  shapes=['(rectangle (start -15.24 33.02) (end 15.24 -33.02) (stroke (width 0.254) (type default)) (fill (type background)))']
 elif ref in PIN_LAYOUTS:
  pmap,w,h=PIN_LAYOUTS[ref];length=5.08
  shapes=[f'(rectangle (start {-w} {h}) (end {w} {-h}) (stroke (width 0.254) (type default)) (fill (type background)))']
 elif kind in ['mosfet','led_driver']:
  pmap={'1':(-10.16,0,0),'2':(2.54,10.16,270),'3':(2.54,-10.16,90)};h=7.62;length=5.08
  shapes=['(polyline (pts '+p+') (stroke (width 0.254) (type default)) (fill (type none)))' for p in ['(xy -5.08 0) (xy -2.54 0) (xy -2.54 4) (xy -2.54 -4)','(xy 0 5.08) (xy 0 2.0)','(xy 0 1.5) (xy 0 -1.5)','(xy 0 -2.0) (xy 0 -5.08)','(xy 2.54 5.08) (xy 0 5.08)','(xy 2.54 -5.08) (xy 0 -5.08)','(xy 2.54 -5.08) (xy 2.54 0) (xy 0 0) (xy 1.27 0.8) (xy 0 0) (xy 1.27 -0.8)']]
  if kind=='led_driver':pmap['2'],pmap['3']=pmap['3'],pmap['2']
 elif kind in ['diode','led']:
  pmap={'1':(-5.08,0,0),'2':(5.08,0,180)};h=0;length=3.81
  shapes=['(polyline (pts '+p+') (stroke (width 0.254) (type default)) (fill (type none)))' for p in ['(xy -1.27 -2) (xy -1.27 2)','(xy -1.27 0) (xy 1.27 2) (xy 1.27 -2) (xy -1.27 0)']]
  if kind=='led':
   pmap={'1':(5.08,0,180),'2':(-5.08,0,0)}
   shapes=[re.sub(r'\(xy (-?[\d.]+) (-?[\d.]+)\)',lambda m:f'(xy {-float(m[1]):g} {m[2]})',s) for s in shapes]
   for ax in [-1.5,1.5]:
    shapes.append(f'(polyline (pts (xy {ax} 3) (xy {ax+2} 5) (xy {ax+1} 5) (xy {ax+2} 5) (xy {ax+2} 4)) (stroke (width 0.2) (type default)) (fill (type none)))')
 elif kind=='l':
  pmap={'1':(-5.08,0,0),'2':(5.08,0,180)};h=0;length=1.08
  shapes=['(polyline (pts '+ ' '.join(f'(xy {x} {y})' for x,y in [(-4,0),(-3,1.5),(-2,0),(-1,1.5),(0,0),(1,1.5),(2,0),(3,1.5),(4,0)])+') (stroke (width 0.254) (type default)) (fill (type none)))']
 else:
  nums=sorted(c['pins'],key=lambda n:int(n) if n.isdigit() else 1000);half=(len(nums)+1)//2;h=max(5.08,(half+1)*2.54);w=17.78 if ref=='U1' else 15.24
  if kind=='hole':w=h=2.54
  pmap={n:((-w-5.08 if i<half else w+5.08),h-5.08-(i%half)*5.08,0 if i<half else 180) for i,n in enumerate(nums)};length=5.08
  shapes=[f'(rectangle (start {-w} {h}) (end {w} {-h}) (stroke (width 0.254) (type default)) (fill (type background)))']
 if ref=='R21':pmap={'1':pmap['2'],'2':pmap['1']}
 for n,(x,y,a) in pmap.items():
  nm='~' if kind in ['r','c'] else c['names'].get(n,n);typ=c['types'].get(n,'passive')
  hidden=' hide' if ref=='J5' and n in ['A9','B4','B9','B6','B7','A12','B1','B12'] else ''
  pins.append(f'(pin {typ} line (at {x} {y} {a}) (length {length}){hidden} (name {q(nm)} {E(.95)}) (number {q(n)} {E(.95)}))')
 symbols[ref]=f'(symbol "{ref}" (pin_names (offset 0.762)) (in_bom yes) (on_board yes) {prop("Reference",ref,0,h+6.35)} {prop("Value",c["value"],0,h+3.81)} (symbol "{ref}_0_1" '+''.join(shapes)+f') (symbol "{ref}_1_1" '+''.join(pins)+'))'
 if ref=='D43':symbols[ref]=symbols[ref].replace('(pin_names (offset 0.762))','(pin_names (offset 0.762) hide)')
 if kind=='testpoint':symbols[ref]=symbols[ref].replace('(pin_names (offset 0.762))','(pin_names hide) (pin_numbers hide)')
 return pmap,h

def place(ref,x,y,rotate=False,ports=True,skip_ports=()):
 x=round(x,4);y=round(y/1.27)*1.27
 c=parts[ref];pm,h=symdef(ref)
 if rotate:
  # Rotate all graphic points and pins, not just capacitor plates.
  symbols[ref]=re.sub(r'\(xy (-?[\d.]+) (-?[\d.]+)\)',lambda m:f'(xy {float(m[2]):g} {-float(m[1]):g})',symbols[ref])
  for n,(px,py,pa) in pm.items():
   symbols[ref]=symbols[ref].replace(f'(at {px} {py} {pa}) (length',f'(at {py} {-px} {(pa-90)%360}) (length')
  pm={n:(py,-px,(pa-90)%360) for n,(px,py,pa) in pm.items()}
 rx=x+3.81 if rotate else x;ry=y-1.27 if rotate else y-h-6.35;vy=ry+2.54
 if ref in ['U70','U71','U72','U73']:rx=x;ry=y+39.37;vy=ry+2.54
 if c['kind']=='led':rx=x;ry=y-10.16;vy=ry+2.54
 if ref in ['D70','D71','D72','D73']:rx=x+20.32;ry=y-6.35;vy=ry+2.54
 if ref=='D43':rx=x+10.16;ry=y-7.62;vy=ry+2.54
 if ref=='U3':rx=x+17.78;ry=y-19.05;vy=ry+2.54
 meta=prop('Reference',ref,rx,ry).replace('(font (size 1.27 1.27))','(font (size 1.27 1.27)) (justify left)' if rotate else '(font (size 1.27 1.27))')+prop('Value',c['value'],rx,vy).replace('(font (size 1.27 1.27))','(font (size 1.27 1.27)) (justify left)' if rotate else '(font (size 1.27 1.27))')+prop('Footprint',c['footprint'],x,y,True)+prop('MPN',c['mpn'],x,y,True)+prop('LCSC',c['lcsc'],x,y,True)
 from tesla_reservoirs import MPN,DATASHEET
 if c['mpn']==MPN:meta+=prop('Manufacturer','TDK',x,y,True)+prop('Datasheet',DATASHEET,x,y,True)
 items.append(f'(symbol (lib_id "Tesla:{ref}") (at {x} {y} 0) (unit 1) (in_bom {"no" if c["kind"] in ["hole","testpoint"] else "yes"}) (on_board yes) (uuid "{uid(ref)}") {meta} (instances (project "controller" (path "/{uid("root")}" (reference "{ref}") (unit 1)))))')
 coords={}
 for n,(dx,dy,a) in pm.items():
  pt=(round(x+dx,4),round(y-dy,4));coords[n]=pt
  if not ports or n in skip_ports:continue
  net=c['pins'][n]
  if net is None:
   items.append(f'(no_connect (at {pt[0]} {pt[1]}) (uuid "{uid(ref+n+"nc")}"))');continue
  z=(round(pt[0]+(-7.62 if a==0 else 7.62),4),pt[1]);wire(pt,z);label(net,*z,0 if a==180 else 180)
 return coords
pc=0
def power(n,x,y):
 global pc
 pc+=1;name='PWR_'+n.replace('+','P');ref=f'#PWR{pc:03d}'
 shape='(polyline (pts (xy 0 0) (xy 0 -1.27) (xy -2.54 -1.27) (xy 0 -3.81) (xy 2.54 -1.27) (xy 0 -1.27)) (stroke (width 0.254) (type default)) (fill (type none)))' if n=='GND' else '(polyline (pts (xy 0 0) (xy 0 3.81) (xy -1.27 2.54) (xy 0 3.81) (xy 1.27 2.54)) (stroke (width 0.254) (type default)) (fill (type none)))'
 if n.startswith('-'):shape='(polyline (pts (xy 0 0) (xy 0 -3.81) (xy -1.27 -2.54) (xy 0 -3.81) (xy 1.27 -2.54)) (stroke (width 0.254) (type default)) (fill (type none)))'
 symbols[name]=f'(symbol "{name}" (power) (pin_names hide) (pin_numbers hide) (in_bom no) (on_board no) {prop("Reference","#PWR",0,0,True)} {prop("Value",n,0,5.08)} (symbol "{name}_0_1" {shape}) (symbol "{name}_1_1" (pin power_in line (at 0 0 90) (length 0) (name {q(n)} {E()}) (number "1" {E()}))))'
 items.append(f'(symbol (lib_id "Tesla:{name}") (at {x} {y} 0) (unit 1) (in_bom no) (on_board no) (uuid "{uid(ref)}") {prop("Reference",ref,x,y,True)} {prop("Value",n,x,y+(5.08 if n=="GND" or n.startswith("-") else -6.35),n=="GND")} (instances (project "controller" (path "/{uid("root")}" (reference "{ref}") (unit 1)))))')
from tesla_schematic_blocks import draw
# Presentation-only: contract pins/names and board geometry are immutable.
draw(globals())

# Mechanical-only symbols retain parity but stay small along the bottom margin.
for i,ref in enumerate(['H1','H2','H3','H4','H5']):place(ref,30.48+i*40.64,800.1)
for i,(n,x,y) in enumerate([('+5V_ADC',81.28,685.8),('GND',111.76,685.8),('VBAT_24V',510.54,760.73),('-5V_CT',278.13,1270),('+12V_AUX',114.3,558.8)]):
 x=round((15.24+(x-15.24)*0.75)/1.27)*1.27
 name='FLAG';ref=f'#FLG{i+1:03d}'
 symbols[name]=f'(symbol "FLAG" (power) (pin_names hide) (pin_numbers hide) (in_bom no) (on_board no) {prop("Reference","#FLG",0,0,True)} {prop("Value","PWR_FLAG",0,0,True)} (symbol "FLAG_0_1" (circle (center 0 0) (radius 0.8) (stroke (width 0.254) (type default)) (fill (type none)))) (symbol "FLAG_1_1" (pin power_out line (at 0 0 90) (length 0) (name "pwr" {E()}) (number "1" {E()}))))'
 flag_value=prop('Value','PWR_FLAG',x,y-5.08 if n=='-5V_CT' else y,n!='-5V_CT')
 items.append(f'(symbol (lib_id "Tesla:FLAG") (at {x} {y} 0) (unit 1) (in_bom no) (on_board no) (uuid "{uid(ref)}") {prop("Reference",ref,x,y,True)} {flag_value} (instances (project "controller" (path "/{uid("root")}" (reference "{ref}") (unit 1)))))');power(n,x,y)
# Snap final presentation coordinates together; symbol-library geometry stays unchanged.
# This retains the standard connection grid after whitespace compaction.
def snap_item(item):
 return re.sub(r'\((at|xy|start|end) (-?[\d.]+) (-?[\d.]+)',lambda m:f'({m[1]} {round(math.floor(float(m[2])/1.27+0.500001)*1.27,4)} {round(math.floor(float(m[3])/1.27+0.500001)*1.27,4)}',item)
items=[snap_item(item) for item in items]
from tesla_schematic_layout import reflow
items,paper=reflow(items,symbols,uid,D/'docs')
lib=''.join(s.replace('(symbol "'+n+'"','(symbol "Tesla:'+n+'"',1) for n,s in symbols.items())
(D/'controller.kicad_sch').write_text(f'(kicad_sch (version 20250114) (generator "eeschema") (uuid "{uid("root")}") (paper "User" {paper[0]:.2f} {paper[1]:.2f}) (title_block (title "Tesla coil controller / sensing, control and power") (rev "A0 - NOT FOR FABRICATION")) (lib_symbols {lib}) '+''.join(items)+')\n')
(D/'Tesla.kicad_sym').write_text('(kicad_symbol_lib (version 20250114) (generator "kicad_symbol_editor") '+''.join(symbols.values())+')\n')
print('Wrote acquisition draft schematic.')

# Presentation rebuilds never rewrite the PCB. Verify against the circuit contract.
import subprocess,tempfile,xml.etree.ElementTree as ET
with tempfile.TemporaryDirectory() as td:
 out=Path(td)/'net.xml'
 subprocess.run(['kicad-cli','sch','export','netlist','--format','kicadxml','-o',str(out),str(D/'controller.kicad_sch')],check=True,capture_output=True)
 actual={(p.get('ref'),p.get('pin')):n.get('name') for n in ET.parse(out).findall('./nets/net') for p in n.findall('node')}
 for ref,c in parts.items():
  for pin,expected in c['pins'].items():
   got=actual.get((ref,pin))
   if expected is None:
    assert got is None or got.startswith('unconnected-'),(ref,pin,got)
   else:assert got==expected,(ref,pin,expected,got)
print('Circuit contract verified; PCB untouched.')
