#!/usr/bin/env python3
"""Build the documented Tesla controller subsystem map (no external dependencies)."""
from pathlib import Path
from html import escape
D=Path(__file__).resolve().parents[2]/'boards/tesla-coil-controller/docs'
out=['<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="1190" viewBox="0 0 1440 1190"><rect width="1440" height="1190" fill="#1a1b26"/><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10z" fill="#c0caf5"/></marker></defs><g font-family="DejaVu Sans, sans-serif">']
def text(x,y,s,size=16,color='#c0caf5'):
 out.append(f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}">{escape(s)}</text>')
def box(x,y,w,h,title,lines,color='#7aa2f7',planned=False):
 dash=' stroke-dasharray="8 5"' if planned else ''
 out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="#24283b" stroke="{color}" stroke-width="2"{dash}/>')
 text(x+14,y+27,title,18,color)
 for i,line in enumerate(lines):text(x+14,y+53+22*i,line,14)
def arrow(points,label=None,lx=0,ly=0):
 out.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in points)+'" fill="none" stroke="#c0caf5" stroke-width="2" marker-end="url(#arrow)"/>')
 if label:text(lx,ly,label,13,'#7dcfff')
text(35,44,'Tesla coil controller · subsystem map',29)
text(35,74,'Solid: present in schematic   •   Dashed: planned circuitry or external hardware',16)
text(35,101,'Design draft — partly routed; power values and protection remain to be validated.',14,'#e0af68')
text(35,144,'POWER DOMAINS',19,'#e0af68')
box(35,165,220,110,'24 V nominal battery pair',['J4 + J30 • one 12 V each','Input fuse / reverse / surge','protection still pending'],'#e0af68')
box(310,165,245,110,'12 V bias module',['U30 • LMZ14202H','Bias for GDT gate drivers','UVLO ≈21 V on / 19.4 V off'],'#e0af68')
box(610,165,245,110,'5 V logic module',['U31 • LMZ14202H','Daughterboard + ADC AVCC','Independent battery input'],'#e0af68')
box(910,165,280,110,'3.3 V logic',['U2 • AP2112K','ADC VDRIVE / logic interfaces','Daughterboard: local rails'],'#e0af68')
arrow([(255,215),(310,215)]);arrow([(145,165),(145,130),(730,130),(730,165)],'battery DC',565,120);arrow([(855,215),(910,215)])
box(310,315,545,105,'Direct battery distribution',['No main buck • C335–C342 ceramic bank','Single 24 V PSU: + to J4.1, − to J30.2; midpoint unused'],'#e0af68')
arrow([(145,275),(145,365),(310,365)],'battery DC',170,351)
arrow([(530,275),(530,295),(1050,295),(1050,315)],'12 V bias',710,290)
box(910,315,280,105,'Two GDT primary drivers',['4 × UCC27282 / 8 × STD80N10F7','2.2 uF + 15R/1uF per channel','24 V bridges / 12 V gate bias'],'#e0af68')
arrow([(855,367),(910,367)],'VBAT',862,353)
text(35,468,'MEASUREMENT AND REAL-TIME CONTROL',19,'#7dcfff')
box(35,495,245,95,'Two CST inputs',['10 ohm burden + TVS clamp','Target ±2 V; select CT ratio'],'#7dcfff')
box(35,625,245,95,'Raw / envelope paths',['Raw currents → CH5 / CH7','Magnitudes → CH6 / CH8'],'#7dcfff')
box(35,755,245,90,'Zero-cross comparator',['2 × TLV3501 → CT1_ZERO / CT2_ZERO','Separate from sampled path'],'#7dcfff')
box(340,545,280,135,'8-channel simultaneous ADC',['U1 • AD7606C-16','200 kSPS initial target','CH1–4: four auxiliary 0–5 V inputs','100R / 1nF input EMI RC'],'#7dcfff')
box(340,730,280,110,'Auxiliary instrumentation',['Four unity-buffered 0–5 V inputs','Common conversion instant','Anti-alias design still required'],'#7dcfff')
box(700,510,300,180,'Daughterboard FPGA',['iCE40UP5K • 3.3 V I/O','4 × ADC data + BUSY / CONVST','Phase / amplitude estimation','Digital phase lead + drive timing','8 direct commands; enable in fabric'],'#bb9af7')
box(700,755,300,110,'Daughterboard ESP32-S2',['USB / Wi-Fi configuration','Supervision and telemetry','Module link / service signals'],'#9ece6a')
box(1070,530,330,145,'Direct FPGA drive interface',['33R damping + 2.2k pull-downs','Driver input interlock + UVLO','Overcurrent: ADC → FPGA','FPGA inserts timed deadtime'],'#f7768e')
box(1070,735,330,105,'External bridge / coil',['2 × existing 1:1 GDTs','8 × CM600HA: 2 per switch','Four-switch H-bridge'],'#e0af68',True)
arrow([(155,590),(155,625)])
arrow([(280,670),(310,670),(310,595),(340,595)],'CH5–8',283,582)
arrow([(480,730),(480,680)])
arrow([(280,555),(300,555),(300,800),(280,800)])
arrow([(280,800),(320,800),(320,885),(655,885),(655,650),(700,650)],'Phase edges → FPGA globals G0 / G1',335,907)
arrow([(620,600),(700,600)],'4 lanes',630,585)
arrow([(850,690),(850,755)],'module comms',863,721)
arrow([(825,755),(825,690)])
arrow([(1000,565),(1070,565)],'drive',1005,548)

arrow([(1235,530),(1235,367),(1190,367)],'8 gate commands',1250,472)
arrow([(1190,395),(1370,395),(1370,710),(1235,710),(1235,735)],'isolated gate drive',1192,719)
text(35,969,'OPERATING FLOW',19,'#7aa2f7')
text(35,1004,'1. Apply DC → bias and logic rails start; GDT power is direct; gate drivers require valid bias.',17)
text(35,1037,'2. Configure ADC and FPGA; qualify samples and phase edges; precharge bootstrap supplies.',17)
text(35,1070,'3. FPGA measures CT phase/amplitude and schedules drive; ADC overcurrent requests a current-zero burst ending.',17)
text(35,1113,'Schematic implemented; routing and actual GDT/load qualification are pending.',16,'#f7768e')
text(35,1145,'GDT secondary destinations/polarities and per-device gate networks still require confirmation.',15,'#565f89')
out.append('</g></svg>');(D/'subsystems.svg').write_text('\n'.join(out))
