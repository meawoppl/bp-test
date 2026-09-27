# OLED mounting: soldered 1x4 header, 3 mm gap

DS1 (HS96L03W2C03, LCSC C5248080) is permanently soldered to the carrier through a **straight 1x4 male pin header, 0.1 inch / 2.54 mm pitch**. There is no socket. Four **3 mm insulating spacers** and M2 screws/nuts carry mechanical loads. This replaces the former 6 mm mounting specification.

## Hardware per carrier

| Qty | Item | Specification |
| --- | --- | --- |
| 1 | Würth **61300411121**, WR-PHD | Standard straight 1x4 male header; 2.54 mm pitch; 2.54 mm plastic body; nominal 0.64 mm square pins; 3 mm solder tails / 6 mm upper pins |
| 4 | Würth **960030010**, WA-SPARO | Black polyamide spacer; 3 mm long; 4 mm OD; 2.2 mm bore |
| 4 | M2 × 10 mm machine screw | 0.4 mm pitch; pan head no larger than 4 mm OD; stainless steel |
| 4 | M2 hex nut | 0.4 mm pitch; nominal 1.6 mm thick |
| 8 | M2 insulating washer | Nylon; 2.2 mm bore; OD <=4 mm; 0.3 mm thick |

Verified drawings: [header](https://www.we-online.com/components/products/datasheet/61300411121.pdf), [spacer](https://www.we-online.com/components/products/datasheet/960030010.pdf). Matching generic headers are acceptable if these dimensions match. Hardware is listed in [mechanical-bom.csv](mechanical-bom.csv), separate from the SMT BOM/CPL. JLC installation would require an explicit mechanical-assembly agreement; the files currently specify manual assembly.

## Stack and soldering

From top: screw head, insulating washer, OLED PCB, 3 mm spacer, carrier PCB, insulating washer, nut. Washers stay outside the board-to-board gap. Nominal under-head stack is 1.2 + 3 + 1.6 + 0.6 + 1.6 = **8 mm**, leaving approximately 2 mm of thread beyond the nut with M2x10 screws. Tighten gently without flexing the display.

Seat the header plastic on the carrier top, with 3 mm tails through the carrier. Its 6 mm upper pins extend through the display. The spacers set OLED underside height to **3 mm above carrier top**, leaving nominal 0.46 mm above the header plastic. With the illustrative 1.2 mm display PCB, untrimmed pins project 4.34 mm above the display PCB: trim them to about 1 mm projection (keep clippings away from the glass), then solder the exposed display-top joints and carrier-underside joints. Assemble the spacers before final soldering so joints are not mechanically preloaded. Header pin 1 is GND, then 3.3 V, SCL, SDA.

The carrier header has four 1.1 mm finished holes at 2.54 mm pitch. Mounting-hole grid is **23.3 × 23.8 mm**: (135.35,76.10), (158.65,76.10), (135.35,99.90), (158.65,99.90) mm. Carrier mounting holes are 2.7 mm; OLED drawing specifies 2.5 mm, suitable for M2 hardware.

First assembly must verify actual display PCB thickness, top-pad solder access and underside component height: the display 3D model is an envelope, not a detailed vendor model. Keep carrier components out of the display underside area. Do not force a supplied pre-soldered or right-angle header into this stack; use the specified straight header. If underside components exceed the available 3 mm clearance, revise the spacer height before assembly.

## I2C routing

SDA (ESP_GPIO1) and SCL (ESP_GPIO2) follow the same right-side B.Cu corridor with parallel 45-degree bends. Traces are 0.25 mm wide; their vertical runs have 0.6 mm center spacing (0.35 mm copper gap). Pull-up branches remain local to the display. They are single-ended I2C signals, not a differential pair.
