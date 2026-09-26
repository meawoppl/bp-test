# JLCPCB Assembly Inputs — Revision C

These files match the revision-C schematic and 32 × 20 mm PCB:

- `direction-led-tester-gerbers.zip`: fabrication-only ZIP for the PCB upload.
- `direction-led-tester-jlcpcb.zip`: complete archive with fabrication and BOM/CPL.
- `BOM_direction-led-tester.csv`: D1, D2, J1, and R1, with LCSC numbers.
- `CPL_direction-led-tester.csv`: all four component placements, including J1.
- `CPL_kicad_direction-led-tester.csv`: current native KiCad comparison export.

Population: one C17513 0805 resistor, one C125084 green 1206 LED, one C125086 red 1206 LED, and one C2837587 BNC.
R2 is absent. This is a full-population CPL, not an SMT-only file. J1 needs
explicitly accepted through-hole/wave-solder assembly; the three SMT parts
are R1/D1/D2.

| Reference | X (mm) | Y (mm) | Rotation | Side |
| --- | --- | --- | --- | --- |
| D1 | 23 | -6 | 180° | Top |
| D2 | 23 | -14 | 0° | Top |
| J1 | 8.34 | -10 | 270° | Top |
| R1 | 17 | -10 | 0° | Top |

Coordinates preserve KiCad's native export and board origin; do not negate Y
to make it positive. J1's native -90° is normalized to 270°. Rotation values
are board orientations, not confirmation of JLCPCB library alignment. Inspect
D1/D2 cathodes and J1 placement in the assembly preview before approval.
[JLCPCB's KiCad instructions](https://jlcpcb.com/help/article/how-to-generate-the-bom-and-centroid-file-from-kicad)
describe native export and column mapping.

ERC, DRC, and schematic parity pass. Confirm BNC stock, through-hole service,
and manufacturing preview acceptance before ordering. No order or physical
prototype test has been performed. See the [manufacturing notes](../../docs/manufacturing-notes.md)
and [regeneration instructions](../README.md).
