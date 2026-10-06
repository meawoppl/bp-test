"""J5: self-powered native-USB programming port, using the carrier's connector."""

def populate(add):
    import pcbnew as p
    def component(*args, **kwargs):
        footprint = add(*args, **kwargs)
        for item in footprint.GraphicalItems():
            if item.GetClass() == 'PCB_SHAPE' and item.GetLayer() == p.F_SilkS:
                item.SetWidth(p.FromMM(.15))
        return footprint
    pins = {'A1':'GND','B12':'GND','A12':'GND','B1':'GND','S1':'GND',
            'A4':'USB_VBUS','B9':'USB_VBUS','A9':'USB_VBUS','B4':'USB_VBUS',
            'A5':'USB_CC1','B5':'USB_CC2','A6':'USB_D+','B6':'USB_D+',
            'A7':'USB_D-','B7':'USB_D-','A8':None,'B8':None}
    names = {p: ('SBU1' if p=='A8' else 'SBU2' if p=='B8' else 'SHIELD' if p=='S1' else
                 'VBUS' if n=='USB_VBUS' else n.removeprefix('USB_')) for p,n in pins.items()}
    add('J5','USB-C / PROGRAMMING ONLY','Carrier','USB_C_Receptacle_HRO_TYPE-C-31-M-12',
        pins,128,30.4,180,kind='connector',mpn='TYPE-C-31-M-12',lcsc='C165948',names=names)
    component('U3','USBLC6-2SC6','Package_TO_SOT_SMD','SOT-23-6',
        {'1':'USB_D+','2':'GND','3':'USB_D-','4':'USB_D-','5':'USB_VBUS','6':'USB_D+'},
        119.5,32.5,180,mpn='USBLC6-2SC6',lcsc='C7519',
        names={'1':'D+','2':'GND','3':'D-','4':'D-','5':'VBUS','6':'D+'})
    for ref,val,pins,x,y,a,mpn,lcsc in [
        ('R24','5.1k',{'1':'USB_CC1','2':'GND'},136,31.5,180,'0603WAF5101T5E','C23186'),
        ('R25','5.1k',{'1':'USB_CC2','2':'GND'},119.5,28.8,0,'0603WAF5101T5E','C23186'),
        ('R26','100k',{'1':'USB_VBUS','2':'USB_VBUS_PRESENT'},115,29.3,0,'0603WAF1003T5E','C25803'),
        ('R27','150k',{'1':'USB_VBUS_PRESENT','2':'GND'},112,29.3,0,'0603WAF1503T5E','C22807'),
    ]:
        component(ref,val,'Resistor_SMD','R_0603_1608Metric',pins,x,y,a,kind='r',mpn=mpn,lcsc=lcsc)
    component('C22','100nF / 16V','Capacitor_SMD','C_0603_1608Metric',
        {'1':'USB_VBUS','2':'GND'},115.8,32.5,180,kind='c',
        mpn='CL10B104KO8NNNC',lcsc='C14663')
