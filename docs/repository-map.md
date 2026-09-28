# Repository map

Current workspace structure, 2026-09-27. The manifest registers five boards;
the original direction tester lives at repository root.

```mermaid
flowchart TD
    R["bp-test/"] --> C[".kicad-pcb.json<br/>Five-board portal manifest"]
    R --> B["boards/"]
    B --> M["esp32-fpga-module/<br/>ESP32 + FPGA daughterboard<br/>releases/v1 — ordered"]
    B --> P["programming-carrier/<br/>USB programming + GPIO test<br/>releases/v1 — ordered"]
    B --> G["gps-time-calibrator/<br/>GPS optical timing carrier<br/>releases/rfc-v1 — NOT ORDERED"]
    B --> O["mainboard-reference/<br/>Original imported design"]
    R --> D["direction-led-tester.kicad_*<br/>Root-level polarity tester"]
    D --> F["fab/<br/>Tester fabrication outputs"]
    R --> L["libraries/datasheets/<br/>PDFs, Markdown, source index"]
    R --> T["tools/<br/>hardware/ — generators, routing audits, export<br/>datasheets/ — PDF extraction"]
    R --> DOC["docs/<br/>pcb-playbook/, hardware/, repository map"]
    R --> S["source/fusion/<br/>Original Fusion/Eagle imports"]
    R --> LOC["Root local libraries/models<br/>*.pretty/, *.kicad_sym, 3dmodels/, lcsc/"]
```

The module, programmer and calibrator each keep their own KiCad sources,
project-local symbols/footprints/models, design notes in `docs/`, current
exports in `fab/`, and frozen fabrication snapshots in `releases/`.

```text
boards/<board>/
├── *.kicad_pro / *.kicad_sch / *.kicad_pcb / *.kicad_dru
├── *.kicad_sym / *.pretty/ / 3dmodels/
├── docs/                  design contracts, review notes, drawings
├── fab/
│   ├── checks/            ERC / DRC and other audits
│   ├── gerbers/           copper, mask, silk, outline, drill, ZIP
│   ├── bom/               native BOM / positions / manual assembly
│   └── jlcpcb/            manufacturer BOM / CPL / assembly ZIP
└── releases/<version>/    preserved review or ordered artifacts
```

`tmp/`, `logs/`, `.worktrees/` and uploaded screenshot files are local working
material excluded from Git. The two carriers mate with the same module;
they are separate boards, not daughterboard revisions. RFC v1 ordering waits
for validation of the already ordered module and programmer.
