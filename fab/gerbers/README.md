# Gerber and Drill Outputs — Revision C

Current exports for the 32 × 20 mm PCB. `direction-led-tester-gerbers.zip`
contains fabrication artifacts only; it matches the unpacked files here.
All routing is on F.Cu. B.Cu is an unused copper layer except for plated pad
annuli. The package includes the board outline, copper, mask, paste,
silkscreen, drill data, and auxiliary KiCad plot layers/job metadata.

The BNC barrel intentionally overhangs the left board edge; its off-board
mechanical artwork belongs to F.Fab and is not printed as board silkscreen.
R2 is removed. Front copper, silkscreen, and solder mask were rendered for
visual review after export. ERC/DRC/parity reports are in `../checks/`.

Use the [JLCPCB assembly files](../jlcpcb/README.md) for populated boards.
Follow the [regeneration sequence](../README.md) after any design change.
