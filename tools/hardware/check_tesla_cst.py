#!/usr/bin/env python3
"""Topology-only analog check. Deliberately not a manufacturer-model qualification."""
import json,subprocess,tempfile
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parents[2]/'boards/tesla-coil-controller/docs/cst'
s=(D/'rectifier-topology.cir').read_text();results=[]
with tempfile.TemporaryDirectory() as tmp:
 for amp in [.1,.5,1,2,2.4]:
  f=Path(tmp)/'test.cir';f.write_text(s.replace('SIN(0 2 30k)',f'SIN(0 {amp} 30k)'))
  subprocess.run(['ngspice','-b',str(f)],cwd=tmp,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,check=True)
  a=np.loadtxt(Path(tmp)/'rectifier.dat',skiprows=1);t=a[:,0]
  mean=float(np.trapezoid(a[:,4],t)/(t[-1]-t[0]));ideal=2*amp/np.pi
  results.append(dict(input_peak_v=amp,frequency_hz=30000,envelope_mean_v=mean,ideal_mean_v=ideal,mean_error_percent=100*(mean/ideal-1),abs_min_v=float(a[:,3].min()),abs_max_v=float(a[:,3].max()),envelope_min_v=float(a[:,4].min()),envelope_max_v=float(a[:,4].max())))
  if amp==2:
   import matplotlib;matplotlib.use('Agg')
   import matplotlib.pyplot as plt
   fig,axs=plt.subplots(2,1,figsize=(10,6),sharex=True,facecolor='#1a1b26')
   for ax in axs:
    ax.set_facecolor('#1a1b26');ax.tick_params(colors='#c0caf5');ax.grid(color='#565f89',alpha=.3)
    for sp in ax.spines.values():sp.set_color('#565f89')
    ax.set_ylabel('V',color='#c0caf5')
   axs[0].plot(t*1e6,a[:,1],color='#7aa2f7',label='CST raw')
   axs[0].plot(t*1e6,a[:,3],color='#9ece6a',label='Full-wave output')
   axs[1].plot(t*1e6,a[:,4],color='#e0af68',label='Filtered magnitude (CH2)')
   axs[1].axhline(ideal,color='#bb9af7',ls='--',label='Ideal mean = 2 Vpk / pi')
   for ax in axs:ax.legend(facecolor='#24283b',labelcolor='#c0caf5')
   axs[1].set_xlabel('Time (us)',color='#c0caf5');fig.suptitle('30 kHz topology simulation — generic finite-bandwidth op amps',color='#c0caf5');fig.tight_layout();fig.savefig(D/'rectifier-topology.png',dpi=160);plt.close(fig)
 assert abs(next(r for r in results if r['input_peak_v']==2)['mean_error_percent'])<2
(D/'topology-check.json').write_text(json.dumps({'model_limitations':'Generic 10 MHz op amps, clipped ±4.5 V, generic fast diodes. No vendor macro-model, noise, slew-rate limit, temperature, startup or CT-core model. This checks topology, not hardware accuracy or stability.','results':results},indent=2)+'\n')
print(json.dumps(results,indent=2))
