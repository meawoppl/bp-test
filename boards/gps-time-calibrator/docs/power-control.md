# Always-on controller and switched loads

Updated 2026-09-27. The ordered daughterboard v1 is unchanged.

## Domains

USB VBUS feeds the daughterboard's 5 V contacts, U2 (+3V3_LOGIC), U12 (+3V3_CC), and U11 directly. The controller, OLED, LED buffers and PD sink can therefore start while the high-current load domain is off. U13 NOR and C67 were removed.

U14 TPS259531 enables the switched `VIN_5V` domain: LED anodes, 5 V trigger circuitry, U5 GPS LDO input, and U15 OCXO LDO input. U5 and U15 have independent active-high enables with 100k pulldowns. U7 trigger translation and its C11 bypass use +3V3_GPS so the translator cannot drive an unpowered GNSS EXTINT pin. This also means the translated input trigger is unavailable while GPS power is off.

| Carrier J1 contact | Frozen module ESP32-S2 GPIO | Function |
|---|---|---|
| 15 | GPIO3 / ADC1_CH2 | Filtered eFuse current monitor |
| 16 | GPIO4 | U14 switched 5 V enable |
| 17 | GPIO5 | U15 OCXO 3.3 V enable |
| 18 | GPIO6 | U5 GPS 3.3 V enable |
| 19 | GPIO7 | HUSB238 SDA (USB_PD_SDA) |
| 20 | GPIO8 | HUSB238 SCL (USB_PD_SCL) |

U11 is now **HUSB238_002DD (C7471904)**, a USB-PD sink with I²C address **0x08**. GPIO7/SDA and GPIO8/SCL have 10k pull-ups to +3V3_CC; start at 100 kHz and check rise time on hardware. VSET is directly grounded for **5 V**, and R164 = 22.6k (C3016901) selects a **3 A request**. C64 is 1uF/50V X7R (C28323), immediately adjacent to VIN. The old R165/R166 VBUS detector chain is removed. No external Rd resistors are required.

**This board must never request more than 5 V.** The raw VBUS domain feeds the module and AP2112 regulators directly. I²C overrides the hardware voltage setting: use status reads only during bring-up; firmware must reject every request other than 5 V. A 3 A request does not guarantee a 3 A contract—read actual source capability/contract and keep switched loads off if insufficient.

HUSB238 D+/D− charger-detection pins are intentionally unconnected: USB data runs only to the ESP32 through its existing ESD device. Legacy BC1.2/Apple charger classification is therefore unavailable; do not treat its charger-detection result as permission to draw extra current. GATE is intentionally unused; TPS259531 remains the load switch and current monitor. Non-PD sources require valid Type-C current status plus USB enumeration/suspend limits; if status is uncertain leave high-current loads disabled.

## Firmware sequencing contract (firmware not implemented)

1. Boot with GPIO4/5/6 low, ADC GPIO3 input-only without internal pulls, and display-buffer OE inactive. Keep early boot and radio activity inside the available USB budget.
2. Read/debounce the HUSB238 source/current and contract status and, where relevant, honor USB enumeration/suspend limits. Budget daughterboard and always-on loads as well as the switched loads.
3. Enable GPIO4, wait for the eFuse output to settle (nominal ramp about 12 ms), then enable GPS/OCXO as permitted. For initial bring-up require a verified 3 A source before enabling all subsystems.
4. The OCXO warm-up is up to 2.1 W at 3.3 V, about 0.636 A. A linear regulator draws approximately that same current from 5 V; it does not have the former buck's input-current saving. Wait for oscillator warm-up and measure lock/timing before trusting calibration.
5. Before GPS-off, stop UART transmission and set the controller TX pin high impedance; do not back-power the GNSS through its UART. Disable clock consumers before OCXO-off. Blank LEDs before disabling the 5 V load domain.
6. Respond to reduced source advertisement by shedding load. There is no longer a NOR hardware policy that requires 3 A. The eFuse still independently limits current and shuts down on its own protection conditions.

No new temperature sensor was added. ESP32-S2 internal die temperature is not an OCXO or ambient temperature measurement.

## eFuse telemetry

TPS259531 ILM is both a current-limit programming node and a current monitor. R170 stays **820 ohm**, giving approximately **2.48 A nominal limit**. R176 = 100k isolates it from C78 = 100nF and the ADC; the filter is approximately 10 ms. Do not put a large capacitor directly on ILM and do not drive GPIO3 as an output.

Nominal mirror gain is 276 microamp/A, hence `V_ADC ≈ I_switched × 0.22632 V/A` and `I_switched ≈ V_ADC / 0.22632`. Approximately 0.56 V corresponds to the nominal limit. TI specifies mirror gain tolerance (249–304 microamp/A at 1 A), and ADC error adds to it: calibrate against a meter. This is slow telemetry, not the protection loop. It measures **switched loads only**; raw-VBUS daughterboard/logic current bypasses U14 and must be included separately in the USB budget.

## OCXO linear regulator and heat spreading

U15 is **TPS7A4533DCQR, LCSC C2877942**, fixed 3.3 V, 1.5 A, SOT-223-6. Pins 1 EN, 2 IN, 3 GND, 4 OUT, 5 SENSE (connected locally to OUT), 6 grounded tab. The former TPS62160, L2 and R171/R172 feedback divider are removed. C70 is 10uF input bypass; C71 is 22uF/25V output bypass; C73/C74 retain 100nF/10uF at Y1. The LDO needs at least 10uF effective output capacitance; verify C71's DC-bias/tolerance/temperature derating at 3.3 V when substituting parts. C72 is removed.

The regulator sits below/right of Y1, with a front-copper heat spreader covering approximately x142–166, y56.7–73.3 mm (398.4 mm² before clearance cutouts). The complete thermal area fits between the daughterboard bottom edge at y55 and the OLED top edge at y74.1: the outer moat boundary leaves 1.1 mm to the daughterboard and 0.2 mm to the display body. Y1 is centered at (153,62) and U15 at (160.5,70), both entirely outside the daughterboard body. The display and mating connector positions are unchanged. A **0.6 mm moat in F.Cu** separates this pour from the surrounding front ground pour. U15 ground/tab pads connect solidly to it. External ground vias near the tab and the existing ground network maintain a low-impedance electrical return. In1 ground remains continuous beneath the clock: this is **partial thermal isolation of the top copper**, not a fully thermally isolated oven island, slot or independent ground domain.

At 5.0 V and 2.1 W/3.3 V load, pass-element dissipation is about **1.08 W**, rising to **1.24 W at 5.25 V**, plus regulator ground-current loss. TI's 50.5 °C/W SOT-223 reference-board figure would imply about 55–63 °C junction rise, but is **not a validated thermal model of this layout**. The compacted spreader is about 35% smaller than the earlier 610 mm² version; do not assume its thermal resistance is unchanged. The OCXO itself heats the local region; copper size, enclosure, airflow and silicon temperature must be measured. Target junction below 125 °C with margin, using the datasheet's thermal-characterization method. Test worst-case warm-up at maximum intended ambient and input voltage and confirm no thermal cycling or frequency upset. Change copper/isolation if measurements demand it.

Some LDO heat may warm the oscillator's surroundings; no reduction of oven power or improvement in frequency stability is claimed. The internal oven remains responsible for temperature control. The chip's built-in thermal shutdown is fault protection, not a normal operating thermostat.

The local STEP is a **drawing-derived illustrative envelope**, generated by `tools/hardware/calibrator_ldo_model.py`, not vendor CAD. Review U15 orientation in the assembler preview before ordering.

## References and validation

- [TPS7A45 PDF](../../../libraries/datasheets/TPS7A45.pdf) / [text](../../../libraries/datasheets/TPS7A45.md)
- [TPS2595 PDF](../../../libraries/datasheets/tps2595.pdf) / [text](../../../libraries/datasheets/tps2595.md)
- [HUSB238 PDF](../../../libraries/datasheets/HUSB238.pdf) / [text](../../../libraries/datasheets/HUSB238.md)
- [AOC97 PDF](../../../libraries/datasheets/AOC97.pdf) / [text](../../../libraries/datasheets/AOC97.md)

Native ERC/DRC/parity reports are generated with the final fabrication build. Electrical checks do not validate RF performance, USB power compliance, heat flow, ADC accuracy or oscillator timing. These remain prototype bring-up measurements.

### Broader quality audit

The post-change heuristic audit reports **51 errors, 4,718 warnings and 31 info**, compared with 65 errors/4,722 warnings/31 info before the OCXO swap. It is not a green quality signoff. Saved counts are in `power-quality-summary.json`.

Examples reviewed: it misclassifies USB data and trigger signals as supply pins, generates thousands of all-to-all bypass-distance warnings, and reports R175 via-in-pad despite the native rotated-pad geometry audit finding zero drill encroachments. It applies a USB high-speed length rule to the unchanged full-speed USB pair (3.4 mm difference). Optical row/bit labels intentionally remain on silk. Existing low-current power-branch and silk heuristics remain part of prototype review rather than being suppressed globally. The LDO thermal assessment above is a separate hardware validation gate.

## GNSS reset and antenna update

Carrier J1.21 / ESP32 GPIO40 controls U6 RESET_N through R180 33R. Use open-drain low for at least 1ms, then release; keep released while GPS power is off. U6 VCC_RF now supplies the passive antenna bias tee. The separate U8 antenna switch and U16 PPS LED buffer are removed; see [reference reconciliation](gps-reference-review.md).
