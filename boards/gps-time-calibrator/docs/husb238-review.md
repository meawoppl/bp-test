# HUSB238 replacement review

U11 now HUSB238_002DD/C7471904. Hardware VSET grounded: 5 V only. R164 22.6k programs a 3 A request; actual available current must be checked over I²C. GPIO7 = SDA, GPIO8 = SCL, address 0x08. Existing 10k pullups use always-on +3V3_CC. Firmware must never override to a higher voltage. USB data bypasses the unused BC1.2 pins; GATE is unused. TPS259531 and its filtered current-mirror ADC circuit remain unchanged.

C64 upgraded to 1uF/50V X7R 0805. R165/R166 and the obsolete VBUS detection chain removed. Package pin mapping checked against the Hynetek datasheet; local footprint based on KiCad's DFN 3x3mm, 0.5mm pitch, 1.8x2.5mm EP. 3D envelope is drawing-derived, not vendor CAD.

CC1 was completely removed and rerouted using short front escapes plus a straight/45-degree back-layer route, with two vias total. Antenna-bias R5/C10/L1 were aligned into vertical runs; the feed from U6 has been moved outward from the other pads. The main GNSS RF feed remains unchanged.

29 visible exterior pin-1 silk dots cover all 13 ICs and 16 MOSFETs. Board-level graphics deliberately avoid changing shared library geometry. Marker coordinates and pad-1 associations are recorded in pin1-markers.json. Passives have no new orientation dots.

JLC preview corrections are saved by LCSC part in jlcpcb-placement-offsets.json: U7/U10 and Q1–Q16 +180 degrees; U15 -90 degrees. These change only the CPL, not PCB orientation. Review new U11 orientation against the new pin-1 marker in the assembler preview.

TP10/11 now identify PD_SDA/PD_SCL. OLED probe labels were corrected: GPIO2 = OLED_SCL, GPIO1 = OLED_SDA; wiring unchanged.

Native DRC/ERC/parity and probe-access/via-pad audits are rerun before publishing. These checks do not qualify USB behavior, RF, heat or timing; prototype measurements and the firmware power-sequencing contract remain required.

Trigger fanout cleanup: R81/ESP branch above R80/FPGA branch; the single common TRIG_3V3 point remains (redundant ESP/FPGA-side points removed). Two parallel inner-layer runs approach the module without the former folded-back branch. U7 feeds a straight common spine, and the GNSS branch leaves south from its bottom. Electrical destinations remain unchanged.

R164 purchasing substitution (2026-09-27): VO SCR0805F22K6 / C3016901 replaces unavailable C17554. Same 22.6 kOhm, 1%, 0805, 125 mW rating; no placement, routing or current-selection change. HUSB238 Table 6 assigns 22.6 kOhm to 3 A. At the 105 uA maximum setting current, dissipation is approximately 0.25 mW. JLC listing supports Economic and Standard assembly: https://jlcpcb.com/partdetail/VO-SCR0805F22K6/C3016901 . LCSC listed 4300 units when checked: https://www.lcsc.com/product-detail/C3016901.html .
