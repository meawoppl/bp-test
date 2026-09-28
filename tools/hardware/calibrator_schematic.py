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
  ground=[n for n,v in c['pins'].items() if v=='GND'];supply=[n for n,v in c['pins'].items() if v in ['VIN_5V','USB_VBUS']];other=sorted([n for n in c['pins'] if n not in ground+supply],key=int);half=(len(other)+1)//2
  m={n:((-17.78 if i<half else 17.78),38.1-(i%half)*5.08,(0 if i<half else 180)) for i,n in enumerate(other)}
  m.update({n:((i-(len(ground)-1)/2)*2.54,-48.26,90) for i,n in enumerate(ground)})
  m.update({n:((i-(len(supply)-1)/2)*5.08,48.26,270) for i,n in enumerate(supply)})
  return m,12.7,43.18
 if ref in ['U2','U5','U12']:
  return {'1':(-12.7,5.08,0),'3':(-12.7,0,0),'5':(12.7,5.08,180),'4':(12.7,-5.08,180),'2':(0,-15.24,90)},7.62,10.16
 if ref in ['U7','U10','U13','U16']:
  m={'2':(-12.7,0,0),'4':(12.7,0,180),'5':(0,15.24,270),'3':(0,-15.24,90)}
  m['1']=(-12.7,-5.08,0) if ref in ['U7','U16'] else (-5.08,-15.24,90) if ref=='U10' else (-12.7,5.08,0)
  return m,7.62,10.16
 if ref=='U1':return {'1':(-12.7,2.54,0),'3':(-12.7,-2.54,0),'6':(12.7,2.54,180),'4':(12.7,-2.54,180),'5':(0,15.24,270),'2':(0,-15.24,90)},7.62,10.16
 if ref=='U8':return {'1':(-12.7,5.08,0),'3':(-12.7,0,0),'5':(-12.7,-5.08,0),'6':(12.7,5.08,180),'4':(12.7,-5.08,180),'2':(0,-15.24,90)},7.62,10.16
 if ref=='U9':return {'3':(-12.7,5.08,0),'1':(-12.7,-5.08,0),'5':(12.7,5.08,180),'4':(0,15.24,270),'2':(0,-15.24,90),'6':(5.08,-15.24,90)},7.62,10.16
 if ref=='U11':return {'4':(-20.32,7.62,0),'5':(-20.32,2.54,0),'2':(-20.32,-7.62,0),'3':(-20.32,-12.7,0),'6':(20.32,7.62,180),'7':(20.32,2.54,180),'9':(20.32,-7.62,180),'10':(20.32,-12.7,180),'8':(-7.62,-22.86,90),'11':(0,-22.86,90),'1':(0,22.86,270)},15.24,17.78
 if ref=='U14':return {'3':(-17.78,7.62,0),'4':(-17.78,2.54,0),'2':(-17.78,-7.62,0),'5':(17.78,7.62,180),'6':(17.78,-7.62,180),'1':(-7.62,-17.78,90),'7':(10.16,-17.78,90),'8':(0,-17.78,90),'9':(5.08,-17.78,90)},12.7,12.7
 if ref=='U15':return {'2':(-17.78,7.62,0),'1':(-17.78,-2.54,0),'4':(17.78,7.62,180),'5':(17.78,-2.54,180),'3':(-5.08,-20.32,90),'6':(5.08,-20.32,90)},12.7,15.24
 if ref=='J8':return {'2':(0,20.32,270),'1':(0,-17.78,90),'3':(-12.7,7.62,0),'4':(-12.7,-2.54,0)},7.62,12.7
 if ref=='Y1':return {'4':(0,15.24,270),'2':(0,-15.24,90),'3':(17.78,0,180),'1':(-17.78,-5.08,0)},12.7,10.16
 if ref=='U6':
  m={'2':(-22.86,10.16,0),'3':(-22.86,5.08,0),'4':(-22.86,0,0),'5':(-22.86,-5.08,0),'11':(22.86,0,180)}
  m.update({n:(x,30.48,270) for n,x in [('6',-7.62),('7',0),('8',7.62)]});m.update({n:(x,-30.48,90) for n,x in [('1',-7.62),('10',0),('12',7.62)]})
  m.update({n:(-22.86,y,0) for n,y in [('9',-10.16),('13',-15.24),('14',-20.32)]});m.update({n:(22.86,y,180) for n,y in [('15',15.24),('16',10.16),('17',-10.16),('18',-15.24)]});m['14']=(22.86,20.32,180)
  m.update({n:(-22.86,y,0) for n,y in [('2',-5.08),('3',-10.16),('5',-15.24),('9',-20.32),('13',-25.4)]});m['13']=(22.86,-20.32,180)
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
 if ref=='Y1':rx=vx=x-6.35;ry=y+36.83;vy=ry+2.54
 if ref=='U1':rx=vx=x-20.32
 if ref=='J8':rx=vx=x+13.97;ry=y+17.78;vy=ry+2.54
 if ref in ['J1','J2','U3','U4']:rx=vx=x+15.24
 if False: # Input pulldowns removed; R140 is now the OE pull-up.
  rx=x-3.81;vx=x+3.81;ry=vy=y-2.54
 val=c['value'];hide=c['kind']=='led' or ref in ['J1','J2','J6','DS1']
 meta=prop('Reference',ref,rx,ry)+prop('Value',val,vx,vy,hide)
 if vert:meta=meta.replace('(effects (font (size 1.27 1.27)))','(effects (font (size 1.27 1.27)) (justify left))')
 for k,vv in [('Footprint',c['footprint']),('LCSC',c['lcsc']),('MPN',c['mpn']),('Assembly',c.get('assembly','JLCPCB')),('Supplier URL',c.get('supplier_url',''))]:meta+=prop(k,vv,x,y,True)
 if c.get('manufacturer'):meta+=prop('Manufacturer',c['manufacturer'],x,y,True)
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
 if right and angle==0:angle=180
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
 vs=[n for n,vv in parts[ref]['pins'].items() if vv in ['VIN_5V','USB_VBUS']]
 if vs:bus(ref,vs,29.21,parts[ref]['pins'][vs[0]])
 for n in parts[ref]['pins']:
  if (ref,n) not in covered:port(ref,n,7.62)
note('25 mm mating spacing / module top flush / no reset or boot switch',17.78,143.51,1.1)
box('USB-C PD / 5 V, 3 A sink and protected power',271.78,12.7,553.72,137.16)
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
place('U11',438.15,71.12)
for n in ['4','5','2','3','10']:port('U11',n)
bus('U11',['8','11'],99.06,'GND')
bypass('C64',408.94,41.91,'USB_VBUS',upper=33.02)
path(P('U11',1),(438.15,33.02),(408.94,33.02));power('USB_VBUS',438.15,33.02)
place('R164',478.79,93.98,270)
path(P('U11',9),(478.79,78.74),P('R164',1));power('GND',*P('R164',2))
label('PD_ISET',466.09,78.74)
for ref,x,n,y in [('R167',478.79,'6',63.5),('R168',502.92,'7',68.58)]:
 place(ref,x,45.72,270);path(P(ref,2),(snap(x),snap(y)),P('U11',n));junction((x,y));power('+3V3_CC',*P(ref,1));label(parts[ref]['pins']['2'],x,y)
note('5 V ONLY: VSET grounded / ISET 22.6k = 3 A / I2C 0x08',353.06,121.92,1.2)
note('D+/D- charger detection unused; USB data stays with ESP32',353.06,129.54,1.2)
# Compact, explicitly wired LDO macro used for all three rails.
def ldo(ref,ci,co,x,y):
 place(ref,x,y);a=P(ref,1);en=P(ref,3);out=P(ref,5)
 lx=snap(x-25.4);rx=snap(x+26.67);top=snap(y-5.08)
 path(a,(lx,top),(lx,snap(y)))
 if parts[ref]['pins']['3']==parts[ref]['pins']['1']:
  path(en,(lx,en[1]));junction((lx,en[1]))
 else:port(ref,3,7.62)
 bypass(ci,lx,y+8.89,parts[ref]['pins']['1'],upper=top);power(parts[ref]['pins']['1'],lx,top)
 path(out,(rx,top));bypass(co,rx,y+8.89,parts[ref]['pins']['5'],upper=top);power(parts[ref]['pins']['5'],rx,top)
 port(ref,2,2.54);port(ref,4)
ldo('U12','C65','C66',558.8,46.99)
place('U14',699.77,60.96)
# Raw input reservoir and parallel IN pins.
bypass('C69',641.35,58.42,'USB_VBUS',upper=44.45)
path(P('U14',3),(666.75,53.34),(666.75,44.45),(641.35,44.45));path(P('U14',4),(666.75,58.42),(666.75,53.34));junction((666.75,53.34));power('USB_VBUS',641.35,44.45)
port('U14',2,20.32)
place('R169',657.86,107.95,270);path(P('R169',1),(657.86,68.58),P('U14',2));junction((657.86,68.58));power('GND',*P('R169',2))
place('C68',673.1,102.87,270);path(P('U14',1),(692.15,87.63),(673.1,87.63),P('C68',1));label('USB_DVDT',673.1,87.63);power('GND',*P('C68',2))
place('R170',737.87,102.87,270);path(P('U14',7),(709.93,87.63),(737.87,87.63),P('R170',1));label('USB_ILIM',715.01,87.63);power('GND',*P('R170',2));bus('U14',['8','9'],81.28,'GND')
path(P('U14',5),(746.76,53.34));power('VIN_5V',746.76,53.34)
place('R176',787.4,100.33);path((737.87,87.63),(760.73,87.63),(760.73,100.33),P('R176',1));junction((737.87,87.63))
bypass('C78',805.18,121.92,'ESP_GPIO3',upper=100.33);path(P('R176',2),(805.18,100.33));label('ESP_GPIO3',805.18,100.33)
# One real power indicator, wired as LED plus its own resistor.
place('R3',774.7,58.42,270);place('D1',774.7,83.82,270)
path(P('R3',1),(774.7,45.72));power('VIN_5V',774.7,45.72)
path(P('R3',2),P('D1',2));label(parts['R3']['pins']['2'],774.7,71.12);power('GND',*P('D1',1))
note('ESP_GPIO4 enables loads; 820R sets ~2.48 A. ADC: 0.226 V/A nominal, switched loads only.',486.41,140.97,1.1)
note('Module and logic boot from raw 5 V. GPIO7/8 read PD status over I2C; firmware budgets current before enabling loads.',486.41,146.05,1.1)
# ---- GNSS receiver and active-antenna bias ------------------------------------
box('GNSS / PPS reference and active antenna bias',12.7,156.21,236.22,118.11)
place('U6',139.7,218.44)
bus('U6',['6','7','8'],179.07,'+3V3_GPS');bus('U6',['1','10','12'],254,'GND')
for ref,x in [('C8',100.33),('C9',115.57)]:
 bypass(ref,x,190.5,'+3V3_GPS',upper=179.07);path((x,179.07),(132.08,179.07))
port('U6',2,10.16);port('U6',3,10.16);port('U6',5,10.16)
# One visible PPS tree: two upward, independently damped timing destinations,
# and the indicator resistor/LED directly below the common node.
path(P('U6',4),(30.48,218.44));label('GPS_PPS',91.44,218.44)
for ref,x,title in [('R6',30.48,'FPGA PPS / G0'),('R7',73.66,'ESP32 PPS / GPIO38')]:
 place(ref,x,195.58,90);path(P(ref,1),(x,218.44))
 path(P(ref,2),(x,187.96));label(parts[ref]['pins']['2'],x,187.96)
 note(title,x,176.53,1.1)
place('R179',30.48,233.68,270);place('D74',30.48,254,270)
path((30.48,218.44),P('R179',1));path(P('R179',2),P('D74',2));label('PPS_LED_A',30.48,245.11)
power('GND',*P('D74',1))
note('PPS indicator',43.18,254,1.1)
# Compact VCC_RF-powered bias tee adjacent to RF_IN.
place('R5',194.31,198.12);path(P('U6',14),P('R5',1));label('ANT_PWR',166.37,198.12)
place('L1',222.25,205.74,90);path(P('R5',2),(222.25,198.12),P('L1',2));label('ANT_BIAS',209.55,198.12)
bypass('C10',207.01,204.47,'ANT_BIAS',upper=198.12)
place('J5',238.76,218.44);path(P('U6',11),P('J5',1));label('GNSS_RF',170.18,218.44)
path(P('L1',1),(222.25,218.44));port('J5',2)
# Reset input stays below the UART/trigger labels, clear of the PPS tree.
place('R180',93.98,238.76);path(P('U6',9),P('R180',2));label('GPS_RESET_N',104.14,238.76)
port('R180',1,3.81)
def translate_section(first, previous_refs, dx, dy):
 # Move a presentation block, including its fields, power symbols and unused-pin stubs.
 for i in range(first,len(items)):
  items[i]=re.sub(r'\((at|xy|start|end) (-?[0-9.]+) (-?[0-9.]+)',lambda m:f'({m[1]} {snap(float(m[2])+dx)} {snap(float(m[3])+dy)}',items[i])
 for ref in placed-previous_refs:
  pins[ref]={n:(snap(x+dx),snap(y+dy)) for n,(x,y) in pins[ref].items()}
# ---- External trigger input ---------------------------------------------------
section_start=len(items);section_refs=set(placed)
box('Trigger input / 5 V TTL / threshold ~2.5 V',322.58,156.21,236.22,118.11)
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
bypass('C11',501.65,175.26,'+3V3_GPS',upper=170.18);path(P('U7',5),(480.06,170.18),(501.65,170.18));power('+3V3_GPS',480.06,170.18);port('U7',3)
for ref,y in [('R80',193.04),('R81',208.28)]:
 place(ref,530.86,y);path(P('U7',4),(515.62,193.04),(515.62,snap(y)),P(ref,1));port(ref,2,3.81)
label('TRIGGER_3V3',500.38,193.04)
translate_section(section_start,section_refs,-66.04,0)
# ---- External trigger output --------------------------------------------------
box('Trigger output / 5 V TTL',500.38,156.21,139.7,118.11)
section_start=len(items);section_refs=set(placed)
# Grounded enable, input pulldown and series output damping.
place('U10',474.98,248.92);place('R162',509.27,248.92);place('J7',547.37,248.92)
path(P('U10',4),P('R162',1));label('TRIGGER_DRV',490.22,248.92);path(P('R162',2),P('J7',1));label('TRIGGER_OUT',519.43,248.92);port('J7',2)
place('R163',444.5,256.54,270);path(P('U10',2),(444.5,248.92),P('R163',1));label('FPGA_IOT_51A',429.26,248.92);path((429.26,248.92),(444.5,248.92));power('GND',*P('R163',2));bus('U10',['1','3'],267.97,'GND')
bypass('C15',501.65,231.14,'VIN_5V',upper=223.52);path(P('U10',5),(474.98,223.52),(492.76,223.52),(501.65,223.52));power('VIN_5V',492.76,223.52)
translate_section(section_start,section_refs,78.74,-40.64)
# ---- OCXO supply and clock ----------------------------------------------------
box('10 MHz OCXO / 3.3 V linear supply',647.7,156.21,177.8,118.11)
place('U15',684.53,196.85)
bypass('C70',654.05,194.31,'VIN_5V',upper=189.23);path(P('U15',2),(654.05,189.23));power('VIN_5V',654.05,189.23)
# Shared physical 3.3 V rail: regulator output/sense, three bypasses and OCXO VCC.
place('Y1',774.7,204.47)
path(P('U15',4),(740.41,189.23),(774.7,189.23),P('Y1',4));power('+3V3_OCXO',740.41,189.23)
for ref,x in [('C71',713.74),('C73',731.52),('C74',749.3)]:
 bypass(ref,x,203.2,'+3V3_OCXO',upper=189.23)
path(P('U15',5),(706.12,199.39),(706.12,189.23));bus('U15',['3','6'],227.33,'GND')
place('R178',665.48,219.71,270);path(P('R178',1),(665.48,199.39),P('U15',1));label('ESP_GPIO5',665.48,212.09,right=True);power('GND',*P('R178',2))
place('R173',805.18,222.25,270)
path(P('Y1',3),(805.18,204.47),P('R173',1));label('OCXO_CLK',800.1,204.47,right=True)
path(P('R173',2),(805.18,238.76));label(parts['R173']['pins']['2'],805.18,238.76,right=True,stub=False)
port('Y1',2)
note('SOT-223 heat spreader below OCXO; GPIO5 enables.',654.05,250.19,1.0)
note('2.1 W max warm-up; ~1.1 W LDO loss at 5 V; allow 3 min.',654.05,257.81,1.0)
note('Manual-fit AOC97FAJC-10.0000. Clock -> J2.32 / FPGA G6.',654.05,265.43,1.0)
# ---- Display buffers and local supply rails -----------------------------------
for bank,bx in [(0,12.7),(1,213.36)]:
 box(f'Display buffer / bits {15-bank*8}..{8-bank*8}',bx,281.94,193.04,97.79)
 ref='U'+str(3+bank);cx=snap(bx+116.84);cy=330.2;place(ref,cx,cy)
 for k in range(8):
  port(ref,str(k+2),20.32);port(ref,str(18-k),16.51)
 # One shared active-low blanking control; external pull-up keeps outputs off.
 port(ref,'1',20.32)
 a=P(ref,'19');path(a,(cx-25.4,a[1]),(cx-25.4,374.65),(cx,374.65),P(ref,10));power('GND',cx,374.65)
 if bank==0:
  place('R140',bx+35.56,351.79,270)
  power('+3V3_LOGIC',*P('R140',1))
  path(P('R140',2),(bx+35.56,P(ref,1)[1]),P(ref,1));junction((cx-40.64,P(ref,1)[1]))
 note('OE high: blank. Configure data before OE low.',bx+3.81,377.19,1.0)
 cc='C'+str(4+bank);bypass(cc,cx+34.29,298.45,'+3V3_LOGIC',upper=292.1)
 path(P(ref,20),(cx+34.29,292.1));power('+3V3_LOGIC',cx+34.29,292.1)
box('Logic / GNSS rails and RUN default',414.02,281.94,190.5,97.79)
ldo('U2','C2','C3',457.2,308.61);ldo('U5','C6','C7',457.2,355.6)
place('R177',441.96,369.57,270);path(P('R177',1),(441.96,355.6),P('U5',3));junction((441.96,355.6));power('GND',*P('R177',2))
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
place('J8',777.24,337.82)
for ref,x,pin,net in [('R174',737.87,3,'ESP_GPIO2'),('R175',753.11,4,'ESP_GPIO1')]:
 place(ref,x,309.88,270);path(P(ref,1),(x,297.18));path(P(ref,2),(x,P('J8',pin)[1]),P('J8',pin));label(net,x-20.32,P('J8',pin)[1]);path((x-20.32,P('J8',pin)[1]),(x,P('J8',pin)[1]))
path((737.87,297.18),(753.11,297.18),(777.24,297.18));path((777.24,297.18),P('J8',2));power('+3V3_LOGIC',777.24,297.18)
for ref,x in [('C76',802.64),('C77',817.88)]:
 bypass(ref,x,326.39,'+3V3_LOGIC',upper=307.34);path((x,307.34),(777.24,307.34));junction((777.24,307.34))
port('J8',1,2.54)
place('DS1',727.71,355.6)
note('OLED',723.9,355.6,1.27)
note('HS96L03W2C03',715.01,363.22,1.0)
note('DS1 solders onto J8; GND / VCC / SCL / SDA.',711.2,367.03,1.0)
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
# Dedicated compact probe index; same named nets as the functional blocks.
probe_refs=sorted((r for r in parts if parts[r]['kind']=='testpoint'),key=lambda r:int(r[2:]))
if probe_refs:
 box('Diagnostic probe pads / functional names on PCB / bare copper, no assembly parts',12.7,546.1,640.08,35.56)
 for i,ref in enumerate(probe_refs):
  c=parts[ref];x=snap(17.78+(i%14)*45.72);y=snap(556.26+(i//14)*8.89)
  symbols[ref]=f'(symbol "{ref}" (pin_names hide) (pin_numbers hide) (in_bom no) (on_board yes) {prop("Reference",ref,3.81,2.54)} {prop("Value",c["value"],0,0,True)} (symbol "{ref}_0_1" (circle (center 0 1.27) (radius .635) (stroke (width .254) (type default)) (fill (type none)))) (symbol "{ref}_1_1" (pin passive line (at 0 0 90) (length .635) (name "~" {E()}) (number "1" {E()}))))'
  placed.add(ref);covered.add((ref,'1'));pins[ref]={'1':(x,y)}
  meta=prop('Reference',ref,x,y,True)+prop('Value',c['value'],x,y,True)+prop('Footprint',c['footprint'],x,y,True)
  items.append(f'(symbol (lib_id "Calibrator:{ref}") (at {x} {y} 0) (unit 1) (in_bom no) (on_board yes) (uuid "{uid(ref)}") '+meta+f'(instances (project "calibrator" (path "/{uid("root")}" (reference "{ref}") (unit 1)))))')
  note(ref+' / '+c['value'],x+2.54,y-2.54,.85)
  path((x,y),(x+2.54,y));label(c['pins']['1'],x+2.54,y,stub=False)
  items[-1]=items[-1].replace('(size 1.27 1.27)','(size .85 .85)')
else:
 note('4 x 16 green LEDs / individual 470R 1% resistors / all four rows show the same bit / 1 LSB = 1/65536 s = 15.258789 us',15.24,570.23,1.5)
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
