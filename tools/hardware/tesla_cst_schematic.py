"""Wired CST functional blocks; no disconnected component inventory."""
def _draw_cst(g):
 globals().update(g)
 # Additional compaction of the continuous input/rectifier chain only.
 saved={k:globals()[k] for k in ['put','pt','route','junction','place','note','box']}
 sx=lambda x:15.24+(x-15.24)*0.70
 globals()['put']=lambda r,x,y,*a:saved['put'](r,sx(x),y,*a)
 globals()['pt']=lambda r,n:((saved['pt'](r,n)[0]-15.24)/0.70+15.24,saved['pt'](r,n)[1])
 globals()['route']=lambda n,*ps:saved['route'](n,*[(sx(x),y) for x,y in ps])
 globals()['junction']=lambda p:saved['junction']((sx(p[0]),p[1]))
 globals()['place']=lambda r,x,y,*a:saved['place'](r,sx(x),y,*a)
 globals()['note']=lambda t,x,y,*a:saved['note'](t,sx(x),y,*a)
 globals()['box']=lambda t,x,y,w,h:saved['box'](t,sx(x),y,w*0.70,h)
 box('CST cable filter / permanent burden / precision full-wave magnitude',15.24,825.5,1153.16,190.5)
 put('J40',48.26,894.08)
 put('L40',139.7,899.16)
 put('U40',350.52,894.08);put('U41',589.28,894.08)
 sy=pt('U40',4)[1]
 for r,x in [('R400',195.58),('R401',238.76),('D40',281.94)]:
  put(r,x,sy+20.32,True)
  route('CT1_RAW',pt(r,1),(x,sy));junction((x,sy))
 rail(['R400','R401','D40'],'GND',sy+38.1,'2')
 put('R402',302.26,sy)
 route('CT1_CABLE_P',pt('J40',1),(88.9,pt('J40',1)[1]),(88.9,pt('L40',1)[1]),pt('L40',1))
 route('CT1_CABLE_N',pt('J40',2),(78.74,pt('J40',2)[1]),(78.74,pt('L40',4)[1]),pt('L40',4))
 route('CT1_RAW',pt('L40',2),pt('R402',1))
 route('GND',pt('L40',3))
 for r,x in [('C427',60.96),('C428',139.7),('C429',218.44)]:
  put(r,x,947.42,True);route(net(r,1),pt(r,1));route('GND',pt(r,2))
 route('CT1_RECT_SUM',pt('R402',2),pt('U40',4))
 put('R403',363.22,850.9)
 route('CT1_RECT_SUM',pt('R403',1),(317.5,850.9),(317.5,sy));junction((317.5,sy))
 put('D41',391.16,873.76,True);put('D42',429.26,894.08)
 route('CT1_RECT_SUM',pt('D41',1),(317.5,pt('D41',1)[1]));junction((317.5,pt('D41',1)[1]))
 route('CT1_RECT_DRIVE',pt('U40',1),pt('D42',1));route('CT1_RECT_DRIVE',pt('D41',2),(391.16,894.08));junction((391.16,894.08))
 route('CT1_HALF',pt('R403',2),(464.82,850.9),(464.82,894.08),pt('D42',2))
 # Bring the summing stage next to the half-wave feedback loop.
 sy=pt('U41',4)[1];put('R404',505.46,sy)
 route('CT1_RAW',(467.36,sy),pt('R404',1));route('CT1_ABS_SUM',pt('R404',2),pt('U41',4))
 put('R405',505.46,927.1);put('R406',505.46,947.42)
 route('CT1_HALF',pt('D42',2),(464.82,894.08),(464.82,927.1),pt('R405',1))
 route('CT1_HALF',(464.82,927.1),(464.82,947.42),pt('R406',1));junction((464.82,927.1))
 route('CT1_ABS_SUM',pt('R405',2),(551.18,927.1),(551.18,sy));route('CT1_ABS_SUM',pt('R406',2),(551.18,947.42),(551.18,927.1));junction((551.18,sy));junction((551.18,927.1))
 put('R407',601.98,850.9)
 route('CT1_ABS_SUM',pt('R407',1),(551.18,850.9),(551.18,sy))
 route('CT1_ABS',pt('R407',2),(652.78,850.9),(652.78,894.08),pt('U41',1))
 put('R408',701.04,894.08);route('CT1_ABS',pt('U41',1),pt('R408',1));junction((652.78,894.08))
 put('C400',754.38,909.32,True)
 route('CT1_ENVELOPE',pt('R408',2),(754.38,894.08),(800.1,894.08));route('CT1_ENVELOPE',pt('C400',1),(754.38,894.08));junction((754.38,894.08));route('GND',pt('C400',2))
 # Probe points fit below the stages instead of extending the block to the right.
 for r,x in [('TP40',320.04),('TP41',414.02),('TP42',685.8),('TP43',779.78)]:place(r,x,947.42)
 note('10R burden: 2 x 20R / nominal +/-2 V. Choose CT ratio N = 5 x primary peak amperes.',30.48,970.28,1.3)
 note('Vhalf = -max(Vct,0); U41 sums -(Vct + 2 Vhalf) = |Vct|. 1k/10nF: 10 us smoothing, not peak hold.',30.48,982.98,1.3)
 note('Keep a secondary clamp at the CT itself if the cable can unplug. Overcurrent decisions are made by the FPGA from ADC samples.',30.48,995.68,1.3)
 globals().update(saved)
 box('Fast phase path / local 1.65 V reference / 3.3 V FPGA input',15.24,1026.16,355.6,154.94)
 put('U42',238.76,1069.34);yy=pt('U42',3)[1]
 put('C425',45.72,yy);put('R410',91.44,yy);route('CT1_RAW',(25.4,yy),pt('C425',1));chain('CT1_PHASE_AC',('C425',2),('R410',1))
 put('R411',127,1043.94,True);route('+3V3',pt('R411',1))
 route('CT1_PHASE',pt('R410',2),pt('U42',3));route('CT1_PHASE',pt('R411',2),(127,yy));junction((127,yy))
 put('C410',162.56,yy+15.24,True);route('CT1_PHASE',pt('C410',1),(162.56,yy));junction((162.56,yy));route('GND',pt('C410',2))
 if not g.get('second_channel'):
  # Mirror the lower bias resistor about CT1_PHASE, directly below R411.
  put('R422',127,2*yy-1043.94,True)
  route('CT1_PHASE',pt('R422',1),(127,yy));route('GND',pt('R422',2))
  put('D43',109.22,1112.52)
  power('+3V3',*pt('D43',2));used.add(('D43','2'))
  route('GND',pt('D43',1))
 else:
  put('R422',162.56,1112.52,True);route('CT1_PHASE',pt('R422',1));route('GND',pt('R422',2));put('D43',109.22,1112.52)
 put('R416',304.8,pt('U42',5)[1]);chain('CT1_ZERO_DRV',('U42',5),('R416',1));route('CT1_ZERO',pt('R416',2),(337.82,pt('R416',2)[1]))
 # Keep the quiet midpoint beside the comparator and wire it to IN-.
 # draw_cst's channel mapping applies this same circuit to U62 / CT2_MID.
 put('R414',238.76,1098.55,True);put('R415',238.76,1131.57,True)
 route('+3V3',pt('R414',1));chain('CT1_MID',('R414',2),('R415',1));route('GND',pt('R415',2))
 put('C412',299.72,1131.57,True)
 mid=(238.76,1115.06)
 route('CT1_MID',pt('C412',1),(299.72,mid[1]),mid)
 route('CT1_MID',mid,(187.96,mid[1]),(187.96,pt('U42',1)[1]),pt('U42',1))
 junction(mid);route('GND',pt('C412',2))
 note('Vphase = 1.65 V + Vct/2; compare with CT1_MID.',30.48,1150.62,1.3)
 note('22pF EMI filter; 6mV internal comparator hysteresis.',30.48,1158.24,1.3)
 note('Timing threshold + delay must be calibrated versus amplitude.',30.48,1170.94,1.15)
 note('Phase midpoint: 1.65 V. Wait >=100 ms after rails stabilize before arming.',30.48,1178.56,1.2)
 if not g.get('second_channel'):
  box('Rectifier negative supply / isolated from phase and OC paths',15.24,1193.8,355.6,175.26)
  put('U44',109.22,1257.3);yy=pt('U44',2)[1]
  put('C421',50.8,yy+15.24,True);route('+5V_ADC',pt('C421',1),(50.8,yy),pt('U44',2));route('GND',pt('C421',2))
  put('C420',175.26,1252.22,True);chain('CT1_FLY_P',('U44',5),('C420',1));chain('CT1_FLY_N',('U44',3),('C420',2))
  oy=pt('U44',1)[1]
  put('C422',165.1,oy+15.24,True);put('R421',208.28,oy);put('C423',251.46,oy+15.24,True)
  route('CT1_NEG_PUMP',pt('U44',1),pt('R421',1));route('CT1_NEG_PUMP',pt('C422',1),(165.1,oy));junction((165.1,oy));route('GND',pt('C422',2))
  route('-5V_CT',pt('R421',2),(251.46,oy));route('-5V_CT',(251.46,oy),pt('C423',1));junction((251.46,oy));route('GND',pt('C423',2))
  # The -5 V power flag is drawn at this endpoint by tesla_schematic.py.
  # Connect it to the filtered rail rather than leaving a separate labeled island.
  wire((251.46,oy),(278.13,oy))
  note('250 kHz charge pump; 10R/10uF ripple filter.',50.8,1333.5,1.3)
  note('Negative rail feeds both rectifiers and the AUX buffers.',50.8,1346.2,1.3)
 box('Local supply bypass / place at each IC supply pin',777.24,1193.8,391.16,175.26)
 capbank(['C401','C403'],810.26,1252.22,'U40/U41 positive supply')
 # Negative-rail capacitors use net labels to avoid an upward positive-supply arrow.
 for r,x in [('C402',922.02),('C404',975.36)]:
  put(r,x,1252.22,True);route('-5V_CT',pt(r,1));route('GND',pt(r,2))
 capbank(['C413','C424'],810.26,1323.34,'Phase comparator supply bypass')


def draw_cst(g):
 _draw_cst(g)
 if 'U60' not in g['parts']:return
 from tesla_dual_cst import ref2,net2
 dy=1000.76
 h=dict(g,second_channel=True)
 h['put']=lambda r,x,y,*a:g['put'](ref2(r),x,y+dy,*a)
 h['pt']=lambda r,n:(g['pt'](ref2(r),n)[0],g['pt'](ref2(r),n)[1]-dy)
 h['net']=lambda r,n:g['net'](ref2(r),n)
 h['route']=lambda n,*ps:g['route'](net2(n),*[(x,y+dy) for x,y in ps])
 h['junction']=lambda p:g['junction']((p[0],p[1]+dy))
 h['place']=lambda r,x,y,*a:g['place'](ref2(r),x,y+dy,*a)
 h['chain']=lambda n,*pins:g['chain'](net2(n),*[(ref2(r),p) for r,p in pins])
 h['rail']=lambda refs,n,y,pins='1':g['rail']([ref2(r) for r in refs],net2(n),y+dy,pins)
 h['capbank']=lambda refs,x,y,title=None:g['capbank']([ref2(r) for r in refs],x,y+dy,title.replace('U40/U41','U60/U61') if title else None)
 h['note']=lambda t,x,y,*a:g['note'](t.replace('U40/U41','U60/U61').replace('CT1_MID','CT2_MID'),x,y+dy,*a)
 h['box']=lambda t,x,y,w,hh:g['box']('CST 2 / '+t,x,y+dy,w,hh)
 _draw_cst(h)
