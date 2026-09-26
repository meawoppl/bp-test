# Fabrication Package — Revision C

These outputs were regenerated from the synchronized revision-C schematic
and 32 × 20 mm PCB. ERC and schematic-parity DRC pass. Assembly-service
acceptance, stock, preview approval, and physical prototype testing remain
outstanding; see [manufacturing notes](../docs/manufacturing-notes.md).

- [jlcpcb/](jlcpcb/README.md): Gerber/drill ZIP, BOM, full-population CPL, and
  native KiCad placement comparison. The `-jlcpcb.zip` includes BOM/CPL; `-gerbers.zip` is fabrication-only.
- [gerbers/](gerbers/README.md): fabrication-only ZIP and unpacked layer files.
- `checks/`: saved KiCad ERC and DRC JSON reports.
- [release-manifest.json](release-manifest.json): source/output hashes and
  verification summary for this revision.

## Regeneration from the project root

```sh
/home/meawoppl/agent-portal-plugins/backplane/bin/backplane erc --json --cwd .
/home/meawoppl/agent-portal-plugins/backplane/bin/backplane drc --json --cwd .
/home/meawoppl/agent-portal-plugins/backplane/bin/backplane export gerbers --cwd . --out fab/gerbers
/home/meawoppl/agent-portal-plugins/backplane/bin/backplane export jlcpcb --cwd . --out fab/jlcpcb
kicad-cli pcb export pos --output fab/jlcpcb/CPL_kicad_direction-led-tester.csv --side both --format csv --units mm direction-led-tester.kicad_pcb
```

Confirm DRC actually includes schematic parity. After export, preserve native
X/Y positions, normalize rotations modulo 360, and use `Top` for these front
placements. Keep the CPL inside the JLCPCB ZIP identical to the separate CSV.
Backplane does not refresh the retained native comparison CSV automatically;
run the explicit position export above. Refresh saved reports and the release
manifest when sources change. Export success alone is not order approval.
