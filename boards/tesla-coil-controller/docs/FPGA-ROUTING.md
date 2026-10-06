# FPGA data and control routing

> The latest J2 remap is recorded in [fpga-remux-review.txt](fpga-remux-review.txt), with current assignments in [daughterboard-pinout.csv](daughterboard-pinout.csv) and [tesla-controller.pcf](integration/tesla-controller.pcf).

> Historical milestone: later placement, package, contact-map and routing changes are documented in [COMMAND-AND-ADC-CLEANUP.md](COMMAND-AND-ADC-CLEANUP.md). Use `circuit.json`, `daughterboard-pinout.csv`, and the latest validation reports for current state.

> Historical milestone. The current analog routing/channel swap and removal of command-enable gates are described in [ANALOG-AND-DRIVE-CLEANUP.md](ANALOG-AND-DRIVE-CLEANUP.md). Counts, U50/U55 references, and incremental routing recipes below describe the earlier revision; use `tesla_route_reviewed.py` for the current circuit.


**Historical FPGA milestone.** The subsequent [H-bridge pass](HBRIDGE-ROUTING.md)
separates four incorrectly shared low-side gate-output nets from the raw FPGA
commands, rebuilds the driver-input routes and completes the supply feeds. The
49-net/137-pad and 154-open figures below describe the earlier checkpoint; use
the current routing audit and validation JSON for present counts. The carrier
contact assignments below describe that earlier checkpoint.

All 27 assigned signal contacts on the carrier's J2 FPGA connector are routed to their respective destinations. Including the intervening enable/series-resistor nets, ADC FIRST output and buffered status LEDs, the native connectivity audit covers **49 nets and 137 pads**. The daughterboard itself and its frozen v1 connector assignment are unchanged.

The board remains **two copper layers**, nominal 1.6 mm. This is a routing milestone, not a fabrication release: battery entry, regulator internals, 3.3 V distribution, switching-power connections, ESP32 service signals and four CST analog-to-ADC handoffs still need work. Whole-board unconnected count is **154**, down from 235 before the FPGA pass.

## Connected paths

- ADC CONVST, RESET, SCLK, CS, SDI, BUSY and all four DOUT lanes, including their pull resistors. FIRST reaches its existing test point.
- Both CST phase-comparator returns to FPGA global-clock inputs G0 and G1; the external clock service input remains on G6.
- Eight independent GDT commands, their enable logic, local pull-downs, series resistors and driver-input destinations; DRIVE_ARM, FAULT_N and their existing service/status branches.
- Five logic/status paths through U80 and the corresponding buffered LED anode connections. This does not imply that their still-incomplete 3.3 V source rail is powered.

See [daughterboard-pinout.csv](daughterboard-pinout.csv) for the complete physical-contact map and [circuit.json](circuit.json) for the electrical contract.

## Carrier pin changes

Five ADC controls were reassigned on the carrier to reduce crossings. Update the Tesla FPGA constraints accordingly; the module pin names still identify the same physical FPGA pads.

| Carrier J2 contact | Module signal | New carrier function |
|---|---|---|
| 14 | FPGA_IOT_36B | ADC_CONVST |
| 12 | FPGA_IOB_25B_G3 | ADC_RESET |
| 11 | FPGA_IOB_29B | ADC_SCLK |
| 9 | FPGA_IOT_37A | ADC_BUSY |
| 7 | FPGA_IOB_20A | ADC_SDI |

J2.10 remains ADC_CS_N. DOUT_D/C/B/A remain J2.6/5/4/2. CT1_ZERO remains J2.22/G0, CT2_ZERO remains J2.24/G1, and EXT_CLOCK remains J2.32/G6.

## Layout

Fine-pitch connector escapes use 0.15 mm traces, widening to 0.20 mm for the ADC and branch routing; selected existing/manual control trunks use 0.25 mm. All new tracks use horizontal, vertical or 45-degree geometry. Through vias use 0.60 mm copper lands and 0.30 mm drills, outside SMD solder pads. There are no filled/capped via-in-pad requirements introduced by this pass.

The ADC routes fan out from the connector's north row, cross the existing supply trunks with short front-layer bridges, then enter the converter from its digital sides. ADC pull resistors sit below the converter. The long +5V_ADC CST feed changed from back to front copper at its existing 0.5 mm width, freeing the back layer for digital routes without narrowing the power feed.

Gate commands leave the connector's south row as an ordered bundle. U50/U55 enable logic and the pull/series resistor rows were aligned to leave access to the driver inputs. The existing wide GDT output copper remains intact. The buffered indicator inputs pass around the mounting-hole exclusion; D84–D88 now face their associated resistors, and C80 sits next to U80's supply pin.

Ground pours were refilled. Six local pad thermal-angle overrides restore complete reliefs around nearby signal copper; there is no blanket direct-to-plane pad override. Unused escape vias and dangling branches were removed, and partial pad entries were extended to positive contact. Native DRC now retains only the four explicitly unfinished CST analog route ends.

## Checks and reproducibility

- `check_tesla_fpga_routing.py`: every expected pad on the 49 signal nets is in its native KiCad connected cluster; no duplicate UUIDs, off-angle owned tracks, same-net collinear overlaps or via drills over SMD pads.
- Existing AUX, CST and positive-supply connectivity audits run against the updated board as regression checks.
- Native ERC: 0. Schematic/PCB parity: 0. Native DRC: four documented open CST analog handoff ends, with no other physical violations. The 154 whole-board opens remain visible and are not waived.
- Native front/back copper and top 3D views are reviewed. The plugin's broader layout-quality findings remain a separate draft-review list; see `fpga-layout-quality.json`. Its whole-board summary is 309 errors, 2583 warnings and 30 informational findings, dominated by draft silk/BOM and heuristic placement checks. Six via-in-pad reports were independently checked against rotated native pad geometry: minimum drill-to-pad separation is 0.238 mm, with no overlap (`fpga-via-review.json`). No blanket waiver was applied.

`/usr/bin/python3 tools/hardware/tesla_route_fpga.py` reapplies the fixed reviewed geometry in `tools/hardware/tesla_fpga_routing.json`, including placements, five changed J2 assignments, pad thermal angles and the existing supply-track layer override. It does not run an autorouter or rebuild the board. The recipe can be replayed after the CST, positive-supply and AUX passes, in that order. Follow it with `tesla_route_hbridge.py` to restore the newer gate-output correction and driver routing. Validate again after replaying or making upstream changes.

Placement metadata is synchronized into `tools/hardware/tesla_placement.json` and `docs/circuit.json`. The schematic and connector mapping record the same new ADC assignments. Do not run the full board constructor over routed work. No fabrication or assembly exports were published for this milestone.

Reviewed native copper exports: [front](fpga-routing-F_Cu.svg), [back](fpga-routing-B_Cu.svg). The [top 3D view](floorplan-top.png) is refreshed to this placement/routing state.
