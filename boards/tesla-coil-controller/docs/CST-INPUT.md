# Current-sense transformer front end

Implemented schematic and initial unrouted placement, 2026-09-28. This is not a fabrication release. See [schematic](controller-schematic.pdf), [datasheets](datasheets/README.md), and [simulation results](cst/topology-check.json).

## Range and transformer

J40 accepts an isolated CT secondary, dotted end to pin 1, return to pin 2/GND. R400/R401 are two 20 ohm, 1 W, 2512 resistors in parallel: 10 ohms nominal permanent burden. Target ±2 V peak at nominal maximum tank current. For effective current ratio N = primary/secondary, choose N = 5 × primary peak amperes; for example, 1000 A peak calls for 5000:1 effective ratio. This is a scaling example, not a specified maximum tank current. Cascaded CTs may be practical; core material, turns, magnetizing inductance, volt-seconds, bandwidth and burst droop remain to be designed.

At 2 V peak sine, burden power is 0.2 W total during the burst (0.1 W each), multiplied by duty factor for long-term average. Front-end loading makes the effective burden approximately 9.97 ohms at 30 kHz; calibrate the assembled transfer gain. D40 is an SMBJ5.0CA transient clamp, not a precision 5 V limiter: rated pulse clamp can reach 9.2 V. Qualify fault energy and temperature. The board burden cannot protect an unplugged CT: provide a burden/clamp at the transformer if the cable can be disconnected under excitation.

## Three parallel measurement paths

- **Raw ADC:** CT1_RAW through R5/C15 into AD7606C-16 CH5. Configure ±2.5 V range and high analog bandwidth. ±2 V uses 80% of full span; ideal code step is 76.3 microvolts, not a claim of effective resolution.
- **Magnitude ADC:** U40 precision half-wave produces `CT1_HALF = -max(CT1_RAW,0)`. U41 sums raw plus twice the half-wave to produce absolute value. R408/C400 (1 kohm/10 nF) smooth it into CT1_ENVELOPE, then R6/C16 feed CH6 (0–5 V range). This is filtered full-wave magnitude, not peak hold. A steady sine averages to 2/pi times its peak; estimate/average digitally and handle burst transients explicitly.
- **Phase timing:** C425 and the 5k/10k/10k bias network produce approximately `CT1_PHASE = 1.65 V + CT1_RAW/2`. U42 TLV3501 compares against CT1_MID; R416 drives CT1_ZERO to FPGA global input G0, carrier J2.22. C410 is 22 pF EMI filtering. AC coupling prevents the bias network injecting DC into the CT winding. Nominal high-pass time constant is 10 ms. The 2.5 kohm source resistance and 22 pF give 55 ns low-pass delay before clamp/input/parasitic capacitance; comparator offset, internal hysteresis and propagation delay add amplitude-dependent timing error. Calibrate with the actual assembly.

There are now two independent instances of this front end. J40 feeds CT1_RAW / CT1_ENVELOPE into ADC CH5/CH6; J60 feeds CT2_RAW / CT2_ENVELOPE into CH7/CH8. The second instance uses U60/U61/U62, L60, R600-series and C600-series components with the same values and topology. Its local phase midpoint is CT2_MID; neither sensor signal is tied to the other.

J3/J8/J9/J10 are separate two-pin JST PH AUX1–4 inputs (signal and GND), mapped to ADC CH1–4. They feed four unity-gain OPA197 buffers with input RC/clamps and ADC-side filtering; see [AUX-INPUTS.md](AUX-INPUTS.md). They accept 0–5 V signals, not bare CT secondaries. CST monitor outputs remain at TP40–43 and TP60–63.

The first phase edge uses carrier J2.22 / FPGA IOT_46B_G0; the second uses J2.24 / IOT_45A_G1. J2.33 / IOT_44B now carries GDT2_L_HI; J6 and its former FAULT_N service net are removed. EXT_CLOCK remains on J2.32 / IOB_3B_G6. The frozen daughterboard is unchanged; see daughterboard-pinout.csv for carrier assignments.

U44 is shared and placed between the two front ends. Eight OPA197 amplifiers (four rectifiers plus four AUX followers) draw about 8 mA typical quiescent current, or 10.4 mA using 1.3 mA each, before dynamic loading. Reserve at least 20 mA provisionally against the TPS60403 60 mA rating; the 10-ohm filter drops 0.2 V at 20 mA. Ripple, temperature and signal-dependent loading still need qualification; see AUX-INPUTS.md.

## ADC-owned overcurrent detection

The separate U43 window comparator, U45 NOR, threshold ladder and J41 trip output are removed by design. The FPGA uses raw CH5/CH7 samples for overcurrent decisions and CT1_ZERO / CT2_ZERO for phase/selected zero-current shutdown. CH6/CH8 are the filtered magnitude paths, not the preferred fast trip source. At 200 kSPS, sampling alone contributes up to 5 us detection latency, followed by conversion, readout and FPGA pipeline latency. Firmware must bound this total and handle missing samples/phase edges.

Wait at least 100 ms after stable analog rails before arming so the phase-path AC bias settles. See [OUTPUT-STAGE.md](OUTPUT-STAGE.md) for drive states and sequencing. There is no independent analog overcurrent latch.

## Supply and test access

U44 TPS60403 generates a negative rail from +5V_ADC; R421/C423 filter it for the two OPA197 rectifiers. The timing comparator operates from 3.3 V independently of this charge pump. Local bypass capacitors are included. TP40–TP43 expose raw, half-wave, absolute and filtered magnitude.

## Simulation evidence

Run `python3 tools/hardware/check_tesla_cst.py`. The committed ngspice topology deck and results are under `docs/cst/`. Generic 10 MHz op amps with clipped ±4.5 V output and generic fast diodes test topology; these are not vendor macro-models. Slew limiting, noise, temperature, supply startup and CT magnetics are absent.

At 30 kHz and 2 V peak, filtered mean is 1.269776 V versus 1.273240 V ideal (−0.272%). Filtered ripple is 1.032–1.484 V. At 0.1 V peak, mean error is −2.60%. There are simulated zero-crossing glitches before the smoothing filter. Do not infer final accuracy or stability from these results. Vendor-model and bench checks, fault-clamp tests, anti-alias analysis and phase calibration remain.

## Release gates

Complete routing and return paths; select exact passives and qualify component availability; resolve D41/D42 manufacturer datasheet against their final ordering code; validate CT magnetics and all protection behavior; qualify the GDT stage and FPGA shutdown timing. The supplied Diodes Incorporated 1N4148W document is not the exact Nexperia ordering-code datasheet currently in the draft.

## UD3-inspired CT cable filtering — 2026-09-28

J40 now carries CT1_CABLE_P and CT1_CABLE_N; **neither cable contact is directly tied to board ground**. Both pass through L40, TAI-TECH WCM4532F2SF-900T20 (LCSC C357325): 90 ohms common-mode impedance at 100 MHz, 2 A rated, 50 milliohms maximum DCR per winding. At nominal 0.2 A peak CT secondary current there is ample rated-current margin. The manufacturer's PDF and Markdown are stored in datasheets/. Observed LCSC listing: 1825 pieces, $0.2009 at 5+, 2026-09-28; recheck PCBA availability before ordering.

- L40 winding 1→2: CT1_CABLE_P → CT1_RAW.
- L40 winding 4→3: CT1_CABLE_N → analog ground. Dots are at cable-side pins 1 and 4, so differential CT current cancels magnetizing flux.
- C427/C428: matched 150 pF, 50 V C0G, 0805 from each **cable-side** conductor to ground. Position side-by-side with short equal return paths at the connector. This placement is deliberate: the filtered return is grounded, so putting its shunt capacitor after the choke would be redundant.
- C429: 1 nF, 50 V C0G, 0805 across CT1_RAW and ground, adjacent to the permanent 10-ohm burden. R400/R401 and D40 remain permanently connected; there is no burden switch or jumper.
- Route both conductors as a tight pair through the choke. Ground only on its circuit side; do not bypass the return winding with a connector ground trace or cable shield. This is an EMI filter, not a safety isolation component.

The project-local footprint uses the manufacturer's 4.8 × 3.8 mm recommended land envelope: four 1.15 × 1.55 mm pads centered at x=±1.825 and y=±1.125 mm. Numbering viewed from top: 1 upper-left, 2 upper-right, 3 lower-right, 4 lower-left. Its 3D model is an illustrative 4.5 × 3.2 × 2.8 mm envelope, not manufacturer CAD.

`python3 tools/hardware/check_tesla_ud3.py` verifies independent drive net paths and this filter topology, then plots a small-signal differential model. The model uses an ideal current-source CT, maximum winding DCR and assumed total differential leakage of 0, 0.2 and 2 uH. At 30 kHz it predicts about -0.1243 degrees / 11.5 ns added phase delay with essentially unity gain relative to the 10-ohm burden. See cst/cable-filter-results.json and cst/cable-filter-response.png. These numbers exclude TVS capacitance, actual cable/transformer parasitics and nonlinear core behavior; the sweep is not a common-mode attenuation qualification. Measure the assembled input's amplitude/phase response and noise immunity. It is not an anti-alias filter for 1 MSPS acquisition.

Reference: UD3.1 Analog IO schematic, https://github.com/TMaxElectronics/UD3.1/blob/master/Schematic%2BBoard.PDF . Our bipolar burden and active rectifier remain; this borrows the cable-filter concept without substituting UD3's current rectifier topology.
