# Component and design references

Checked during design, 2026-09-26. Inventory is transient.

- LED: https://www.lcsc.com/product-detail/C30584801.html — YLED1206G, 1206 green; replaces blue YLED1206B. See green-led-review.md for electrical and assembly polarity checks.
- GNSS: https://www.lcsc.com/product-detail/C24834155.html — MAX-M10S-00B-01, seven live units at selection (search snippets were stale).
- GNSS integration: https://content.u-blox.com/sites/default/files/MAX-M10S_IntegrationManual_UBX-20053088.pdf
- Antenna current limit: https://www.ti.com/lit/ds/symlink/tps2553.pdf — ILIM-to-IN fixed 50–100 mA mode.
- GNSS bias choke: https://www.lcsc.com/product-detail/C38841159.html — Coilcraft 0805CS-270XGLC, 27 nH 0805; recommended lands from https://www.coilcraft.com/getmedia/dd5f20e4-1ff7-43df-8317-b693eb2dce3e/0805cs.pdf .
- LED resistor: https://www.lcsc.com/product-detail/C17710.html — 0805W8F4700T5E, 470 ohm 1%, 0805.
- Distributed bulk: https://www.lcsc.com/product-detail/C15850.html — Samsung CL21A106KAYNNNE, 10 µF 25 V 0805 X5R.

Every purchased line in the grouped BOM includes its exact MPN, LCSC identifier and supplier link. J1/J2 use the ordered programming carrier's locally renumbered mating footprints; the frozen module contract, not a generic Hirose pin-number convention, is the electrical authority.

## Power and timing redesign

- OCXO LDO: https://www.ti.com/lit/ds/symlink/tps7a45.pdf — TPS7A4533DCQR / C2877942.
- Local copies and searchable Markdown: [shared datasheet index](../../../libraries/datasheets/README.md).

- USB-C sink detection: https://www.ti.com/lit/ds/symlink/tusb320lai.pdf — GPIO current-advertisement outputs and UFP configuration.
- eFuse: https://www.ti.com/lit/ds/symlink/tps2595.pdf — TPS259531, current limit and startup slew.
- Former NOR enable logic removed; power sequencing now uses ESP32 GPIOs.
- OCXO: https://abracon.com/datasheets/AOC97.pdf — AOC97FAJC-10.0000, 10 MHz variant mechanical drawing and 3.3 V power; manual assembly, not a JLCPCB part.
- Trigger comparator: https://www.ti.com/lit/ds/symlink/tlv3501.pdf .
- 5 V trigger output: https://www.ti.com/lit/ds/symlink/sn74ahct1g125.pdf .
- SMA: https://www.lcsc.com/product-detail/C3172723.html — Amphenol 132289; standard KiCad edge-launch footprint, 1.6 mm PCB.
- Intended stackup: https://jlcpcb.com/impedance — JLC04161H-7628, nominal 1.6 mm.

The full replacement R/C/L mapping is recorded in `passive-parts-0805.json`; the circuit contract and current BOM contain the selected MPNs. Old 0402/0603 parts and the external terminal are superseded. Inventory must be rechecked at ordering.

- Trigger filter C75: [CCTC TCC0805COG102G500BT / C5375915](https://jlcpcb.com/partdetail/CCTC-TCC0805COG102G500BT/C5375915), 1 nF, 50 V, C0G, ±2%, 0805. Catalog specifications checked 2026-09-26; allocation/stock must be checked at order time.

- Date/time OLED DS1: [HS96L03W2C03 / C5248080](https://www.lcsc.com/product-detail/C5248080.html), [manufacturer datasheet](https://datasheet.lcsc.com/datasheet/pdf/4cfb1fe29ff7e4fbff30eb4e2a452c3a.pdf), especially pp. 6–10 for mechanical drawing, four-pin order, default 0x3C address and voltage/current limits. LCSC listed 5,053 stock on 2026-09-26; this is not a reservation. Manual assembly.
- R174/R175 OLED pull-ups: [UNI-ROYAL 0805W8F4701T5E / C17673](https://jlcpcb.com/partdetail/C17673), 4.7k, 1%, 0805.

- C75 input filter replacement (2026-09-27): FH 0805CG102J500NT / C29925, 1 nF, 50 V, C0G, 0805, ±5%; replaces C5375915 / TCC0805COG102G500BT (±2%). Same nominal RC filtering and footprint; wider tolerance accepted for noise filtering, not a timing reference. LCSC listed 163,600 stock at review; JLC assembly stock must be confirmed in the order. https://www.lcsc.com/product-detail/C29925.html

## HUSB238 controller replacement (2026-09-27)

- HUSB238_002DD / C7471904: https://jlcpcb.com/partdetail/Hynetek-HUSB238_002DD/C7471904 (Economic/Standard listed).
- Hynetek full datasheet archived in libraries/datasheets/HUSB238.pdf; pin map table1, VSET table5, ISET table6, DFN drawing figure6.
- R164 22.6k 0805: SCR0805F22K6 / C3016901, https://item.szlcsc.com/18242.html.
- C64 1uF 50V X7R 0805: CL21B105KBFNNNE / C28323, https://www.lcsc.com/product-detail/C28323.html.
- Footprint based on KiCad WDFN-10-1EP 3x3mm / 0.5mm pitch / 1.8x2.5mm EP, matching package maximum exposed-pad dimensions; STEP is a drawing-derived envelope.
- User JLC preview corrections: U7/U10 and Q1–Q16 +180°, U15 -90° (clockwise), persisted by LCSC ID. U11 is a new package and needs assembler-preview orientation review.
