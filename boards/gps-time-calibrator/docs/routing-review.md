# Routing review — 2026-09-26

Pre-routing checkpoint: `127c1f3`, pushed on `gps-calibrator-routing` before edits.
The canonical carrier PCB is authoritative; ordered module/programmer files were
not modified. Connector pin numbering, optical LED mapping and schematic nets
are unchanged.

## Routing and placement

Completed connector-side USB-C/CC/eFuse, trigger input/output and GNSS support
circuits first, then regulator/OCXO supplies, and finally the module interface and
LED-buffer signals. R4, R169, C68, R6/R7 and C73/C74 were repositioned/reoriented
for their local routes. Final positions are recorded in `final-placements.json`
and `circuit.json`; all discrete passives retain their 0805-or-larger packages.

J1/J2 retain the ordered daughterboard mapping. The 0.4 mm connector fanout uses
short 0.15 mm escapes and spreads to 0.5/0.25 mm vias. Ordinary signals use
0.2 mm routing, with wider supply trunks and pours. In1 remains principally GND;
a few local buffer/control routes use it, with clearances refilled. Ground islands
have explicit stitches and regulator/ESD grounds have short via escapes. The
confirmed U15 supply via was moved outside its SMD pad. Unused fanout vias were
removed after connectivity was established.

USB ESD-to-module copper path lengths are 38.693 mm (+) and 39.927 mm (-),
**1.234 mm disparity**, excluding package/barrel lengths; both use two vias.
`usb-route-lengths.json` records the measured connected paths. The Type-C duplicate
contact branches are additional copper, not a second end-to-end differential path.
This is the module's full-speed USB interface; no 480 Mbit/s qualification or
fabricator-confirmed 90-ohm differential impedance is claimed.

GNSS RF remains straight, 9.21 mm long and 0.26 mm wide. Post-route refill sampling
found In1 GND under all 115 RF centerline samples and 0.155 mm measured front-ground
gaps at the recorded sample locations. The existing JLCPCB nominal 50.50-ohm
calculation and 1.6 mm stackup remain applicable; launch/bias-tee effects still
need hardware validation. Amphenol 132289 is the .062-inch / 1.57 mm connector
([manufacturer](https://www.amphenolrf.com/zh-cn/part/132289/1030/)); confirm finished
board tolerance/fit. Stale 1.3 mm and 0.23 mm README wording was corrected.

The edge-launch lands end exactly at x=200 mm. Their existing pad-specific
edge-clearance rule now permits 0.01 mm numerical overlap so KiCad accepts this
intentional edge contact. This exception applies only to J5/J6/J7 pads; ordinary
copper-edge, track, via, drill and clearance rules were not relaxed.

## Validation and deliverables

- Native KiCad ERC: 0 violations.
- Native refilled DRC: 0 violations, 0 unconnected items, 0 schematic-parity issues.
- Native rotated-pad polygon audit: no via drill intersects an SMD pad, including
  an extra 0.05 mm drill-to-pad margin (`fab/checks/native-via-pad.json`).
- Four generated copper Gerber layers rendered with PyGerber and visually reviewed.
  Front/bottom component areas, SMA launches, inner planes and module escapes were
  checked alongside the native 3D top view. This does not replace fab CAM review.
- Gerber/drill ZIP, assembly BOM/CPL (306 placements), native positions, GLB and
  top/angled previews regenerated. `fab/EXPORT.json` binds exports to the PCB hash.
- USB path audit: `tools/hardware/calibrator_usb_lengths.py`; rotated-pad audit:
  `tools/hardware/calibrator_via_pad_audit.py` (pcbnew + shapely).

## Broader quality-tool limitations

`fab/checks/quality-advisory.json` preserves the plugin result: 71 errors,
5310 warnings and 38 informational findings. **The aggregate quality result is
not green.** Do not present it as a complete manufacturing or electrical sign-off.

Concrete discrepancies were checked rather than changing the design to silence
heuristics:

- kct silk geometry reports MODULE v1 at (175,62), although its actual board
  location is (155,52), and similarly shifts row labels/board graphics. Native
  KiCad silk checks and rendered output are clean. The apparent (20,10) origin
  shift invalidates those reported overlaps.
- Five via-in-pad claims at rotated R175/U3/U4 pads are not reproduced by native
  pad polygons. The separate, real U15 via-in-pad finding was corrected.
- Missing-decoupling claims identify USB_D+, TRIGGER_3V3 and TRIGGER_5V as supply
  pins. These are signals. GNSS VCC_RF is intentionally unused; ANT_PWR feeds the
  existing 10-ohm/filter network, with bypassing after the resistor.
- The USB heuristic sums all net copper, including duplicate USB-C branches, and
  assumes High-Speed operation. Connected-path lengths are recorded above.
- Optical row/bit labels and connector legends intentionally conflict with the
  generic profile's ban on explanatory silkscreen. They are required for this
  calibration instrument.
- The thousands of bypass-distance warnings include remote same-rail capacitors,
  rather than assigning the intended local bypass pair to each load. Remaining
  acute-junction, tombstoning, short power-escape and typography advisories remain
  available for fabrication/assembly review; they are not all individually waived.

Before ordering: review JLCPCB component rotations/offsets, manual OCXO/OLED/module
assembly and mounting clearances. On hardware: test USB 3 A attach/startup,
OCXO warmup, all-on LED load and brightness/edge timing, GNSS antenna operation,
and trigger RC/comparator latency. Firmware and absolute timing calibration are
outside this routing task and remain incomplete.
