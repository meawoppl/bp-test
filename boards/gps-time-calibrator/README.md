# GPS optical time calibrator carrier — revision A, redesign in progress

180 × 100 mm carrier for the **ordered module v1**, using the programming carrier's exact mating contacts and pad numbering. The ordered daughterboard and programmer files are unchanged. This carrier is not ready for fabrication: the USB-power, OCXO and connector redesign still needs routing and final checks. See `fab/STATUS.md`.

## Optical display

Four identical rows of sixteen blue 1206 LEDs show bit 15 at the left through bit 0 at the right. Rows update together, without multiplexing. Each LED has its own **470 Ω, 1%, 0805** resistor. Sixteen AO3400A MOSFETs switch the columns through two SN74LVC541 buffers, with individual gate resistors and pulldowns. Each column has 100 nF and 10 µF bypass capacitors. All discrete resistors, capacitors and inductors are 0805 or larger; exact substitutions are in `docs/passive-parts-0805.json`.

Expected display current is approximately 0.26–0.33 A with all LEDs on, depending on LED forward voltage. Equal resistors reduce electrical mismatch but do not remove optical bin variation; use a common LED lot and measure brightness, supply bounce and optical edge timing on assembled hardware.

## USB power and installation

J3 is USB-C power and native USB data. A TUSB320 detects the source's **5 V / 3 A Type-C advertisement**. A NOR gate enables the TPS259531 eFuse only when both current-status outputs indicate 3 A. This is not higher-voltage USB-PD negotiation. A default-current or 1.5 A port leaves the main board off; the CC detector and its logic supply remain powered.

The eFuse has a nominal 2.48 A current limit and approximately 12 ms startup ramp. Downstream bulk capacitance is behind the eFuse. Module radio peaks, OCXO warmup and LED switching must be measured together before release. The external power terminal was removed to avoid backfeeding USB.

There are no BOOT/RUN or RESET switches: the installed module stays in normal run mode using its own strap and EN pullups. Its existing firmware/ROM USB behavior must support the intended recovery procedure; this carrier does not provide a hardware boot override.

The module body extends from x=145 to 165 mm and y=10 to 55 mm, flush with the carrier's top edge. J1/J2 are at (155,24.3) and (155,49.3) mm, retaining 25 mm spacing. H1 is at their midpoint (155,36.8). Retain the programmer's 2.0 mm mounting spacer and frozen connector numbering.

## Right-edge connectors and GNSS

Top to bottom: USB-C J3, input SMA J6, output SMA J7, GPS antenna SMA J5. The SMA connectors are Amphenol 132289 edge-launch parts with approximately 11.43 mm projection beyond the edge and a nominal 1.3 mm board slot.

Input accepts 0–5 V logic into a TLV3501 comparator referenced to half the 5 V supply, nominally 2.5 V. A 3.3 V Schmitt buffer feeds FPGA, ESP32 and GNSS EXTINT. Output is an AHCT buffer producing 5 V logic into a **high-impedance receiver**, not 5 V into a 50 Ω termination. Neither port should be treated as a protected industrial-voltage input.

MAX-M10S provides UART to ESP GPIO43/44 and PPS to FPGA G0 / ESP GPIO38. Its RF pin 11 connects straight along the top layer to J5, following the original board's topology. The receiver was moved left to accommodate the larger 0805 bias choke and capacitor. A current-limited 3.3 V active-antenna bias feeds the line through 10 Ω and 27 nH; confirm antenna current/voltage and RF performance. VCC_RF is unused. Backup power follows the receiver supply; there is no battery.

## Precision oscillator

Y1 is the manually assembled **Abracon AOC97FAJC-10.0000**, 10 MHz, 3.3 V OCXO. It has a dedicated TPS62160 1 A buck supply, local bypassing, and a 33 Ω series clock resistor to J2 pin 32 / FPGA IOB_3B_G6. Allow the specified warmup before precision measurements. This is a concrete replacement for the original project's unpopulated, untested oscillator provision; firmware must be adapted to 10 MHz.

Y1 is separately procured and excluded from the JLCPCB placement/BOM pair. Its local 3D model is an illustrative dimensional envelope, not manufacturer CAD.

## Stackup and release checks

Nominal 1.3 mm, four-layer JLC04161H-7628 construction is intended for the SMA slots. Outer copper 0.035 mm; outer dielectric 0.21040 mm; inner copper 0.0152 mm; core dielectric 1.065 mm. Source: https://jlcpcb.com/impedance . The nominal RF feed remains 0.23 mm wide with a 0.15 mm coplanar-ground clearance target. This is a routing target, not a verified impedance result: confirm stackup, uninterrupted return geometry and the bias-tee discontinuity before release. USB differential routing also remains to be completed and reviewed.

The intended optical word is in 1/65536-second units (15.258789 µs per LSB). Sub-LSB calibration uses rolling-shutter transitions; the hardware alone does not establish absolute microsecond accuracy. Existing firmware is incomplete. `docs/display-map.json` and `docs/circuit.json` define the current mapping and circuit.

Canonical KiCad files are authoritative. Initial construction scripts are destructive and must not be rerun over incremental layout work. Current BOMs are design-review artifacts; fabrication outputs remain withdrawn until routing, ERC/DRC/parity, assembly orientation, power and RF review are complete.

## Schematic presentation

The complete circuit is on one A1 sheet, with dashed functional sections matching the module schematic. Filters, regulator support parts, bias networks and decouplers are connected by wires and conventional supply/ground symbols. The optical display is grouped into four banks of four columns, each showing its four individual resistor/LED branches, MOSFET and bypass pair. The single-page PDF is `docs/calibrator-schematic.pdf`. Regenerate with `tools/hardware/calibrator_schematic.py`; the generator preserves the audited circuit contract and changes PCB schematic paths only.

### Trigger input filter

C75 is 1 nF C0G, 50 V, 2%, 0805 (CCTC TCC0805COG102G500BT,
JLCPCB C5375915), shunting TRIGGER_LIMIT to GND after R8 (1 kohm).
It sits beside U9 IN+, with its ground pad thermally connected to the ground pour.
With R9 = 100 kohm, ideal low-impedance 0–5 V drive and a 2.5 V threshold,
tau is 0.990 us, cutoff is about 161 kHz, and nominal rising/falling threshold
latencies are 0.696/0.676 us (before comparator/translator delay).
These are calculated RC delays, not measured calibration constants. Source impedance,
amplitude, edge slew and component tolerances change them; short pulses can be rejected.
Account for the complete input path when validating absolute trigger timing.

### Date/time OLED

DS1 is the HS HS96L03W2C03 (LCSC C5248080), a white 0.96-inch 128x64
SSD1315 I2C OLED module. It is manually installed below the daughterboard/OCXO,
with its four-pin edge toward the top of the carrier. Pin order is GND, 3.3V,
SCL, SDA; the default 7-bit I2C address is 0x3C. ESP_GPIO2 (J1.14) is SCL and
ESP_GPIO1 (J1.13) is SDA. These module pins were previously unused on this carrier.
R174/R175 are 4.7k pull-ups to +3V3_LOGIC. C76/C77 provide 100nF/10uF locally.
All support passives are 0805. Do not supply this module or its bus with 5V.

The footprint uses the manufacturer's 27.30 x 27.80 mm outline, a centered
four-pin 2.54 mm header 1.32 mm from its top edge, and a 23.30 x 23.80 mm mounting
hole grid. Use M2 hardware and 3 mm insulating standoffs; the module's holes are
2.5 mm and carrier holes 2.7 mm. Fit straight 0.64 mm square header pins through
the carrier's 1 mm plated holes and solder manually. Confirm the received
module/header and mounting hardware before assembly. Keep the region beneath
its body free of added tall components. The STEP is an illustrative envelope,
not a manufacturer model; screen contents are not implemented.

The logic LDO powers the display; reserve 50mA in the power budget (about 85mW
additional dissipation in the 5V-to-3.3V LDO at that allowance). The display is
for human-readable date/time/lock status, not the calibrated optical time code.
Firmware should start with 100kHz I2C, validate actual bus rise time and any
on-module pull-ups, and can blank the OLED during optical measurements if needed.
The LCD/OLED datasheet mixes module and bare-panel voltage tables: follow its
3.3V module drawing and verify the received module at bring-up.

The module-v1 body outline is on F.Fab and grouped in KiCad with J1, J2 and H1.
Its current limits are x145..165, y10..55 mm. Use the group when moving the module
interface: 25 mm connector spacing and the midpoint hole must stay fixed.
`tools/hardware/calibrator_module_boundary.py` regenerates the envelope from J1
and verifies the other two anchors. A KiCad group is an editing aid, not a solver;
moving an individual member after entering/ungrouping it can still break alignment.

### Right-edge connector spacing

USB J3 is centered at y30 mm, trigger input J6 at y50, output J7 at y70,
and GPS antenna J5 at y90: **20 mm between adjacent connector centerlines**.
The right corner mounts remain at (196,14) and (196,106) mm, giving 13 mm
vertical center spacing to the nearest connector. Actual foot/washer/cable
clearance depends on the hardware selected. GPS circuitry moved upward together
with its jack, preserving the straight 9.21 mm antenna feed.

The GPS feed targets 50 ohm on nominal **1.3 mm JLC04161H-7628**:
0.23 mm width, 0.15 mm coplanar gap, 0.2104 mm to In1 GND. See
[the recorded impedance calculations](docs/rf/GPS-FEED.md).

### Display mounting hardware

The OLED uses four Würth 960030010 insulating spacers (3 mm), M2×10 screws,
M2 nuts and insulating washers. See [mounting/assembly notes](docs/display-mounting.md)
and the separate [mechanical BOM](docs/mechanical-bom.csv). This hardware is not
part of the SMT BOM/CPL. The 3D display envelope includes the spacers.
