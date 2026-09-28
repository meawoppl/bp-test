# MAX-M10S reference reconciliation — 2026-09-27

Reference: [SparkFun MAX-M10S v1.0 schematic](references/SparkFun_u-blox_GNSS_MAX-M10S_Schematic_v10.pdf),
2022-08-16, SparkFun Electronics, CC BY-SA 4.0. Used as a circuit reference;
our carrier symbols and layout remain project-local.
Manufacturer references: [MAX-M10S datasheet](https://content.u-blox.com/sites/default/files/MAX-M10S_DataSheet_UBX-20035208.pdf)
and [integration manual](../../../libraries/datasheets/MAX-M10S-integration.pdf).

## Changes

- Removed U16 and C79. TIMEPULSE drives D74 through its own 1k R179, as in
  SparkFun's PPS indicator. R179 sits at the source end of the indicator branch;
  the LED remains immediately above antenna SMA J5. Typical current is about
  1mA; u-blox specifies output logic levels at 2mA. The LED does not require
  a separate driver. The prior high-impedance buffer justification was overly
  conservative relative to this reference circuit.
- Removed U8 TPS2553 and C12. U6 pin 14 (VCC_RF) now supplies the antenna
  through R5, C10 and L1. VCC_RF is the receiver's internally RF-filtered supply,
  not an independently current-limited output. Limit antenna operating current
  to 50mA, allow its voltage drop and the 10-ohm feed-resistor drop, and do not
  assume this simplified circuit tolerates a sustained antenna-cable short.
- R6/R7 PPS source resistors changed from 100 to 33 ohms, matching the reference
  damping value. Separate branches still serve FPGA G0 and ESP32 GPIO38.
- Added R180, 33 ohms: carrier J1.21 / ESP_GPIO40 -> R180 -> U6.9 RESET_N.
  The frozen module maps J1.21 to ESP32 U1 package pin 44 / GPIO40.
  Assert reset low for at least 1ms, then release to high impedance using
  open-drain mode. Keep it released while GPS is off; do not drive it high
  from the always-on domain into an unpowered receiver. No extra pull-up is
  added. Firmware changes are not included.
- Corrected the U6 symbol's previously incorrect unused pin names:
  15 VIO_SEL, 16 SDA, 17 SCL, 18 SAFEBOOT_N. They remain unconnected;
  VIO_SEL open selects 3.3V I/O. No physical pad-number changes.
- Straightened the J1 PPS/trigger exits and adjacent UART traces. Removed
  backward takeoffs and the tiny staircase around the mounting-hole clearance;
  replacements use straight sections and 45-degree corners.

## Intentional application differences

- Keep GPIO-switched U5 and its supply bypassing: the carrier must switch GPS
  power independently. The reference breakout has no such requirement.
- Keep the comparator and U7 for the external 5V trigger input. They provide
  the requested 2.5V threshold and 3.3V translation; MAX-M10S EXTINT does not
  accept an unconditioned 5V trigger.
- Keep both PPS consumers and UART. I2C/Qwiic headers and backup coin cell
  are not added; backup power still follows the receiver supply.
- Keep the existing 0805 27nH bias choke and 10nF RF bypass rather than copying
  an unspecified-value/reference ferrite footprint. RF impedance uses this
  carrier's 1.6mm four-layer stackup, not SparkFun's two-layer 1mm-wide feed.
- SparkFun has a PESD0402-140 RF ESD suppressor. It is not fitted in this
  revision pending the user's requested package-size preference; it is an
  outstanding protection difference, not functionality supplied by the module.
  This board must not be represented as having equivalent antenna ESD protection.

## Bring-up

Validate cold-start with the direct LED, PPS rise time/timing at FPGA and ESP32,
reset assertion/release, antenna current and voltage, and reception with the
selected active antenna. TIMEPULSE also affects boot mode; the reference uses
this small LED load, but additional loads or a hard pull-down are not permitted.
PPS indication follows configured pulse polarity/width and is not a separate
fix-valid output. RF, thermal and optical qualification remain prototype tests.

## Schematic presentation

The GPS block is narrowed from 302.26 to 236.22 mm. The two independently
damped PPS branches leave TIMEPULSE to the left and rise to explicit FPGA G0
and ESP32 GPIO38 destinations; R179/D74 are wired into the same tree.
The VCC_RF bias tee sits immediately beside RF_IN instead of stretching
across most of the block. Pin numbers, net connectivity and PCB layout are
unchanged by this presentation pass.
