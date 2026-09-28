# GPS optical time calibrator carrier — revision A, routed prototype

180 × 100 mm carrier for the **ordered module v1**, using the programming carrier's exact mating contacts and pad numbering. The ordered daughterboard and programmer files are unchanged. Connector-first routing is complete with clean native ERC, DRC and schematic parity. See `docs/routing-review.md` and `fab/STATUS.md` for validation scope and prototype bring-up checks.

## Optical display

Four identical rows of sixteen green 1206 LEDs (YLED1206G / C30584801) show bit 15 at the left through bit 0 at the right. Rows update together, without multiplexing. Each LED has its own **470 Ω, 1%, 0805** resistor. Sixteen AO3400A MOSFETs switch the columns through two SN74LVC541 buffers, with individual gate resistors and pulldowns. Each column has 100 nF and 10 µF bypass capacitors. All discrete resistors, capacitors and inductors are 0805 or larger; exact substitutions are in `docs/passive-parts-0805.json`.

Expected display current is approximately 0.26–0.33 A with all LEDs on, depending on LED forward voltage. Equal resistors reduce electrical mismatch but do not remove optical bin variation; use a common LED lot and measure brightness, supply bounce and optical edge timing on assembled hardware.

## USB power and installation

J3 is USB-C power and native USB data. The daughterboard and local logic are always powered from VBUS. The ESP32 reads HUSB238 source/contract status over I²C, enables the TPS259531 switched 5 V domain, and independently controls GPS and OCXO regulator enables. The NOR gate is removed. HUSB238 defaults to a 5 V / 3 A request; higher-voltage requests are forbidden because the always-on domain is fed directly from VBUS.

The eFuse has a nominal 2.48 A switched-load limit and approximately 12 ms ramp. Its current mirror is filtered to ESP GPIO3 / ADC1_CH2. Always-on current bypasses this measurement. Firmware must enforce the source's total budget, sequence the rails, and prevent UART back-powering; this firmware is not implemented here. See [power control, pin mapping and thermal calculations](docs/power-control.md).

There are no BOOT/RUN or RESET switches: the installed module stays in normal run mode using its own strap and EN pullups. Its existing firmware/ROM USB behavior must support the intended recovery procedure; this carrier does not provide a hardware boot override.

The module body extends from x=145 to 165 mm and y=10 to 55 mm, flush with the carrier's top edge. J1/J2 are at (155,24.3) and (155,49.3) mm, retaining 25 mm spacing. H1 is at their midpoint (155,36.8). Retain the programmer's 2.0 mm mounting spacer and frozen connector numbering.

## Right-edge connectors and GNSS

Top to bottom: USB-C J3, input SMA J6, output SMA J7, GPS antenna SMA J5. The SMA connectors are Amphenol 132289 edge-launch parts with approximately 11.43 mm projection beyond the edge and a nominal 1.57 mm (.062-inch) board slot.

Input accepts 0–5 V logic into a TLV3501 comparator referenced to half the 5 V supply, nominally 2.5 V. A 3.3 V Schmitt buffer feeds FPGA, ESP32 and GNSS EXTINT. Output is an AHCT buffer producing 5 V logic into a **high-impedance receiver**, not 5 V into a 50 Ω termination. Neither port should be treated as a protected industrial-voltage input.

MAX-M10S provides UART to ESP GPIO43/44 and PPS to FPGA G0 / ESP GPIO38. Its RF pin 11 connects straight along the top layer to J5, following the original board's topology. The receiver was moved left to accommodate the larger 0805 bias choke and capacitor. The module's VCC_RF output feeds the antenna through 10 Ω and 27 nH; confirm antenna current (50 mA maximum), voltage drop and RF performance. The separate antenna power switch is removed. RESET_N connects to ESP32 GPIO40 through 33 Ω. Backup power follows the receiver supply; there is no battery.

## Precision oscillator

Y1 is the manually assembled **Abracon AOC97FAJC-10.0000**, 10 MHz, 3.3 V OCXO. It has a dedicated TPS7A4533 1.5 A linear supply, enabled by GPIO5, local bypassing, and a 33 Ω series clock resistor to J2 pin 32 / FPGA IOB_3B_G6. Allow the specified warmup before precision measurements. This is a concrete replacement for the original project's unpopulated, untested oscillator provision; firmware must be adapted to 10 MHz.

Y1 is separately procured and excluded from the JLCPCB placement/BOM pair. Its local 3D model is an illustrative dimensional envelope, not manufacturer CAD.

## Stackup and release checks

Nominal 1.6 mm, four-layer JLC04161H-7628 construction is intended for the SMA slots. Outer copper 0.035 mm; outer dielectric 0.21040 mm; inner copper 0.0152 mm; core dielectric 1.065 mm. Source: https://jlcpcb.com/impedance . The nominal RF feed remains 0.26 mm wide with a 0.15 mm coplanar-ground clearance target. The manufacturer coated-coplanar calculation gives 50.50 ohm nominal; see `docs/rf/GPS-FEED.md`. Confirm the finished stackup, launch and bias tee at fabrication/bring-up. USB data is routed as a nearby pair for the module's full-speed interface.

The intended optical word is in 1/65536-second units (15.258789 µs per LSB). Sub-LSB calibration uses rolling-shutter transitions; the hardware alone does not establish absolute microsecond accuracy. Existing firmware is incomplete. `docs/display-map.json` and `docs/circuit.json` define the current mapping and circuit.

Canonical KiCad files are authoritative. Initial construction scripts are destructive and must not be rerun over incremental layout work. Generated fabrication and assembly outputs correspond to the routed PCB. Assembly orientation approval, power/thermal measurements and RF/optical timing validation remain prototype release checks.

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

[Display assembly instructions (PDF)](docs/display-mounting.pdf) · [Editable instructions](docs/display-mounting.md)

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
the carrier's 1.1 mm plated holes and solder manually. Confirm the received
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
The right corner mounts remain at (196,14) and (196,106) mm, giving 16 mm
vertical center spacing to the nearest connector. Actual foot/washer/cable
clearance depends on the hardware selected. GPS circuitry moved upward together
with its jack, preserving the straight 9.21 mm antenna feed.

The GPS feed targets 50 ohm on nominal **1.6 mm JLC04161H-7628**:
0.26 mm width, 0.15 mm coplanar gap, 0.2104 mm to In1 GND. See
[the recorded impedance calculations](docs/rf/GPS-FEED.md).

### Display mounting hardware

The OLED uses four Würth 960030010 insulating spacers (3 mm), M2×10 screws,
M2 nuts and insulating washers. See [mounting/assembly notes](docs/display-mounting.md)
and the separate [mechanical BOM](docs/mechanical-bom.csv). This hardware is not
part of the SMT BOM/CPL. The 3D display envelope includes the spacers.

## Display bus update (2026-09-27)

See [display bus reroute](docs/display-bus-reroute.md) for the new FPGA mapping, shared active-low OE control, OCXO G6 verification and current export convention.

Support passives and routing were tidied further; see [passive cleanup review](docs/passive-tidy-review.md) for current validation and outputs.

The FPGA interface and USB VBUS routes were further simplified; see [I/O routing cleanup](docs/io-routing-cleanup.md).

Reference PDFs and page-numbered Markdown extracts are indexed in [the shared datasheet library](../../libraries/datasheets/README.md).

## Connector-side cleanup and PPS indication

D74 above the GPS SMA follows PPS directly through its own 1k resistor; the redundant buffer is removed. See [GPS reference reconciliation](docs/gps-reference-review.md).
USB power is grouped beside J3, trigger stages align with their SMA ports,
and the input damping resistors and PPS fanout now sit beside their drivers.
See [placement and routing review](docs/io-placement-review.md).

## Bring-up access

The carrier has 33 labeled, unpopulated signal/power probe pads outside the module/display envelopes. See [testpoint map](docs/testpoints.md) and [CSV](docs/testpoints.csv). Per-channel LED probe pads are intentionally omitted; use their existing component pads.

## RFC snapshot — ordering deferred

[The RFC v1 snapshot](releases/rfc-v1/README.md) preserves the current review files.
Wait for validation of the ordered module and programming carrier before ordering this board.

## Firmware integration

Start with the [integration and bring-up guide](docs/integration/README.md) for pin assignments, power sequencing, current monitoring, Affogato/OTA integration, M10S command frames, trigger capture and both displays. This is an implementation guide; it does not claim those firmware services are already implemented.
