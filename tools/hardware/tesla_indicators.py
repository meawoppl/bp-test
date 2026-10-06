"""Local rail and bridge-leg indicators. No buffer or FPGA status outputs."""
CONTACTS={}
ROWS={
 0:('BAT','POWER','GREEN','VBAT_24V','12k'),
 1:('12V','POWER','GREEN','+12V_BIAS','5.1k'),
 2:('5V','POWER','GREEN','VIN_5V','1.5k'),
 3:('3V3','POWER','GREEN','+3V3','680R'),
 4:('GDT1 L','LEG','GREEN','GDT1_L_SW','12k'),
 6:('GDT1 R','LEG','GREEN','GDT1_R_SW','12k'),
 7:('GDT2 L','LEG','GREEN','GDT2_L_SW','12k'),
 8:('GDT2 R','LEG','GREEN','GDT2_R_SW','12k'),
}
PROTECT={4:'D90',6:'D91',7:'D92',8:'D93'}
# Resistor, LED, reverse-protection diode: x/y in mm, rotation in degrees.
PLACEMENTS={0: [[35, 37.3, 90], [35, 33.5, 270]], 1: [[54.5, 66.2, 270], [54.5, 70, 90]], 2: [[86, 66.2, 270], [86, 70, 90]], 3: [[106.6, 107.8, 180], [103, 107.8, 0]], 4: [[136, 64, 90], [136, 60, 270], [139, 62, 90]], 6: [[154, 64, 90], [154, 60, 270], [157, 62, 90]], 7: [[136, 119, 90], [136, 115, 270], [139, 117, 90]], 8: [[154, 119, 90], [154, 115, 270], [157, 117, 90]]}
LABELS={0: [35, 30.6], 1: [54.5, 73], 2: [86, 73], 3: [103, 110.05], 4: [136, 57.5], 6: [154, 57.5], 7: [136, 112.5], 8: [154, 112.5]}
def populate(add):
 for i,(label,meaning,color,signal,rv) in ROWS.items():
  an=f'LED_{80+i}_A';rpos,dpos,*dp=PLACEMENTS[i]
  add(f'R{800+i}',rv,'Resistor_SMD','R_0805_2012Metric',{'1':signal,'2':an},*rpos,kind='r')
  add(f'D{80+i}','GREEN','LED_SMD','LED_0805_2012Metric',{'1':'GND','2':an},*dpos,kind='led',mpn='KT-0805G',lcsc='C2297',names={'1':'K','2':'A'})
  if i in PROTECT:
   add(PROTECT[i],'1N4148W,115','Diode_SMD','D_SOD-123',{'1':an,'2':'GND'},*dp[0],kind='diode',mpn='1N4148W,115',names={'1':'K','2':'A'})
def draw_indicators(g):
 globals().update(g)
 box('LOCAL POWER + BRIDGE LEG INDICATORS',15.24,2410,406.4,275)
 for j,(i,(name,meaning,color,signal,rv)) in enumerate(ROWS.items()):
  x=40.64+(j%2)*182.88;y=[2458.26,2493.82,2544.62,2600.50][j//2]
  note(name+' / GREEN',x,y-15.24,1.27)
  r=f'R{800+i}';d=f'D{80+i}';put(r,x+30.48,y);put(d,x+76.20,y)
  if i<4:
   wire((x,y),pt(r,1));power(signal,x,y);used.add((r,'1'))
  else:route(signal,(x,y),pt(r,1))
  left=(x+53.34,y);right=(x+96.52,y)
  wire(pt(r,2),left);wire(left,pt(d,2));label(net(r,2),*left)
  used.update([(r,'2'),(d,'2'),(d,'1')])
  wire(pt(d,1),right)
  if i in PROTECT:
   dd=PROTECT[i];put(dd,x+76.20,y+20.32)
   wire(left,(left[0],pt(dd,1)[1]));wire((left[0],pt(dd,1)[1]),pt(dd,1));junction(left)
   wire(right,(right[0],pt(dd,2)[1]));wire((right[0],pt(dd,2)[1]),pt(dd,2))
   power('GND',right[0],pt(dd,2)[1]);used.update([(dd,'1'),(dd,'2')])
  else:power('GND',*right)
 note('Each bridge lamp senses its switching node through 12k; no FPGA status pins.',30.48,2650,1.27)
 note('1N4148W protects each LED from negative switching-node excursions.',30.48,2660,1.27)
 note('Brightness follows positive duty cycle; not a fault, enable or current monitor.',30.48,2670,1.27)
