# OLED display mounting and assembly

For the GPS time calibrator carrier and **HS96L03W2C03 (C5248080)** display. The display faces upward, with its four-pin header edge toward the OCXO and daughterboard. Use a straight **1x4, 2.54 mm (0.1 inch) male header soldered to both PCBs**, without a socket. Four insulating spacers support the display; the solder joints must not carry mounting loads.

## Parts for one board

| Qty | Part | Specification |
| --- | --- | --- |
| 1 | Display | HS96L03W2C03, C5248080 |
| 1 | Straight header | J8: Wurth 61300411121 / C5184785; 1x4, 2.54 mm pitch, 0.64 mm square pins; 2.54 mm plastic body, 3 mm short tails, 6 mm long ends |
| 4 | Insulating spacer | Wurth 960030010; 3 mm length, 4 mm OD, 2.2 mm bore |
| 4 | Screw | M2x10, 0.4 mm pitch; pan head no larger than 4 mm OD |
| 4 | Nut | M2, 0.4 mm pitch; nominal 1.6 mm thickness |
| 8 | Insulating washer | Nylon; 2.2 mm bore, at most 4 mm OD, nominal 0.3 mm thickness |

J8 is a separate JLCPCB BOM/CPL item (C5184785), fitted to the carrier by through-hole assembly. DS1 and the spacers/screws/nuts/washers remain manual-assembly items; see mechanical-bom.csv. A generic header is acceptable only if its dimensions and straight-pin geometry match; do not substitute a socket or right-angle header.

## Orientation and pin order

View the carrier from its component side, with the LED array to the left and USB/SMA connectors to the right. Place the display below the OCXO, screen upward, header along its upper edge. From **left to right** along that header:

| Pin | Display marking | Carrier connection |
| --- | --- | --- |
| 1 | GND | Ground |
| 2 | VCC | +3V3_LOGIC, 3.3 V only |
| 3 | SCL | ESP_GPIO2 |
| 4 | SDA | ESP_GPIO1 |

Check the markings on the received display before soldering. Do not infer the pin order from another four-pin OLED model. Do not apply 5 V to the display or I2C pins.

## Mechanical stack

At each mounting hole, from top to bottom:

1. M2 screw head.
2. Insulating washer.
3. OLED module PCB.
4. **3 mm insulating spacer.**
5. **1.6 mm carrier PCB.**
6. Insulating washer.
7. M2 nut.

The 3 mm dimension is the clear distance from carrier top to display PCB underside. Keep washers outside this gap. The header plastic sits on the carrier top and nominally clears the display underside by 0.46 mm.

Mounting-hole centers form a **23.30 x 23.80 mm** rectangle. The carrier holes are 2.7 mm and the display drawing specifies 2.5 mm. Use M2 hardware, not M3. With an illustrative 1.2 mm display PCB and 1.6 mm nut, the stack below the screw head is about 8 mm, leaving about 2 mm of M2x10 thread beyond the nut. Measure the received parts; display PCB thickness is not yet verified.

## Assembly procedure

1. **Disconnect USB and all other power.** Inspect the received display for damage, underside components, and accessible top-side header solder pads. Check the pin order above. If a different header is already fitted, do not force it into this stack; obtain the bare module or have that header removed properly.
2. **Check the fitted header, or dry-fit it if supplied loose.** Put its short 3 mm tails down through the carrier's four plated holes, with the plastic seated on the carrier top and the 6 mm ends pointing up. Do not solder yet.
3. **Dry-fit the display and hardware.** Fit four 3 mm spacers, slide the display over the long pins, and loosely install all four screw/washer/nut stacks. The screen must sit flat on all spacers without pressing on the header plastic or underside components. Confirm access to all four display-top solder pads. If it does not fit, resolve the spacing before soldering; do not pull it into place with the screws.
4. **Mark and shorten the upper pins.** Mark each pin about 1 mm above the display PCB. Remove the display, lift out the header, and cut at those marks away from the screen and boards. Deburr and remove all metal clippings. The expected removal is roughly 3.3 mm from each long end for a 1.2 mm display PCB, but use the actual dry-fit marks rather than this estimate.
5. **Reassemble and align.** Refit the header, spacers, display, washers and screws. Tighten the nuts only enough to seat the stack evenly. Do not flex the display PCB, press on the glass, or overtighten the nylon spacers.
6. **Tack and inspect.** Tack one outer header pin on the carrier underside and one on the display top. Check that the display is parallel to the carrier, all spacers remain seated, and every pin passes through both boards. Reflow the tack joints if alignment needs correction; do not bend the assembly against solid joints.
7. **Solder all eight joints.** Solder the four carrier-underside joints and four display-top joints. Use brief, controlled heating and avoid touching the glass or flex with the iron. Support the assembly by the carrier while turning it over, never by the screen. Inspect for full pad wetting and solder bridges. The short carrier tails nominally project 1.4 mm below the 1.6 mm carrier; trim only excessive protrusion if necessary and collect the clippings.
8. **Finish the mechanical inspection.** Verify all four spacers are seated, the PCB is unbowed, no hardware touches exposed circuitry or the glass, and no clippings or flux residues remain where they could cause a short. Keep any protective screen film on until soldering and cleaning are complete; use only display-compatible cleaning methods.

## Checks before power-up

- Verify continuity through each header pin from carrier pad to corresponding display pad.
- Check for unintended solder bridges between adjacent pins and a persistent low-resistance short between 3.3 V and ground. Capacitors and on-module circuitry can affect resistance readings; investigate a suspicious reading rather than using the continuity beep alone as a pass/fail test.
- Confirm the four connections by pin number: GND, 3.3 V, SCL/GPIO2, SDA/GPIO1.
- At first powered bring-up, verify the display supply is approximately 3.3 V. With suitable firmware, the expected default 7-bit I2C address is **0x3C**. A blank display alone does not establish an assembly fault; firmware must initialize it.

## Fit status and source drawings

The carrier and illustrative 3D envelope use this mounting arrangement. The first physical assembly must confirm actual module PCB thickness, underside clearance, glass-to-screw clearance and top-pad solder access. The 3D model is not a detailed vendor model. If the 3 mm gap is insufficient, revise the spacer/header combination before soldering.

Local source drawings: libraries/datasheets/HS96L03W2C03.pdf, Wurth-61300411121.pdf, and Wurth-960030010.pdf (paths relative to repository root). The header is permanently soldered; removing the display later requires desoldering its four pins.

## JLCPCB header purchasing entry

J8 is Wurth 61300411121, JLCPCB C5184785 (one per board), separately listed from DS1. JLC lists it for wave-solder assembly on Economic and Standard services: https://jlcpcb.com/partdetail/C5184785 . No spacers or mounting hardware are included in the JLC assembly BOM. J8 owns the four plated holes; DS1 retains the display outline, mechanical holes, and elevated display model. The display projection is a mechanical drawing rather than a carrier-level courtyard because it intentionally covers J8. Header pins are shown at their nominal untrimmed length; trim after fitting the display as described above.
