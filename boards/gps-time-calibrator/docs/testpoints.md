# Bring-up test points

31 labeled bare-copper signal/power probe pads. Dedicated ground pads were removed at the user’s request; use the grounded SMA connector shields. The 16 per-channel LED gate/drain pairs were removed at the user’s request; use the existing large LED, resistor and MOSFET pads. TP31–TP62 are deliberately unused reference numbers.

All pads are on the component side, outside the assembled module, OLED, mounting hardware and other component envelopes. Functional labels are 0.9 mm silkscreen text. `testpoint-audit.json` records native pad and label access checks; native DRC separately verifies electrical and silkscreen/mask clearance.

All 31 pads are uniformly 1 mm in diameter. These are bare probe pads, not fitted wire loops. TP6, TP64 and TP63 form a vertical column at X=146.25 mm beside the OCXO.

No paste apertures, purchased parts, BOM entries or placement entries. The bare pads connect solidly to same-net copper zones; soldering thermal reliefs are unnecessary for these unpopulated features.

## Probe use

- `CLK_FPGA` sits directly on the receiver-side clock route after R173, with no testpoint branch. Use a low-capacitance probe and a short connection to existing ground copper; probing still loads the clock.
- `PPS_SRC` is on the common GPS PPS net near its indicator branch; `PPS_FPGA` and `PPS_ESP` are after their respective source resistors. These are electrical access points, not calibrated timing-reference planes. Include probing and propagation delay in timing characterization.
- `GPS_TX` is GNSS TX → ESP RX; `GPS_RX` is GNSS RX ← ESP TX.
- `I_MON` is the filtered ADC node after R176. Do not drive it. The eFuse programming/mirror node itself has no added testpoint.
- `BOOT_N` may be grounded for recovery during reset/power-up; it is not an added reset circuit.
- `ANT_PWR` and `ANT_BIAS` are on the DC side of the antenna bias network. No probe pad was added to GNSS_RF or USB D+/D−.
- The SMA connectors already expose the external trigger input and output.

## Point map

| Ref | Silkscreen | Net | Pad Ø (mm) | X / Y (mm) |
|---|---|---|---:|---|
| TP1 | VBUS | `USB_VBUS` | 1 | 187.050 / 14.500 |
| TP2 | 5V_LOAD | `VIN_5V` | 1 | 168.050 / 43.000 |
| TP3 | 3V3_LOGIC | `+3V3_LOGIC` | 1 | 167.637 / 18.000 |
| TP4 | 3V3_CC | `+3V3_CC` | 1 | 177.137 / 19.550 |
| TP5 | 3V3_GPS | `+3V3_GPS` | 1 | 178.300 / 73.550 |
| TP6 | 3V3_OCXO | `+3V3_OCXO` | 1 | 146.250 / 57.500 |
| TP7 | LOAD_EN | `ESP_GPIO4` | 1 | 180.887 / 30.500 |
| TP8 | OCXO_EN | `ESP_GPIO5` | 1 | 164.700 / 61.900 |
| TP9 | GPS_EN | `ESP_GPIO6` | 1 | 170.246 / 77.633 |
| TP10 | PD_SDA | `USB_PD_SDA` | 1 | 192.700 / 23.500 |
| TP11 | PD_SCL | `USB_PD_SCL` | 1 | 193.000 / 21.500 |
| TP12 | I_MON | `ESP_GPIO3` | 1 | 177.695 / 33.800 |
| TP13 | PPS_SRC | `GPS_PPS` | 1 | 170.200 / 97.200 |
| TP14 | PPS_FPGA | `FPGA_IOT_46B_G0` | 1 | 171.409 / 83.921 |
| TP15 | PPS_ESP | `ESP_GPIO38` | 1 | 167.500 / 81.100 |
| TP16 | CLK_FPGA | `FPGA_IOB_3B_G6` | 1 | 161.171 / 58.059 |
| TP17 | TRIG_FILT | `TRIGGER_LIMIT` | 1 | 186.300 / 44.750 |
| TP18 | TRIG_2V5 | `TRIGGER_VREF` | 1 | 185.000 / 58.000 |
| TP19 | TRIG_CMP | `TRIGGER_5V` | 1 | 179.700 / 57.000 |
| TP20 | TRIG_3V3 | `TRIGGER_3V3` | 1 | 176.954 / 48.000 |
| TP23 | OUT_FPGA | `FPGA_IOT_51A` | 1 | 182.613 / 71.350 |
| TP24 | OUT_DRV | `TRIGGER_DRV` | 1 | 188.588 / 72.500 |
| TP25 | GPS_TX | `ESP_GPIO44_RXD` | 1 | 171.500 / 66.450 |
| TP26 | GPS_RX | `ESP_GPIO43_TXD` | 1 | 166.550 / 35.500 |
| TP27 | GPS_RST_N | `GPS_RESET_N` | 1 | 178.213 / 94.487 |
| TP28 | ANT_PWR | `ANT_PWR` | 1 | 189.500 / 77.338 |
| TP29 | ANT_BIAS | `ANT_BIAS` | 1 | 196.000 / 78.000 |
| TP30 | LED_OE_N | `FPGA_IOT_44B` | 1 | 58.575 / 21.137 |
| TP63 | OLED_SCL | `ESP_GPIO2` | 1 | 146.250 / 68.088 |
| TP64 | OLED_SDA | `ESP_GPIO1` | 1 | 146.250 / 65.388 |
| TP65 | BOOT_N | `ESP_GPIO0_BOOT` | 1 | 166.621 / 14.000 |

## Validation

- Native ERC: 0 violations. Native DRC: 0 violations, 0 unconnected items, 0 schematic-parity issues.
- Access audit: 31 pads and their functional labels clear all component and assembled module/OLED envelopes.
- Native drill-to-SMD-pad audit: 0 encroachments, including a 0.05 mm drill margin.
- GPS-side passives R177/R7/R6/C8/C9/R180/R179 align at X=174 mm. Their local routes and TP13 were adjusted. FPGA_IOT_48B now remains on F.Cu at J2; two unnecessary transition vias were removed. No added branch on CLK_FPGA.
- Native top-view 3D render inspected for visible pads and labels; fabrication outputs republished with matching source hashes. BOM/CPL remain 36 groups / 290 populated placements.
- The broader kct/plugin heuristic audit is **not green**: 57 errors, 4,824 warnings and 25 informational findings. It runs `check --drc-only --mfr jlcpcb`, `detect-mistakes`, and `optimize-traces --dry-run`.

The new probe-related silk flags disagree with native mask/glyph checks and the inspected native render: kct reports transformed board-line locations outside their actual native line extents, and conservative bounding boxes near ANT_BIAS. The 0.9 mm probe label height is an intentional compact, uniform exception to the general 1 mm preference. Bare copper test points need no assembly models, paste or soldering thermal reliefs. Native pad/label obstruction checks and native DRC pass; no rule was disabled. Previously documented optical text, false supply-pin/bypass classifications, all-to-all capacitor distances, unchanged USB full-speed skew and generic power/placement heuristics remain prototype review items. See the retained quality summary and prior GPS/power review notes. This change is not a whole-board production qualification.

TRIG_3V3 is the shared trigger probe. TP21/TRIG_FPGA and TP22/TRIG_ESP were removed with their branch stubs; the large series-resistor pads remain accessible on each destination side.
