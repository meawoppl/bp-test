# Layout-quality triage for the command/ADC checkpoint

This is an incomplete development board. These findings are retained, not suppressed or treated as universal waivers. Native checks and scoped copper checks are recorded separately.

The CST handoffs are complete: no `track_dangling` findings remain. The latest front-layer 3V3, ground-remnant and parallel gate-resistor cleanup reduces the previous report by nine silk errors and one acute-angle warning. Native physical DRC is zero. Copper plots and the native top render were reviewed for pad exits, absence of tails, indicator/ADC_FIRST label clearance, aligned resistor pairs and ground-return access. The remaining silk heuristics include large region-line bounding boxes that require reconciliation against actual native geometry; the full-board DFM backlog stays open.

| Severity | Rule | Count | Review/disposition |
|---|---|---:|---|
| error | `mistake.via_placement.via_in_smd_pad` | 4 | All reported flags checked against rotated pad geometry and native HitTest; no drill overlap. See command-adc-via-review.json. These are rotated-footprint detection false positives. |
| error | `silk_explanatory_text` | 20 | User explicitly requested labeled subsystem frames and indicator legends; retain these text annotations. ADC_FIRST identifies the requested local test point; retain this functional net label. |
| error | `silk_over_copper` | 65 | Unmasked-versus-covered copper context requires review. Native silk/mask DRC passes; full heuristic backlog remains open. |
| error | `silk_overlap` | 157 | Broad text/graphic overlap heuristic; native DRC has no silk collision. Current changed regions visually inspected; full-board finding-by-finding typography review remains open. |
| error | `silk_pad_clearance` | 55 | Native silk/mask DRC passes; full heuristic backlog remains open. |
| info | `mistake.bypass_capacitor.bypass_capacitor_placement_could_be_improved` | 25 | Shared-rail proximity suggestions; full-board association review remains open. |
| info | `mistake.differential_pair.differential_pair_length_matching_could_be_improved` | 1 | USB/service routing remains incomplete; no differential impedance or matching claim. |
| info | `mistake.thermal_management.thermal_pad_may_need_more_vias` | 2 | Thermal design suggestions; loss/temperature and final via-area evaluation remain open. |
| info | `optimize_traces.mergeable_segments` | 1 | The edited ADC bundle was merged; one other reported collinear merge remains outside this scope. |
| warning | `decoupling_distance` | 29 | Local moved groups inspected; whole-board ADC/reference and other bypass placement/connection review remains open. |
| warning | `mistake.bom_health.component_missing_manufacturer_part_number` | 207 | Draft procurement backlog; includes the newly selected 0603 packages. Resolve before assembly export. |
| warning | `mistake.bypass_capacitor.bypass_capacitor_too_far_from_power_pin` | 1062 | Shared rail inference generates many capacitor/pin combinations, not this many distinct misplaced capacitors. Local moved regulator/driver caps reviewed; full association and placement audit remains open. |
| warning | `mistake.connectivity.led_missing_series_resistor` | 4 | Flags are D84/D86/D87/D88: each anode net joins an LED, a 12k series resistor and its antiparallel clamp. The detector does not confirm this branched topology. check_tesla_indicators.py and native netlist/PCB inspection verify all eight series resistors and four reverse clamps. |
| warning | `mistake.connectivity.missing_pull_up_resistor` | 1 | Requires device-pin-specific functional review; not dismissed on routing connectivity alone. |
| warning | `mistake.manufacturability.acute_angle_in_trace_acid_trap` | 18 | Tracks pass 45/90-degree angle checks; junction-level acute geometry still needs separate whole-board review. |
| warning | `mistake.manufacturability.thermal_imbalance_may_cause_tombstoning` | 102 | Plane-versus-track thermal asymmetry heuristic; soldering/thermal relief review remains a release task. |
| warning | `mistake.power_trace.power_trace_too_narrow` | 10 | The new 0.25 mm indicator taps carry about 2 mA and are deliberately narrower than the main rails. Remaining whole-board current-budget/ampacity review stays open. |
| warning | `mistake.thermal_management.thermal_pad_not_connected_to_ground` | 8 | Power MOSFET drain tabs/switch nodes are intentionally not ground; grounding these pads would short the power circuit. Confirm each thermal-role assignment at release. |
| warning | `pad_grid` | 3 | Package pad pitches need not fall on one universal grid; footprint/datasheet dimensions control. Final footprint audit remains open. |
| warning | `silk_edge_clearance` | 6 | Subsystem frames closely follow the outline by user request; final silkscreen clipping/manufacturer clearance review remains open. |
| warning | `silk_text_below_min` | 19 | Compact text is intentional, but manufacturer print legibility remains unqualified. |
| warning | `silkscreen_line_width` | 934 | Includes many footprint graphics; final manufacturable stroke/legibility cleanup remains open. TP1 reuses the standard 1 mm test-point footprint with a 0.12 mm silk ring; final DFM cleanup remains open. |
| warning | `silkscreen_text_height` | 19 | Compact text is intentional, but manufacturer print legibility remains unqualified. |

The −5 V block shift adds two heuristic `silk_overlap` reports for D62/U41 against moved subsystem-frame lines. Native coordinates put those pairs over 28 mm apart; both are detector-coordinate false positives. See `negative-rail-shift-quality-delta.json` for the actual endpoints and the complete delta. The local capacitor spacing is unchanged; no additional bypass-placement pairings or warnings appeared. Current totals: 301 errors, 2422 warnings, 29 informational findings. This scoped edit does not close the existing full-board quality backlog.

The C333 jog removal keeps the totals at 301 errors, 2422 warnings and 29 informational findings. Six existing capacitor-to-capacitor proximity descriptions change distance after C333 turns; these inferred shared-rail associations do not represent IC bypass connections. Its two existing 0.12 mm silk-width warnings move with the footprint. The optimizer summary changes with the three removed segments. No rule counts increase; see `c333-jog-quality-delta.json`. Native ERC, physical DRC and schematic parity remain zero; all pad connectivity components and 25 existing unrouted connections remain unchanged. The copper preview was inspected for pad clearance, the centered supply connection, absence of the former detour and preserved trace width.

The D42 placement adds three heuristic silk-overlap errors caused by the detector applying the board origin to region lines but not footprint graphics. Native-coordinate separations are 29.06, 31.17 and 30.80 mm; native silk/mask DRC is zero. See `d42-placement-quality-delta.json` for UUIDs and endpoints. Current totals are 304 errors, 2422 warnings and 29 infos; no findings are suppressed. Existing dispositions above remain open.
