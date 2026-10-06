# Dual GDT output stage — 2026-09-28 development design

Current cleanup: [COMMAND-AND-ADC-CLEANUP.md](COMMAND-AND-ADC-CLEANUP.md); preceding bridge milestone: [HBRIDGE-ROUTING.md](HBRIDGE-ROUTING.md). Earlier placement/unrouted remarks below are historical design checkpoints; the circuit and validation files describe the current board.

Two identical 24 V full bridges drive the two existing 1:1 gate-drive transformers. This preserves UD2.7's differential primary excitation, ceramic DC block, local reservoir and damping. Four modern bootstrap half-bridge drivers replace the older complementary MOSFET/predriver arrangement. The existing **12 V bias** powers the drivers; **24 V** powers the bridges. **No 9 V rail.** Each bridge now receives four independent FPGA commands (eight total). FPGA commands now feed the driver inputs directly through 33-ohm damping resistors, with 2.2-kohm default-off pull-downs. U50/U55 and their shared ARM gate have been removed; enable/blanking is implemented in FPGA fabric. The ARM indicator and J6 service header are removed. External winding assignments and polarities must map these independently controlled channels to the intended coil-bridge legs.

## Selected active parts and procurement evidence

| Function | Part / package | LCSC | Evidence observed 2026-09-28 |
|---|---|---|---|
| Four half-bridge gate drivers | TI UCC27282DR / SOIC-8 | C2867844 | LCSC page 524 in stock |
| Eight bridge MOSFETs | ST STD80N10F7 / DPAK | C2832811 | LCSC search snapshot 2683; older crawl, recheck before order |
| Two main DC-block capacitors | TDK C3225X7R1H225KT000N / 2.2 uF 50 V X7R 1210 | C76683 | Original UD2.7 value/family; availability recheck before order |
| Two damping capacitors | KEMET C1206C105K5RACTU / 1 uF 50 V X7R 1206 | C2167287 | Exact original UD2.7 BOM part |

Sources: [driver](https://www.lcsc.com/product-detail/C2867844.html), [MOSFET](https://www.lcsc.com/product-detail/C2832811.html), [2.2 uF ceramic](https://www.lcsc.com/product-detail/C76683.html), [1 uF ceramic](https://www.lcsc.com/product-detail/C2167287.html). Availability is not reserved inventory or confirmation of economic PCBA eligibility. Manufacturer PDFs and Markdown extractions are in datasheets/.

UCC27282DR pinout: 1 VDD, 2 HB, 3 HO, 4 HS, 5 HI, 6 LI, 7 VSS, 8 LO. **This SOIC version has no enable pin**; there is no separate hardware ARM input; FPGA fabric owns output enable. It has an internal bootstrap diode and input interlock: HI=LI=1 forces both gate outputs low. It does **not** generate timed deadtime. STD80N10F7 pins are 1 gate, 2/tab drain, 3 source; 100 V VDS and 10 milliohm maximum RDS(on) at the stated datasheet test condition. Gate charge is approximately 45 nC at the stated 10 V test condition; re-evaluate at our 12 V drive.

## Per-channel circuit

- Two half bridges, each with 1 uF/25 V X7R bootstrap, 100 nF + 4.7 uF local 12 V bypass, 4.7-ohm gate resistors and 10k gate-source resistors.
- Eight parallel 22uF/50V X7R 2220 MLCCs per bridge, plus existing 2.2uF and 100nF local bypass and SMBJ30A. C526/C531–C537 and C566/C571–C577 use TDK CGA9P3X7R1H226MT0Y0N (C49297044). Each bank is 176uF nominal; see [CERAMIC-RESERVOIRS.md](CERAMIC-RESERVOIRS.md) for effective-capacitance sensitivity, ripple and input-damping gates.
- **Original UD2.7 network:** C529/C569 are 2.2 uF/50 V X7R 1210 in series with each GDT primary. A parallel branch of R529/R569 (15 ohms, 1 W 2512) and C530/C570 (1 uF/50 V X7R 1206) damps the network without passing sustained DC. The two capacitors are NOT simply parallel.
- Removed the two 10 uF film capacitors per channel, the separate 0.47-ohm series resistor, and the 10-ohm/1 nF output snubber. No film capacitors remain in the output stage.
- Reference evidence: [original schematic image](gdt/UD27-original-output.png), [original Rev C BOM](datasheets/UD27C-original-BOM.pdf), and [Loneoceans gate-driver explanation](https://www.loneoceans.com/labs/ud27/). Original references C21/C30 = 2.2 uF 50 V 1210; C24/C31 = 1 uF 50 V 1206. The separate through-hole redraw labels the main capacitor 22 uF; this design intentionally follows the original schematic/BOM/explanation instead.
- MLCC capacitance is voltage/temperature dependent; 2.2 uF and 1 uF are nominal values, not guaranteed in-circuit effective capacitance. Final AC-current/self-heating, pulse duty and DC-bias curves remain bench/part qualification items.
- J50/J51 pin 1 is the capacitor-coupled output; pin 2 is the right-hand switch node. **Neither output terminal is ground.**

## FPGA interface and sequencing

| Carrier contact | Net |
|---|---|
| J2.37 | GDT1_L_HI |
| J2.38 | GDT1_L_LO |
| J2.39 | GDT1_R_HI |
| J2.40 | GDT1_R_LO |
| J2.33 | GDT2_L_HI |
| J2.34 | GDT2_L_LO |
| J2.35 | GDT2_R_HI |
| J2.36 | GDT2_R_LO |
| J2.31 | Unused (former ARM status) |
| J2.22 | CT1_ZERO, module global clock input G0 |

GDT1 drives J50; GDT2 drives J51. J6 is removed; the complete command interface is the daughterboard connector. J2.36–39 were unused GPIOs, not ground or module-reserved contacts. The same per-bridge state table below applies independently to each bank. Separate commands enable phase/pulse-skipping strategies; HDL must still guarantee safe coil-leg commutation and transformer flux balance. Do not assume the two physical GDTs are interchangeable redundant outputs.

These contact assignments preserve the frozen module pinout; the updated mapping is in daughterboard-pinout.csv. The former ARM_REQUEST and WATCHDOG functions are removed; J1.13/J1.14 and J2.25/J2.30/J2.31 are unused. There is no separate hardware watchdog or analog overcurrent latch. The former FAULT_N/FAULT_CLEAR service contacts were removed with J6.

| FPGA-commanded state | L_HI | L_LO | R_HI | R_LO |
|---|---:|---:|---:|---:|
| Bootstrap precharge / zero-voltage hold | 0 | 1 | 0 | 1 |
| Positive drive | 1 | 0 | 0 | 1 |
| Negative drive | 0 | 1 | 1 | 0 |
| All switches off | 0 | 0 | 0 | 0 |

The command pull-downs are 2.2k rather than 10k to dominate weak configuration pull-ups; at 128 uA they develop only 0.282 V. The MOSFET gate-source resistors remain 10k.

1. Default all commands low; 2.2k command pull-downs enforce this with the module absent/reset. Qualify rails and ADC configuration; allow the phase bias to settle (initial 100 ms).
2. With highs low, assert both lows to precharge bootstrap capacitors. Initial 100 us precharge is a bench-check starting point, not a measured requirement.
3. Insert deadtime before enabling each opposite device; initial 100–200 ns requires checking driver delays, MOSFET turnoff and the actual layout. Keep positive/negative volt-seconds balanced and bound each high-side on-time. Bootstrap drivers cannot sustain arbitrary static high-side ON.
4. FPGA detects overcurrent from raw ADC CH5 or CH7, then schedules the selected current-zero burst termination. At 200 kSPS the sample phase alone adds up to 5 us; include conversion, serial readout, logic, phase prediction and zero-wait in the latency budget. Do not use the slower envelope as the only current limit.
5. Transition to an appropriate zero-voltage hold, allow gate/transformer energy to decay, then command all outputs low in the FPGA. The actual IGBT commutation and emergency-stop behavior need measurement; all-off and low-side hold are electrically different states. Missing ADC data/phase edges and excessive pulse duration require explicit FPGA behavior and intentional rearm.

## Calculations and simulations

`python3 tools/hardware/check_tesla_output.py` runs ngspice; topology, numeric results and plotted traces are in gdt/. The model now matches the original UD2.7 network: **2.2 uF in parallel with a series 15-ohm/1 uF branch**, all in series with the GDT. It applies eight cycles at 30 kHz from an ideal +/-24 V bridge with 0.15-ohm wiring, 1 mH magnetizing inductance, and varied leakage/reflected gate capacitance. Nominal 0.8 uF approximates four devices × 3 uC / 15 V, not a measured +/-24 V gate-charge curve. Individual gate resistors are modeled as 5.1 ohms per device (1.275 ohms reflected equivalent).

Nominal result: 21.89 A peak primary current, 5.06 A RMS during the burst, gate-equivalent swing -20.91 to +20.19 V, 9.47 V peak across the DC block. Damping dissipation is 1.99 W during the nominal burst, 5.39 W in the heavy-load case, before burst-duty scaling. The 1 W resistor is not a continuous-drive rating; verify pulse energy and repetition rate. These are illustrative results, not measured GDT/IGBT waveforms. The smaller capacitor causes more droop under the assumed heavy reflected gate load. MLCC nonlinearity and self-heating are not modeled.

Earlier 20 uF film-bank results are retained only under gdt/superseded-film/ and do not describe the current circuit.

Bootstrap droop estimate: 45 nC / 1 uF = 45 mV from gate charge alone; driver quiescent current, leakage and effective capacitance under bias add to this. Approximate gate-drive power for eight MOSFETs is 8 × 45 nC × 12 V × 30 kHz = 0.13 W, excluding quiescent and switching losses. The high GDT current pulses come from the 24 V local reservoir, not the logic rail.

The model excludes nonlinear Miller behavior, IGBT collector current/tail, core saturation, exact coupled windings, driver/MOSFET macromodels and most layout parasitics. It does not validate zero-current switching, usable burst duty, supply sizing or final snubber values. Core volt-seconds and measured gate voltages on all eight devices remain required.

## Status

Native schematic, project-local libraries, daughterboard mapping and an initial unrouted floorplan are implemented. The separate 17-part analog overcurrent section is removed. ERC and schematic/PCB parity are checked; no fabrication release or routed-board claim is made. Next work is ceramic and damping pulse qualification with actual GDT/burst requirements, routing the high-current loops, and bench validation. Existing input fuse/reverse/transient protection is also unfinished.

Battery update: the bridge rail is now VBAT_24V directly from two series 12 V car batteries. It is not regulated. Existing 24 V simulations remain nominal-point simulations, not qualification over the battery voltage range.

## Compact PCB update

The board is now 188 × 160 mm. Each bridge has four reservoir capacitors above and four below its MOSFETs, all on the component face. Low-side MOSFETs have been rotated so their drains face the high-side source path. Local switch-node and main output links are 2.5 mm F.Cu with no vias; the damping branch is 1 mm. These are partial routes only: driver/gate/bootstrap, reservoir, battery and ground return circuits are not completed. See FLOORPLAN.md and output-copper.json.

Horizontal compaction: the half-bridge pitch is now 18 mm instead of 24 mm. Left-hand MOSFETs, drivers, control support and reservoir capacitors moved 6 mm toward the right-hand leg. Output terminals stay at the board edge; the long switch-node runs are 6 mm shorter. Local 12 V capacitors were relocated into the remaining central clearance.

Vertical compaction: D50/D51 (SMBJ30A) now sit beside the upper reservoir rows at the right edge. GDT 2 and its control parts moved up 18 mm, reducing channel pitch from 73 to 55 mm. The four-above/four-below reservoir arrangement is preserved; local output copper follows the moved stage. Native checks pass with the existing 499 open connections still pending routing.

The two complete placement groups and their local output tracks were translated 28 mm right and 30 mm down to form a separate output column. Internal relative geometry and trace lengths are unchanged.
