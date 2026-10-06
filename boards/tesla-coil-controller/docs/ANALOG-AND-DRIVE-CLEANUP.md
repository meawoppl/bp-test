# Analog feeds and direct FPGA drive — 2026-09-28

> Historical milestone: later placement, package, contact-map and routing changes are documented in [COMMAND-AND-ADC-CLEANUP.md](COMMAND-AND-ADC-CLEANUP.md). Use `circuit.json`, `daughterboard-pinout.csv`, and the latest validation reports for current state.

The analog supply detours and ADC channel order are corrected. The eight FPGA gate commands now reach the half-bridge drivers through their damping resistors, with no intervening AND gates or shared carrier enable path.

## Direct command paths

Removed **U50, U55, C500, C501 and R504**, along with their obsolete supply/enable branches. R505–R508 and R513–R516 remain as 33-ohm series damping resistors. R500–R503 and R509–R512 remain as 2.2-kohm default-off pull-downs. The original driver input interlock and UVLO are intrinsic to the UCC27282; no added enable logic remains.

FPGA fabric must implement enable/blanking, deadtime, current-zero shutdown and volt-second balance. The `*_BUS` nets are the damped driver inputs; the separate `*_LO_DRV` nets remain the 12 V driver outputs. The ARM lamp is now `LED_ARM` on J2.31 and connects only to the indicator buffer and its pull-down. **J6.5 is NC.** The frozen daughterboard is unchanged.

See [OUTPUT-STAGE.md](OUTPUT-STAGE.md) for driver sequencing and the [current contact map](daughterboard-pinout.csv) for FPGA constraints.

## Analog supply cleanup

- R740 (10 ohms) is now at the upper AUX supply entry, with C740 beside its filtered output. This removes the former trip to the bottom of the AUX region and back up to the amplifiers.
- R20 (0 ohms) and C10 now sit beside the ADC supply entry. The ADC/AUX supply joins the nearby horizontal back-layer trunk.
- The CST +5 V feed branches downward from the adjacent AUX clamp-supply bus instead of wrapping around the right side of the ADC.
- All new routing uses 45/90-degree segments. New through-vias are 0.60 mm diameter / 0.30 mm drill and remain outside SMD pads.

Lengths below sum the net's track segments, not one source-to-load path:

| Rail | Before | After | Via count |
|---|---:|---:|---:|
| +5V_ADC | 414.461 mm | 321.126 mm | 23 → 21 |
| +12V_AUX | 106.604 mm | 80.830 mm | 7 → 7 |
| +12V_BIAS | 364.969 mm | 331.262 mm | 6 → 6 |

Measured data: [analog-rail-changes.json](analog-rail-changes.json).

## Revised ADC order

The AUX routes enter the upper four filter rows. The lower four now face the CST circuitry below. All eight RC networks connect through to the ADC; the four CST source handoffs remain deliberately open, as requested during the CST routing pass.

| ADC channel | Signal | Series / shunt | U1 input pin |
|---|---|---|---:|
| 1 | AUX1_BUFFERED | R1 / C11 | 49 |
| 2 | AUX2_BUFFERED | R2 / C12 | 51 |
| 3 | AUX3_BUFFERED | R3 / C13 | 53 |
| 4 | AUX4_BUFFERED | R4 / C14 | 55 |
| 5 | CT1_RAW | R5 / C15 | 57 |
| 6 | CT1_ENVELOPE | R6 / C16 | 59 |
| 7 | CT2_RAW | R7 / C17 | 61 |
| 8 | CT2_ENVELOPE | R8 / C18 | 63 |

Firmware must use this revised order: raw current on CH5/CH7, envelopes on CH6/CH8. Configure the raw inputs for the documented bipolar range and the remaining inputs for 0–5 V. Machine-readable mapping: [adc-channel-map.json](adc-channel-map.json).

## Checks and limits

Native ERC: **0**. Schematic/PCB parity: **0**. Native DRC reports the **four intentional dangling CST handoffs** and **34 unfinished connections** across the draft; no other physical violations. The previous revision had 42 unfinished connections. This is not a fabrication release.

The power, AUX, CST, FPGA and H-bridge connectivity/geometry audits pass. The direct-drive audit explicitly verifies the eight J2 → damping resistor → driver paths, default-off pull-downs, absence of obsolete enable parts/nets, status-only ARM and the NC service contact. All eight ADC RC connections and the revised channel contract are also checked. Whole-board track angles and via-hole/pad overlap checks pass. See [validation.json](validation.json), [aux-routing-audit.json](aux-routing-audit.json), and [hbridge-routing-audit.json](hbridge-routing-audit.json).

The broader plugin quality report remains a draft backlog: 310 errors, 2487 warnings and 29 informational findings. This is not an all-clear quality score. Its six via-in-pad warnings were individually checked against rotated pad geometry and native hole hit tests: none overlap, with minimum hole-to-pad distance 0.225 mm. The four dangling tracks are the intentional CST handoffs. The 21 explanatory text flags correspond to the requested region labels. Remaining silk, decoupling, thermal, power-width and missing-part-number findings still need final review; native DRC does not reproduce the broad silk heuristic count. The quality run preceded only the final NC net-name and presentation-label cleanup; copper geometry is unchanged. Reports: [analog-drive-layout-quality.json](analog-drive-layout-quality.json) and [analog-drive-via-review.json](analog-drive-via-review.json).

Native schematic crops, copper layers and the top 3D view were inspected. The removed gates are absent; the input-filter order and supply entries match the revised intent. Updated full schematic: [controller-schematic.pdf](controller-schematic.pdf).

## Reproducing the current revision

`tools/hardware/tesla_route_reviewed.py` with `tesla_reviewed_routing.json` is the current fixed copper replay. It requires the matching circuit contract, retains the existing zones and board, preserves project settings and does not construct a new board. Two successive replays were byte-identical. The earlier `tesla_route_cst/power/aux/fpga/hbridge.py` scripts and their milestone documents describe historical incremental steps; do not run those over this revision.

Use `tesla_schematic.py` to rebuild the schematic from the circuit contract, then `check_tesla_draft.py` and the scoped routing audits to refresh validation. No new Gerber/BOM/CPL ordering package was issued for this partially routed board.
