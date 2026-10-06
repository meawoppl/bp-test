#!/usr/bin/env python3
"""Illustrative GDT drive/load transient sweep, not an IGBT or vendor macro-model."""
from pathlib import Path
import subprocess,tempfile,json
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
D=Path(__file__).resolve().parents[2]/'boards/tesla-coil-controller/docs/gdt';D.mkdir(exist_ok=True)
# Eight cycles at 30 kHz, positive/negative equal duration; zero-output hold afterwards.
T=1/30000;points=[(0,0),(10e-6,0)];edge=10e-6
for n in range(16):
 val=24 if n%2==0 else -24
 points.extend([(edge,points[-1][1]),(edge+100e-9,val),(edge+T/2-200e-9,val),(edge+T/2-100e-9,0)])
 edge+=T/2
points.extend([(edge,0),(400e-6,0)])
results=[];curves=[]
for cg,ll in [(0.8e-6,.5e-6),(.4e-6,.2e-6),(1.6e-6,2e-6)]:
 with tempfile.TemporaryDirectory() as td:
  td=Path(td);out=td/'wave.dat';deck=f'''GDT ideal bridge / lumped load approximation
Vdrive src 0 PWL({' '.join(f'{t:.12g} {v}' for t,v in points)})
Rbridge src blk 0.02
Cblock blk damp 2.2u
Rleak blk damp 1G
Rwire damp leak 0.15
Lleak leak pri {ll}
Lmag pri 0 1m
Rgate pri gate 1.275
Cgate gate 0 {cg}
Rsn blk sn 15
Csn sn damp 1u
.tran 10n 400u
.control
set wr_singlescale
set wr_vecnames
run
wrdata {out} v(src) v(pri) v(gate) i(Vdrive) v(blk,damp) v(blk,sn)
quit
.endc
.end
'''
  (td/'model.cir').write_text(deck);subprocess.run(['ngspice','-b',str(td/'model.cir')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  a=np.loadtxt(out,skiprows=1);active=(a[:,0]>10e-6)&(a[:,0]<edge)
  rms=float(np.sqrt(np.trapezoid(a[active,4]**2,a[active,0])/(a[active,0][-1]-a[active,0][0])))
  results.append({'primary_rms_during_burst_a':rms,'damping_during_burst_w':float(np.trapezoid(a[active,6]**2/15,a[active,0])/(a[active,0][-1]-a[active,0][0])),'gate_equivalent_f':cg,'leakage_h':ll,'gate_min_v':float(a[active,3].min()),'gate_max_v':float(a[active,3].max()),'peak_primary_a':float(abs(a[active,4]).max()),'coupling_cap_peak_v':float(abs(a[:,5]).max()),'limitations':'Ideal voltage bridge; linear lumped reflected capacitance and magnetizing inductance. No Miller plateau, IGBT switching/tail current, core saturation, winding coupling, MOSFET/driver models, or layout parasitics beyond specified L/R.'})
  curves.append(a)
  if len(results)==1:(D/'topology.cir').write_text(deck.replace(str(out),'wave.dat'))
(D/'simulation.json').write_text(json.dumps(results,indent=2)+'\n')
plt.rcParams.update({'figure.facecolor':'#1a1b26','axes.facecolor':'#1a1b26','text.color':'#c0caf5','axes.labelcolor':'#c0caf5','xtick.color':'#c0caf5','ytick.color':'#c0caf5','axes.edgecolor':'#565f89','font.size':10})
fig,ax=plt.subplots(3,1,figsize=(12,9),layout='constrained')
for a,r,col in zip(curves,results,['#7aa2f7','#9ece6a','#e0af68']):
 label=f"Ceq={r['gate_equivalent_f']*1e6:g} uF, Lleak={r['leakage_h']*1e6:g} uH"
 ax[0].plot(a[:,0]*1e6,a[:,3],color=col,label=label)
 ax[1].plot(a[:,0]*1e6,-a[:,4],color=col)
 ax[2].plot(a[:,0]*1e6,a[:,3],color=col)
ax[0].set(ylabel='Referred gate voltage (V)',xlim=(0,320));ax[1].set(ylabel='Primary current (A)',xlim=(0,320));ax[2].set(xlabel='Time (us)',ylabel='First reversal (V)',xlim=(25,34))
ax[0].legend(facecolor='#1a1b26',labelcolor='#c0caf5',loc='upper right')
for z in ax:z.grid(color='#565f89',alpha=.3)
fig.suptitle('GDT output: 24 V bridge, UD2.7 2.2 uF DC block with 15 ohm + 1 uF shunt damping\nIllustrative lumped-load sweep — not validated IGBT waveforms')
fig.savefig(D/'transient-sweep.png',dpi=150);print(json.dumps(results,indent=2))
