"""Eight parallel 2220 MLCCs per battery/GDT reservoir; see CERAMIC-RESERVOIRS.md."""
MPN='CGA9P3X7R1H226MT0Y0N'
LCSC='C49297044'
DATASHEET='https://www.lcsc.com/datasheet/C49297044.pdf'
BANKS={'battery':['C335']+[f'C{i}' for i in range(336,343)],
       'gdt1':['C526']+[f'C{i}' for i in range(531,538)],
       'gdt2':['C566']+[f'C{i}' for i in range(571,578)]}
def populate(add,key,x,y):
 for i,ref in enumerate(BANKS[key]):
  f=add(ref,'22uF 50V X7R','Capacitor_SMD','C_2220_5750Metric',
      {'1':'VBAT_24V','2':'GND'},x+(i%4)*8,y+(i//4)*6.5,
      kind='c',mpn=MPN,lcsc=LCSC)
  if f is not None:
   for k,val in [('Manufacturer','TDK'),('Datasheet',DATASHEET)]:
    f.SetField(k,val);f.GetField(k).SetVisible(False)
