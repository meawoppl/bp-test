# GPS time calibrator RFC v1 — 2026-09-27

**Review snapshot only. NOT ORDERED; ordering is on hold.**

Wait for bring-up and validation of the already ordered ESP32/FPGA module and
programming carrier before ordering this higher-cost calibrator assembly.
This is not a production release or approval to manufacture.

These files preserve the exact fabrication/assembly outputs supplied at this
review, without regenerating them. 37 BOM groups, 289 assembly placements;
64 green YLED1206G / C30584801 display LEDs with individual 470-ohm resistors.
Request a common LED brightness bin; equal part numbers alone do not ensure
matched light output. PCB: 1.6 mm, four layers, JLC04161H-7628 stackup.

The CPL already includes the recorded part-specific assembly corrections.
Do not apply them twice. Review the final vendor placement preview when
ordering. Separate manual assembly items and display-header instructions are
included. Native ERC/DRC, unconnected and schematic-parity counts are zero;
hardware, RF, optical, thermal and power-sequencing validation remains pending.

Keep this directory immutable; put future revisions in a new snapshot folder.
Git tag: `gps-calibrator-rfc-v1`.
