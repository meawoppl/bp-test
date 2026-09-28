# Passive and support routing cleanup — 2026-09-27

Reoriented/repositioned 17 passives: C2, C6, C7, C12, C13, C15, C65,
C70, C71, C72, R8, R9, R160, R161, R162, R171 and R172.

- LDO input capacitors face their supply pins. C2 is vertical to keep the
  existing interface-signal corridor clear; the CC/GNSS input caps use the
  supply-pin row. The GNSS output capacitor now connects directly along that row.
- The trigger input resistor follows the SMA centerline. C75/R9 share an aligned
  shunt bus; R160/R161/C13 form one column with a shared threshold-node trunk.
- R162 is aligned with the output SMA; C15 sits immediately above, with a clean
  centered supply-pad exit. Removed overlapping segments and grid-sized jogs
  from the output-control approach. Moved U10's reference clear of C12.
- Buck C70 faces the input pin; C71/C72 share an output-power column. R171/R172
  form a compact divider directly below U15. Total feedback copper drops from
  16.662 mm to 6.793 mm, without changing component values or connections.
- Added short, explicit ground returns for C70/C71/C72 with vias outside the
  lands and package bodies. Removed the obsolete trigger-threshold supply via.

The schematic circuit is unchanged. PCB placement changes are mirrored in
circuit.json/final-placements.json; neither ordered daughterboard nor programmer
hardware was edited. Connector mechanics, USB routing, straight GNSS RF feed,
OCXO global-clock assignment and the display bus were preserved.

## Checks and visual review

Native refilled DRC: 0 violations, 0 unconnected, 0 schematic-parity issues.
ERC: 0 violations. No courtyard overlaps or silk-to-pad collisions. Native
rotated-pad audit finds zero via drill overlaps with its extra 0.05 mm margin.
The display connectivity audit still passes all 16 channels and OCXO G6.
USB path lengths remain 38.693/39.927 mm, 1.234 mm disparity.

Reviewed component spacing, centered pad exits, divider polarity, short supply
and ground paths, front copper routing, published front Gerber and native 3D
views. Component values and manufacturer part numbers are unchanged.

The aggregate heuristic quality check remains non-green: **65 errors, 5213
warnings, 39 informational findings**, down from 67/5220/38. Acute-junction
warnings reduced from 23 to 18. The remaining error categories are unchanged:
7 supply-pin/net misclassifications, 1 USB total-net-length/high-speed assumption,
1 R175 rotated-pad false positive, 26 required instrument legends, and 30 silk
geometry/origin discrepancies. See display-bus-reroute.md and routing-review.md
for the evidence and category dispositions. The remaining warning categories
are unchanged; no quality rule or native clearance was relaxed to obtain a pass.

## Outputs

Rebuilt/published Gerbers, BOM, placement files and 3D models, then applied the
carrier's manual-assembly exclusions and saved JLCPCB corrections through
calibrator_export.py. 291 automatic placements remain. The artifact hashes are
recorded in fab/assembly-finalization.json, and the raw publisher provenance is
in fab/.kicad-pcb-build.json. Current files use absolute origin with native
negative CPL Y; do not combine with older auxiliary-origin files.

The plugin's badge currently reports artifact modifications because the carrier
finalizer intentionally groups the BOM, corrects CPL and strips drawing exports
after Publish. Source-stage keys are current; the separate finalization manifest
has been verified against every handed-off file. Republishing without rerunning
the finalizer would discard those assembly corrections. This is a publisher
integration limitation, not a stale PCB export.


## Trigger, OCXO and GPS follow-up

R160/R161 and C13/TP18 form a 2x2 grid. R177/R7/R6/C8/C9/R180/R179 share X=174 mm; C8/C9 were included after the initial resistor-only alignment. R173/R178/C70 share X=162 mm beside the OCXO, and C73/C74 spacing is reduced. TP6/TP64/TP63 share X=146.25 mm; all 33 remaining testpoints use the same 1 mm bare-copper library footprint. The R178 enable via is outside the resistor pads.

C15 supply and ground vias near the output driver are intentional: VIN_5V is supplied from In2.Cu and the ground via provides a local return to the ground planes. Neither is a dangling copper item. Native track_dangling and via_dangling checks are enabled as warnings; unconnected_items is an error. Electrical DRC does not prove that every connected via is necessary.

Native DRC/parity and pad-drill/access audits pass. Native 3D crop reviewed for aligned passive columns, the 2x2 group and probe-label access. Broader heuristic quality limitations remain recorded in testpoints.md and testpoint-quality-summary.json.

Three trackless GND stitching vias under the OLED were removed at (155.662,94.95), (155.025,98), and (159.975,90) mm. All three touched F.Cu/B.Cu/In1.Cu ground before removal, but served no local component or signal transition. The PPS layer-transition via at (161.55,75.3) is retained. Zone refill and native DRC show zero violations, opens or parity issues after removal.

## D74 edge placement and GPS UART cleanup

D74 moved from X=197.0 to X=199.2 mm at unchanged Y=81.7 mm and 90-degree rotation. Pad copper ends at X=199.675, leaving 0.325 mm to the right board edge at X=200; its courtyard remains inside the outline. The anode route now reaches a via directly above the LED with a single back-layer diagonal instead of the old extra horizontal segment.

ESP_GPIO43_TXD lower back-layer route was reduced from nine segments to a straight X=176.6 mm run from Y=59.35 to 84.1, followed by a short 45-degree connection to the existing GPS via at (177,84.5). No electrical pin mapping changed. Native DRC/parity and connectivity remain clean.

## Direct OCXO supply and GPS enable

The OCXO 3.3 V output now routes on F.Cu at 0.65 mm from C71 via (152.4,69.75), (147.6,64.95) to the oscillator bypass node at (147.6,60). Both supply vias and the inner-layer detour were removed. One GND stitch at (143.5,64) connects the ground area partitioned by this new top trace; the thermal moat is retained.

GPIO6/GPS enable now exits its inner-layer approach at (171.3,78.45), runs straight across to U5 EN, and branches briefly down to R177. The previous lower via and loop below the resistor were removed. The GPS_EN testpoint remains connected. Native DRC/parity/connectivity clean after both changes.

## GPS supply detour and OCXO support cleanup

The +3V3_GPS back-layer supply to U7 now follows (180.4,55) -> (181.3,55.9) -> (181.3,76.55), replacing the wide five-segment excursion to X=187. The overlapping front-layer output segment at U5 was removed; the existing 0.4 mm output connection remains.

R178 and C70 exchanged their Y=62.2/64.4 mm positions at X=162. R178's enable connection now passes below the resistor, and C70's supply and ground vias sit outside its pads. Updated circuit.json preserves the placements. All +3V3_OCXO tracks, including local bypass and testpoint branches, are now 0.65 mm wide. Native refilled DRC: zero violations, zero opens, zero schematic parity issues.

## VBUS junction, power LED orientation, and PPS LED stub

USB_VBUS's upper inner-layer trunk is now a uniform 0.65 mm horizontal run at Y=15.5, meeting the X=176 branch as a T rather than a diagonal jog and reverse vertical segment. The U11 front-layer VIN lead now uses a short 45-degree entry followed by a straight approach. D1 rotated 180 degrees (now 0 degrees) so its anode faces R3; the three-segment hump is replaced by one straight connection. The obsolete ground tail at (197,82.4875)->(198.4,82.4875), left behind when D74 moved toward the edge, was removed. Ground-plane connections are retained.

R179, the 1k PPS LED resistor, now sits at (196.5,80.9125), immediately left of D74. Its output connects straight to D74's anode. The PPS approach uses the existing lower back-layer corridor, with the obsolete LED-net vias removed and a GPS_PPS transition at (194.5,80.9125). Component courtyards remain clear. Native DRC, connectivity, and schematic parity all report zero issues.
