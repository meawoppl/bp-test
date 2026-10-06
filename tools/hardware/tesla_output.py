"""Two all-N-channel 24 V GDT bridges; FPGA owns timing and overload handling."""
REMOVED_CST={'U43','U45','J41','D44','R412','R413','R417','R418','R419','R420','R423','C411','C414','C415','C416','C417','C426'}
COMMANDS=[f'GDT{ch}_{leg}_{level}' for ch in [1,2] for leg in ['L','R'] for level in ['HI','LO']]
from tesla_fpga_pinmap import COMMAND_CONTACTS as CONTACTS
def populate(add,res,cap):
 def r(ref,val,a,b,x,y,size='0805'):
  return add(ref,val,'Resistor_SMD',{'0805':'R_0805_2012Metric','2512':'R_2512_6332Metric'}[size],{'1':a,'2':b},x,y,kind='r')
 def c(ref,val,a,b,x,y,fp='C_0805_2012Metric',lib='Capacitor_SMD',**kw):return add(ref,val,lib,fp,{'1':a,'2':b},x,y,kind='c',**kw)
 # FPGA fabric owns enable/blanking. Passive default-off bias and source damping
 # remain on each direct command path; there is no carrier ARM gate.
 for ch in range(2):
  commands=COMMANDS[ch*4:ch*4+4]
  for i,n in enumerate(commands):
   r('R'+str((500 if ch==0 else 509)+i),'2.2k',n,'GND',131+i*4,55+ch*24)
   r('R'+str((505 if ch==0 else 513)+i),'33R',n,n+'_BUS',131+i*4,59+ch*24)
 for ch,y in enumerate([42,103]):
  base=520+ch*40; pre=f'GDT{ch+1}_';cr=lambda n:'C'+str(base+n);rr=lambda n:'R'+str(base+n)
  # Two half bridges with independent logical commands and power stages.
  for leg,x in enumerate([148,172]):
   j=ch*2+leg;u='U'+str(51+j);stem=pre+('L_' if leg==0 else 'R_');sw=stem+'SW'
   ip={'1':'+12V_BIAS','2':stem+'HB','3':stem+'HO','4':sw,'5':COMMANDS[ch*4+leg*2]+'_BUS','6':COMMANDS[ch*4+leg*2+1]+'_BUS','7':'GND','8':stem+'LO_DRV'}
   add(u,'UCC27282DR','Package_SO','SOIC-8_3.9x4.9mm_P1.27mm',ip,x,y,mpn='UCC27282DR',lcsc='C2867844',names={'1':'VDD','2':'HB','3':'HO','4':'HS','5':'HI','6':'LI','7':'VSS','8':'LO'},types={k:('input' if k in ['5','6'] else 'output' if k in ['3','8'] else 'passive') for k in ip})
   c(cr(leg*3),'1uF 25V X7R',stem+'HB',sw,x+5,y)
   c(cr(leg*3+1),'100nF 25V','+12V_BIAS','GND',x-5,y-3)
   c(cr(leg*3+2),'4.7uF 25V X7R','+12V_BIAS','GND',x-5,y+2)
   for hilo,dy in [(0,-10),(1,11)]:
    q='Q'+str(50+ch*4+leg*2+hilo);gn=stem+('HG' if hilo==0 else 'LG');source=sw if hilo==0 else 'GND';drain='VBAT_24V' if hilo==0 else sw
    add(q,'STD80N10F7','Package_TO_SOT_SMD','TO-252-2',{'1':gn,'2':drain,'3':source},x+10,y+dy,kind='mosfet',mpn='STD80N10F7',lcsc='C2832811',names={'1':'G','2':'D','3':'S'})
    r(rr(leg*4+hilo*2),'4.7R',stem+('HO' if hilo==0 else 'LO_DRV'),gn,x+3,y+dy)
    r(rr(leg*4+hilo*2+1),'10k',gn,source,x+10,y+dy+6)
  from tesla_reservoirs import populate as reservoir
  reservoir(add,f'gdt{ch+1}',192,y-19)
  c(cr(7),'2.2uF 50V X7R','VBAT_24V','GND',195,y,'C_1210_3225Metric')
  c(cr(8),'100nF 50V','VBAT_24V','GND',195,y+5)
  # Original UD2.7 Rev C: 2.2uF DC block, shunted by 15R + 1uF damping.
  c(cr(9),'2.2uF 50V X7R',pre+'L_SW',pre+'OUT_P',212,y+3,'C_1210_3225Metric',mpn='C3225X7R1H225KT000N',lcsc='C76683')
  r(rr(9),'15R 1W',pre+'L_SW',pre+'SNUB',207,y+10,'2512')
  c(cr(10),'1uF 50V X7R',pre+'SNUB',pre+'OUT_P',217,y+10,'C_1206_3216Metric',mpn='C1206C105K5RACTU',lcsc='C2167287')
  add('J'+str(50+ch),f'GDT {ch+1} PRIMARY','TerminalBlock_Phoenix','TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal',{'1':pre+'OUT_P','2':pre+'R_SW'},239,y,kind='connector',names={'1':'PRIMARY +','2':'PRIMARY -'})
  add('D'+str(50+ch),'SMBJ30A','Diode_SMD','D_SMB',{'1':'VBAT_24V','2':'GND'},194,y+13,kind='diode',mpn='SMBJ30A-13-F',names={'1':'K','2':'A'})

def finish_placement(fps,parts,p,v):
 """Roomy unrouted placement, with clear device courtyards."""
 def move(ref,x,y,a=0):
  f=fps[ref];f.SetPosition(v(x,y));f.SetOrientationDegrees(a);parts[ref]['position']=[x,y,a]
  f.Reference().SetPosition(v(x,y-8 if ref.startswith('J') else y-5))
 move('J4',220,27)
 for i in range(4):move('R'+str(500+i),128+i*4.5,81)
 for ch,y in enumerate([42,103]):
  base=520+ch*40
  for leg,x in enumerate([148,172]):
   move('C'+str(base+leg*3),x+6.5,y,90)
   move('C'+str(base+leg*3+1),x-6.5,y-3,90)
   move('C'+str(base+leg*3+2),x-6.5,y+2,90)
   for hilo,dy in [(0,-10),(1,11)]:move('R'+str(base+leg*4+hilo*2),x+1,y+dy,90)
  move('J'+str(50+ch),239,y)
