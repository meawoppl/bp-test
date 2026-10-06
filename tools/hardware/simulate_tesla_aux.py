#!/usr/bin/env python3
"""Small-signal analytical model, not a vendor SPICE or EMC qualification."""
from pathlib import Path
import json,numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
D=Path(__file__).resolve().parents[2]/'boards/tesla-coil-controller/docs/aux';D.mkdir(exist_ok=True)
f=np.logspace(1,7,1000);s=2j*np.pi*f
# Source 50 ohm; cable-side 1M || 150pF; 1k into 2.2nF;
# unity amplifier approximated by a 10MHz pole; ADC isolation 100R/1nF, 1M input.
def h(freq):
 s=2j*np.pi*np.asarray(freq);rf=1000;cf=2.2e-9;rs=50;rp=1e6;cp=150e-12
 a=1+s*rf*cf
 vin=1/(a*(1+rs/rp+s*rs*cp)+rs*s*cf)
 return vin/(1+s/(2*np.pi*1e7))/(1+100/1e6+s*100*1e-9)
plt.rcParams.update({'figure.facecolor':'#1a1b26','axes.facecolor':'#1a1b26','text.color':'#c0caf5','axes.labelcolor':'#c0caf5','xtick.color':'#c0caf5','ytick.color':'#c0caf5','axes.edgecolor':'#565f89','grid.color':'#565f89'})
fig,ax=plt.subplots(2,1,figsize=(9,7),layout='constrained');ax[0].semilogx(f,20*np.log10(abs(h(f))),color='#7aa2f7');ax[0].set(ylabel='Gain (dB)',title='AUX input filter — analytical small-signal estimate',ylim=(-70,1));ax[0].grid(True,alpha=.35)
ax[1].semilogx(f,np.angle(h(f),deg=True),color='#9ece6a');ax[1].set(xlabel='Frequency (Hz)',ylabel='Phase (degrees)');ax[1].grid(True,alpha=.35)
fig.savefig(D/'filter-response.png',dpi=150)
rows=[dict(frequency_hz=q,gain_db=float(20*np.log10(abs(h(q)))),phase_deg=float(np.angle(h(q),deg=True))) for q in [1000,10000,30000,72000,100000,1e6]]
(D/'filter-response.json').write_text(json.dumps(dict(model='Linear RC network; 50-ohm source, 1M ADC load, 10MHz one-pole unity amplifier; no diode conduction, parasitics, EMI or power sequencing model',results=rows),indent=2)+'\n')
print(json.dumps(rows,indent=2))
