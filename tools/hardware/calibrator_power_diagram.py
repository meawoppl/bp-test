#!/usr/bin/env python3
"""Power architecture diagram; detailed sequencing/limits in docs/power-control.md."""
from pathlib import Path
from html import escape
out=Path(__file__).resolve().parents[2]/'boards/gps-time-calibrator/docs/diagrams/power-domains.svg'
s=['<svg xmlns="http://www.w3.org/2000/svg" width="900" height="1040" viewBox="0 0 900 1040">','<rect width="900" height="1040" fill="#1a1b26"/>','<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#7aa2f7"/></marker></defs>']
def text(x,y,t,size=17,color='#c0caf5'):s.append(f'<text x="{x}" y="{y}" font-family="sans-serif" font-size="{size}" fill="{color}">{escape(t)}</text>')
def box(x,y,w,h,title,lines,color='#7aa2f7'):
 s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="#24283b" stroke="{color}" stroke-width="2"/>');text(x+15,y+28,title,19,color)
 for i,l in enumerate(lines):text(x+15,y+55+24*i,l,15)
def arrow(points):s.append(f'<polyline points="{points}" fill="none" stroke="#7aa2f7" stroke-width="2.5" marker-end="url(#arrow)"/>')
text(35,40,'GPS calibrator — power and control',27)
text(35,69,'5 V-only USB-PD sink · firmware must never request higher voltage',16,'#a9b1d6')
box(300,95,300,80,'USB-C J3',['USB_VBUS (always on)']);arrow('450,175 450,205 230,205 230,230');arrow('450,175 450,205 685,205 685,230')
box(35,230,400,130,'Always-on controller domain',['Daughterboard → onboard 3.3 V / FPGA rails','U2 → +3V3_LOGIC: OLED and LED buffers','U12 → +3V3_CC: I²C pull-ups'],'#9ece6a')
box(500,230,365,130,'HUSB238 U11',['SDA → GPIO7 / SCL → GPIO8','I²C address 0x08; read source/contract','VSET = GND (5 V); ISET = 22.6k (3 A)'])
arrow('685,360 685,391 230,391 230,420')
box(35,420,400,130,'ESP32 firmware policy',['Read contract and honor USB power limits','GPIO4 → main eFuse enable','GPIO5 → OCXO enable; GPIO6 → GPS enable'],'#bb9af7')
box(500,420,365,130,'TPS259531 eFuse U14',['USB_VBUS → switched VIN_5V','GPIO4 + 100k pull-down; defaults OFF','~2.48 A current limit / ~12 ms ramp'])
arrow('435,480 500,480');arrow('685,550 685,580 450,580 450,610')
box(35,610,255,150,'5 V switched loads',['LED anodes / 16 columns','Trigger comparator','5 V trigger output buffer'],'#e0af68')
box(315,610,270,150,'GPS subsystem',['U5 AP2112 + GPIO6','+3V3_GPS → GNSS / bias','Also U7 trigger translator'],'#e0af68')
box(610,610,255,150,'OCXO subsystem',['U15 TPS7A4533 + GPIO5','3.3 V linear → Y1','2.1 W max warm-up','~1.1 W LDO loss at 5 V'],'#e0af68')
arrow('450,580 162,580 162,610');arrow('450,580 737,580 737,610')
box(35,805,830,100,'Current telemetry',['U14 ILM → R176 100k → GPIO3 / ADC1_CH2; C78 100nF to GND','Nominal 0.22632 V/A · ~10 ms filter · excludes always-on loads · calibrate'],'#7dcfff')
text(35,946,'Boot: keep enables low → check budget → enable 5 V → GPS / OCXO → await warm-up.',16)
text(35,975,'Top copper moat confines the local heat spreader; inner ground stays continuous.',16)
text(35,1004,'Thermal behavior, USB load budget and absolute timing still require prototype measurements.',15,'#e0af68')
s.append('</svg>');out.parent.mkdir(exist_ok=True);out.write_text('\n'.join(s)+'\n');print(out)
