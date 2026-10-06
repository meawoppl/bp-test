# Schematic presentation

The single sheet uses a landscape aspect ratio of 1.77:1. Symbols and text retain their original scale, and connected groups move together on the electrical connection grid.

- Left column: battery input, ceramic reservoir, 12 V and 5 V conversion, analog/logic supplies, shared charge pump and mounting.
- Upper middle: daughterboard, programming-only USB-C, design notes and indicators.
- Middle: four AUX unity buffers in a two-by-two group beside the ADC and its input filters/bypass.
- Lower band: CST 1 and CST 2, each followed by its phase, reference and bypass sections.
- Right column: GDT 1 and GDT 2; each command block precedes its corresponding full bridge.

All 27 functional boxes fit their contents with consistent title margins and 12.7 mm gaps. Repeated regulator, AUX and GDT blocks share widths. Each GDT command block has one column per bridge leg, and the bridge output/reservoir rows are closer to the drivers. The current sheet occupies 23.55% less area than the preceding layout.

Presentation source: `tools/hardware/tesla_schematic_layout.py` and `tesla_schematic_layout.json`. The JSON describes rows and columns; the generator measures each block before packing it. Per-block bounds are recorded in `schematic-layout.json`. The generator rejects overlapping boxes and verifies every contract pin/net after regeneration.

Native ERC and DRC report zero violations, zero open connections and zero schematic parity issues. The full exported netlist is unchanged: 331 components and 187 nets. The PCB is byte-identical to the preceding revision. The existing board quality backlog remains 303 errors and 2390 warnings; all findings are unchanged. See [the scoped review](schematic-repack-review.txt) and `schematic-repack-checks/` for validation and visual evidence.

[Schematic PDF](controller-schematic.pdf)
