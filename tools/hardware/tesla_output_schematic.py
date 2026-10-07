"""Readable GDT bridges with direct FPGA commands and passive default-off bias."""
from tesla_reservoirs import BANKS
def draw_output(g):
 globals().update(g)
 def connect(n,*points):
  if n!='GND':
   route(n,*points)
  else:
   for a,b in zip(points,points[1:]):
    if a!=b:wire(a,b)
   for r,pp in placed.items():
    for pin,xy in pp.items():
     if xy in points and net(r,pin)==n:used.add((r,pin))
 for ch,x in enumerate([383.54,1041.4]):
  box(f'GDT {ch+1} direct FPGA commands / bias and damping',x,1026.16,508,99.06)
  for i in range(4):
   # One column per bridge leg, high/low commands in matching rows.
   xx=x+(i//2)*241.3;yy=1051.56+(i%2)*30.48
   r='R'+str((505 if ch==0 else 513)+i);rp='R'+str((500 if ch==0 else 509)+i)
   put(r,xx+172.72,yy);put(rp,xx+111.76,yy+10.16,True)
   route(net(r,1),(xx+20.32,yy),(xx+111.76,yy),pt(r,1))
   route(net(rp,1),(xx+111.76,yy),pt(rp,1));junction((xx+111.76,yy));route('GND',pt(rp,2))
   route(net(r,2),pt(r,2),(xx+213.36,yy))
  note('FPGA owns enable, zero-current shutdown, deadtime and flux balance.',x+10.16,1111.25,1.1)
 for ch,x in enumerate([15.24,599.44]):
  y=1384.3;base=520+ch*40;pre=f'GDT{ch+1}_';cr=lambda n:'C'+str(base+n);rr=lambda n:'R'+str(base+n)
  box(f'GDT {ch+1} / battery-fed full bridge / 12 V MOSFET gate bias',x,y,568.96,370.84)
  for leg,dx in enumerate([0,274.32]):
   u='U'+str(51+ch*2+leg);qh='Q'+str(50+ch*4+leg*2);ql='Q'+str(51+ch*4+leg*2);stem=pre+('L_' if leg==0 else 'R_');sw=stem+'SW'
   put(u,x+55.88+dx,y+93.98);up=placed[u]
   put(qh,x+203.2+dx,up['3'][1]);put(ql,x+203.2+dx,up['8'][1])
   for hilo,q,pin in [(0,qh,3),(1,ql,8)]:
    gy=pt(q,1)[1];r=rr(leg*4+hilo*2)
    put(r,x+139.7+dx,gy)
    connect(net(r,1),up[str(pin)],pt(r,1));connect(net(r,2),pt(r,2),pt(q,1))
    # Gate-source pull-down physically spans the gate and source rails.
    rp=rr(leg*4+hilo*2+1);rx=x+167.64+dx
    put(rp,rx,gy+7.62,True)
    connect(net(rp,1),(rx,gy),pt(rp,1));junction((rx,gy))
    sy=up['4'][1] if hilo==0 else gy+17.78
    if hilo==0:
     connect(net(rp,2),pt(rp,2),(rx,sy));junction((rx,sy))
    else:
     connect('GND',pt(rp,2),(rx,sy),(pt(q,3)[0],sy),pt(q,3))
     power('GND',pt(q,3)[0],sy)
   power('VBAT_24V',*pt(qh,2));used.add((qh,'2'))
   connect(sw,pt(qh,3),pt(ql,2));junction((pt(qh,3)[0],up['4'][1]));route(sw,up['4'],(pt(qh,3)[0],up['4'][1]))
   # Capacitor above HO: the HO crossing is on its lower wire, clear of the symbol.
   cb=cr(leg*3);put(cb,x+101.6+dx,up['2'][1]+5.08,True)
   connect(stem+'HB',up['2'],pt(cb,1))
   connect(sw,pt(cb,2),(x+101.6+dx,up['4'][1]));junction((x+101.6+dx,up['4'][1]))
   # Decoupling pair grouped beneath each driver, connected to its bias net.
   for k,xx in [(1,x+38.1+dx),(2,x+78.74+dx)]:put(cr(leg*3+k),xx,y+157.48,True)
   rail([cr(leg*3+1),cr(leg*3+2)],'+12V_BIAS',y+147.32)
   rail([cr(leg*3+1),cr(leg*3+2)],'GND',y+167.64,'2')
  # UD2.7 DC block with a series RC damping branch across the capacitor.
  left=x+139.7;right=x+330.2
  put(cr(9),x+234.95,y+193.04)
  route(pre+'L_SW',(left,y+193.04),pt(cr(9),1))
  route(pre+'OUT_P',pt(cr(9),2),(right,y+193.04))
  put(rr(9),x+195.58,y+223.52);put(cr(10),x+274.32,y+223.52)
  route(pre+'L_SW',(left,y+193.04),(left,y+223.52),pt(rr(9),1));junction((left,y+193.04))
  chain(pre+'SNUB',(rr(9),2),(cr(10),1))
  route(pre+'OUT_P',pt(cr(10),2),(right,y+223.52),(right,y+193.04));junction((right,y+193.04))
  put('J'+str(50+ch),x+426.72,y+198.12)
  route(pre+'OUT_P',(right,y+193.04),pt('J'+str(50+ch),1))
  bank=BANKS[f'gdt{ch+1}']
  capbank(bank[:4],x+45.72,y+269.24,'8 x 22uF / 50V X7R / 2220 reservoir')
  capbank(bank[4:],x+45.72,y+304.8)
  put('D'+str(50+ch),x+350.52,y+292.1,True);route('VBAT_24V',pt('D'+str(50+ch),1));route('GND',pt('D'+str(50+ch),2))
  note('Precharge: both lows ON, both highs OFF. Insert deadtime before each leg commutation.',x+12.7,y+325.12,1.1)
  note('UD2.7: 2.2uF / 50V X7R DC block, with parallel 15R + 1uF / 50V X7R damping branch.',x+12.7,y+335.28,1.1)
