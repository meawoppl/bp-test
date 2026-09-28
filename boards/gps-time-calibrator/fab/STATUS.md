# Routed prototype fabrication snapshot

Regenerated 2026-09-27 after the always-on controller / GPIO power-control and
OCXO linear-regulator changes, compact thermal-area placement, direct PPS indicator, VCC_RF antenna bias, GPIO40 GPS reset and connector-exit routing cleanup. Native ERC, DRC, unconnected-item and schematic-parity
counts are zero. Native drill-to-pad audit finds no vias within the 0.05 mm drill margin.
`EXPORT.json` and `assembly-finalization.json` identify these source-matched outputs.

This remains an unqualified prototype. Review JLCPCB U15 orientation and other
placement previews, USB power sequencing/inrush, total source-current budget,
LDO/OCXO warm-up temperature and timing, RF and optical performance on hardware.
The daughterboard, OCXO, OLED and mechanical hardware are manually installed.
See `../docs/power-control.md` for the new GPIO contract and thermal limitations.
Existing broader layout-audit findings are not equivalent to native DRC results;
see the review notes before treating this as production-qualified.
