# Positive supply routing — two-layer development milestone

> Historical milestone. The current analog routing/channel swap and removal of command-enable gates are described in [ANALOG-AND-DRIVE-CLEANUP.md](ANALOG-AND-DRIVE-CLEANUP.md). Counts, U50/U55 references, and incremental routing recipes below describe the earlier revision; use `tesla_route_reviewed.py` for the current circuit.


The subsequent [ADC passive routing](adc-passives-review.txt) closes the five C6–C9 reference/regulator connections. The current board has six unrelated opens; native ERC, physical DRC and schematic parity remain zero.

## Converter controls completed — 2026-09-30

U30/U31 feedback, RON, soft-start and UVLO nets are now routed. All converter and supporting-part pads are connected. This closes 14 connections, leaving 11 unrelated board-wide opens. Native ERC, physical DRC and schematic parity are zero. Added 0.25 mm control traces and six 0.6/0.3 mm vias; minimum new-copper clearance is 0.30 mm. The existing supply distribution and bypass returns still pass their audit.

The reviewed routing recipe reproduces the saved board exactly. See [verification](supply-controls-verification.json), [copper preview](supply-controls-after.png) and [review](supply-controls-review.txt). The existing layout-quality backlog remains 301 errors, 2422 warnings and 29 informational findings; all error and warning entries are unchanged. The sections below are historical milestones.

## Current 3V3 cleanup — 2026-09-29

The U2 output-to-ADC supply now runs on F.Cu at 0.40 mm, with a direct 45-degree approach to C5. The regulator-side layer-change via and rear-layer diagonal have been removed; the former two-via ADC-to-C5 hop is also removed. That final front-layer approach uses 0.20 mm through the fine-pitch escape and beside the DOUT_A via, then widens to 0.40 mm for the capacitor connection. The comparator/CST branch also uses F.Cu at 0.35 mm, clearing C21 and joining the existing CST distribution at R414's supply via. It no longer drops down from the ADC pull-up branch. D83/R803 form a horizontal row above-left of U2, away from the trunk; the indicator feed is a short 0.25 mm F.Cu tap.

`power-routing-audit.json` checks +3V3 as a fifth rail: all 26 pads connect to U2.5, in addition to the 70 pads on the four rails below. All 25 audited bypass/bulk returns remain connected. Current native checks report zero ERC, physical DRC and schematic-parity findings, with 25 unrelated whole-board opens. The following counts and incremental commands are historical; use `tesla_route_reviewed.py` for the current snapshot.


This records the positive-supply milestone. Later [AUX](AUX-ROUTING.md), [FPGA](FPGA-ROUTING.md) and [H-bridge](HBRIDGE-ROUTING.md) routing supersedes the remaining-work counts below. The FPGA pass moves the long +5V_ADC CST-feed segment to front copper at the same width to allow the digital bus to cross behind it.

The +5 V and +12 V output-distribution networks are routed on the canonical `controller.kicad_pcb`. No component values, net assignments, or schematic connections changed. The board remains two copper layers, nominal 1.6 mm.

| Rail | Source | Routed destinations | Pads connected |
|---|---|---|---:|
| VIN_5V | U31.7 | Output capacitor bank and feedback/ripple taps; J1 module supply contacts; J5 service 5 V; R802 indicator; R20 ADC-rail link; U2 input and enable, C20 | 16 |
| +5V_ADC | R20.2 | ADC AVCC pins and bypasses; four AUX input clamps; both CST rectifiers/summers and the −5 V charge pump | 24 |
| +12V_BIAS | U30.7 | Output capacitor bank and feedback/ripple taps; four UCC27282 driver VDD pins and bypass pairs; R801 indicator; R740 AUX filter input | 20 |
| +12V_AUX | R740.2 | Filter bulk capacitor C740 and four AUX amplifiers with individual bypass capacitors | 10 |

R20 remains the existing 0-ohm link between VIN_5V and +5V_ADC; R740 remains the existing 10-ohm series element feeding +12V_AUX. Both sides are checked as separate nets so these intentional boundaries are preserved. J5's 5 V pin remains directly on VIN_5V; this routing change adds no USB power-source isolation.

## Placement and routing

The two regulator output banks sit in matching rows below their modules. Their positive terminals face the regulators, connected by short, wide output buses; the feedback/ripple taps branch separately. The gate-driver bypass pairs are horizontal with aligned positive pads, keeping each local 100 nF connection short. The AUX positive bypass capacitors are centered over their amplifier supply pins, and the ADC supply capacitors have been regrouped near AVCC.

The main 5 V distribution uses 1.0 mm copper, with a separate 0.8 mm branch to the local 3.3 V regulator and ADC-rail link. The main 12 V distribution uses 0.8 mm copper, with 0.5–0.6 mm local supply branches. ADC/local analog branches are generally 0.3–0.6 mm. Short 0.18 mm module-connector escapes and 0.20 mm ADC pin escapes accommodate the fine-pitch pads; these widen beyond their pad neighborhoods. Feedback taps and indicator feeds use 0.3 mm traces because they carry only their local low current.

Both original ground pours now cover the board and use thermal reliefs on ordinary plane-connected pads. Local bypass returns have dedicated ground vias. The native audit confirms conductive returns for all 25 bypass/bulk capacitors covered by this step. This is not a completed high-current battery/GDT return-layout review: the remaining battery routing and switching-current paths still need to be finished and reviewed together.

All new routes are 0/45/90 degrees. Simple corners are mitered; branch points and component-pad anchors remain in place. New through vias use 0.6 mm lands and 0.3 mm drills. The audit rejects via drills overlapping SMD pads and same-net overlapping segments that can hide stubs.

## Verification and remaining scope

`power-routing-audit.json` records native KiCad source-to-load connectivity: all 70 supply pads connected, all 25 audited capacitor returns connected, no off-angle power tracks, no duplicate/overlapping power segments, and no new via holes over SMD pads. The existing 35-net CST connectivity audit also passes.

Native ERC and schematic parity are zero. Native physical DRC reports only the six documented, intentionally open ADC/FPGA handoff ends in `routing-intent.json`; no additional shorts, clearance violations, courtyard overlaps or isolated fill remain. Whole-board unconnected count is 284. This board is still a routing draft: battery/input power, remaining regulator control/feedback nets, +3V3 distribution, the −5 V AUX extension, and many signal/gate-control routes remain unfinished. Completing the positive output nets does not make the regulators or controller ready to power up.

The whole-board layout-quality report still contains the previously documented draft silkscreen/BOM/placement findings, plus the six intentional handoff-end errors. Latest counts are **311 errors, 2573 warnings and 29 informational findings**, recorded in `power-layout-quality.json`; they are not a fabrication waiver. No manufacturing outputs were published for this routing milestone.

Native front/back copper previews and the top 3D floorplan were reviewed for regulator-bank orientation, centered pad entries, driver bypass placement, connector access, layer crossings, supply trunks, and separated local ground returns.

## Reproduction

Use `/usr/bin/python3 tools/hardware/tesla_route_power.py` to replace only this step's owned tracks/vias, reapply the supply placements, extend/refill the existing ground zones and save the canonical board. It preserves the CST and GDT signal copper. If rebuilding the CST routing first, run `tesla_route_cst.py` **before** `tesla_route_power.py`, since the CST generator restores its local-only ground-zone outlines.

Run `check_tesla_power_routing.py`, `check_tesla_cst_routing.py`, and `check_tesla_draft.py` afterward. Placement changes are persisted in `tools/hardware/tesla_placement.json` and `docs/circuit.json`; do not run the full placement constructor over the routed board.
