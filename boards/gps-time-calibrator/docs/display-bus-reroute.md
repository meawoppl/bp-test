# Display bus reroute — 2026-09-27

The carrier now uses an ordered 16-line display bus. U3/U4 are rotated to 270 degrees,
with their outputs facing the MOSFET gate-resistor row. Their bank centers align
with the LED columns; C4/C5 bypass the VCC end directly. Gate pulldowns R120–R135
remain, aligned with the MOSFET gate pads. Optical bit 15 is still leftmost.

Fifteen FPGA data nets remain entirely on F.Cu. The one bottom-row connector
contact (J2.21) uses two vias to escape on B.Cu before joining the bundle.
Input/output pad exits are straight; the long bundle uses parallel 45-degree bends.
Power uses the inner signal layer, and the static OE line uses B.Cu. In1 GND is
unchanged. The ordered module's pinout and hardware were not modified.

## Blanking / startup

Removed sixteen 100k buffer-input pulldowns. R140 is now a single 10k pull-up from
+3V3_LOGIC to FPGA_IOT_44B (carrier J2.33 / module FPGA pin 34), connected to
both buffer OE1 pins. OE2 remains grounded. OE high disables both output banks;
MOSFET gate pulldowns keep the LEDs off. Firmware must set all data outputs before
driving OE low. Carrier J2.24 / FPGA G1 is now unused. This is a firmware mapping
change; no firmware was implemented here.

## OCXO and PPS

Verified against both native PCBs: Y1.3 -> R173 (33 ohm) -> carrier J2.32 ->
module J2.32 -> FPGA U2 pin 44, IOB_3B/G6. G6 drives GBUF6 according to the
[Lattice UltraPlus data sheet](https://www.latticesemi.com/-/media/LatticeSemi/Documents/DataSheets/iCE/iCE40-UltraPlus-Family-Data-Sheet.ashx).
Firmware must instantiate/use the global clock input and constrain its 10 MHz clock.
PPS remains on carrier J2.22 / FPGA IOT_46B/G0. The clock routes were preserved.

## Current mapping

| Optical bit | Carrier J2 | FPGA package pin | FPGA net | Buffer input / output |
|---|---|---|---|---|
| 15 | 2 | 10 | FPGA_IOB_18A | U3.9 / 11 |
| 14 | 4 | 9 | FPGA_IOB_16A | U3.8 / 12 |
| 13 | 5 | 12 | FPGA_IOB_22A | U3.7 / 13 |
| 12 | 6 | 6 | FPGA_IOB_13B | U3.6 / 14 |
| 11 | 7 | 11 | FPGA_IOB_20A | U3.5 / 15 |
| 10 | 9 | 23 | FPGA_IOT_37A | U3.4 / 16 |
| 9 | 10 | 21 | FPGA_IOB_23B | U3.3 / 17 |
| 8 | 11 | 19 | FPGA_IOB_29B | U3.2 / 18 |
| 7 | 12 | 20 | FPGA_IOB_25B_G3 | U4.9 / 11 |
| 6 | 14 | 25 | FPGA_IOT_36B | U4.8 / 12 |
| 5 | 15 | 27 | FPGA_IOT_38B | U4.7 / 13 |
| 4 | 16 | 26 | FPGA_IOT_39A | U4.6 / 14 |
| 3 | 17 | 28 | FPGA_IOT_41A | U4.5 / 15 |
| 2 | 19 | 31 | FPGA_IOT_42B | U4.4 / 16 |
| 1 | 20 | 32 | FPGA_IOT_43A | U4.3 / 17 |
| 0 | 21 | 36 | FPGA_IOT_48B | U4.2 / 18 |

Machine-readable mapping is in `display-map.json`; native connectivity assertions
and measured copper lengths are in `display-bus-audit.json`. Recheck with
`/usr/bin/python3 tools/hardware/calibrator_display_bus_audit.py`.

## Validation

- ERC: 0 violations; refilled DRC: 0 violations, 0 opens, 0 schematic parity issues.
- Native rotated-pad audit: no via-drill intersections with SMD pads (0.05 mm margin).
- PCB front routing, buffer schematic blocks and native 3D top view reviewed by eye:
  ordered lanes, no display-data crossings, no loose display stubs, aligned local gate
  connections, bypass locations and package orientation.
- Published F.Cu and In2.Cu Gerbers rendered and inspected: ordered fanout and supply trunk match the native board.
- USB connected-path lengths are unchanged: 38.693/39.927 mm (1.234 mm difference).
- Quality checker: 67 errors, 5220 warnings, 38 informational findings; not green.
  The nine electrical/placement errors comprise seven previously documented supply
  misclassifications (USB/trigger signals, unused VCC_RF and filtered ANT_PWR),
  one USB total-branched-length comparison against a high-speed assumption, and
  one R175 via-in-pad false positive not reproduced by native pad polygons.
  The 58 silk errors comprise 26 required optical/connector legends plus 32
  geometry/origin discrepancies already recorded in `routing-review.md`.
  Native silk DRC and the native 3D render pass. Warning classes retain the prior
  review dispositions: remote same-rail capacitor distance heuristics; small
  pad escape/thermal asymmetry and acute-junction assembly advisories; and
  functional typography. D1's series resistor is present in circuit.json and
  the native netlist. These board-wide advisories are preserved, not silently
  waived or called manufacturing approval.

## Exports

Native files were regenerated with plugin Build/Publish. The carrier finalizer
then grouped the BOM, excluded manual-fit Y1/DS1 from automated assembly, applied
saved JLCPCB orientation/position corrections, and removed drawing layers from the
fabrication ZIP. There are 291 automatic placements. U3/U4 native rotation is
270 degrees; their existing -90-degree JLC correction produces 180 degrees in CPL.
Coordinates now use absolute KiCad origin, with negative Y in CPL, consistently
with the plugin's Gerber/drill export. Do not mix these with older CPLs using the
board's auxiliary origin. `fab/assembly-finalization.json` records the derivative
hashes; `fab/.kicad-pcb-build.json` retains the original publisher provenance.
Reproduce using `python3 tools/hardware/calibrator_export.py` while the pane server
is running. `--published` finalizes only a source-matching, already published build.
Review JLC's assembly preview before ordering; manual OCXO/OLED/module assembly,
startup/load tests and timing calibration remain as documented in routing-review.md.
