"""CST input circuit: normalized ±2 V burden signal, independent phase timing."""
def populate(add,res,cap):
 def r(ref,val,a,b,x,y,large=False,mpn=''):
  return add(ref,val,'Resistor_SMD','R_2512_6332Metric' if large else 'R_0805_2012Metric',{'1':a,'2':b},x,y,kind='r',mpn=mpn)
 def c(ref,val,a,b,x,y):return add(ref,val,'Capacitor_SMD','C_0805_2012Metric',{'1':a,'2':b},x,y,kind='c')
 def diode(ref,mpn,k,a,x,y):return add(ref,mpn,'Diode_SMD','D_SOD-123',{'1':k,'2':a},x,y,kind='diode',mpn=mpn,names={'1':'K','2':'A'})
 add('J40','CST SECONDARY','TerminalBlock_Phoenix','TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal',{'1':'CT1_CABLE_P','2':'CT1_CABLE_N'},29,87,kind='connector',names={'1':'S1 / DOT','2':'S2 / RETURN'})
 # Both cable conductors pass through the same current-compensated core.
 add('L40','90R @100MHz / 2A CMC','Tesla','CMC_TAI-TECH_WCM4532F2SF',{'1':'CT1_CABLE_P','2':'CT1_RAW','4':'CT1_CABLE_N','3':'GND'},40,105,kind='cmc',mpn='WCM4532F2SF-900T20',lcsc='C357325',names={'1':'P IN','2':'P OUT','4':'N IN','3':'N OUT'})
 c('C427','150pF 50V C0G','CT1_CABLE_P','GND',38,115)
 c('C428','150pF 50V C0G','CT1_CABLE_N','GND',38,121)
 c('C429','1nF 50V C0G','CT1_RAW','GND',48,118)
 for ref,y in [('R400',84),('R401',89)]:r(ref,'20R 1% 1W','CT1_RAW','GND',40,y,True,'CRCW251220R0FKEG')
 add('D40','SMBJ5.0CA','Diode_SMD','D_SMB',{'1':'CT1_RAW','2':'GND'},40,97,kind='tvs',mpn='SMBJ5.0CA',names={'1':'~','2':'~'})
 # Precision half-wave followed by weighted sum: Vabs = -(Vin + 2 Vhalf).
 for ref,ip,im,op,x in [('U40','GND','CT1_RECT_SUM','CT1_RECT_DRIVE',59),('U41','GND','CT1_ABS_SUM','CT1_ABS',80)]:
  add(ref,'OPA197IDBVR','Package_TO_SOT_SMD','SOT-23-5',{'1':op,'2':'-5V_CT','3':ip,'4':im,'5':'+5V_ADC'},x,90,mpn='OPA197IDBVR',names={'1':'OUT','2':'V-','3':'+','4':'-','5':'V+'},types={'1':'output','2':'power_in','3':'input','4':'input','5':'power_in'})
 for ref,val,a,b,x,y in [
 ('R402','10k 0.1%','CT1_RAW','CT1_RECT_SUM',52,86),('R403','10k 0.1%','CT1_RECT_SUM','CT1_HALF',59,82),
 ('R404','10k 0.1%','CT1_RAW','CT1_ABS_SUM',73,86),('R405','10k 0.1%','CT1_HALF','CT1_ABS_SUM',75,95),('R406','10k 0.1%','CT1_HALF','CT1_ABS_SUM',80,98),
 ('R407','10k 0.1%','CT1_ABS_SUM','CT1_ABS',82,82),('R408','1k','CT1_ABS','CT1_ENVELOPE',88,91)]:r(ref,val,a,b,x,y)
 diode('D41','1N4148W,115','CT1_RECT_SUM','CT1_RECT_DRIVE',65,86)
 diode('D42','1N4148W,115','CT1_RECT_DRIVE','CT1_HALF',65,95)
 c('C400','10nF C0G','CT1_ENVELOPE','GND',88,95)
 for ref,n,x,y in [('C401','+5V_ADC',56,90),('C402','-5V_CT',62,90),('C403','+5V_ADC',77,90),('C404','-5V_CT',83,90)]:c(ref,'100nF',n,'GND',x,y)
 # AC-coupled phase timing; overcurrent is handled by ADC/FPGA.
 r('R410','5k 0.1%','CT1_PHASE_AC','CT1_PHASE',95,82)
 r('R411','10k 0.1%','+3V3','CT1_PHASE',99,82)
 c('C425','1uF 16V','CT1_RAW','CT1_PHASE_AC',91,82)
 r('R422','10k 0.1%','CT1_PHASE','GND',91,90)
 c('C410','22pF C0G','CT1_PHASE','GND',95,86)
 add('D43','BAT54S,215','Package_TO_SOT_SMD','SOT-23',{'1':'GND','2':'+3V3','3':'CT1_PHASE'},95,90,kind='clamp',mpn='BAT54S,215',names={'1':'A1','2':'K2','3':'K1/A2'})
 r('R414','1k 0.1%','+3V3','CT1_MID',93,113);r('R415','1k 0.1%','CT1_MID','GND',98,113);c('C412','1uF','CT1_MID','GND',98,117)
 add('U42','TLV3501AIDBVR','Package_TO_SOT_SMD','SOT-23-6',{'1':'CT1_MID','2':'GND','3':'CT1_PHASE','4':'+3V3','5':'CT1_ZERO_DRV','6':'GND'},102,89,mpn='TLV3501AIDBVR',names={'1':'-','2':'V-','3':'+','4':'V+','5':'OUT','6':'SHDN'},types={'1':'input','2':'power_in','3':'input','4':'power_in','5':'output','6':'input'})
 r('R416','33R','CT1_ZERO_DRV','CT1_ZERO',109,88);c('C413','100nF','+3V3','GND',102,85)
 # Negative rail is only for the rectifier; phase timing does not depend on it.
 add('U44','TPS60403DBVR','Package_TO_SOT_SMD','SOT-23-5',{'1':'CT1_NEG_PUMP','2':'+5V_ADC','3':'CT1_FLY_N','4':'GND','5':'CT1_FLY_P'},59,117,mpn='TPS60403DBVR',names={'1':'OUT','2':'IN','3':'CFLY-','4':'GND','5':'CFLY+'},types={'1':'power_out','2':'power_in','3':'passive','4':'power_in','5':'passive'})
 c('C420','1uF 16V','CT1_FLY_P','CT1_FLY_N',59,112);c('C421','1uF 16V','+5V_ADC','GND',55,117);c('C422','10uF 16V','CT1_NEG_PUMP','GND',63,117)
 r('R421','10R','CT1_NEG_PUMP','-5V_CT',68,117);c('C423','10uF 16V','-5V_CT','GND',73,117)
 c('C424','2.2uF','+3V3','GND',106,117)
 for ref,n,x in [('TP40','CT1_RAW',40),('TP41','CT1_HALF',50),('TP42','CT1_ABS',80),('TP43','CT1_ENVELOPE',90)]:
  add(ref,n,'TestPoint','TestPoint_Pad_D1.0mm',{'1':n},x,106,kind='testpoint',names={'1':n})

def finish_placement(fps,parts,pcb,v):
 """Initial CST floorplan corrections; call only on explicit creation/placement."""
 for r in ['C401','C402','C403','C404','R422']:
  fps[r].SetOrientationDegrees(90);parts[r]['position'][2]=90
 for r,x,y in [('C401',55.5,90),('C402',62.5,90),('C403',76.5,90),('C404',83.5,90)]:
  fps[r].SetPosition(v(x,y));parts[r]['position']=[x,y,90]
 fps['J40'].Reference().SetPosition(v(29,79.5))
 for r,y in [('R400',84),('R401',89)]:
  fps[r].SetPosition(v(45.5,y));parts[r]['position']=[45.5,y,0]
 for r in ['D40','D41','D42','D43']:fps[r].Reference().SetVisible(False)
 for r,x,y in [('U40',59,86.5),('U41',80,86.5),('U42',102,94),('U44',59,121.5)]:fps[r].Reference().SetPosition(v(x,y))
