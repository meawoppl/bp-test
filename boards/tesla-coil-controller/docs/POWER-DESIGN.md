# Battery distribution and auxiliary supplies

Two 12 V batteries connect separately to J4 (upper) and J30 (lower); pin 1 is positive on both connectors. The PCB links J4.2 to J30.1 on BAT_MID_12V. J4.1 supplies VBAT_24V and J30.2 is board ground. For one 24 V PSU instead, use J4.1 (+) and J30.2 (−) and leave both midpoint terminals unused. J30 is now the lower battery input. VBAT_24V directly supplies both GDT bridges. Gate-drive amplitude follows actual battery voltage; there is no 24 V converter. The earlier LM5116 main converter has been removed. See [series-input verification](series-battery-input-review.txt).

## Implemented auxiliary modules

U30 and U31 are now **TI LMZ14202HTZX/NOPB**, LCSC **C2861493**, using project-local copies of KiCad Texas_NDW-7_TabPin8 footprints and a project-local illustrative TO-PMOD 3D envelope. Both inputs connect independently to VBAT_24V. Neither supply is cascaded through the other.

| Supply | Output | Upper/lower feedback | RON | Output bank |
|---|---|---|---|---|
| U30 | +12V_BIAS, nominal 11.993 V | R300 34k / R301 2.43k | R302 249k | C304–C306: 3 × 47uF/25V X7R |
| U31 | VIN_5V, nominal 4.991 V | R310 34k / R311 6.49k | R312 100k | C314–C316: 3 × 47uF/25V X7R |

Values follow TI Figure 46. Output setpoint is 0.8 × (1 + Rtop/Rbottom). Approximate CCM switching frequencies are 370.5 kHz and 383.9 kHz from Vout/(1.3e-10 × RON). RON connects to VIN, not ground. Each 22nF feed-forward capacitor spans its upper feedback resistor. Each 4.7nF SS capacitor gives nominal 0.47ms soft start.

Pin mapping: 1 VIN, 2 RON, 3 EN, 4 GND, 5 SS, 6 FB, 7 VOUT, 8 exposed ground pad (library pad number). Tie both 4 and 8 to ground. The module contains the switching stage and shielded inductor; it does not contain the required output capacitance.

The 168k/10k input-enable dividers give typical 21.004 V rising and 19.402 V falling using TI's 1.18 V / 1.09 V thresholds. These are nominal thresholds, not tolerance limits. EN is about 2.36 V even at 42 V input, below its 6.5 V recommended maximum. Threshold matching between supplies is not guaranteed: all eight FPGA drive commands must remain low until logic and driver bias are valid. Bias UVLO does not disconnect the battery-fed bridges.

These modules have no PGOOD output. J31 and the old PGOOD pull-ups/nets were removed. No firmware monitoring signal is implied. Module device ratings are up to 2 A and 42 V input; sustained current depends on PCB cooling and temperature. The 12 V and 5 V configurations require at least 15 V and 8 V input respectively under TI's reference conditions, comfortably below the chosen battery UVLO.

## Capacitor and layout qualification

Each input uses two nominal 10uF/50V X7R 1210 capacitors. Select exact parts with at least 10uF combined **effective** capacitance at maximum operating input voltage and temperature, including tolerance. Each output uses three nominal 47uF/25V X7R 1210 capacitors; require at least 47uF effective on the 12 V rail and 100uF on 5 V. Exact capacitor MPNs/DC-bias curves remain unresolved; nominal sums are not validated effective capacitance. Check combined ESR, ripple current, load-step response and startup with all downstream bypass capacitance. TI's reference ESR ranges are 1–75mOhm at 12 V and 1–145mOhm at 5 V.

The old discrete inductors, bootstrap/ripple-injection networks and LM5164 converters are removed. The local input/output loops and feedback routing remain to be routed. Follow TI's exposed-pad copper and thermal recommendations; the standard footprint is not itself thermal qualification. The input capacitors are outside the module courtyards. Component changes were made through the existing generator/contract workflow rather than replacing the full board.

## Battery reservoir and protection

The single 22uF/50V 1812 (C333) that sat beside the reservoir on its own stub was removed on 2026-10-07 as redundant. C335–C342 form an eight-part 22uF/50V X7R 2220 battery reservoir; each bridge has the same bank. These replace all three 470uF electrolytics. See [CERAMIC-RESERVOIRS.md](CERAMIC-RESERVOIRS.md): 176uF nominal per bank is not 470uF effective, and losing can ESR increases hot-plug ringing. Input protection/damping remains a release blocker.

D50/D51 SMBJ30A remain bridge rail clamps. Their specified peak clamp is 48.4 V, which **does not guarantee the new modules remain below 42 V**. Input transient suppression/filtering must be coordinated before energizing the assembly. Input fuse/reverse protection, switching-noise separation from the ADC, rail load budgets and thermal tests remain open. This board is an unrouted circuit/placement draft, not a fabrication release.

## Sources and procurement

- [TI LMZ14202H datasheet](datasheets/LMZ14202H.pdf), [text extraction](datasheets/LMZ14202H.md), Figure 46 and sections 8–10.
- [LCSC C2861493](https://www.lcsc.com/product-detail/C2861493.html): 1,434 units, $10.0338 at one / $8.5952 at ten when checked 2026-09-28. JLC assembly inventory not independently confirmed.
- TRACO TSR modules were considered but not fitted; the 5 V version was out of stock.
- Existing GDT simulations remain idealized nominal 24 V results, not validation of battery-range behavior. See DRIVE-DECISION.md and OUTPUT-STAGE.md.
