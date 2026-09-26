# Current layout milestone — Revision B

The layout now matches the corrected schematic: 32 × 20 mm, edge-mounted BNC,
paired labeled LEDs, one shared resistor, no R2, and all routing on F.Cu without
vias. KiCad ERC and DRC including schematic parity pass with zero issues.
Gerber/drill, BOM, full-population CPL, native placement comparison, and check
reports were regenerated. See [manufacturing notes](manufacturing-notes.md)
for current review limits and [layout-review.svg](layout-review.svg) for the board.

The BNC footprint was checked against the linked manufacturer drawing, with
row spacing and drill sizes corrected. Its off-board silkscreen was moved to
F.Fab. The STEP model required a -13.275 mm Y offset with 180° Z rotation to
align to its pins; native rendering confirmed the correction.

Export findings: Backplane uses the `LCSC` schematic field for BOM part
numbers, so that field is now present. The JLCPCB CPL includes through-hole
J1. The plugin does not replace a previous `CPL_kicad_...csv`; that comparison
file was explicitly regenerated. Final CPL rotations were normalized and the
ZIP's copy updated to match.

All entries below are historical snapshots, including statements that the
PCB is stale, R2 remains, or layout synchronization is pending. They do not
describe revision B's current release status.

---

# Backplane Workflow: Current Status

As of schematic B-sch (2026-09-22), the circuit uses one shared resistor and
antiparallel LEDs. R2 is removed; the standard KiCad LED symbol replaces the
incorrect custom artwork. Schematic ERC reports zero violations; exact netlist
checks confirm three nets and four components. The revised drawing is
[schematic-review.svg](schematic-review.svg).

**The PCB and all fabrication/assembly files are still from the earlier
layout. No current schematic-parity or manufacturing release pass is claimed.**
See [manufacturing notes](manufacturing-notes.md) for outstanding work.

## Current plugin findings

- Installed KiCad is 10.0.6. Schematic/PCB/3D rendering and check/BOM cards were
  visually exercised using Firefox under Xvfb with software GL.
- Source and GLB startup prewarming passed. The persistent pane was restarted
  after the B-sch edit and serves the new schematic alongside the older PCB.
- Plugin commit `17dce21` added clean export staging, constrained ZIP contents,
  and explicit JLCPCB BOM/CPL generation. Existing fabrication files were not
  regenerated for B-sch.
- Plugin commit `d53bc43` enabled schematic parity and parity issue cards.
  Before the B-sch rewrite, the live API reported 13 parity issues despite
  zero geometric violations. That count is historical, not the revised
  schematic's validation result.
- `plugin open` lost its server process after returning. The working pane uses
  `bp-test-backplane-pane.service` on port 41905 at
  https://d4efc63a.portal.cosmicfrontier.org/ . This is a session-specific URL.
- Pure headless Firefox failed WebGL creation on this host; native viewers
  stayed on “Loading preview…”. Xvfb resolved rendering. Gerbers remained a
  file list, STEP was uninitialized, and 3D surface artifacts need review.

## Historical record

The entries below preserve the sequence of earlier tests. References to KiCad
7, missing export support, clean DRC, separate resistors, and proposed-but-not-
implemented antiparallel LEDs describe superseded states. Use the status above
and the manufacturing notes for the current design and release requirements.

---

# Historical Backplane Plugin Workflow Log

## Commands Run

```console
agent-portal plugin list
agent-portal plugin info backplane
agent-portal plugin help backplane
agent-portal plugin doctor backplane
agent-portal plugin open --help
agent-portal plugin open backplane
agent-portal forward list
curl -fsS http://127.0.0.1:40849/healthz
systemd-run --user --unit bp-test-backplane --collect /home/meawoppl/agent-portal-plugins/backplane/bin/backplane serve --port 48888 --cwd /home/meawoppl/repos/bp-test --session bp-test
agent-portal forward 48888
agent-portal plugin status backplane
sudo apt-get update
sudo apt-get install -y kicad
kicad-cli --version
kicad-cli pcb export gerbers --output fab/kicad-export-20260922/ --layers F.Cu,B.Cu,F.Mask,B.Mask,F.Paste,F.SilkS,B.SilkS,Edge.Cuts direction-led-tester.kicad_pcb
kicad-cli pcb export drill --output fab/kicad-export-20260922/ direction-led-tester.kicad_pcb
kicad-cli pcb export pos --output fab/jlcpcb/CPL_kicad_direction-led-tester.csv --side front --format csv --units mm direction-led-tester.kicad_pcb
```

Backplane surface initially launched, but the process stopped after
`agent-portal plugin open backplane` returned. The durable workaround is now
running as `bp-test-backplane.service` and forwarded here:

```text
https://179171cd.portal.cosmicfrontier.org/
```

## Historical issue log

1. The installed Backplane plugin source is local:
   `/home/meawoppl/agent-portal-plugins/backplane`, with source
   `/home/meawoppl/repos/agent-portal-plugins/backplane`. This does not fully
   exercise a fresh install from
   `github:meawoppl/agent-portal-plugins//backplane`.
2. The plugin manifest declares `agent_portal >=2.15.0`, while the session
   reports Agent Portal `2.14.1525`. The plugin still listed, opened, and ran
   doctor successfully, so compatibility enforcement appears soft or bypassed
   for this local install.
3. `agent-portal plugin help backplane` failed with `unrecognized subcommand
   'backplane'`. The outer CLI exposes `agent-portal plugin help`, but there is
   no discoverable per-plugin help path through that spelling.
4. `agent-portal plugin doctor backplane` initially reported `kicad-cli: false`.
   Installing Ubuntu package `kicad` provided KiCad CLI `7.0.11`; Backplane
   doctor now reports `kicad-cli: true`.
5. The plugin describes itself as a smoke wrapper, not the full upstream
   Backplane runtime. It validates install/open/detect plumbing, but does not
   synthesize KiCad files or perform real board visualization/DRC/export.
6. Because of those limits, KiCad source files, JLCPCB BOM/CPL, and
   source-derived Gerber/drill draft artifacts were created manually first.
   After installing KiCad CLI, native KiCad Gerber/drill exports were generated
   in `fab/kicad-export-20260922/`.
7. Through-hole/wave-solder assembly availability for the BNC should be
   confirmed during JLCPCB quoting. The SMT LED/resistor portion is
   straightforward.
11. The initial board used embedded, hand-authored footprint geometry. Project
    library tables and `.pretty` footprint libraries were added so R/LED parts
    resolve to vendored KiCad stock footprints. The BNC was later replaced
    with EasyEDA/LCSC imported `C2837587` / `KH-BNC50-3511`; the alternate pin
    header was removed.
12. `backplane export gerbers --json` and `backplane export jlcpcb --json`
    are not accepted even though `drc --json` and `erc --json` are. The export
    commands still print JSON-shaped output by default, but the CLI flag shape
    is inconsistent.
13. The 3D tab initially showed a board-only GLB because `kicad-packages3d`
    was missing and the vendored stock footprints referenced legacy `.wrl`
    paths. Installing `kicad-packages3d`, vendoring the matching stock `.step`
    files under `3dmodels/`, changing the project model references to
    `${KIPRJMOD}/3dmodels/...`, and adding `--subst-models` to Backplane's GLB
    export path fixed stock component rendering.
14. JLCPCB/LCSC part `C2837587` / `KH-BNC50-3511` imported successfully with
    `easyeda2kicad --full --lcsc_id=C2837587 --project-relative`, producing
    `lcsc/lcsc.kicad_sym`, `lcsc/lcsc.pretty/ANT-TH_KH-BNC50-3511.kicad_mod`,
    and matching WRL/STEP models under `lcsc/lcsc.3dshapes/`.
8. `agent-portal plugin open backplane` left a portal forward pointing at port
   `40849` after the server process was gone; `curl` to `/healthz` failed.
   Workaround: run the wrapper under `systemd-run --user` and forward that
   fixed port.
9. `agent-portal plugin status backplane` is not a recognized command, so there
   is no obvious status command beyond `plugin list`, `plugin info`, and
   `forward list`.
10. Backplane's DRC wrapper still fails with KiCad 7 because it calls
    `kicad-cli pcb drc`, but this Ubuntu KiCad 7 CLI only supports
    `kicad-cli pcb export ...`. DRC/ERC need KiCad GUI or a newer KiCad CLI.

## Plugin Doctor Result Summary

```json
{
  "ok": true,
  "tools": {
    "python3": true,
    "node": true,
    "kicad-cli": true,
    "kikit": false
  },
  "detected_files": [
    "fab/jlcpcb/BOM_direction-led-tester.csv",
    "fab/jlcpcb/CPL_direction-led-tester.csv",
    "fab/jlcpcb/CPL_kicad_direction-led-tester.csv",
    "direction-led-tester.kicad_pcb",
    "direction-led-tester.kicad_pro",
    "direction-led-tester.kicad_sch",
    "fab/jlcpcb/direction-led-tester-gerbers.zip"
  ]
}
```

## 2026-09-22 continuation smoke (supersedes earlier runtime limitations)

Installed Backplane startup prewarming passed: `/healthz` reports
`preloaded: true` with source revision and warm timestamp. Source snapshot and
917632-byte GLB responses took about 2–3 ms after startup; GLB was HTTP 200,
`model/gltf-binary`, with immutable cache headers.

Fresh doctor found KiCad 10.0.6 and all bundled viewer assets. Fresh DRC found
0 violations and 0 unconnected items; ERC found 0 violations under the current
project settings. Clean-directory JLCPCB export produced valid Gerber/drill
files. SMT CPL was regenerated preserving native negative Y; both fabrication
ZIPs were replaced with clean exports without stale CSV/README entries.

Visual smoke used Firefox under Xvfb with software GL. Screenshots in
`tmp/smoke-20260922/` confirm actual schematic and routed PCB rendering, a 3D
board with connector, clean DRC/ERC summary cards, and BOM table/download cards.
Pure headless Firefox could not create WebGL on this host; under that failure,
schematic/PCB remained on “Loading preview…” rather than showing an actionable
error. Xvfb resolved the environment problem. The 3D view has visible surface
artifacts and needs further appearance review. Gerbers is still a file list,
not a layer viewer; the STEP tab has an uninitialized viewer.

`agent-portal plugin open backplane` again returned a working URL then lost
its process. The pane was restored on the same port using a persistent user
service `bp-test-backplane-pane` (port 41905):
https://d4efc63a.portal.cosmicfrontier.org/

Reported to the plugin agent: stale destination contents in export ZIPs,
JLCPCB command omitting assembly tables, lifecycle failure, and WebGL error
feedback gap. The agent is addressing exports separately in the plugin repo.

Hardware release remains blocked by the LED reverse-voltage margin and final
BNC mechanical/assembly review; see manufacturing notes. A possible revision
is to place the LEDs directly antiparallel with one shared series resistor,
so the conducting LED clamps the reverse voltage of the other. This topology
has not been implemented or validated in this revision.

## Revision C — larger packages and color distinction (2026-09-23)

R1 changed to 0805 1 kOhm C17513; D1 to green 1206 C125085 and D2 to red
1206 C125086. Local footprints/models and routed pad endpoints were updated.
The 32 × 20 mm outline and BNC geometry are retained. ERC and schematic-parity
DRC pass with zero issues. Previews and all fabrication/assembly outputs were
regenerated. Prototype brightness and assembly preview approval remain pending.

### Revision C BOM stock substitution

D1 changed from C125085/LTST-C150KGKT to C125084/LTST-C150GKT due to order
stock shortage. Same footprint and polarity; lower brightness documented.
Updated canonical part fields, standalone BOM, packaged BOM, and hashes.
