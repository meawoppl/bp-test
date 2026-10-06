"""Tesla carrier J2 assignments, ordered for separate ADC and gate escapes.

These are carrier functions; the mating module pinout does not change.
Keep phase inputs on G0/G1 and leave the module's shared RGB pins unused.
"""
ADC_CONTACTS = dict(zip(
    map(str, range(31, 41)),
    ['ADC_CONVST', 'ADC_RESET', 'ADC_SCLK', 'ADC_CS_N', 'ADC_BUSY',
     'ADC_SDI', 'ADC_DOUT_D', 'ADC_DOUT_C', 'ADC_DOUT_B', 'ADC_DOUT_A'],
))
COMMAND_CONTACTS = dict(zip(
    ['7', '9', '10', '11', '2', '4', '5', '6'],
    [f'GDT{channel}_{leg}_{level}' for channel in [1, 2]
     for leg in ['L', 'R'] for level in ['HI', 'LO']],
))
PHASE_CONTACTS = {'22': 'CT1_ZERO', '24': 'CT2_ZERO'}
CONTACTS = ADC_CONTACTS | COMMAND_CONTACTS | PHASE_CONTACTS
