# Local power and bridge-leg indicators

The octal buffer U80, C80 and R820/R822/R823/R824 are removed. There are no READY, ACTIVE, ARM or FAULT lamps, no `LED_BUF_*` circuit nets, and no FPGA-generated LED signals. Carrier J2.15, J2.16, J2.17 and J2.19 are now unused; the frozen module pinout is unchanged.

Eight green KT-0805G (C2297) lamps each have an individual 0805 series resistor. Rail lamps sit by the supply they indicate; two switching-node lamps sit above the corresponding drivers in each GDT section. All labels are next to the lamps, outside component bodies.

| Label | LED / resistor | Sensed net | Series resistance | Placement |
|---|---|---|---|---|
| BAT | D80 / R800 | VBAT_24V | 12k | Beside J4 battery input |
| 12V | D81 / R801 | +12V_BIAS | 5.1k | Beside U30 output |
| 5V | D82 / R802 | VIN_5V | 1.5k | Beside U31 output |
| 3V3 | D83 / R803 | +3V3 | 680R | Above-left of U2, clear of the 3V3 trunk |
| GDT1 L | D84 / R804 | GDT1_L_SW | 12k | Above U51 |
| GDT1 R | D86 / R806 | GDT1_R_SW | 12k | Above U52 |
| GDT2 L | D87 / R807 | GDT2_L_SW | 12k | Above U53 |
| GDT2 R | D88 / R808 | GDT2_R_SW | 12k | Above U54 |

Each bridge lamp senses the actual MOSFET half-bridge midpoint, not a gate-drive command or a gate pin. A 1N4148W,115 antiparallel diode (D90–D93) clamps reverse voltage across that LED: diode cathode to LED anode, diode anode to GND. The 12k resistor is upstream of both devices, so negative excursions are current-limited too. The four repeated circuits use the existing project-local SOD-123 diode footprint/model and component already used in the CST rectifiers. Its exact procurement code remains part of the draft BOM work.

At a representative 2.0 V green LED drop, the 24 V bridge/battery branches draw about 1.83 mA while high; the 12 V, 5 V and 3.3 V rail indicators draw about 1.96, 2.0 and 1.91 mA. Actual forward voltage and brightness vary. A 12k resistor dissipates about 40 mW at 24 V or 65 mW at 30 V with a 2 V LED drop. Use 0805 resistors rated at least 0.125 W, with normal thermal derating. These are visual rail/node-presence indicators, not precision voltage thresholds.

Brightness follows positive switching-node duty cycle and burst duty. Both leg lamps can illuminate when both bridge outputs are high even though the transformer sees zero differential voltage. A lit lamp therefore does not establish successful firing, output current, correct deadtime, or a fault state. No firmware pulse stretching or dedicated FPGA LED outputs are needed.

The former top-strip signal and power branches have been ripped up. New local resistor/LED/clamp wiring is on F.Cu. Ground pads connect thermally to the filled ground plane. D83 and R803 now form a horizontal row above-left of U2, with the LED farther left and the resistor next to the supply trunk. A short front-layer branch feeds the pair; its GND pad uses the front-plane thermal relief. Both the lamp connection and the main regulator-to-ADC feed now stay on F.Cu. The former regulator supply via is removed. Existing GDT power copper and command pin assignments are preserved. The board remains a development draft with unrelated routing unfinished.

## External clock header

`EXT_CLOCK` is a separate optional 3.3 V logic timing input from service header J7.8 through carrier J2.32 to the module FPGA's `FPGA_IOB_3B_G6` global-clock-capable input. It is not an oscillator, LED output or gate-driver output. Leave J7.8 open when no external reference is used; select/disable the input in FPGA fabric as appropriate. Its mapping is unchanged by this LED revision.
