"""Four high-impedance unity-gain 0–5 V auxiliary channels on J3/J8/J9/J10."""
def populate(add):
 def r(ref,val,a,b,x,y):return add(ref,val,'Resistor_SMD','R_0805_2012Metric',{'1':a,'2':b},x,y,kind='r')
 def c(ref,val,a,b,x,y):return add(ref,val,'Capacitor_SMD','C_0805_2012Metric',{'1':a,'2':b},x,y,kind='c')
 for i in range(4):
  n=i+1;k=700+10*i;x=31+15*i;y=160
  raw=f'AUX{n}_0_5V';filt=f'AUX{n}_FILTERED';out=f'AUX{n}_BUFFERED'
  r(f'R{k}','1k 0.1%',raw,filt,x,y-7)
  r(f'R{k+1}','1M 1%',raw,'GND',x-5,y-7)
  c(f'C{k}','150pF 50V C0G',raw,'GND',x-5,y-3)
  c(f'C{k+1}','2.2nF 50V C0G',filt,'GND',x,y-3)
  add(f'D{70+i}','BAV199,215','Package_TO_SOT_SMD','SOT-23',{'1':'GND','2':'+5V_ADC','3':filt},x+5,y-3,kind='clamp',mpn='BAV199,215',names={'1':'A1','2':'K2','3':'K1/A2'})
  add(f'U{70+i}','OPA197IDBVR','Package_TO_SOT_SMD','SOT-23-5',{'1':out,'2':'-5V_CT','3':filt,'4':out,'5':'+12V_AUX'},x,y,mpn='OPA197IDBVR',names={'1':'OUT','2':'V-','3':'+','4':'-','5':'V+'},types={'1':'output','2':'power_in','3':'input','4':'input','5':'power_in'})
  c(f'C{k+2}','100nF 25V X7R','+12V_AUX','GND',x-4,y)
  c(f'C{k+3}','100nF 16V X7R','-5V_CT','GND',x+4,y)
  # Bare copper probes: connector input, buffered output, and local return.
  for off,signal,name,tx,ty in [(0,raw,'IN',x-7,y-7),(1,out,'OUT',x+8,y),(2,'GND','GND',x+8,y+4)]:
   add(f'TP{k+off}',signal,'Tesla','TestPoint_Pad_D1.0mm_Silk0.15mm',{'1':signal},tx,ty,kind='testpoint',names={'1':name})
 r('R740','10R','+12V_BIAS','+12V_AUX',85,155)
 c('C740','10uF 25V X7R','+12V_AUX','GND',85,159)
 c('C741','10uF 16V X7R','-5V_CT','GND',85,163)
