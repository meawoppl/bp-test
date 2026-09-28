# FPGA interface and USB power routing cleanup — 2026-09-27

Four FPGA interface nets were rebuilt with centered exits and 0.20 mm tracks:
OCXO G6, trigger output IOT_51A, PPS G0, and trigger input IOT_50B. The four
routes now total 34 segments instead of 54. Tiny grid jogs, unnecessary width
changes and the backwards clock-pad approach were removed. No vias were added.
Necessary detours around component pads and mounting hardware remain.

The G6 trace from J2.32 to R173 now uses three segments (17.271 -> 13.409 mm).
The OCXO source connection, 33-ohm resistor and module pin-44/GBUF6 assignment
are unchanged. PPS and trigger functions are unchanged; no firmware remapping
is required for this cleanup. `io-routing-comparison.json` gives whole-net
track-length/count comparisons, excluding via barrels.

USB VBUS now joins its upper/lower connector escapes beneath the USB connector
body on In2.Cu, maintaining the existing 0.65 mm width. The inner ground
reference layer and USB data copper are unchanged. The new route clears both
plastic locating holes and grounded shell stakes. The old detour beside the ESD
array was removed; the ESD VBUS connection, capacitor, protection/power-control
connections remain intact. Total VBUS copper was reduced by 9.869 mm.

Native refilled DRC: 0 violations, 0 unconnected items, 0 schematic parity issues.
The native via-drill/pad audit and display/OCXO mapping audit pass. USB connected
path lengths remain 38.693/39.927 mm. Connector escape, clock resistor approach,
PPS detour and the In2 route beneath the jack were visually reviewed, along with
the regenerated native 3D preview. No component positions or schematic nets changed.

Manufacturing outputs and 3D assets were regenerated with Build/Publish and the
carrier assembly finalizer. The finalizer preserves manual-assembly exclusions
and saved JLCPCB placement corrections; its manifest binds the corrected files
to this PCB. The plugin may flag intentional artifact postprocessing as stale;
see passive-tidy-review.md for that publisher limitation and existing board-wide
heuristic review dispositions. This layout cleanup is not a hardware timing or
USB power qualification.

Current heuristic quality result: 65 errors, 5208 warnings, 39 informational findings; not green. Categories/dispositions remain as documented in passive-tidy-review.md.
