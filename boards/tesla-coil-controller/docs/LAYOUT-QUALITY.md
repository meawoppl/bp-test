# Development placement quality status

> Historical milestone: later placement, package, contact-map and routing changes are documented in [COMMAND-AND-ADC-CLEANUP.md](COMMAND-AND-ADC-CLEANUP.md). Use `circuit.json`, `daughterboard-pinout.csv`, and the latest validation reports for current state.

The native KiCad checks after the compact-layout and output-link changes report 0 ERC, 0 physical DRC and 0 schematic-parity violations. The board has local GDT output links but remains substantially unrouted (499 unconnected items reported). No fabrication package is published.

The separate plugin quality audit is **not green**: 244 errors, 1,891 warnings, 29 information items. Counts by rule are in layout-quality-summary.json. These must not be treated as completed routing/manufacturing review.

- Nine explanatory-silkscreen findings are retained because the user explicitly requested the subsystem boundaries and names. Their 0.9 mm headings also trigger the default 1 mm text recommendation.
- The independent kct silkscreen checks disagree with native KiCad on numerous placements. Previous inspection found text/region bounding-box reports that did not match the native geometry. These need tool-level geometry/transform reconciliation before a manufacturing release, rather than blindly moving electrically appropriate parts. Small footprint silk clearances and line widths also remain manufacturing-review candidates.
- Missing manufacturer part numbers, decoupling-distance candidates and thermal/return-via recommendations remain open design work. The bypass audit produces many rail-wide pairings; each IC needs a local-return review during routing rather than treating all capacitors on the rail as its local bypass. The phase midpoint capacitor distance is also flagged despite being a reference-filter node, not an IC supply pin.
- Thirty-four manually specified output-link segments are present; their geometry is octilinear and the main width is uniform at 2.5 mm. No vias or copper pours have been added. The incomplete power/gate/return paths mean a finished layout cannot be established. Exact BOM qualification, transistor thermal copper and input-transient protection also remain outstanding.

Visual review covered the two matching CST clusters, shared pump between them, module envelope at the top edge, terminal screw/cable direction, repeated bridge placement and model coverage. Power entry/conversion is now upper-left, CSTs below, ADC beneath the FPGA header, and GDT stages to the right. Module connector spacing and hole geometry are unchanged. The schematic auxiliary connector/filter block and duplicated CST circuits were inspected in native exports; an exact contract check confirms independent sensor signals and shared supply rails only.

Compact-board placement: 160 × 160 mm. ADC capacitor center distances are recorded in adc-capacitor-placement.csv; the 0805 parts exceed the default 2 mm rule (primary bypass/reference parts 2.5–4.5 mm, additional C3 6.5 mm), so their routed fan-out and ground returns need a focused review. No manufacturing-readiness claim is made.

The quality-count snapshot above predates the subsequent 6 mm GDT horizontal compaction; native ERC/DRC/parity were rerun for that change. The broad quality audit remains outstanding for release.

The snapshot also predates the four AUX buffers and subsequent left-edge analog reflow. Native checks were rerun with zero physical/ERC/parity violations; the independent quality snapshot has not been refreshed for these changes.
