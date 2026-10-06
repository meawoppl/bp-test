# Command routing and ADC placement — 2026-09-29

This is the current layout checkpoint; the earlier routing milestone documents retain historical measurements. The board remains a two-layer development draft. The authoritative electrical interface is [daughterboard-pinout.csv](daughterboard-pinout.csv), backed by [circuit.json](circuit.json) and native schematic/PCB parity.

## Placement and copper

- Removed J6 and its FAULT_N/FAULT_CLEAR wiring. J1.14 is now unused; J2.33 was subsequently reused for a gate-drive command. Removed ARM indicator D85, its series resistor R805 and input pull-down R821; J2.31 is unused. A subsequent LED simplification removed U80/C80 and all remaining status pull-downs; see [local indicators](INDICATORS.md).
- Removed the old command-gate feeder routes. The eight 33-ohm series resistors and 2.2-kohm pull-downs now form compact pairs at the driver inputs. FPGA fabric owns qualification/blanking. The high-voltage driver outputs remain electrically separate from the FPGA commands.
- Grouped all eight gate commands on consecutive carrier contacts J2.33–J2.40, in physical destination order. The layer-change column moved 11 mm closer to J2, removing the previous out-and-back section and straightening the lower-bank approach. See [measured changes](gate-command-grooming.json). The frozen daughterboard has not changed. Both command banks reach their drivers, and the +12 V branch crosses the lower command bundle once on the opposite layer.
- Moved the complete −5 V charge-pump group into the gap between AUX and CST, preserving the local flying-capacitor loop. Its frame and the neighboring frames now have matching notches.
- Converted R1–R8, R20–R23, C1–C18, C20 and C21 to project-local 0603 footprints and models. Exact new package-specific BOM selections remain a draft/release task; package conversion alone is not a procurement qualification.
- Placed the eight ADC input resistor/capacitor pairs to the left of U1. All eight filter outputs now reach the ADC entirely on F.Cu, removing 16 signal vias. AUX remains CH1–4; CST1 raw/envelope is CH5/CH6 and CST2 raw/envelope is CH7/CH8.
- Moved U2 (AP2112K-3.3) to the ADC frame's lower-right corner, with C20/C21 immediately beside its input/output. Its main 5 V feed follows B.Cu around the input-filter side and bottom of the ADC area. A short F.Cu crossing near the source clears the filtered +5V_ADC distribution. The 3.3 V output returns directly to the existing ADC/digital rail.
- Removed the two intermediate via rows from all ten FPGA/ADC digital links: DOUT A–D, SDI, BUSY, CS, SCLK, RESET and CONVST. Each link now has two endpoint vias instead of four: **20 fewer signal vias**. The long sections stay on B.Cu; equal-width collinear sections were merged. ADC_FIRST subsequently moved to local TP1, removing its long header route and both vias; J7.7 is unused. See [test-point geometry and verification](ADC-FIRST-TESTPOINT.md).
- Follow-up bus grooming: removed the early lateral shifts below J2. All ten B.Cu links run straight down from their connector escape vias to their destination breakouts, then use 45-degree miters. This is a parallel-trunk / delayed-breakout transformation. Five right-hand links are each about 4.97 mm shorter; no contacts or endpoint vias changed. See [before/after lengths](adc-bus-grooming.json).
- CT1_ZERO and CT2_ZERO now run together on B.Cu beside the four GDT2 command traces, at 0.80 mm pitch and a uniform 0.20 mm width. Each has one comparator-side via and one return via beside the FPGA-side command via column; the short front connections preserve J2.22/G0 and J2.24/G1. The +12 V crossing via moved 2 mm left to (118, 119) mm so the rail crosses all six lanes on F.Cu. Component placement, the four command routes and all other copper are unchanged. See [phase-route measurements and verification](phase-route-grooming.json) and the [route overview](ct-zero-backside.png).

- Replaced the buffered top-strip LED bank with eight local indicators: four supply-presence lamps and one directly sensed lamp per bridge leg, each with an individual resistor. Bridge LED reverse clamps protect against negative node excursions. Removed 219 obsolete routing/footprint/text objects, then added the short local connections. Former FPGA LED pins J2.15/16/17/19 are free; gate-command and clock mappings are unchanged. See [indicator circuit and current calculations](INDICATORS.md).

## Revised drive contact map

The latest placement/routing cleanup completes all four CST analog feeds to CH5–8; see [CST routing](CST-ROUTING.md). The main 3V3 ADC feed now uses 0.40 mm F.Cu; its regulator-side transition via and rear diagonal are gone. The comparator 3V3 rail has a separate 0.35 mm F.Cu feed from U2/C21 to the existing R414 supply via. D83/R803 form a horizontal row above-left of U2 with a short front-layer tap.

R513/R514/R509/R510 now form an aligned 2×2 group below U53, matching the input-resistor arrangement below U54. Short 0.20 mm front-layer traces connect the driver pins, series resistors and pull-downs; the two rear-layer command trunks have clean 45-degree approaches. Values and pin assignments are unchanged. The four low-side gate resistor/pull-down pairs (R522/R523, R526/R527, R562/R563, R566/R567) are now parallel horizontal rows. Their pull-down gate pads align with their MOSFET gate pads, removing four routing tails. A disconnected-from-components ground remnant near (126, 92) mm was removed: nine track segments and one via, left over from the earlier command-logic layout. It had been connected only through plane fill. Together with the regulator supply transition, this cleanup removes four vias and adds none, including the subsequently removed two-via hop between the ADC supply pin and C5. The short 0.20 mm ADC escape clears adjacent fine-pitch pins and the DOUT_A via before widening to 0.40 mm. See [cleanup geometry and removed-item record](3v3-front-and-gate-pairs.json).

| Carrier contact | FPGA command |
|---|---|
| J2.37 | GDT1_L_HI |
| J2.38 | GDT1_L_LO |
| J2.39 | GDT1_R_HI |
| J2.40 | GDT1_R_LO |
| J2.33 | GDT2_L_HI |
| J2.34 | GDT2_L_LO |
| J2.35 | GDT2_R_HI |
| J2.36 | GDT2_R_LO |

Firmware constraints must follow the current CSV, not a previous routing document. J2.15/16/17/19, J2.25, J2.30 and J2.31 are NC. J2.33 is now GDT2_L_HI.

## Verification and remaining work

[Native checks](validation.json): ERC 0, schematic parity 0, physical violations 0, dangling tracks 0 and **25 whole-board unconnected items**. The four CST analog handoffs are complete; `routing-intent.json` has no accepted open ends. Remaining work includes regulator internals, ADC reference connections and ESP32/service connections. There is no fabrication-ready claim or new manufacturing package.

The FPGA, H-bridge, power, AUX and CST scoped audits pass. They check required pad connectivity, copper angles, overlapping segments, duplicate UUIDs and via drills over SMD pads. See `*-routing-audit.json`. [Detailed ADC/phase measurements](command-adc-routing-review.json) verify the eight front-layer input routes, 32 converted passive footprints, and the ten digital links' 4-to-2 via reduction. The −5 V converter, driver bypass returns and relocated 3.3 V rail remain connected.

Visual review used native [top-side 3D](floorplan-top.png) and separate F.Cu/B.Cu copper plots. Checked the new U2/C20/C21 grouping, package clearances, outside-pad vias, resistor/capacitor alignment, ADC fanout, paired phase trunks, driver resistor placement, local LED labels and reverse-clamp polarity. No new oblique tracks or same-net overlaps were found by the scoped audits. Decoupler ground vias were retained for short inter-layer returns. Full-board signal integrity, all reference-pin decoupling, final BOM, assembly preview and bench validation remain open.

The [layout-quality report](command-adc-layout-quality.json) is **not green**: 299 error, 2422 warning and 29 informational entries. These are reported findings, not all independently confirmed defects. [Triage by rule](command-adc-quality-triage.md) distinguishes the checked false positives, requested region text and unresolved broader layout/part-selection work. Nothing was hidden by weakening the quality profile or adding DRC exclusions.

## Reproduction

`tools/hardware/tesla_placement.json` and `docs/circuit.json` hold the updated placement/electrical metadata. `tools/hardware/tesla_reviewed_routing.json` stores the reviewed copper and placement snapshot. `tools/hardware/tesla_route_reviewed.py` checks the pin contract and footprint IDs before replaying it, fills zones, and preserves project rules. This supersedes the older incremental routing passes; do not run an old constructor/routing pass over this board.

Regenerate the schematic with `tesla_schematic.py`; validate with `check_tesla_draft.py` and the five scoped routing checks. [3D model audit](3d-model-audit.json) and the carrier contact CSV were regenerated. No fab publish was performed because routing is incomplete.
