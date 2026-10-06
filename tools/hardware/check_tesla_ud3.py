#!/usr/bin/env python3
"""Independent channel contract checks and illustrative differential CT filter sweep.
Not a vendor choke macromodel: leakage is swept; no common-mode attenuation claim.
"""
import json,itertools
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
D=Path(__file__).resolve().parents[2]/'boards/tesla-coil-controller'
p=json.loads((D/'docs/circuit.json').read_text())
from tesla_output import COMMANDS,CONTACTS
assert len(set(COMMANDS))==8
assert set(COMMANDS).issubset(p['J2']['pins'].values())
assert all(r not in p for r in ['U50','U55','C500','C501','R504'])
assert not any(n=='DRIVE_ARM' for part in p.values() for n in part['pins'].values())
for ch in range(2):
 for i in range(4):
  n=COMMANDS[ch*4+i]
  r='R'+str((505 if ch==0 else 513)+i)
  assert p[r]['pins']=={'1':n,'2':n+'_BUS'}
 for leg in range(2):
  d=p['U'+str(51+ch*2+leg)]['pins']
  assert [d['5'],d['6']]==[n+'_BUS' for n in COMMANDS[ch*4+leg*2:ch*4+leg*2+2]]
assert p['L40']['pins']=={'1':'CT1_CABLE_P','2':'CT1_RAW','4':'CT1_CABLE_N','3':'GND'}
assert p['J40']['pins']=={'1':'CT1_CABLE_P','2':'CT1_CABLE_N'}
for r in ['R400','R401','D40','C429']:assert p[r]['pins']=={'1':'CT1_RAW','2':'GND'}
assert p['C427']['pins']=={'1':'CT1_CABLE_P','2':'GND'}
assert p['C428']['pins']=={'1':'CT1_CABLE_N','2':'GND'}
def transfer(freq,leak):
 w=2*np.pi*freq;jw=1j*w;g=1/(.05+jw*leak/2)
 # Differential leakage equivalent, matched 150pF on cable conductors,
 # 1nF across 10R burden, ideal current source P->N. Both choke DCRs included.
 a=np.array([[g+jw*150e-12,0,-g],[0,g+jw*150e-12,0],[-g,0,g+.1+jw*1e-9]])
 return np.linalg.solve(a,np.array([1,-1,0]))[2]/10
f=np.geomspace(1e3,1e6,600);results=[]
plt.rcParams.update({'figure.facecolor':'#1a1b26','axes.facecolor':'#1a1b26','text.color':'#c0caf5','axes.labelcolor':'#c0caf5','xtick.color':'#c0caf5','ytick.color':'#c0caf5','axes.edgecolor':'#565f89'})
fig,axs=plt.subplots(2,1,figsize=(9,6),sharex=True)
for leak,col in zip([0,0.2e-6,2e-6],['#7aa2f7','#9ece6a','#e0af68']):
 h=np.array([transfer(x,leak) for x in f]);h30=transfer(30000,leak)
 results.append(dict(assumed_differential_leakage_uH=leak*1e6,gain_at_30k=float(abs(h30)),phase_deg_at_30k=float(np.angle(h30,deg=True)),delay_ns_at_30k=float(-np.angle(h30)/(2*np.pi*30000)*1e9)))
 axs[0].semilogx(f,20*np.log10(abs(h)),color=col,label=f'Assumed leakage {leak*1e6:g} µH')
 axs[1].semilogx(f,np.angle(h,deg=True),color=col)
for ax in axs:ax.axvline(30000,color='#bb9af7',ls='--');ax.grid(alpha=.18)
axs[0].set_ylabel('Gain relative to 10 Ω burden (dB)');axs[1].set_ylabel('Added phase (degrees)');axs[1].set_xlabel('Frequency (Hz)');axs[0].legend(facecolor='#1a1b26',labelcolor='#c0caf5')
fig.suptitle('CT input filter: differential small-signal model\nIdeal CT, linear parts; choke leakage assumed, not measured')
fig.tight_layout();out=D/'docs/cst';out.mkdir(exist_ok=True)
fig.savefig(out/'cable-filter-response.png',dpi=160)
(out/'cable-filter-results.json').write_text(json.dumps({'model':'Ideal current source, 50mΩ/winding, 150pF cable shunts, 1nF burden shunt; no TVS/cable/CT parasitics or core saturation','results':results},indent=2)+'\n')
print('Independent command paths and filter topology verified.');print(json.dumps(results,indent=2))
