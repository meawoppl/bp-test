# JLCPCB manufacturing notes

## Design rules

"DRC clean" means nothing until the rules are the fab's rules. The module's
generic limits hid real violations until they were replaced with JLCPCB's
published limits. Start every JLC board from
[`boards/esp32-fpga-module/module.kicad_dru`](../../boards/esp32-fpga-module/module.kicad_dru)
(4-layer, 1 oz outer / 0.5 oz inner, routed edges). Its key rules:

| Rule | Minimum |
| --- | ---: |
| Track / space (project choice) | 0.10 mm |
| Via pad / drill (no surcharge) | 0.45 / 0.20 mm |
| Via drill → foreign copper | 0.20 mm |
| Different-net SMD pad spacing | 0.15 mm |
| PTH drill → copper (outer / inner) | 0.28 / 0.30 mm |
| PTH annular ring | 0.15 mm |
| Silkscreen text height / stroke | 1.0 / 0.15 mm |
| Via types | through only |

Record the capability URL and the date the rules were checked in the
`.kicad-pcb.json` manufacturer block.

## Stackup and impedance

- 4-layer default: **JLC04101H-7628**, 1.0 mm nominal, 0.2104 mm prepreg
  top→In1.
- 50 Ω coated CPWG on that stack: **0.26 mm trace / 0.15 mm gap**
  (≈50.15 Ω, JLC calculator). Encode the gap as a netclass/zone rule, e.g.
  `/RF_*` to GND clearance.
- Specify the stackup *and* controlled impedance on the order, because board
  thickness alone doesn't fix the stackup. Save the calculator inputs in the repo.

## Parts

- Search JLCPCB/LCSC directly. Prefer Basic parts and high stock.
- Before assigning an LCSC number, confirm that its package matches the
  footprint.
- Check stock at order time. The session hit five out-of-stock parts (LED
  C125085, LED C72043, chip antenna, crystal, buck).
- Group the BOM by LCSC/MPN, not by value string.
- DNP parts: leave them off the JLC BOM but keep them in the review BOM.

## CPL placement corrections

KiCad's footprint zero orientation and origin often differ from JLCPCB's
library model. Record each correction **on the part** as two hidden fields
(put them on the symbol, run *Update PCB from Schematic*, and keep the
footprint copies on F.Fab so silkscreen is unchanged):

| Field | Value | Meaning |
| --- | --- | --- |
| `JLCPCB Rotation Offset` | degrees, e.g. `-90` | added to KiCad's rotation (CCW positive); `-90` = 90° CW |
| `JLCPCB Position Offset` | `x,y` mm, e.g. `0,-2.75` | shift in the **footprint-local** frame (KiCad +Y down, before rotation/flip) |

The kicad-pcb plugin (and `tools/hardware/carrier_export.py`) apply them only
to the JLCPCB CPL. They map the local offset to the board like a pad offset
(bottom-side parts mirror local Y, then the footprint rotation applies), then
to CPL +Y up. Because the offsets are footprint-local, they stay correct when
the part is moved, rotated or flipped. No native-rotation assertion is needed.
The footprint value wins if it disagrees with the schematic (the build log
warns). An unparseable value fails the export. Every export lists each
corrected ref with its values and source, and writes
`<board>-placement-corrections.json` beside the CPL. The Libraries tab shows a
`JLC corr.` badge. Bottom-side rotation corrections are mirrored and flagged;
confirm them in the preview.

These corrections were confirmed from the carrier's previews and are worth
reusing. Copy the fields onto the same part in other boards:

| LCSC | Part | Fields |
| --- | --- | --- |
| C113281 | SN74LVC541APWR (TSSOP-20) | Rotation `-90` (90° CW) |
| C51118 | AP2112K-3.3 (SOT-23-5) | Rotation `-90` |
| C7519 | USBLC6-2SC6 (SOT-23-6) | Rotation `-90` |
| C221660 | JS102011SAQN slide switch | Position `0,-2.75` (model origin on terminal row) |
| C165948 | TYPE-C-31-M-12 | Position `0,-1.425` |

To derive a new correction:
1. Use the pin-1 pad in the preview for rotation.
2. Use locating pegs or shield holes for translation.
3. Cross-check against the EasyEDA package origin.
4. Convert the observed shift to local coordinates. Take the CPL shift
   (dx, dy) (+Y up, from the preview) at the part's rotation θ. Then
   `x_local = dx·cosθ + dy·sinθ` and `y_local = dx·sinθ − dy·cosθ`. For
   example, SW1 at 0° moved 2.75 mm up gives `0,-2.75`, and J3 at 180° moved
   1.425 mm down gives `0,-1.425`.

**Migration.** The earlier per-board, LCSC-keyed
`docs/jlcpcb-placement-offsets.json` table (CPL-frame offsets pinned by
`verified_native_rotation_degrees`) is deprecated. The plugin still reads it
as a fallback for parts without fields and prints a warning. Part fields
take precedence. To migrate, move each entry onto its parts using the formula
above, check that the CPL is unchanged, and delete the table. The carrier was
migrated this way; its regenerated CPL is byte-identical to `releases/v1`.

## Release snapshot

Once an order is placed:

1. Tag the commit (`v1`) and push.
2. Copy the *exact ordered* Gerber ZIP, BOM, CPL, schematic PDF, and check
   results into `boards/<board>/releases/v1/`.
3. Write SHA-256 hashes of the sources and outputs, e.g.
   `fab/checks/revision-sha256.json` and `EXPORT.json`.
4. After further edits, compare the hashes to detect stale fab outputs. The
   module's working `fab/` diverged from its sources within an hour of the
   last export.
