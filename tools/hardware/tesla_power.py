"""Two battery-fed TI LMZ14202H integrated-inductor auxiliary supplies."""
def populate(add,res,cap):
 def c(r,val,a,z,x,y,size='0805_2012'):
  return add(r,val,'Capacitor_SMD','C_'+size+'Metric',{'1':a,'2':z},x,y,kind='c')
 for idx,x,y,out,bottom,ron in [(30,132,145,'+12V_BIAS','2.43k','249k'),(31,180,145,'VIN_5V','6.49k','100k')]:
  tag=f'P{idx}';n=idx*10
  pins={'1':'VBAT_24V','2':tag+'_RON','3':tag+'_UVLO','4':'GND','5':tag+'_SS','6':tag+'_FB','7':out,'8':'GND'}
  add('U'+str(idx),'LMZ14202HTZX/NOPB','Package_TO_SOT_SMD','Texas_NDW-7_TabPin8',pins,x,y,mpn='LMZ14202HTZX/NOPB',lcsc='C2861493',names={'1':'VIN','2':'RON','3':'EN','4':'GND','5':'SS','6':'FB','7':'VOUT','8':'EP'},types={'1':'power_in','4':'power_in','7':'power_out','8':'power_in'})
  for off,val,a,z,dx,dy in [(0,'34k',out,tag+'_FB',-12,8),(1,bottom,tag+'_FB','GND',-12,11),(2,ron,'VBAT_24V',tag+'_RON',-12,-7),(4,'168k','VBAT_24V',tag+'_UVLO',-18,-2),(5,'10k',tag+'_UVLO','GND',-18,2)]:res('R'+str(n+off),val,a,z,x+dx,y+dy)
  c('C'+str(n),'4.7nF',tag+'_SS','GND',x-12,y+4)
  c('C'+str(n+1),'22nF',out,tag+'_FB',x-8,y+9)
  # Parallel input ceramics: confirm >=10 uF effective at maximum battery voltage.
  for off,dy in [(2,-9),(3,-13)]:c('C'+str(n+off),'10uF 50V X7R','VBAT_24V','GND',x-3,y+dy,'1210_3225')
  # Reference targets: >=47 uF effective at 12 V, >=100 uF at 5 V.
  for off,dy in [(4,0),(5,4),(6,8)]:c('C'+str(n+off),'47uF 25V X7R',out,'GND',x+10,y+dy,'1210_3225')
 c('C333','22uF 50V','VBAT_24V','GND',220,78,'1812_4532')
 from tesla_reservoirs import populate as reservoir
 reservoir(add,'battery',215,65)
 add('J30','12V BATTERY / LOWER','TerminalBlock_Phoenix','TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal',{'1':'BAT_MID_12V','2':'GND'},239,75,kind='connector',names={'1':'+','2':'-'})
