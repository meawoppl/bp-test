#!/usr/bin/env python3
"""Single-sheet, visibly wired calibrator schematic from the audited circuit contract."""
from pathlib import Path
import json,uuid,re,math
R=Path(__file__).resolve().parents[2];D=R/'boards/gps-time-calibrator';parts=json.loads((D/'docs/circuit.json').read_text())
uid=lambda s:str(uuid.uuid5(uuid.NAMESPACE_URL,'bp-calibrator-a/'+s));q=lambda s:json.dumps(str(s),ensure_ascii=False);items=[];symbols={};pins={};count=0
E=lambda size=1.27,justify='':f'(effects (font (size {size} {size})) '+(f'(justify {justify})' if justify else '')+')'
def prop(k,val,x,y,hide=False):return f'(property {q(k)} {q(val)} (at {x} {y} 0) {E()}'+(' (hide yes)' if hide else '')+')'
def wire(a,b):
 global count
 count+=1;items.append(f'(wire (pts (xy {a[0]} {a[1]}) (xy {b[0]} {b[1]})) (stroke (width 0) (type default)) (uuid "{uid("wire"+str(count))}"))')
def label(n,x,y,angle=0,right=False,stub=True):
 global count
 count+=1;items.append(f'(global_label {q(n)} (shape bidirectional) (at {x} {y} {angle}) {E(.65 if n.startswith(('BUF_','LED_')) else .95,"right" if right else "left")} (uuid "{uid("lab"+str(count))}"))')
def note(t,x,y,size=1.27):items.append(f'(text {q(t)} (at {x} {y} 0) {E(size,"left")} (uuid "{uid(t+str(x)+str(y))}"))')
def box(title,x,y,w,h):
 if x==10:x+=2.54;w-=2.54
 if y==10:y+=2.54;h-=2.54
 items.append(f'(rectangle (start {x} {y}) (end {x+w} {y+h}) (stroke (width 0.254) (type default)) (fill (type none)) (uuid "{uid(title)}"))');note(title,x+2.54,y+3.81,1.8)
def symdef(ref):
 c=parts[ref];kind=c['kind'];name=ref;pinmap={};shapes=[];s=[]
 if kind=='mosfet':
  lib=Path('/usr/share/kicad/symbols/Device.kicad_sym').read_text();start=lib.index('  (symbol "Q_NMOS_GSD"');end=lib.index('  (symbol "Q_NMOS_SDG"',start)
  sym=lib[start:end].strip().replace('Q_NMOS_GSD',ref);symbols[ref]=sym
  return {'1':(-5.08,0,0),'2':(2.54,-5.08,90),'3':(2.54,5.08,270)},5.08
 if kind in ['r','c','led','l']:
  # Horizontal KiCad-standard passive geometry, connected directly in each LED chain.
  pinmap={'1':(-5.08,0,0),'2':(5.08,0,180)}
  if kind=='l':
   shapes=[f'(arc (start {a} 0) (mid {a+.635} 1.27) (end {a+1.27} 0) (stroke (width 0.254) (type default)) (fill (type none)))' for a in [-2.54,-1.27,0,1.27]]
  elif kind=='r':shapes=['(polyline (pts (xy -2.54 0) (xy -1.905 1.016) (xy -0.635 -1.016) (xy 0.635 1.016) (xy 1.905 -1.016) (xy 2.54 0)) (stroke (width 0.254) (type default)) (fill (type none)))']
  elif kind=='c':shapes=['(polyline (pts (xy -0.635 -2.032) (xy -0.635 2.032)) (stroke (width 0.254) (type default)) (fill (type none)))','(polyline (pts (xy 0.635 -2.032) (xy 0.635 2.032)) (stroke (width 0.254) (type default)) (fill (type none)))']
  else:shapes=['(polyline (pts (xy -1.27 -1.27) (xy -1.27 1.27)) (stroke (width 0.254) (type default)) (fill (type none)))','(polyline (pts (xy -1.27 0) (xy 1.27 1.27) (xy 1.27 -1.27) (xy -1.27 0)) (stroke (width 0.254) (type default)) (fill (type none)))','(polyline (pts (xy 0 2) (xy -1.8 3.8) (xy -1.2 2.5)) (stroke (width 0.18) (type default)) (fill (type none)))']
  if kind=='led':
   pinmap={'1':(5.08,0,180),'2':(-5.08,0,0)}
   shapes=[re.sub(r'\(xy (-?[0-9.]+) (-?[0-9.]+)\)',lambda m:f'(xy {-float(m[1])} {m[2]})',t) for t in shapes]
  length=2.54 if kind in ['r','l'] else 4.445 if kind=='c' else 3.81
  for num,(x,y,a) in pinmap.items():s.append(f'(pin passive line (at {x} {y} {a}) (length {length}) (name "~" {E()}) (number "{num}" {E()}))')
  h=0;w=0
 else:
  if ref in ['U3','U4']:
   pinmap={str(i+2):(-20.32,17.78-i*5.08,0) for i in range(8)};pinmap.update({str(18-i):(20.32,17.78-i*5.08,180) for i in range(8)});pinmap.update({'1':(-20.32,-25.4,0),'19':(-20.32,-30.48,0),'10':(0,-38.1,90),'20':(0,38.1,270)});w=15.24;h=33.02
  elif kind=='connector' and ref in ['J1','J2']:
   nums=sorted(c['pins'],key=int);pinmap={n:((-12.7 if i<20 else 12.7),24.13-(i%20)*2.54,(0 if i<20 else 180)) for i,n in enumerate(nums)};w=7.62;h=26.67
  else:
   nums=list(c['pins']);half=(len(nums)+1)//2;w=15.24 if ref=='U6' else 7.62;h=max(5.08,(half+1)*2.54)
   pinmap={n:((-(w+5.08) if i<half else w+5.08),h-5.08-(i%half)*5.08,(0 if i<half else 180)) for i,n in enumerate(nums)}
  if kind=='hole':w=2.54;h=2.54
  shapes=[f'(rectangle (start {-w} {h}) (end {w} {-h}) (stroke (width 0.254) (type default)) (fill (type background)))']
  for num,(x,y,a) in pinmap.items():
   nm=c['names'].get(num,num);tp=c['types'].get(num,'passive')
   if ref in ['J1','J2']:nm='~'
   s.append(f'(pin {tp} line (at {x} {y} {a}) (length 5.08) (name {q(nm)} {E(1.0)}) (number {q(num)} {E(1.0)}))')
 symbols[name]=f'(symbol {q(name)} (pin_names (offset 0.762)'+(' hide' if kind in ['r','c','led','l'] else '')+') '+('(pin_numbers hide)' if kind in ['r','c','led','l'] else '')+f' (in_bom {"yes" if c["bom"] else "no"}) (on_board yes) {prop("Reference",ref,0,h+5.08)} {prop("Value",c["value"],0,h+2.54)} (symbol "{name}_0_1" '+''.join(shapes)+f') (symbol "{name}_1_1" '+''.join(s)+'))'
 return pinmap,h
base_symdef=symdef
# Symbol coordinates are conventional: supply up, return down, signal left-to-right.
def custom_map(ref):
 c=parts[ref]
 if ref in ['J1','J2']:
  ground=[n for n,v in c['pins'].items() if v=='GND'];supply=[n for n,v in c['pins'].items() if v=='VIN_5V'];other=sorted([n for n in c['pins'] if n not in ground+supply],key=int);half=(len(other)+1)//2
  m={n:((-17.78 if i<half else 17.78),38.1-(i%half)*5.08,(0 if i<half else 180)) for i,n in enumerate(other)}
  m.update({n:((i-(len(ground)-1)/2)*2.54,-48.26,90) for i,n in enumerate(ground)})
  m.update({n:((i-(len(supply)-1)/2)*5.08,48.26,270) for i,n in enumerate(supply)})
  return m,12.7,43.18
 if ref in ['U2','U5','U12']:
  return {'1':(-12.7,5.08,0),'3':(-12.7,0,0),'5':(12.7,5.08,180),'4':(12.7,-5.08,180),'2':(0,-15.24,90)},7.62,10.16
 if ref in ['U7','U10','U13']:
  m={'2':(-12.7,0,0),'4':(12.7,0,180),'5':(0,15.24,270),'3':(0,-15.24,90)}
  m['1']=(-12.7,-5.08,0) if ref=='U7' else (-5.08,-15.24,90) if ref=='U10' else (-12.7,5.08,0)
  return m,7.62,10.16
 if ref=='U1':return {'1':(-12.7,2.54,0),'3':(-12.7,-2.54,0),'6':(12.7,2.54,180),'4':(12.7,-2.54,180),'5':(0,15.24,270),'2':(0,-15.24,90)},7.62,10.16
 if ref=='U8':return {'1':(-12.7,5.08,0),'3':(-12.7,0,0),'5':(-12.7,-5.08,0),'6':(12.7,5.08,180),'4':(12.7,-5.08,180),'2':(0,-15.24,90)},7.62,10.16
 if ref=='U9':return {'3':(-12.7,5.08,0),'1':(-12.7,-5.08,0),'5':(12.7,5.08,180),'4':(0,15.24,270),'2':(0,-15.24,90),'6':(5.08,-15.24,90)},7.62,10.16
 if ref=='U11':return {'1':(-20.32,7.62,0),'2':(-20.32,2.54,0),'4':(-20.32,-7.62,0),'7':(20.32,7.62,180),'8':(20.32,2.54,180),'5':(20.32,-2.54,180),'6':(20.32,-7.62,180),'9':(20.32,-12.7,180),'3':(-7.62,-22.86,90),'10':(0,-22.86,90),'11':(7.62,-22.86,90),'12':(0,22.86,270)},15.24,17.78
 if ref=='U14':return {'3':(-17.78,7.62,0),'4':(-17.78,2.54,0),'2':(-17.78,-7.62,0),'5':(17.78,7.62,180),'6':(17.78,-7.62,180),'1':(-7.62,-17.78,90),'7':(10.16,-17.78,90),'8':(0,-17.78,90),'9':(5.08,-17.78,90)},12.7,12.7
 if ref=='U15':return {'2':(-17.78,7.62,0),'3':(-17.78,2.54,0),'7':(17.78,7.62,180),'6':(17.78,-2.54,180),'5':(17.78,-7.62,180),'8':(17.78,-12.7,180),'1':(-5.08,-20.32,90),'4':(5.08,-20.32,90)},12.7,15.24
 if ref=='DS1':return {'2':(0,20.32,270),'1':(0,-17.78,90),'3':(-12.7,7.62,0),'4':(-12.7,-2.54,0)},7.62,12.7
 if ref=='Y1':return {'4':(0,15.24,270),'2':(0,-15.24,90),'3':(17.78,0,180),'1':(-17.78,-5.08,0)},12.7,10.16
 if ref=='U6':
  m={'2':(-22.86,10.16,0),'3':(-22.86,5.08,0),'4':(-22.86,0,0),'5':(-22.86,-5.08,0),'11':(22.86,0,180)}
  m.update({n:(x,30.48,270) for n,x in [('6',-7.62),('7',0),('8',7.62)]});m.update({n:(x,-30.48,90) for n,x in [('1',-7.62),('10',0),('12',7.62)]})
  m.update({n:(-22.86,y,0) for n,y in [('9',-10.16),('13',-15.24),('14',-20.32)]});m.update({n:(22.86,y,180) for n,y in [('15',15.24),('16',10.16),('17',-10.16),('18',-15.24)]})
  return m,17.78,25.4
 if ref=='J3':
  m={n:(x,25.4,270) for n,x in [('A4',-7.62),('B9',-2.54),('A9',2.54),('B4',7.62)]}
  m.update({n:(x,-25.4,90) for n,x in [('A1',-10.16),('B12',-5.08),('A12',0),('B1',5.08),('S1',10.16)]})
  m.update({n:(17.78,y,180) for n,y in [('A6',17.78),('B6',12.7),('A5',5.08),('B5',0),('A7',-10.16),('B7',-15.24)]});m.update({'A8':(-17.78,0,0),'B8':(-17.78,-5.08,0)})
  return m,12.7,20.32
 if ref in ['J5','J6','J7']:return {'1':(-10.16,0,0),'2':(0,-10.16,90)},5.08,5.08
 return None

def symdef(ref):
 cm=custom_map(ref)
 if cm is None:return base_symdef(ref)
 pm,w,h=cm;c=parts[ref];assert set(pm)==set(c['pins']),(ref,pm,c['pins'])
 shape=f'(rectangle (start {-w} {h}) (end {w} {-h}) (stroke (width 0.254) (type default)) (fill (type background)))'
 ss=[]
 for n,(x,y,a) in pm.items():
  nm=c['names'].get(n,n);tp=c['types'].get(n,'passive')
  if ref in ['J1','J2']:nm='~'
  ss.append(f'(pin {tp} line (at {x} {y} {a}) (length 5.08) (name {q(nm)} {E(1.0)}) (number {q(n)} {E(1.0)}))')
 symbols[ref]=f'(symbol "{ref}" (pin_names (offset 0.762)) (in_bom yes) (on_board yes) {prop("Reference",ref,0,h+5.08)} {prop("Value",c["value"],0,h+2.54)} (symbol "{ref}_0_1" {shape}) (symbol "{ref}_1_1" '+''.join(ss)+'))'
 return pm,h

placed=set();covered=set();directions={};power_count=0
snap=lambda x:round(round(x/1.27)*1.27,4)
def place(ref,x,y,angle=0):
 x,y=snap(x),snap(y);c=parts[ref];pm,h=symdef(ref);placed.add(ref);a=math.radians(angle)
 def rot(dx,dy):return snap(x+dx*math.cos(a)-dy*math.sin(a)),snap(y-dx*math.sin(a)-dy*math.cos(a))
 if angle:
  def bake(m):
   dx,dy=float(m[2]),float(m[3]);xx=round(dx*math.cos(a)-dy*math.sin(a),4);yy=round(dx*math.sin(a)+dy*math.cos(a),4)
   aa=' '+str((float(m[4])+angle)%360) if m[4] is not None else ''
   return f'({m[1]} {xx} {yy}{aa})'
  symbols[ref]=re.sub(r'\((xy|at|start|end|mid|center) (-?[0-9.]+) (-?[0-9.]+)(?: (-?[0-9.]+))?\)',bake,symbols[ref])
 pins[ref]={n:rot(dx,dy) for n,(dx,dy,_) in pm.items()}
 for n,(_,_,pa) in pm.items():directions[ref,n]=(pa+angle)%360
 vert=angle%180!=0 and c['kind'] in ['r','c','led','l'];small=c['kind'] in ['r','c','led','l']
 rx,ry=(x+3.81,y-1.27) if vert else (x,y-h-(5.08 if small else 6.35));vx,vy=(rx,y+1.27) if vert else (x,ry+2.54)
 if ref in ['U6','U7','U9','U10','U11','U13','Y1']:
  rx=vx=x+22.86;ry=y+h+5.08;vy=ry+2.54
 if ref=='U1':rx=vx=x-20.32
 if ref=='DS1':rx=vx=x+13.97;ry=y+17.78;vy=ry+2.54
 if ref in ['J1','J2','U3','U4']:rx=vx=x+15.24
 if ref.startswith('R') and 140<=int(ref[1:])<=155:
  rx=x-3.81;vx=x+3.81;ry=vy=y-2.54
 val=c['value'];hide=c['kind']=='led' or ref in ['J1','J2','J6','DS1']
 meta=prop('Reference',ref,rx,ry)+prop('Value',val,vx,vy,hide)
 if vert:meta=meta.replace('(effects (font (size 1.27 1.27)))','(effects (font (size 1.27 1.27)) (justify left))')
 for k,vv in [('Footprint',c['footprint']),('LCSC',c['lcsc']),('MPN',c['mpn']),('Assembly',c.get('assembly','JLCPCB')),('Supplier URL',c.get('supplier_url',''))]:meta+=prop(k,vv,x,y,True)
 items.append(f'(symbol (lib_id "Calibrator:{ref}") (at {x} {y} 0) (unit 1) (in_bom {"yes" if c["bom"] else "no"}) (on_board yes) (uuid "{uid(ref)}") '+meta+f'(instances (project "calibrator" (path "/{uid("root")}" (reference "{ref}") (unit 1)))))')
 return pins[ref]
def P(r,n):covered.add((r,str(n)));return pins[r][str(n)]
def path(*pts):
 for a,b in zip(pts,pts[1:]):
  a=tuple(map(snap,a));b=tuple(map(snap,b))
  if a!=b:wire(a,b)
def junction(pt):
 x,y=map(snap,pt);items.append(f'(junction (at {x} {y}) (diameter 0) (color 0 0 0 0) (uuid "{uid("junction"+str((x,y)))}"))')
def label(n,x,y,angle=0,right=False,stub=True):
 global count
 count+=1;x,y=snap(x),snap(y)
 if stub:path((x,y),(x,y-2.54));y=snap(y-2.54)
 items.append(f'(global_label {q(n)} (shape passive) (at {x} {y} {angle}) {E(1.27,"right" if right else "left")} (uuid "{uid("label"+str(count))}"))')
def power(n,x,y,flag=False):
 global power_count
 x,y=snap(x),snap(y);power_count+=1;name='PWR_'+re.sub('[^A-Za-z0-9]','_',n);ref=f'#PWR{power_count:04d}'
 if name not in symbols:
  if n=='GND':shape='(polyline (pts (xy 0 0) (xy 0 -1.27) (xy -2.54 -1.27) (xy 0 -3.81) (xy 2.54 -1.27) (xy 0 -1.27)) (stroke (width 0.254) (type default)) (fill (type none)))'
  else:shape='(polyline (pts (xy 0 0) (xy 0 3.81) (xy -1.27 2.54) (xy 0 3.81) (xy 1.27 2.54)) (stroke (width 0.254) (type default)) (fill (type none)))'
  symbols[name]=f'(symbol "{name}" (power) (pin_names hide) (pin_numbers hide) (in_bom no) (on_board no) {prop("Reference","#PWR",0,0,True)} {prop("Value",n,0,5.08)} (symbol "{name}_0_1" {shape}) (symbol "{name}_1_1" (pin power_in line (at 0 0 90) (length 0) (name {q(n)} {E()}) (number "1" {E()}))))'
 items.append(f'(symbol (lib_id "Calibrator:{name}") (at {x} {y} 0) (unit 1) (in_bom no) (on_board no) (uuid "{uid(ref)}") {prop("Reference",ref,x,y,True)} {prop("Value",n,x,y+(5.08 if n=="GND" else -6.35),n=="GND")} (instances (project "calibrator" (path "/{uid("root")}" (reference "{ref}") (unit 1)))))')
 if flag:
  name='PWR_FLAG';ref=f'#FLG{power_count:04d}'
  symbols[name]=f'(symbol "{name}" (power) (pin_names hide) (pin_numbers hide) (in_bom no) (on_board no) {prop("Reference","#FLG",0,0,True)} {prop("Value","PWR_FLAG",0,0,True)} (symbol "{name}_0_1" (circle (center 0 1.27) (radius 1.27) (stroke (width 0.254) (type default)) (fill (type none)))) (symbol "{name}_1_1" (pin power_out line (at 0 0 90) (length 0) (name "pwr" {E()}) (number "1" {E()}))))'
  items.append(f'(symbol (lib_id "Calibrator:{name}") (at {x} {y} 0) (unit 1) (in_bom no) (on_board no) (uuid "{uid(ref)}") {prop("Reference",ref,x,y,True)} {prop("Value","PWR_FLAG",x,y,True)} (instances (project "calibrator" (path "/{uid("root")}" (reference "{ref}") (unit 1)))))')
def port(r,n,length=7.62):
 pt=P(r,n);nn=parts[r]['pins'][str(n)]
 if nn is None:items.append(f'(no_connect (at {pt[0]} {pt[1]}) (uuid "{uid(r+str(n)+"nc")}"))');return
 angle=directions[r,str(n)];dx,dy={0:(-length,0),180:(length,0),90:(0,length),270:(0,-length)}[angle];end=(pt[0]+dx,pt[1]+dy);path(pt,end)
 if nn=='GND' or nn.startswith('+') or nn in ['VIN_5V','USB_VBUS']:power(nn,*end)
 else:label(nn,*end,right=dx<0,stub=dy==0)
def bus(r,nums,y,n,flag=False):
 ps=[P(r,nn) for nn in nums];xx=[a[0] for a in ps];y=snap(y)
 for a in ps:path(a,(a[0],y));junction((a[0],y))
 path((min(xx),y),(max(xx),y));power(n,min(xx),y,flag)
def bypass(ref,x,y,n,upper=None,lower=None):
 place(ref,x,y,270);a=P(ref,1);b=P(ref,2)
 top=(a[0],snap(upper if upper is not None else a[1]-3.81));bot=(b[0],snap(lower if lower is not None else b[1]+2.54));path(top,a);path(b,bot)
 if upper is None:power(n,*top)
 if lower is None:power('GND',*bot)
 return top,bot
# Match the module schematic's dashed section outlines.
def box(title,x,y,w,h):
 x,y,w,h=map(snap,(x,y,w,h));items.append(f'(rectangle (start {x} {y}) (end {x+w} {y+h}) (stroke (width 0.254) (type dash)) (fill (type none)) (uuid "{uid(title)}"))');note(title,x+2.54,y+3.81,1.8)
# ---- Interface and USB-C power ------------------------------------------------
box('MODULE v1 / exact programmer mating interface',12.7,12.7,251.46,137.16)
for ref,x in [('J1',73.66),('J2',205.74)]:
 place(ref,x,82.55)
 gs=[n for n,vv in parts[ref]['pins'].items() if vv=='GND'];bus(ref,gs,134.62,'GND')
 vs=[n for n,vv in parts[ref]['pins'].items() if vv=='VIN_5V']
 if vs:bus(ref,vs,29.21,'VIN_5V')
 for n in parts[ref]['pins']:
  if (ref,n) not in covered:port(ref,n,7.62)
note('25 mm mating spacing / module top flush / no reset or boot switch',17.78,143.51,1.1)
box('USB-C / 5 V, 3 A source detection and protected power',271.78,12.7,553.72,137.16)
place('J3',302.26,81.28)
bus('J3',['A4','B9','A9','B4'],50.8,'USB_VBUS',True);bus('J3',['A1','B12','A12','B1','S1'],111.76,'GND',True)
for nn in ['A8','B8','A5','B5']:port('J3',nn)
for nums,name in [(['A6','B6'],'USB_D+'),(['A7','B7'],'USB_D-')]:
 ps=[P('J3',n) for n in nums];x=325.12
 for pt in ps:path(pt,(x,pt[1]))
 path((x,ps[0][1]),(x,ps[1][1]));label(name,x,ps[0][1])
place('U1',360.68,68.58)
for n in ['1','3','4','6']:port('U1',n)
bypass('C1',382.27,44.45,'USB_VBUS',upper=35.56)
path(P('U1',5),(360.68,35.56),(382.27,35.56));power('USB_VBUS',360.68,35.56);port('U1',2)
place('U11',438.15,71.12);port('U11',1);port('U11',2)
bus('U11',['3','10','11'],99.06,'GND')
bypass('C64',408.94,41.91,'USB_VBUS',upper=33.02)
path(P('U11',12),(438.15,33.02),(408.94,33.02));power('USB_VBUS',438.15,33.02)
# Required 900k VBUS detection chain is visibly in series.
for ref,x in [('R164',365.76),('R165',387.35),('R166',408.94)]:place(ref,x,124.46)
path(P('R164',2),P('R165',1));label('VBUS_DET_A',*P('R164',2))
path(P('R165',2),P('R166',1));label('VBUS_DET_B',*P('R165',2))
path(P('R164',1),(353.06,124.46));power('USB_VBUS',353.06,124.46)
path(P('R166',2),(419.1,124.46),(419.1,111.76),(412.75,111.76),(412.75,78.74),P('U11',4));label('VBUS_DET',419.1,124.46)
# Pull-ups go to the always-on logic rail, directly on the status outputs.
for ref,x,n,y in [('R167',478.79,'7',63.5),('R168',502.92,'8',68.58)]:
 place(ref,x,45.72,270);path(P(ref,2),(snap(x),snap(y)),P('U11',n));junction((x,y));power('+3V3_CC',*P(ref,1));label(parts[ref]['pins']['2'],x,y)
place('U13',553.72,111.76)
path(P('U11',7),(478.79,63.5),(478.79,106.68),P('U13',1))
path(P('U11',8),(502.92,68.58),(502.92,111.76),P('U13',2))
bypass('C67',577.85,91.44,'+3V3_CC',upper=80.01)
path(P('U13',5),(553.72,80.01),(577.85,80.01));power('+3V3_CC',553.72,80.01);port('U13',3)
# Compact, explicitly wired LDO macro used for all three rails.
def ldo(ref,ci,co,x,y):
 place(ref,x,y);a=P(ref,1);en=P(ref,3);out=P(ref,5)
 lx=snap(x-25.4);rx=snap(x+26.67);top=snap(y-5.08)
 path(a,(lx,top),(lx,snap(y)));path(en,(lx,en[1]));junction((lx,en[1]))
 bypass(ci,lx,y+8.89,parts[ref]['pins']['1'],upper=top);power(parts[ref]['pins']['1'],lx,top)
 path(out,(rx,top));bypass(co,rx,y+8.89,parts[ref]['pins']['5'],upper=top);power(parts[ref]['pins']['5'],rx,top)
 port(ref,2,2.54);port(ref,4)
ldo('U12','C65','C66',558.8,46.99)
place('U14',699.77,60.96)
# Raw input reservoir and parallel IN pins.
bypass('C69',641.35,58.42,'USB_VBUS',upper=44.45)
path(P('U14',3),(666.75,53.34),(666.75,44.45),(641.35,44.45));path(P('U14',4),(666.75,58.42),(666.75,53.34));junction((666.75,53.34));power('USB_VBUS',641.35,44.45)
path(P('U13',4),(613.41,111.76),(613.41,68.58),P('U14',2));label('USB_3A_EN',600.71,111.76)
place('R169',598.17,124.46,270);path(P('R169',1),(598.17,111.76));junction((598.17,111.76));power('GND',*P('R169',2))
place('C68',673.1,102.87,270);path(P('U14',1),(692.15,87.63),(673.1,87.63),P('C68',1));label('USB_DVDT',673.1,87.63);power('GND',*P('C68',2))
place('R170',737.87,102.87,270);path(P('U14',7),(709.93,87.63),(737.87,87.63),P('R170',1));label('USB_ILIM',715.01,87.63);power('GND',*P('R170',2));bus('U14',['8','9'],81.28,'GND')
path(P('U14',5),(746.76,53.34));power('VIN_5V',746.76,53.34)
# One real power indicator, wired as LED plus its own resistor.
place('R3',774.7,58.42,270);place('D1',774.7,83.82,270)
path(P('R3',1),(774.7,45.72));power('VIN_5V',774.7,45.72)
path(P('R3',2),P('D1',2));label(parts['R3']['pins']['2'],774.7,71.12);power('GND',*P('D1',1))
note('Main rail enabled only for 3 A advertisement. 820R: ~2.48 A limit; 100nF: ~12 ms soft start.',486.41,140.97,1.1)
note('No high-voltage PD negotiation. Lower-current sources leave the main board off.',486.41,146.05,1.1)
# ---- GNSS receiver and active-antenna bias ------------------------------------
box('GNSS / PPS reference and active antenna bias',12.7,156.21,302.26,118.11)
place('U6',93.98,218.44)
bus('U6',['6','7','8'],181.61,'+3V3_GPS');bus('U6',['1','10','12'],254,'GND')
for ref,x in [('C8',58.42),('C9',73.66)]:
 bypass(ref,x,190.5,'+3V3_GPS',upper=181.61);path((x,181.61),(86.36,181.61));junction((86.36,181.61))
port('U6',2,15.24);port('U6',3,15.24);port('U6',5,15.24)
# PPS fans out through two source damping resistors.
path(P('U6',4),(20.32,218.44),(20.32,231.14));label('GPS_PPS',20.32,218.44)
for ref,y in [('R6',251.46),('R7',266.7)]:
 place(ref,44.45,y);path(P(ref,1),(30.48,snap(y)),(30.48,231.14),(20.32,231.14));port(ref,2,3.81)
# Antenna protector and bias tee: 3V3 -> limiter -> R -> L -> RF line.
place('U8',200.66,184.15)
for n in ['1','3','5']:
 a=P('U8',n);path(a,(177.8,a[1]))
path((177.8,179.07),(177.8,189.23));power('+3V3_GPS',177.8,179.07)
bypass('C12',161.29,187.96,'+3V3_GPS',upper=175.26);path((161.29,175.26),(177.8,175.26),(177.8,179.07));port('U8',2)
place('R5',238.76,179.07);path(P('U8',6),P('R5',1));label('ANT_PWR',218.44,179.07)
place('L1',266.7,205.74,90);path(P('R5',2),(266.7,179.07),P('L1',2));label('ANT_BIAS',254,179.07)
bypass('C10',241.3,199.39,'ANT_BIAS',upper=184.15);path((241.3,184.15),(254,184.15),(254,179.07));junction((254,179.07))
place('J5',295.91,218.44);path(P('U6',11),P('J5',1));label('GNSS_RF',137.16,218.44)
path(P('L1',1),(266.7,218.44));junction((266.7,218.44));port('J5',2)
note('RF feed is straight; protected 3.3 V bias is for an active GPS antenna.',137.16,246.38,1.1)
note('PPS supplies absolute epoch; OCXO supplies the local timebase.',137.16,264.16,1.1)
# ---- External input/output ----------------------------------------------------
box('External triggers / 5 V I-O / input threshold ~2.5 V',322.58,156.21,236.22,118.11)
place('J6',340.36,193.04);place('R8',374.65,193.04);place('U9',419.1,198.12)
# Input SMA points left graphically; lead exits and loops below the connector to R8.
path(P('J6',1),(327.66,193.04),(327.66,182.88),(359.41,182.88),(359.41,193.04),P('R8',1));label('TRIGGER_IN',346.71,182.88);port('J6',2)
path(P('R8',2),P('U9',3));label('TRIGGER_LIMIT',382.27,193.04)
bypass('C75',381,208.28,'TRIGGER_LIMIT',upper=193.04);junction((381,193.04))
place('R9',391.16,208.28,270);path(P('R9',1),(391.16,193.04));junction((391.16,193.04));power('GND',*P('R9',2))
# 2.5 V threshold divider and filter directly feed IN-.
place('R160',368.3,216.535,270);place('R161',368.3,245.11,270)
power('VIN_5V',*P('R160',1));path(P('R160',2),(368.3,231.14),P('R161',1));power('GND',*P('R161',2))
path((368.3,231.14),(401.32,231.14),(401.32,203.2),P('U9',1));label('TRIGGER_VREF',375.92,231.14)
bypass('C13',391.16,246.38,'TRIGGER_VREF',upper=231.14);junction((391.16,231.14))
bypass('C14',439.42,176.53,'VIN_5V',upper=168.91);path(P('U9',4),(419.1,168.91),(439.42,168.91));power('VIN_5V',419.1,168.91);bus('U9',['2','6'],218.44,'GND')
place('U7',480.06,193.04);path(P('U9',5),P('U7',2));label('TRIGGER_5V',441.96,193.04)
bypass('C11',501.65,175.26,'+3V3_LOGIC',upper=170.18);path(P('U7',5),(480.06,170.18),(501.65,170.18));power('+3V3_LOGIC',480.06,170.18);port('U7',3)
for ref,y in [('R80',193.04),('R81',208.28)]:
 place(ref,530.86,y);path(P('U7',4),(515.62,193.04),(515.62,snap(y)),P(ref,1));port(ref,2,3.81)
label('TRIGGER_3V3',500.38,193.04)
# Output below input, with a grounded enable and source resistor.
place('U10',474.98,248.92);place('R162',509.27,248.92);place('J7',547.37,248.92)
path(P('U10',4),P('R162',1));label('TRIGGER_DRV',490.22,248.92);path(P('R162',2),P('J7',1));label('TRIGGER_OUT',519.43,248.92);port('J7',2)
place('R163',444.5,256.54,270);path(P('U10',2),(444.5,248.92),P('R163',1));label('FPGA_IOT_51A',429.26,248.92);path((429.26,248.92),(444.5,248.92));power('GND',*P('R163',2));bus('U10',['1','3'],267.97,'GND')
bypass('C15',501.65,233.68,'VIN_5V',upper=223.52);path(P('U10',5),(474.98,223.52),(492.76,223.52),(501.65,223.52));power('VIN_5V',492.76,223.52)
# ---- OCXO supply and clock ----------------------------------------------------
box('10 MHz OCXO / dedicated 3.3 V buck and clock output',566.42,156.21,259.08,118.11)
place('U15',619.76,201.93);place('L2',656.59,194.31)
bypass('C70',586.74,203.2,'VIN_5V',upper=187.96);path(P('U15',2),(595.63,194.31),(595.63,187.96),(586.74,187.96));path(P('U15',3),(595.63,199.39),(595.63,194.31));junction((595.63,194.31));power('VIN_5V',586.74,187.96)
path(P('U15',7),P('L2',1));label('OCXO_SW',640.08,194.31)
for ref,x in [('C71',687.07),('C72',706.12)]:bypass(ref,x,208.28,'+3V3_OCXO',upper=194.31)
path(P('L2',2),(706.12,194.31));junction((687.07,194.31));power('+3V3_OCXO',706.12,194.31,True)
path(P('U15',6),(679.45,204.47),(679.45,194.31));junction((679.45,194.31))
place('R171',661.67,215.9,270);place('R172',661.67,247.65,270)
path(P('R171',1),(661.67,194.31));junction((661.67,194.31));path(P('R171',2),P('R172',1));path(P('U15',5),(645.16,209.55),(645.16,233.68),(661.67,233.68));junction((661.67,233.68));label('OCXO_FB',645.16,233.68);power('GND',*P('R172',2));bus('U15',['1','4'],227.33,'GND')
place('Y1',755.65,209.55);place('R173',786.13,209.55)
path(P('Y1',3),P('R173',1));path((777.24,209.55),(777.24,217.17));label('OCXO_CLK',777.24,217.17,stub=False);port('R173',2,3.81);port('Y1',2)
for ref,x in [('C73',733.425),('C74',779.78)]:bypass(ref,x,184.15,'+3V3_OCXO',upper=175.26)
path(P('Y1',4),(755.65,175.26),(779.78,175.26));path((733.425,175.26),(755.65,175.26));power('+3V3_OCXO',755.65,175.26)
note('Manual-fit AOC97FAJC-10.0000 / 2.1 W max warmup / allow 3 min.',576.58,261.62,1.15)
note('Clock -> J2.32 / FPGA G6. Firmware must use 10 MHz.',576.58,269.24,1.15)
# ---- Display buffers and local supply rails -----------------------------------
for bank,bx in [(0,12.7),(1,213.36)]:
 box(f'Display buffer / bits {15-bank*8}..{8-bank*8}',bx,281.94,193.04,97.79)
 ref='U'+str(3+bank);cx=snap(bx+116.84);cy=330.2;place(ref,cx,cy)
 gx=snap(bx+13.97);rx=snap(bx+36.83)
 for k in range(8):
  col=bank*8+k;pn=str(k+2);yy=pins[ref][pn][1];rr='R'+str(140+col);place(rr,rx,yy,180)
  path(P(rr,1),P(ref,pn));label(parts[rr]['pins']['1'],rx+10.16,yy)
  path(P(rr,2),(gx,yy));junction((gx,yy));port(ref,str(18-k),16.51)
 path((gx,pins[ref]['2'][1]),(gx,372.11));power('GND',gx,372.11)
 for n in ['1','19']:
  a=P(ref,n);path(a,(cx-25.4,a[1]),(cx-25.4,374.65))
 path((cx-25.4,374.65),(cx,374.65),P(ref,10));power('GND',cx,374.65)
 cc='C'+str(4+bank);bypass(cc,cx+34.29,298.45,'+3V3_LOGIC',upper=292.1)
 path(P(ref,20),(cx+34.29,292.1));power('+3V3_LOGIC',cx+34.29,292.1)
box('Logic / GNSS rails and RUN default',414.02,281.94,190.5,97.79)
ldo('U2','C2','C3',457.2,308.61);ldo('U5','C6','C7',457.2,355.6)
place('R4',558.8,319.405,90)
for n in ['1','2']:port('R4',n)
note('No boot/reset switches.',525.78,345.44,1.2)
note('Module retains EN pull-up.',525.78,353.06,1.2)
note('Normal RUN when fitted.',525.78,360.68,1.2)
box('Main rail bulk / mounts',612.14,281.94,86.36,97.79)
for i in range(4):
 x=622.3+i*20.32;bypass('C'+str(60+i),x,309.88,'VIN_5V',upper=299.72,lower=322.58)
path((622.3,299.72),(683.26,299.72));power('VIN_5V',622.3,299.72)
path((622.3,322.58),(683.26,322.58));power('GND',622.3,322.58)
for i in range(5):place('H'+str(i+1),622.3+i*15.24,353.06)
note('M3 spacer + four corner mounts.',617.22,373.38,1.0)
box('Date / UTC / GPS status OLED',706.12,281.94,119.38,97.79)
place('DS1',777.24,337.82)
for ref,x,pin,net in [('R174',737.87,3,'ESP_GPIO2'),('R175',753.11,4,'ESP_GPIO1')]:
 place(ref,x,309.88,270);path(P(ref,1),(x,297.18));path(P(ref,2),(x,P('DS1',pin)[1]),P('DS1',pin));label(net,x-20.32,P('DS1',pin)[1]);path((x-20.32,P('DS1',pin)[1]),(x,P('DS1',pin)[1]))
path((737.87,297.18),(753.11,297.18),(777.24,297.18));path((777.24,297.18),P('DS1',2));power('+3V3_LOGIC',777.24,297.18)
for ref,x in [('C76',802.64),('C77',817.88)]:
 bypass(ref,x,326.39,'+3V3_LOGIC',upper=307.34);path((x,307.34),(777.24,307.34));junction((777.24,307.34))
port('DS1',1,2.54)
note('SSD1315 / 128x64 / I2C 0x3C',711.2,367.03,1.1)
note('3.3 V only / manual assembly',711.2,373.38,1.1)
# ---- Four compact banks, each with four complete optical columns ---------------
def below(n,x,y):
 label(n,x,y);items[-1]=items[-1]
for bank in range(4):
 bx=12.7+bank*203.2;box(f'OPTICAL BANK {bank+1} / bits {15-bank*4}..{12-bank*4} / four identical rows',bx,387.35,200.66,153.67)
 for kk in range(4):
  col=bank*4+kk;x=12.7+col*50.8;bit=15-col;left=snap(x+3.81);right=snap(x+43.18)
  # Each branch has its own resistor. The two common rails are drawn, not repeated labels.
  for row in range(4):
   y=406.4+row*17.78;idx=row*16+col;rr='R'+str(10+idx);dd='D'+str(10+idx)
   place(rr,x+12.7,y);place(dd,x+30.48,y)
   path((left,y),P(rr,1));path(P(rr,2),P(dd,2));below(parts[rr]['pins']['2'],*P(rr,2));path(P(dd,1),(right,y));junction((left,y));junction((right,y))
  path((left,403.86),(left,505.46));power('VIN_5V',left,403.86)
  path((right,406.4),(right,472.44));label('LED_K'+str(bit),right,464.82,right=True)
  qq='Q'+str(col+1);place(qq,x+40.64,477.52);path((right,472.44),P(qq,3));port(qq,2,2.54)
  rg='R'+str(100+col);place(rg,x+15.24,477.52);path(P(rg,2),P(qq,1));below('GATE'+str(bit),*P(rg,2));a=P(rg,1);path(a,(x+5.08,477.52),(x+5.08,469.90));label(parts[rg]['pins']['1'],x+5.08,469.90)
  rd='R'+str(120+col);place(rd,x+26.67,492.76,270);path(P(rd,1),(x+26.67,477.52));junction((x+26.67,477.52));power('GND',*P(rd,2))
  for ref,xx in [('C'+str(20+col),x+12.7),('C'+str(40+col),x+34.29)]:bypass(ref,xx,515.62,'VIN_5V',upper=505.46,lower=525.78)
  path((left,505.46),(x+12.7,505.46),(x+34.29,505.46))
  path((x+12.7,525.78),(x+34.29,525.78));power('GND',x+12.7,525.78)
  note('BIT '+str(bit),x+12.7,535.94,1.5)
note('4 x 16 blue LEDs / individual 470R 1% resistors / all four rows show the same bit / 1 LSB = 1/65536 s = 15.258789 us',15.24,570.23,1.5)
note('Prototype hardware: firmware, absolute latency, brightness uniformity and power/RF behavior require validation.',15.24,577.85,1.3)
# Only true off-block signals and intentionally unused pins receive loose ports.
for ref in sorted(placed):
 for n in parts[ref]['pins']:
  if (ref,n) not in covered:
   assert parts[ref]['kind'] not in ['r','c','l','led','mosfet'],('unwired passive',ref,n)
   port(ref,n)
assert placed==set(parts),(set(parts)-placed,placed-set(parts))
# Split wires at every endpoint/junction for deterministic KiCad connectivity.
# Retain local labels to preserve the audited net names while making topology visible.
def normalize_wires():
 global items
 wire_items=[a for a in items if a.startswith('(wire ')]
 segs=[]
 for a in wire_items:
  ps=re.findall(r'\(xy (-?[0-9.]+) (-?[0-9.]+)\)',a)
  segs.append(tuple(tuple(round(float(v),4) for v in pt) for pt in ps))
 points={pt for seg in segs for pt in seg}
 def on(pt,a,b):
  return abs((pt[0]-a[0])*(b[1]-a[1])-(pt[1]-a[1])*(b[0]-a[0]))<1e-5 and min(a[0],b[0])-1e-5<=pt[0]<=max(a[0],b[0])+1e-5 and min(a[1],b[1])-1e-5<=pt[1]<=max(a[1],b[1])+1e-5
 result=set()
 for a,b in segs:
  ps=sorted([pt for pt in points if on(pt,a,b)],key=lambda pt:math.dist(a,pt))
  for pp,qq in zip(ps,ps[1:]):
   if pp!=qq:result.add(tuple(sorted([pp,qq])))
 items=[a for a in items if not a.startswith(('(wire ','(junction '))]
 degree={}
 for a,b in sorted(result):
  wire(a,b)
  for pt in [a,b]:degree[pt]=degree.get(pt,0)+1
 for pt,d in degree.items():
  if d>=3:junction(pt)
normalize_wires()
def save():
 lib=''.join(s.replace('(symbol "'+n+'"','(symbol "Calibrator:'+n+'"',1) for n,s in symbols.items())
 (D/'calibrator.kicad_sch').write_text(f'(kicad_sch (version 20250114) (generator "eeschema") (uuid "{uid("root")}") (paper "A1") (title_block (title "GPS optical time calibrator / module v1 carrier") (rev "A draft") (company "bp-test")) (lib_symbols '+lib+') '+''.join(items)+')\n')
 (D/'Calibrator.kicad_sym').write_text('(kicad_symbol_lib (version 20250114) (generator "kicad_symbol_editor") '+''.join(symbols.values())+')\n')
save()
# Footprint positions, nets and tracks stay unchanged; only hierarchy paths flatten.
import pcbnew as p
b=p.LoadBoard(str(D/'calibrator.kicad_pcb'))
for f in b.GetFootprints():f.SetPath(p.KIID_PATH('/'+uid('root')+'/'+uid(f.GetReference())))
p.SaveBoard(str(D/'calibrator.kicad_pcb'),b)
print('Created one A1 sheet with',len(placed),'parts')
