"""Second independent CST frontend and four external ADC inputs.
Channel 1 uses CT1_* nets; channel 2 uses CT2_*. Reference names stay fixed. Both rectifiers share -5V_CT.
"""
import re
SHARED={'U44','R421','C420','C421','C422','C423'}
def ref2(r):
 m=re.fullmatch(r'([A-Z]+)(\d+)',r)
 return m[1]+str(int(m[2])+(200 if m[1] in ['R','C'] else 20))
def net2(n):
 return n.replace('CT1_','CT2_',1) if n and n.startswith('CT1_') else n
# Connector-aligned buffer rows reach CH1..4 in order without crossovers.
# Physical connector numbers stay AUX1..4; software uses adc-channel-map.json.
ADC_INPUTS=[f'AUX{i}_BUFFERED' for i in range(1,5)]+['CT1_RAW','CT1_ENVELOPE','CT2_RAW','CT2_ENVELOPE']
CONNECTOR='TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal'
def populate_second(add):
 from tesla_cst import populate
 def duplicate(ref,value,lib,name,pins,x,y,**kw):
  if ref in SHARED:return
  if 'names' in kw:kw['names']={k:net2(v) for k,v in kw['names'].items()}
  return add(ref2(ref),net2(value).replace('CST SECONDARY','CST 2 SECONDARY'),lib,name,{k:net2(v) for k,v in pins.items()},x,y+65,**kw)
 populate(duplicate,None,None)
def populate_aux(add):
 for i,ref in enumerate(['J3','J8','J9','J10']):
  add(ref,f'AUX {i+1} / 0-5V','Connector_JST','JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal',{'1':f'AUX{i+1}_0_5V','2':'GND'},28,82+i*9,a=270,kind='connector',mpn='S2B-PH-K-S(LF)(SN)',names={'1':f'AUX{i+1}','2':'GND'})
