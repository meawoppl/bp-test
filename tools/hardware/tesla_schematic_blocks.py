"""Readable, wired functional blocks for the Tesla acquisition/power draft."""
def draw(g):
 globals().update({k:g[k] for k in ['parts','place','wire','label','power','note','box','items','uid','E']})
 # Compress whitespace, retaining symbol sizes and grid-aligned electrical endpoints.
 tx=lambda x:round(15.24+(x-15.24)*0.75,4)
 original={k:g[k] for k in ['place','wire','label','power','note','box']}
 def place(r,x,y,**kw):
  pp=original['place'](r,tx(x),y,**kw)
  return {n:(15.24+(a-15.24)/0.75,b) for n,(a,b) in pp.items()}
 def wire(a,b):original['wire']((tx(a[0]),a[1]),(tx(b[0]),b[1]))
 def label(n,x,y,*a):original['label'](n,tx(x),y,*a)
 def power(n,x,y):original['power'](n,tx(x),y)
 def note(n,x,y,*a):original['note'](n,tx(x),y,*a)
 def box(n,x,y,w,h):original['box'](n,tx(x),y,tx(x+w)-tx(x),h)
 placed={};used=set();seq=[0];branches=[]
 def put(r,x,y,vertical=False):
  p=place(r,x,y,rotate=vertical,ports=False);placed[r]=p;return p
 def pt(r,n):return placed[r][str(n)]
 def net(r,n):return parts[r]['pins'][str(n)]
 def junction(p,key=None):
  if key is None:seq[0]+=1;key=str(seq[0])
  items.append(f'(junction (at {tx(p[0])} {p[1]}) (diameter 0.8) (color 0 0 0 0) (uuid "{uid("block-j"+key)}"))')
 def route(n,*points):
  for a,b in zip(points,points[1:]):
   if a!=b:wire(a,b)
  # A local net name on each connected branch identifies functional nodes without boxes.
  seq[0]+=1;x,y=points[0]
  if n=='GND':power(n,x,y)
  else:branches.append((n,points))
  for p in points:
   for r,pp in placed.items():
    for pin,xy in pp.items():
     if abs(xy[0]-p[0])+abs(xy[1]-p[1])<1e-5 and net(r,pin)==n:used.add((r,pin))
 def chain(n,*pins):route(n,*(pt(r,p) for r,p in pins))
 def rail(refs,n,y,pins='1'):
  pp=[pt(r,pins) for r in refs];pp.sort()
  for r,p in zip(sorted(refs,key=lambda r:pt(r,pins)),pp):
   wire(p,(p[0],y));used.add((r,pins));junction((p[0],y))
  if pp[0][0]!=pp[-1][0]:wire((pp[0][0],y),(pp[-1][0],y))
  power(n,pp[-1][0],y)
 def capbank(refs,x,y,title=None):
  if title:note(title,x,y-25.4,1.3)
  for i,r in enumerate(refs):put(r,x+i*30.48,y,True)
  rail(refs,net(refs[0],1),y-10.16);rail(refs,'GND',y+10.16,'2')
 # Acquisition / control occupies the left half.
 box('Daughterboard v1 / control and acquisition interface',15.24,15.24,548.64,142.24)
 place('J1',110,88);place('J2',355,88)
 box('AD7606C-16 / simultaneous sampling / four serial lanes',15.24,165.1,215.9,226.06)
 u=place('U1',114.3,276.86,skip_ports=('15',))
 # FRSTDATA is a local probe point, not a long service-header signal.
 a=u['15'];t=put('TP1',a[0]-40.64,a[1])['1']
 wire(t,a)
 junction(t,'-TP1')
 used.add(('TP1','1'))
 # Keep the global net name identical to the board's existing FRSTDATA net.
 label('ADC_FIRST',t[0],t[1],180)
 # The net label supplies the value beside the wire; retain only TP1 above its circle.
 for i,s in enumerate(items):
  if s.startswith('(symbol (lib_id "Tesla:TP1")'):
   import re
   items[i]=re.sub(r'(\(property "Value" "ADC_FIRST".*?\(effects \(font \(size 1.27 1.27\)\)\))',r'\1 (hide yes)',s)
 note('OS[2:0]=111: software mode',25.4,374.65)
 note('Configure ranges and high bandwidth before capture.',25.4,382.27,1.15)
 box('Analog inputs / EMI filters',236.22,165.1,327.66,226.06)
 for r,x in [('J3',275),('J8',355),('J9',435),('J10',515)]:
  pp=put(r,x,198)
  route(net(r,1),(pp['1'][0]-10.16,pp['1'][1]),pp['1'])
  # Ground below the connector avoids colliding with the next AUX label.
  wire(pp['2'],(pp['2'][0],pp['2'][1]+7.62))
  route('GND',(pp['2'][0],pp['2'][1]+7.62));used.add((r,'2'))
 for ch in range(1,9):
  y=246.38+(ch-1)*17.78;r='R'+str(ch);c='C'+str(ch+10)
  put(r,302.26,y);put(c,347.98,y+5.08,True)
  route(net(r,1),(271.78,y),pt(r,1))
  route(net(r,2),pt(r,2),pt(c,1),(386.08,y));junction(pt(c,1));route('GND',pt(c,2))
 note('CH1-4: AUX1, AUX2, AUX3, AUX4 / 0-5 V; CH5/6 CST 1; CH7/8 CST 2',260,224,1.25)
 note('100R / 1nF: EMI filtering, not anti-alias filtering.',260,232,1.25)
 box('ADC supplies and reference / local bypass groups',15.24,401.32,548.64,116.84)
 capbank(['C1','C2','C3','C4','C10'],35.56,441.96,'AVCC / one local capacitor at each supply pin')
 capbank(['C5'],210.82,441.96,'VDRIVE')
 for r,x in [('C6',302.26),('C7',368.3),('C8',434.34),('C9',510.54)]:
  put(r,x,441.96,True);route(net(r,1),(x,426.72),pt(r,1));route('GND',pt(r,2))
 note('REGCAP_A and REGCAP_D are internal-regulator outputs: bypass only.',30.48,487.68,1.3)
 note('REFCAP pins 44/45 share C9; REF pin 42 uses C8.',30.48,497.84,1.3)
 box('5 V analog feed and 3.3 V logic supply',15.24,528.32,335.28,172.72)
 put('U2',165.1,582.93);put('C20',78.74,601.98,True);put('C21',251.46,601.98,True)
 u=placed['U2'];vy=u['1'][1]
 route('VIN_5V',pt('C20',1),(78.74,vy),u['1']);route('VIN_5V',u['3'],(124.46,u['3'][1]),(124.46,vy));junction((124.46,vy))
 route('+3V3',u['5'],(251.46,u['5'][1]),pt('C21',1));route('GND',u['2']);route('GND',pt('C20',2));route('GND',pt('C21',2))
 put('R20',81.28,629.92);route('VIN_5V',(50.8,629.92),pt('R20',1));route('+5V_ADC',pt('R20',2),(116.84,629.92));power('+5V_ADC',116.84,629.92)
 for i,r in enumerate(['R21','R22','R23']):
  x=165.1+i*60.96;put(r,x,655.32,True);route(net(r,1),(x,670.56 if r=='R21' else 640.08),pt(r,1));route(net(r,2),pt(r,2),(x,640.08 if r=='R21' else 670.56))
 usb_start=len(items);usb_branches=len(branches)
 box('USB-C / programming only',360.68,528.32,406.4,172.72)
 j=put('J5',414.02,591.82);u=put('U3',533.4,591.82)
 put('C22',596.9,561.34,True)
 put('R26',655.32,561.34);put('R27',693.42,591.82,True)
 route('USB_D-',j['A7'],(481.33,j['A7'][1]),(481.33,u['3'][1]),u['3'])
 route('USB_D+',j['A6'],(474.98,j['A6'][1]),(474.98,u['1'][1]),u['1'])
 route('USB_D-',u['4'],(622.3,u['4'][1]));route('USB_D+',u['6'],(622.3,u['6'][1]))
 # Shared VBUS protects the USB pins and feeds only the presence divider.
 route('USB_VBUS',j['A4'],(466.09,j['A4'][1]),(466.09,541.02),(533.4,541.02),u['5'])
 route('USB_VBUS',(533.4,541.02),(596.9,541.02),pt('C22',1));junction((533.4,541.02))
 route('USB_VBUS',(596.9,541.02),(632.46,541.02),(632.46,561.34),pt('R26',1));junction((596.9,541.02))
 route('USB_VBUS_PRESENT',pt('R26',2),(693.42,561.34),pt('R27',1))
 route('GND',pt('C22',2));route('GND',pt('R27',2));route('GND',u['2'])
 route('GND',j['A1']);route('GND',j['S1'])
 for r,p,x,y in [('R24','A5',480.06,632.46),('R25','B5',538.48,657.86)]:
  put(r,x,y);a=pt(r,1);route(net(r,1),j[p],(a[0]-5.08,j[p][1]),(a[0]-5.08,y),a)
  z=(pt(r,2)[0]+10.16,y);wire(pt(r,2),z);used.add((r,'2'));route('GND',z)
 note('PROGRAMMING ONLY - power the controller from its normal supply.',369,675.64,1.27)
 note('USB VBUS is isolated from VIN_5V. No USB-PD or USB-UART bridge.',369,683.26,1.15)
 note('VBUS presence: J1.20 / ESP GPIO8; firmware must monitor this input.',369,690.88,1.15)
 note('A6/B6 = D+; A7/B7 = D-. Each CC pin has its own 5.1k pulldown.',369,698.5,1.15)
 # Place this enlarged source block in unused drafting space before packing;
 # the AUX block occupies the former block's right-hand extension.
 import re
 for i in range(usb_start,len(items)):
  items[i]=re.sub(r'\((at|xy|start|end) (-?[\d.]+) (-?[\d.]+)',lambda m:f'({m[1]} {float(m[2])+750:g} {m[3]}',items[i])
 for r in ['J5','U3','C22','R24','R25','R26','R27']:
  placed[r]={n:(x+1000,y) for n,(x,y) in placed[r].items()}
 for i in range(usb_branches,len(branches)):
  n,points=branches[i];branches[i]=(n,tuple((x+1000,y) for x,y in points))
 box('Main input / mechanical and design notes',15.24,713.74,548.64,71.12)
 note('Input wiring: see BATTERY INPUTS / SERIES LINK + RESERVOIR.',45.72,744.22,1.3)
 note('Values and power-stage thermal performance require validation.',45.72,756.92,1.3)
 # Integrated-inductor modules: compact connected reference circuits.
 for idx,x in [(30,584.2),(31,881.38)]:
  y=15.24;pref=f'P{idx}_';base=idx*10;U=f'U{idx}'
  R=lambda k:f'R{base+k}';C=lambda k:f'C{base+k}'
  vout=net(U,7)
  box(('Battery to 12 V driver bias' if idx==30 else 'Battery to 5 V logic'),x,y,287.02,314.96)
  put(U,x+124.46,y+86.36);u=placed[U]
  # VIN bank and on-time resistor feed the adjacent module pins.
  put(C(2),x+25.4,y+55.88,True);put(C(3),x+60.96,y+55.88,True)
  rail([C(2),C(3)],'VBAT_24V',y+38.1);rail([C(2),C(3)],'GND',y+68.58,'2')
  route('VBAT_24V',u['1'],(x+76.2,u['1'][1]),(x+76.2,y+38.1),(x+60.96,y+38.1));junction((x+60.96,y+38.1))
  put(R(2),x+50.8,u['2'][1]);route('VBAT_24V',pt(R(2),1),(x+25.4,u['2'][1]));power('VBAT_24V',x+25.4,u['2'][1]);route(pref+'RON',pt(R(2),2),u['2'])
  # Programmable battery UVLO and soft start, wired directly to their pins.
  put(R(4),x+50.8,y+114.3,True);put(R(5),x+50.8,y+142.24,True)
  route('VBAT_24V',pt(R(4),1));power('VBAT_24V',*pt(R(4),1))
  chain(pref+'UVLO',(R(4),2),(R(5),1));route('GND',pt(R(5),2))
  route(pref+'UVLO',u['3'],(x+78.74,u['3'][1]),(x+78.74,y+127),(x+50.8,y+127));junction((x+50.8,y+127))
  put(C(0),x+99.06,y+157.48,True);route(pref+'SS',u['5'],(x+99.06,u['5'][1]),pt(C(0),1));route('GND',pt(C(0),2))
  # Output bank with feedback divider and feed-forward capacitor alongside it.
  oy=u['7'][1]
  for i,k in enumerate([4,5,6]):put(C(k),x+185.42+i*38.1,y+88.9,True)
  rail([C(4),C(5),C(6)],vout,oy);rail([C(4),C(5),C(6)],'GND',y+104.14,'2')
  route(vout,u['7'],(x+185.42,oy));junction((x+185.42,oy))
  put(R(0),x+205.74,y+144.78,True);put(R(1),x+205.74,y+177.8,True);put(C(1),x+259.08,y+144.78,True)
  route(vout,pt(R(0),1),(x+205.74,y+127),(x+259.08,y+127),pt(C(1),1));power(vout,x+205.74,y+127)
  chain(pref+'FB',(R(0),2),(R(1),1));route(pref+'FB',pt(C(1),2),(x+259.08,y+160.02),(x+205.74,y+160.02));junction((x+205.74,y+160.02))
  route(pref+'FB',u['6'],(x+165.1,u['6'][1]),(x+165.1,y+160.02),(x+205.74,y+160.02));route('GND',pt(R(1),2))
  note('LMZ14202H: shielded inductor inside the module.',x+15.24,y+226.06,1.3)
  note('UVLO: approx. 21.0 V on / 19.4 V off; soft start 0.47 ms.',x+15.24,y+241.3,1.15)
  note('Output bank: verify DC-biased capacitance before release.',x+15.24,y+256.54,1.2)
  note('2 A device rating; thermal / load qualification pending.',x+15.24,y+271.78,1.2)
 # Direct battery bus replaces the synchronous 24 V converter.
 x=584.2;y=340.36
 box('Direct battery distribution / no 24 V converter',x,y,584.2,149.86)
 from tesla_reservoirs import BANKS
 put('J4',x+40.64,y+50.8);put('J30',x+40.64,y+99.06)
 route('VBAT_24V',pt('J4',1),(x+111.76,pt('J4',1)[1]))
 route('BAT_MID_12V',pt('J4',2),(x+101.6,pt('J4',2)[1]),
       (x+101.6,pt('J30',1)[1]),pt('J30',1))
 route('GND',pt('J30',2))
 capbank(BANKS['battery'][:4],x+172.72,y+55.88,'8 x 22uF / 50V / 2220 reservoir')
 capbank(BANKS['battery'][4:],x+172.72,y+99.06)
 capbank(['C333'],x+340.36,y+71.12,'Local rail bypass')
 note('Series: J4 upper battery, J30 lower battery; pin 1 +, pin 2 -.',x+25.4,y+129.54,1.3)
 note('Single 24 V PSU: + to J4.1, - to J30.2; leave J4.2 / J30.1 unused.',x+25.4,y+137.16,1.3)
 note('BAT_MID_12V joins J4.2 to J30.1 only; it is not board ground.',x+25.4,y+144.78,1.3)
 from tesla_cst_schematic import draw_cst
 draw_cst(dict(globals(),**locals()))
 from tesla_output_schematic import draw_output
 draw_output(dict(globals(),**locals()))
 from tesla_aux_schematic import draw_aux
 draw_aux(dict(globals(),**locals()))
 from tesla_indicators import draw_indicators
 if 'D80' in parts:draw_indicators(dict(globals(),**locals()))
 # Every still-unwired port gets a short tail. Connected support circuits carry the shared net names.
 for r,pp in placed.items():
  for n,p in pp.items():
   if (r,n) in used:continue
   nn=net(r,n)
   if nn is None:
    items.append(f'(no_connect (at {tx(p[0])} {p[1]}) (uuid "{uid(r+n+"nc")}"))');continue
   if nn=='GND':power('GND',*p);continue
   # IC ports are on left/right edges; tails point away from body.
   left=r in ['J50','J51'] or p[0]<sum(v[0] for v in pp.values())/len(pp)
   z=(p[0]+(-10.16 if left else 10.16),p[1]);wire(p,z);label(nn,*z,180 if left else 0)

 # Label connected branches once, at an uncrowded endpoint rather than at every pin.
 from collections import defaultdict
 groups=defaultdict(list)
 for n,pts in branches:groups[n].append(pts)
 for n,paths in groups.items():
  islands=[]
  def touches(a,b):
   for p in a:
    for c,d in zip(b,b[1:]):
     if abs((p[0]-c[0])*(d[1]-c[1])-(p[1]-c[1])*(d[0]-c[0]))<1e-5 and min(c[0],d[0])-1e-5<=p[0]<=max(c[0],d[0])+1e-5 and min(c[1],d[1])-1e-5<=p[1]<=max(c[1],d[1])+1e-5:return True
   return bool(set(a)&set(b))
  for path in paths:
   hits=[i for i,group in enumerate(islands) if any(touches(path,p) or touches(p,path) for p in group)]
   merged=[path]
   for i in reversed(hits):merged+=islands.pop(i)
   islands.append(merged)
  pins=[p for pp in placed.values() for p in pp.values()]
  for group in islands:
   ends=set(p for path in group for p in [path[0],path[-1]])
   mids={((a[0]+b[0])/2,(a[1]+b[1])/2) for path in group for a,b in zip(path,path[1:]) if (a[0]==b[0] or a[1]==b[1]) and abs(a[0]-b[0])+abs(a[1]-b[1])>15.24}
   p=max(ends|mids,key=lambda p:min((p[0]-q[0])**2+(p[1]-q[1])**2 for q in pins))
   if n in ['CT1_RECT_DRIVE','CT2_RECT_DRIVE']:
    d1,d2=('D41','D42') if n=='CT1_RECT_DRIVE' else ('D61','D62')
    p=(placed[d1]['2'][0],(placed[d1]['2'][1]+placed[d2]['1'][1])/2)
   label(n,*p)
   # Terminate deliberate label tails; every otherwise open branch gets its net label.
   for e in ends:
    if e!=p and not any(abs(e[0]-q[0])+abs(e[1]-q[1])<1e-5 for q in pins) and sum(e in path for path in group)==1 and not any(touches([e], path) for path in group if e not in path):
     label(n,*e)
