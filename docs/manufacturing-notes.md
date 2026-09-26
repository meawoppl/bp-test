# Manufacturing Notes — Revision C

## Board and assembly

The schematic and PCB are synchronized. The board is 32 × 20 mm, two copper
layers, 1.6 mm thick. All traces are on F.Cu; there are no vias. Use 1 oz copper
and confirm the chosen finish and solder mask with the assembly service.
The BNC body occupies the left portion of the board, its barrel overhangs the
left edge, and the LEDs are grouped on the right with `+` and `-` labels.

| Reference | Quantity | Part | LCSC number |
| --- | --- | --- | --- |
| R1 | 1 | 1 kOhm, 1%, 0805, 125 mW; 0805W8F1001T5E | C17513 |
| D1 | 1 | Green 1206; LTST-C150GKT | C125084 |
| D2 | 1 | Red 1206; LTST-C150KRKT | C125086 |
| J1 | 1 | Kinghelm KH-BNC50-3511 BNC | C2837587 |

R2 is absent from the schematic, board, BOM, and placements. The assembly CPL
includes all four parts, including through-hole J1; it is not SMT-only.
Arrange J1's wave-solder/through-hole service explicitly. The three SMT parts
are R1, D1, and D2.

## Electrical connections

| Net | Connected pins |
| --- | --- |
| /SIG+ | J1.1 (center), R1.1 |
| /LED_DRV | R1.2, D1.2 (anode), D2.1 (cathode) |
| /SIG- | J1.2/J1.3/J1.4 (shell), D1.1 (cathode), D2.2 (anode) |

D1 conducts for positive center-to-shell voltage; D2 conducts for negative.
R1 limits current in both directions. The forward-biased LED limits reverse
voltage across the other LED. This normal-operation behavior is not a
transient-protection specification.

While an LED conducts, current is approximately `(abs(Vinput) - Vf) / 1 kOhm`.
The Lite-On LEDs have 5 V reverse absolute-maximum ratings and approximately
2–2.1 V typical forward voltage at 20 mA. The shared 1 kOhm resistor gives roughly
3 mA at 5 V; actual current and brightness depend on the LED at that current.
The two colors are not brightness-matched. Resistor dissipation is approximately
9 mW, below its 125 mW rating (even 5 V entirely across R1 gives only 25 mW).
D1 is green/yellow-green (569 nm); D2 is red (624 nm).

Selected assembly listings: [R1](https://jlcpcb.com/partdetail/0805W8F1001T5E/C17513),
[D1](https://jlcpcb.com/partdetail/liteon-LTSTC150GKT/C125084), and
[D2](https://jlcpcb.com/partdetail/liteon-LTSTC150KRKT/C125086).
Manufacturer datasheets: [green](https://media.digikey.com/pdf/Data%20Sheets/Lite-On%20PDFs/LTST-C150GKT.pdf)
and [red](https://datasheet.lcsc.com/datasheet/pdf/67f7a9448eb04055a1008998697edf89.pdf).
Both LED bodies are 3.2 × 1.6 mm; the local 1206 footprint uses cathode pad 1.
The generic STEP models show package geometry, not the emitted light color.


## BNC footprint and model review

The [Kinghelm drawing supplied by LCSC](https://datasheet.lcsc.com/datasheet/pdf/acf23c0ff6c2b2d3cee68c106d68a057.pdf)
for KH-BNC50-3511 was inspected on 2026-09-22. The local footprint now uses
10.10 mm mounting-pin separation, 5.05 mm row separation, and 2.50 mm signal/
shell-pin separation. Drills were aligned to the drawing's PCB pattern:
0.90 mm for pins 1/2 and 2.00 mm for pins 3/4, replacing the imported
approximately 1.00/2.20 mm drills. Pad diameters remain 1.60/2.601 mm.
Confirm finished-hole tolerances with the fabricator and fit on a prototype.

Off-board barrel artwork is on F.Fab. The on-board silkscreen is trimmed to
clear the board edge. The mechanical outline remains available in the local
footprint; no copper pads were removed to hide errors.

The imported WRL and STEP do not share the same origin/orientation. The active
footprint explicitly uses STEP with rotation `(0, 0, 180)` and offset
`(0, -13.275, 0)` mm. This aligns the model's pin rows with the footprint;
the native 3D render confirms an overhanging barrel and unobstructed LEDs.
The old WRL is retained as a source asset but is not used by the active board.

[JLCPCB's C2837587 listing](https://jlcpcb.com/partdetail/Shenzhen_KinghelmElec-KH_BNC503511/C2837587)
identifies wave-solder assembly. Listing presence does not reserve stock or
approve this board for that service.

## Libraries

R1 uses local `Resistor_SMD:R_0805_2012Metric`; D1/D2 use local
`LED_SMD:LED_1206_3216Metric`. Their STEP models are under `3dmodels/`.
`bp-test:R` and `bp-test:LED` are vendored from KiCad `Device:R_Small_US` and
`Device:LED`; the LED retains cathode pin 1 and anode pin 2. J1 uses the
imported `lcsc:KH-BNC50-3511` symbol and corrected local footprint.
The schematic includes `LCSC` fields consumed by Backplane's BOM exporter.

## Verification

KiCad 10.0.6 ERC: 0 violations. DRC with `--schematic-parity`: 0 geometric
violations, 0 unconnected items, and 0 schematic-parity issues. Reports are
under [fab/checks](../fab/checks/). These results use the existing project's
configured checks and do not replace physical or assembly validation.

Native PCB and 3D renders were inspected. Regenerated front copper, silkscreen,
and solder-mask Gerbers were rendered separately for inspection. The package
contains four BOM and four CPL references, with native-coordinate agreement
and no R2. Revision hashes are recorded in [the release manifest](../fab/release-manifest.json).

## Before ordering

1. Confirm the final board options, finished-hole tolerances, and BNC stock/
   through-hole assembly acceptance with JLCPCB.
2. Review Gerber/drill and assembly previews. Check D1/D2 cathodes, J1 rotation,
   and all four placements. Native board rotations may need manufacturer
   library offsets; preview acceptance remains outstanding.
3. Use the matching revision-C files under `fab/jlcpcb/`; do not use old files
   retained under `tmp/` or previous downloads.

No order has been placed. No populated prototype has been tested.

## Prototype test

Check for shorts and verify component orientation. Apply a controlled 5 V
center-to-shell input: D1 should light green and D2 remain off. Reverse polarity:
D2 should light red and D1 remain off. Measure current and brightness in both
directions, and check mechanical fit and BNC cable access.

## D1 stock substitution

C125084 (LTST-C150GKT) replaces C125085 without changing the 1206 footprint,
pin polarity, resistor, routing, Gerbers, or placements. It is a dimmer
yellow-green LED: the manufacturer specifies 6 mcd typical at 10 mA, versus
44.5 mcd typical at 20 mA for the original part (different test currents).
Check visibility at this circuit's approximately 3 mA operating current.
JLCPCB listed 10,173 available to order when checked; stock is not reserved.
