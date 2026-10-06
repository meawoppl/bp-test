# H-bridge and gate-driver routing

## Driver routing and input alignment — 2026-09-29

The four HO connections now run directly under their SOIC drivers on F.Cu at a uniform 0.60 mm width. Each is 11.250 mm long instead of 15.490 mm; eight layer-change vias were removed across the four paths. Bootstrap and switch-node returns were preserved; this change alone does not establish switching-loop performance.

The four input-resistor groups below U51–U54 now share 2.50 mm column spacing and 3.40 mm row spacing. The series row is 6 mm below each driver center, with pull-downs beneath it. Input vias and short ground returns were aligned with the repeated geometry. Native ERC, physical DRC and schematic parity remain zero; 25 unrelated whole-board connections remain unfinished. The current snapshot is `tesla_reviewed_routing.json`, replayed by `tesla_route_reviewed.py`.

> Historical milestone: later placement, package, contact-map and routing changes are documented in [COMMAND-AND-ADC-CLEANUP.md](COMMAND-AND-ADC-CLEANUP.md). Use `circuit.json`, `daughterboard-pinout.csv`, and the latest validation reports for current state.

> Historical milestone. The current analog routing/channel swap and removal of command-enable gates are described in [ANALOG-AND-DRIVE-CLEANUP.md](ANALOG-AND-DRIVE-CLEANUP.md). Counts, U50/U55 references, and incremental routing recipes below describe the earlier revision; use `tesla_route_reviewed.py` for the current circuit.


Both independent 24 V full bridges are routed, including the battery feed,
reservoir banks, four UCC27282 drivers, bootstrap capacitors, gate resistors,
gate-to-source pull-downs, switch-node output links and enable-logic inputs.
The board remains two copper layers. The module and its frozen v1 contact map
are unchanged.

## Gate-output net correction

The inherited circuit generator gave each UCC27282 low-side output the same
`GDTn_L_LO` / `GDTn_R_LO` name as the raw FPGA command. That would connect a
12 V gate-driver output to a 3.3 V FPGA signal. The output is now named
`GDTn_L_LO_DRV` / `GDTn_R_LO_DRV`, exclusively between driver pin 8 and its
gate resistor. The raw FPGA command still enters its enable logic and service
branches; the qualified `*_LO_BUS` signal reaches driver pin 6.

This correction is present in `circuit.json`, the schematic, PCB and
`tesla_output.py`. No firmware contact assignment changes accompany it.
`check_tesla_hbridge_routing.py` explicitly checks the voltage-domain separation;
ordinary ERC cannot infer it through a passive daughterboard connector symbol.

## Copper and placement

- Reservoir capacitors face the front-layer battery buses. The battery feed,
  bridge supply buses and existing switching/output paths use 2.5 mm copper.
  Three 0.60/0.30 mm vias share each principal supply/return layer transition.
- Each low-side MOSFET source has a 1.2 mm front-layer strap to its nearby ground
  via group. The high-current return continues through the ground plane.
- Gate resistors and their pull-downs sit beside the associated MOSFET gates.
  Gate wiring uses 0.4 mm driver-pin necks and 0.5–0.7 mm local runs. The
  high-side drive crosses on the back layer, with a dedicated source-sense
  return to HS beside it; the wide switch-node/output path stays on the front.
- Bootstrap and 12 V bypass capacitors remain close to the driver pins.
  U50/U55 bypass feeds and the 3.3 V logic distribution are connected.
- New segments use horizontal, vertical or 45-degree paths. Via drills remain
  outside SMD solder pads. Ground islands are checked separately from the
  logical netlist; merely assigning a pour to GND does not establish continuity.

Trace widths are layout choices, not a validated pulse-current rating. The
GDT load, battery wiring, switching overshoot, dead time, bootstrap behavior,
MOSFET temperature and gate waveforms still need bench qualification. The
accepted 24 V drive decision remains in [DRIVE-DECISION.md](DRIVE-DECISION.md).

## Validation and reproduction

Final checks: ERC **0**, schematic/PCB parity **0**, and **no physical DRC
violations apart from the four documented open CST handoff ends**. Native DRC
reports no disconnected GDT, supply-feed or GND items. All bridge, FPGA, CST,
AUX and power-routing audits pass. The whole-board unconnected count is **42**,
down from 154 before this pass. Replaying the recipe is byte-stable after
normalization by KiCad.

Ground-return review found split pours around U50 and the indicator buffer.
Explicit local returns, stitching and a short FAULT_N layer bridge restore
continuity. The 1.0 mm 5 V trunk has a 0.2 mm local offset to clear the indicator
buffer's ground via without narrowing the supply trace.

The broader plugin quality audit remains a draft-review list: 304 errors,
2591 warnings and 30 information items across 22 rules. Most concern existing
silkscreen, BOM metadata, placement heuristics and the four intentional route
ends; no global pass or waiver is claimed. The six reported via-in-pad errors
were checked against correctly rotated native pad geometry: minimum drill-to-pad
separation is 0.225 mm, with no overlaps. See
[hbridge-layout-quality.json](hbridge-layout-quality.json) and
[hbridge-via-review.json](hbridge-via-review.json). Ampacity and length-match
checks still lack their project current-path/net-class sidecars and therefore
are not evidence of validated operating current or timing.

The current exact counts and hashes are recorded in [validation.json](validation.json)
and [hbridge-routing-audit.json](hbridge-routing-audit.json). Run the native DRC/ERC
check and the CST, power, AUX, FPGA and H-bridge routing audits together after
changes. Four analog CST-to-ADC handoff ends remain explicitly unfinished.
Remaining regulator/ESP32/analog routing is still visible in native unconnected
reports; this is not a manufacturing release.

`/usr/bin/python3 tools/hardware/tesla_route_hbridge.py` reapplies the fixed
reviewed routing delta in `tesla_hbridge_routing.json`. Apply it **after** the CST,
power, AUX and FPGA routing recipes. It persists placements, gate-output pad
nets, thermal angles, region-text positions and revised copper; it does not
rerun an autorouter. Regenerate the schematic using `tesla_schematic.py` if
replaying against an older circuit contract, then rerun all checks. Never run
the initial board constructor over routed work.

Reviewed native views: [front copper](hbridge-routing-F_Cu.svg),
[back copper](hbridge-routing-B_Cu.svg) and [top 3D](floorplan-top.png). No fabrication or assembly package is published for the unfinished
board.
