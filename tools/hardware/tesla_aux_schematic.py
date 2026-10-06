"""Four wired unity-gain input stages, with visible feedback and local bypass."""
def draw_aux(g):
 globals().update(g)
 for i in range(4):
  x=584.2+(i%2)*297.18;y=500.38+(i//2)*152.4;k=700+10*i
  U=f'U{70+i}';D=f'D{70+i}';R=f'R{k}';RP=f'R{k+1}';C=f'C{k}';CF=f'C{k+1}'
  box(f'AUX {i+1} / 0-5 V / unity buffer',x,y,287.02,144.78)
  put(U,x+167.64,y+66.04);sy=pt(U,3)[1]
  put(R,x+81.28,sy);put(C,x+25.4,sy+15.24,True);put(RP,x+55.88,sy+15.24,True)
  raw=net(R,1);filt=net(R,2);out=net(U,1)
  route(raw,(x+10.16,sy),pt(R,1));route(raw,pt(C,1),(x+25.4,sy));junction((x+25.4,sy));route(raw,pt(RP,1),(x+55.88,sy));junction((x+55.88,sy));route('GND',pt(C,2));route('GND',pt(RP,2))
  put(CF,x+119.38,sy+15.24,True);route(filt,pt(R,2),pt(U,3));route(filt,pt(CF,1),(x+119.38,sy));junction((x+119.38,sy));route('GND',pt(CF,2))
  put(D,x+121.92,y+27.94);route(filt,pt(D,3),(pt(D,3)[0],sy));junction((pt(D,3)[0],sy));power('+5V_ADC',*pt(D,2));used.add((D,'2'));route('GND',pt(D,1))
  # Feedback returns above the signal path, clear of the input filter.
  route(out,pt(U,1),(x+226.06,pt(U,1)[1]));route(out,pt(U,4),(x+144.78,pt(U,4)[1]),(x+144.78,y+40.64),(x+226.06,y+40.64),(x+226.06,pt(U,1)[1]));junction((x+226.06,pt(U,1)[1]))
  cp=f'C{k+2}';cn=f'C{k+3}'
  put(cp,x+195.58,y+53.34,True);put(cn,x+205.74,y+93.98,True)
  route('+12V_AUX',pt(U,5),(pt(U,5)[0],pt(cp,1)[1]),pt(cp,1));power('+12V_AUX',pt(U,5)[0],pt(cp,1)[1]);route('GND',pt(cp,2))
  route('-5V_CT',pt(U,2),(pt(U,2)[0],pt(cn,1)[1]),pt(cn,1));power('-5V_CT',pt(U,2)[0],pt(cn,1)[1]);route('GND',pt(cn,2))
  # Probe the connector input and unity-buffer output against a local return.
  ti=f'TP{k}';to=f'TP{k+1}';tg=f'TP{k+2}'
  put(ti,x+25.4,sy-15.24);route(raw,pt(ti,1),(x+25.4,sy))
  put(to,x+246.38,pt(U,1)[1]-15.24)
  route(out,pt(to,1),(x+246.38,pt(U,1)[1]),(x+226.06,pt(U,1)[1]))
  put(tg,x+246.38,y+111.76);route('GND',pt(tg,1))
  note('1k / 2.2nF: 72 kHz nominal; ADC-side 100R / 1nF follows.',x+10.16,y+123.19,1.1)
  note('1M DC load; shared return; powered operation only.',x+10.16,y+134.62,1.1)
 # Supply RC and bulk bypass fit within the existing analog supply block.
 put('R740',78.74,558.8);route('+12V_BIAS',(43.18,558.8),pt('R740',1));power('+12V_BIAS',43.18,558.8)
 put('C740',114.3,568.96,True);route('+12V_AUX',pt('R740',2),(114.3,558.8),pt('C740',1));power('+12V_AUX',114.3,558.8);route('GND',pt('C740',2))
 put('C741',287.02,566.42,True);power('-5V_CT',*pt('C741',1));used.add(('C741','1'));route('GND',pt('C741',2))
