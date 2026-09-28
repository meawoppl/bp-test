# PCB workspace

**[v1: first 10 ESP32 + FPGA modules ordered](boards/esp32-fpga-module/releases/v1/README.md)** — exact fabrication files and checksums preserved by Git tag `v1`.

Choose a board in the portal using the selector configured in [`.kicad-pcb.json`](.kicad-pcb.json).

Integration guides:

- [Daughterboard v1 ICD](boards/esp32-fpga-module/docs/ICD-v1.md): electrical/mechanical contract and reusable KiCad assets.
- [Programming fixture firmware guide](boards/programming-carrier/README.md): bank tests, walking LEDs and restricted pins.
- [GPS calibrator bring-up](boards/gps-time-calibrator/docs/integration/README.md): power sequencing, Affogato, GNSS/event capture and displays.

- [ESP32 + FPGA module](boards/esp32-fpga-module/README.md): routed four-layer prototype; current checks and fabrication previews are included.
- [Original MainBoard](boards/mainboard-reference): native KiCad import for reference; original Fusion/Eagle exports in [source/fusion](source/fusion).
- Direction LED tester: existing board and fabrication files described below.

# Direction LED Differential Input Test Board

A compact 5 V BNC polarity indicator and Backplane workflow test project.

## Revision C

The schematic, 32 × 20 mm PCB, and fabrication files now match. The board is
73% smaller than the original 75 × 32 mm layout. The BNC body sits at the
left edge with its barrel overhanging, and the two indicators sit together on
the right. All routing is on top copper, with no vias.

- D1 / `+` (green 1206) lights when the BNC center is positive relative to its shell.
- D2 / `-` (red 1206) lights when the center is negative relative to its shell.
- A shared 1 kOhm 0805 resistor feeds directly antiparallel LEDs, limiting current
  and allowing the conducting LED to limit reverse voltage across the other.

There are four components: J1, R1, D1, and D2. R2 is removed.

[Layout drawing](docs/layout-review.svg) · [3D view](docs/layout-3d.png) ·
[Schematic](docs/schematic-review.svg)

## Verification and ordering

KiCad 10.0.6 ERC: **0 violations**. DRC with schematic parity: **0 violations,
0 unconnected items, 0 parity issues**, under the current project settings.
Gerbers, drills, BOM, and placements have been regenerated for revision C.

The package is ready for fabrication/assembly review, not an already approved
order. Confirm JLCPCB stock, through-hole assembly of J1, and LED rotation in
the assembly preview. No physical prototype has been tested. See the
[manufacturing notes](docs/manufacturing-notes.md) and [fabrication package](fab/README.md).

## Project files

| File or directory | Purpose |
| --- | --- |
| `direction-led-tester.kicad_pro` | KiCad project settings |
| `direction-led-tester.kicad_sch` | Revision C schematic |
| `direction-led-tester.kicad_pcb` | Revision C, 32 × 20 mm board |
| `bp-test.kicad_sym` | Vendored KiCad resistor and LED symbols |
| `fp-lib-table`, `sym-lib-table` | Project-local library mappings |
| `Resistor_SMD.pretty/`, `LED_SMD.pretty/` | Local KiCad footprints |
| `3dmodels/` | Resistor and LED STEP models |
| `lcsc/` | BNC symbol, corrected footprint, and STEP/WRL source models |
| `fab/` | Revision C fabrication, assembly, and check outputs |

The [workflow log](docs/plugin-workflow-log.md) records plugin testing and prior
revisions; use the current manufacturing notes for ordering requirements.
