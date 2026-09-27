# Component and design references

Checked during design, 2026-09-26. Inventory is transient.

- LED: https://www.lcsc.com/product-detail/C28310438.html — YLED1206B, 1206 blue, 13,500 listed at selection.
- GNSS: https://www.lcsc.com/product-detail/C24834155.html — MAX-M10S-00B-01, seven live units at selection (search snippets were stale).
- GNSS integration: https://content.u-blox.com/sites/default/files/MAX-M10S_IntegrationManual_UBX-20053088.pdf
- Antenna current limit: https://www.ti.com/lit/ds/symlink/tps2553.pdf — ILIM-to-IN fixed 50–100 mA mode.
- GNSS bias choke: https://www.lcsc.com/product-detail/C38841159.html — Coilcraft 0805CS-270XGLC, 27 nH 0805; recommended lands from https://www.coilcraft.com/getmedia/dd5f20e4-1ff7-43df-8317-b693eb2dce3e/0805cs.pdf .
- LED resistor: https://www.lcsc.com/product-detail/C17710.html — 0805W8F4700T5E, 470 ohm 1%, 0805.
- Distributed bulk: https://www.lcsc.com/product-detail/C15850.html — Samsung CL21A106KAYNNNE, 10 µF 25 V 0805 X5R.

Every purchased line in the grouped BOM includes its exact MPN, LCSC identifier and supplier link. J1/J2 use the ordered programming carrier's locally renumbered mating footprints; the frozen module contract, not a generic Hirose pin-number convention, is the electrical authority.

## Power and timing redesign

- USB-C sink detection: https://www.ti.com/lit/ds/symlink/tusb320lai.pdf — GPIO current-advertisement outputs and UFP configuration.
- eFuse: https://www.ti.com/lit/ds/symlink/tps2595.pdf — TPS259531, current limit and startup slew.
- Enable logic: https://www.ti.com/lit/ds/symlink/sn74lvc1g02.pdf .
- OCXO: https://abracon.com/datasheets/AOC97.pdf — AOC97FAJC-10.0000, 10 MHz variant mechanical drawing and 3.3 V power; manual assembly, not a JLCPCB part.
- Trigger comparator: https://www.ti.com/lit/ds/symlink/tlv3501.pdf .
- 5 V trigger output: https://www.ti.com/lit/ds/symlink/sn74ahct1g125.pdf .
- SMA: https://www.lcsc.com/product-detail/C3172723.html — Amphenol 132289; standard KiCad edge-launch footprint, 1.6 mm PCB.
- Intended stackup: https://jlcpcb.com/impedance — JLC04161H-7628, nominal 1.6 mm.

The full replacement R/C/L mapping is recorded in `passive-parts-0805.json`; the circuit contract and current BOM contain the selected MPNs. Old 0402/0603 parts and the external terminal are superseded. Inventory must be rechecked at ordering.

- Trigger filter C75: [CCTC TCC0805COG102G500BT / C5375915](https://jlcpcb.com/partdetail/CCTC-TCC0805COG102G500BT/C5375915), 1 nF, 50 V, C0G, ±2%, 0805. Catalog specifications checked 2026-09-26; allocation/stock must be checked at order time.

- Date/time OLED DS1: [HS96L03W2C03 / C5248080](https://www.lcsc.com/product-detail/C5248080.html), [manufacturer datasheet](https://datasheet.lcsc.com/datasheet/pdf/4cfb1fe29ff7e4fbff30eb4e2a452c3a.pdf), especially pp. 6–10 for mechanical drawing, four-pin order, default 0x3C address and voltage/current limits. LCSC listed 5,053 stock on 2026-09-26; this is not a reservation. Manual assembly.
- R174/R175 OLED pull-ups: [UNI-ROYAL 0805W8F4701T5E / C17673](https://jlcpcb.com/partdetail/C17673), 4.7k, 1%, 0805.
