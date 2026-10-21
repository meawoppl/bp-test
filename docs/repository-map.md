# Repository map

Current workspace structure, 2026-10-20. The manifest registers three boards
(direction tester at the root, MainBoard reference, Tesla coil controller). The
ESP32 + FPGA module, its programming carrier and the GPS calibrator moved to
[OrbitalCommons/gumstick](https://github.com/OrbitalCommons/gumstick) and
[OrbitalCommons/stratumzero](https://github.com/OrbitalCommons/stratumzero) (the GPS calibrator, now named StratumZero).

```mermaid
flowchart TD
    R["bp-test/"] --> C[".kicad-pcb.json<br/>Three-board portal manifest"]
    R --> B["boards/"]
    B --> TC["tesla-coil-controller/<br/>Tesla coil controller"]
    R --> GS["third_party/gumstick/<br/>submodule: OrbitalCommons/gumstick"]
    B --> O["mainboard-reference/<br/>Original imported design"]
    R --> D["direction-led-tester.kicad_*<br/>Root-level polarity tester"]
    D --> F["fab/<br/>Tester fabrication outputs"]
    R --> L["libraries/datasheets/<br/>PDFs, Markdown, source index"]
    R --> T["tools/<br/>hardware/ — generators, routing audits, export<br/>datasheets/ — PDF extraction"]
    R --> DOC["docs/<br/>pcb-playbook/, hardware/, repository map"]
    R --> S["source/fusion/<br/>Original Fusion/Eagle imports"]
    R --> LOC["Root local libraries/models<br/>*.pretty/, *.kicad_sym, 3dmodels/, lcsc/"]
```

Each board keeps its own KiCad sources,
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
