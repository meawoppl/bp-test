#!/usr/bin/env python3
"""Reservoir sensitivity to effective MLCC C and battery lead impedance.
Charge-pulse load, not a switching-device/core simulation. No TVS model.
"""
from pathlib import Path
import subprocess,tempfile,json
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
D=Path(__file__).resolve().parents[2]/'boards/tesla-coil-controller/docs/gdt'
D.mkdir(exist_ok=True)
results=[];curves=[]
# Per-cap effective C values are sensitivity assumptions, not vendor guaranteed minima.
for label,cbank,esr,lead,load,vbat in [
 ('Former 470uF cans',470e-6,.073,1e-6,1,24),
 ('8 ceramics, 12uF each',96e-6,.005,1e-6,1,24),
 ('8 ceramics, 4uF each',32e-6,.005,1e-6,1,24),
 ('Stress: 4uF each, 2x load, 5uH leads',32e-6,.005,5e-6,2,30)]:
 with tempfile.TemporaryDirectory() as td:
  td=Path(td);out=td/'wave.dat'
  # 0.8uF reflected gate equivalent: Q=C*dV=38.4uC at +/-24V.
  # Twenty-A trapezoidal pulse area = 1.92us * I. Two bridges simultaneous.
  amp=20*load*vbat/24
  points=[(0,0),(10e-6,0)]
  for k in range(24):
   t=10e-6+k/60000
   points.extend([(t,0),(t+50e-9,amp),(t+1.92e-6,amp),(t+1.97e-6,0)])
  points.append((800e-6,0));pwl=' '.join(f'{t:.12g} {i:.12g}' for t,i in points)
  deck=f'''Two synchronized bridges: reservoir charge-pulse sensitivity
Vbat battery 0 {vbat}
Rlead battery n0 .05
Llead n0 bus {lead}
Rin bus ci {esr}
Cin ci 0 {cbank}
Rfeed1 bus nf1 .02
Lfeed1 nf1 b1 .2u
Rcap1 b1 c1 {esr}
Cbank1 c1 0 {cbank}
Rfeed2 bus nf2 .02
Lfeed2 nf2 b2 .2u
Rcap2 b2 c2 {esr}
Cbank2 c2 0 {cbank}
Iload1 b1 0 PWL({pwl})
Iload2 b2 0 PWL({pwl})
.tran 20n 800u
.control
set wr_singlescale
set wr_vecnames
run
wrdata {out} v(bus) v(b1) i(Llead) v(b1,c1)
quit
.endc
.end
'''
  (td/'deck.cir').write_text(deck);subprocess.run(['ngspice','-b',str(td/'deck.cir')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  a=np.loadtxt(out,skiprows=1);t=a[:,0];active=(t>=10e-6)&(t<410e-6)
  cap_i=a[:,4]/esr
  result=dict(case=label,bank_effective_uF=cbank*1e6,assumed_bank_esr_ohm=esr,lead_uH=lead*1e6,battery_V=vbat,pulse_A=amp,charge_per_edge_uC=amp*1.92,bridge_min_V=float(a[:,2].min()),bridge_max_V=float(a[:,2].max()),bank_ripple_Arms_during_burst=float(np.sqrt(np.trapezoid(cap_i[active]**2,t[active])/(t[active][-1]-t[active][0]))))
  results.append(result);curves.append(a)
  (D/('reservoir-'+str(len(results))+'.cir')).write_text(deck.replace(str(out),'wave.dat'))
# Undamped unloaded hot-plug corner: explicitly exposes an unresolved entry-protection requirement.
# Total 3*32uF and 5uH, R=0.05ohm, conservative lossless-cap RLC step estimate.
L=5e-6;C=96e-6;R=.05;zeta=R/2*np.sqrt(C/L)
peak=30*(1+np.exp(-np.pi*zeta/np.sqrt(1-zeta*zeta)))
report=dict(model='Two equal synchronized current pulses; 0.8uF equivalent per GDT at nominal load; 24 reversals at 60kHz. Source 50mOhm; each PCB feed 20mOhm/0.2uH. Linear effective capacitance and lumped ESR.',limitations='Sensitivity only. No measured MLCC bias/aging guarantee, nonlinear IGBT/Miller load, core, TVS, hot-plug contact bounce, MLCC ESL, regulator input impedance or layout. Burst RMS is not continuous thermal qualification. No claim of 470uF equivalence.',cases=results,unclamped_hotplug_30V_5uH_estimated_peak_V=float(peak))
(D/'reservoir-results.json').write_text(json.dumps(report,indent=2)+'\n')
plt.rcParams.update({'figure.facecolor':'#1a1b26','axes.facecolor':'#1a1b26','text.color':'#c0caf5','axes.labelcolor':'#c0caf5','xtick.color':'#c0caf5','ytick.color':'#c0caf5','axes.edgecolor':'#565f89'})
fig,axs=plt.subplots(2,1,figsize=(11,7),layout='constrained')
for a,r,c in zip(curves,results,['#565f89','#9ece6a','#7aa2f7','#f7768e']):
 axs[0].plot(a[:,0]*1e6,a[:,2]-r['battery_V'],color=c,label=r['case'])
 axs[1].plot(a[:,0]*1e6,a[:,2]-r['battery_V'],color=c)
axs[0].set(xlim=(0,650),ylabel='Bridge rail minus battery (V)');axs[1].set(xlim=(8,35),ylabel='Bridge rail minus battery (V)',xlabel='Time (us)')
axs[0].legend(facecolor='#1a1b26',labelcolor='#c0caf5',fontsize=9)
for ax in axs:ax.grid(color='#565f89',alpha=.35)
fig.suptitle('Ceramic reservoir sizing: two synchronized GDT loads\nIllustrative charge-pulse model; DC-bias and lead-inductance sensitivity')
fig.savefig(D/'reservoir-response.png',dpi=160)
print(json.dumps(report,indent=2))
