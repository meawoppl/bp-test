# Tesla coil controller — acquisition-first development board

**A0 development draft, not a complete controller or fabrication release.** Registered as
`tesla-coil-controller` in the workspace selector. The current board contains the module
interface, acquisition circuit, CST conditioning, and first-pass step-down circuits. Two 24 V GDT full bridges are included, with routed power and gate-drive circuits; the remaining regulator/ESP32/analog routing, input protection and bench qualification remain. J6 has been removed.

Uses the ordered [ESP32-S2/iCE40UP5K module v1 ICD](https://github.com/OrbitalCommons/gumstick/blob/main/current-df40-connectors/docs/ICD-v1.md)
and the programmer's exact, renumbered mating footprints. J1/J2 centers are 25 mm apart;
H1 is their midpoint. Correct module outline is shown on Dwgs.User, with 2 mm mating height.

The current 163 × 141.8 mm, two-layer board puts CST and battery connectors on the left edge, acquisition and the module at the top edge, and both GDT outputs on the right edge. Battery entry and both auxiliary power modules occupy the upper-left. The compact AUX stages sit below them, with two wide CST stages underneath; the ADC sits just below the FPGA connector, with GDT stages in a separate column to the right. Silkscreen regions group each circuit and its support components; see [the floorplan](docs/FLOORPLAN.md).
The consolidated power/CST placement and local 2.5 mm GDT output links are described in the floorplan notes; substantial routing remains.
0603 resistors/capacitors around the ADC; larger passives elsewhere, exposed-lead LQFP ADC. No final stackup or impedance claim.

## Acquisition selected

AD7606C-16BSTZ, eight simultaneous 16-bit channels, LQFP-64 10 × 10 mm, 0.5 mm pitch.
LCSC C5371769. Channels 5/6 measure CST 1 raw current / rectified amplitude; channels 7/8 do the same for CST 2. Channels 1–4 are external 0–5 V inputs on J3/J8/J9/J10. All channels sample on the same CONVST edge. Four serial output
lanes go directly to the FPGA, independent of the internal ESP32–FPGA communications bus.

See [ADC research and timing](docs/ADC-SELECTION.md), [architecture and open decisions](docs/ARCHITECTURE.md),
[exact daughterboard contact assignment](docs/daughterboard-pinout.csv), and
[component/net contract](docs/circuit.json).

**J4 and J30 each accept one 12 V battery; the PCB joins them in series for 24 V nominal.** J4 is the upper battery and J30 the lower battery; pin 1 is positive on both. J4.2 connects only to J30.1 through `BAT_MID_12V`. Alternatively, connect one 24 V PSU between J4.1 (+) and J30.2 (−), leaving the two midpoint terminals unused. See the [series-input review and checks](docs/series-battery-input-review.txt). The GDT bridges use the battery rail directly. U30/U31 LMZ14202H modules independently generate 12 V bias and module/ADC 5 V directly from the battery rail. The main 24 V converter and its 27 components were removed. The +5 V/+12 V distribution and AUX −5 V extension are routed; battery input and 3.3 V distribution are now also connected. No rails are bench-validated.
See [power calculations](docs/POWER-DESIGN.md) and the accepted [24 V decision](docs/DRIVE-DECISION.md).
J3/J8/J9/J10 expect already conditioned voltage signals, **not a bare current transformer**.
Its 100R/1nF networks are EMI placeholders, not a complete anti-alias filter or surge protector.

## Files and status

- `controller.kicad_pro/.kicad_sch/.kicad_pcb`: native project, acquisition/power schematic and partially routed layout.
- `Tesla.kicad_sym`, `Tesla.pretty`, local model files: initial project-local libraries.
- `docs/datasheets`: selected ADC datasheet and supplied reference schematic.
- `fab/checks`: latest draft checks. Airwires are expected; no Gerbers/BOM/CPL are offered for ordering.
- `tools/hardware/build_tesla_controller.py`: initial constructor, refuses overwrite without `--replace-draft`.
- `tools/hardware/tesla_schematic.py`: schematic generation and exact native-netlist pad-net synchronization.

Do not rerun the placement constructor over later routing. Unused daughterboard contacts are
explicitly NC; changing a carrier assignment never changes the frozen module pinout.

## Circuit views

- [Subsystem diagram](docs/subsystems.svg): solid blocks exist in the schematic;
  dashed blocks are planned circuitry or external equipment. This is not a completed driver.
- [Readable schematic PDF](docs/controller-schematic.pdf): connected switching,
  feedback, filter and bypass circuits with grouped support components.
- [Presentation validation](docs/schematic-presentation-validation.json): unchanged
  electrical netlist, pin names/numbers and PCB; zero ERC violations.

Rebuild the presentation with `/usr/bin/python3 tools/hardware/tesla_schematic.py`.
It validates the result against `docs/circuit.json` and does not write the PCB.
Rebuild the diagram with `python3 tools/hardware/tesla_subsystems.py`.

## CST front end

[Design and simulation notes](docs/CST-INPUT.md) cover the 10-ohm burden, ±2 V nominal raw signal, precision full-wave magnitude channel, independent phase comparator. [Simulation plot](docs/cst/rectifier-topology.png). Overcurrent decisions belong to the ADC/FPGA. See [output-stage design](docs/OUTPUT-STAGE.md) and [simulation](docs/gdt/transient-sweep.png). The board is partially routed.

J3/J8/J9/J10 now join the CST connectors on the left edge. Their four AUX channels have unity-gain buffers, input clamps and filtering; see [AUX inputs](docs/AUX-INPUTS.md).

CST routing milestone: two copper layers, both sensor front ends and the shared −5 V converter locally connected; The four analog ADC handoffs remain deliberately open; both phase-comparator returns now reach the FPGA. See [CST routing and validation](docs/CST-ROUTING.md).

Positive supply routing: all +5 V and +12 V distribution pads are connected, including the ADC and filtered AUX branches. See [power routing, checks and remaining work](docs/POWER-ROUTING.md).

AUX routing: all four connectors, filters, unity buffers and ADC CH1–4 links are connected, including negative-supply extensions and bypass returns. See [AUX routing](docs/AUX-ROUTING.md).

FPGA routing: all assigned FPGA data/control contacts and downstream driver connections are routed on two layers. Five ADC carrier pin assignments changed for fanout order; firmware constraints must use the updated [contact map](docs/daughterboard-pinout.csv). See [FPGA routing and current checks](docs/FPGA-ROUTING.md). Whole-board routing is still incomplete; see the current counts in [validation.json](docs/validation.json).

H-bridge routing: both stages, drivers, bootstrap/gate networks, reservoirs and battery feeds are connected. The low-side gate-output net names were corrected to keep 12 V outputs separate from raw FPGA commands. See [H-bridge routing and validation](docs/HBRIDGE-ROUTING.md).

Latest cleanup: [command routing, ADC fanout and supply placement](docs/COMMAND-AND-ADC-CLEANUP.md). U50/U55 and the shared enable path are removed; FPGA fabric owns blanking and drive timing. The ARM indicator and J6 service header are removed. Replay current copper with `tools/hardware/tesla_route_reviewed.py`; historical incremental routing scripts describe older circuits.

ADC reference and regulator capacitors C6–C9 are connected, closing five opens; six unrelated connections remain. See [routing review](docs/adc-passives-review.txt), [copper preview](docs/adc-passives-after.png) and [verification](docs/adc-passives-verification.json).

CT2_HALF at TP61 now stays on front copper, eliminating two vias and shortening the route by 6.29 mm. See [trace review](docs/ct2-half-front-review.txt), [copper preview](docs/ct2-half-front-after.png) and [verification](docs/ct2-half-front-verification.json).

Local indicators: [rail-presence and directly sensed H-bridge legs](docs/INDICATORS.md). The buffered LED bank and dedicated FPGA LED/status assignments are removed. The lamps are distributed beside their supplies and half-bridge drivers.

D42 now sits above D41 to match the other CST stack, with clearance to C420. Its two front-copper nets use four fewer vias. See [placement review](docs/d42-placement-review.txt), [preview](docs/d42-placement-after.png) and [verification](docs/d42-placement-verification.json).

J5 is the library HRO TYPE-C-31-M-12 USB-C receptacle, **for programming only**. It connects to the module’s native ESP32-S2 USB data pins; power the controller from its normal supply. Host VBUS is isolated from VIN_5V and feeds only ESD protection and a sense divider on J1.20 (ESP GPIO8). Firmware must configure that GPIO as the self-powered USB VBUS monitor; this edit does not change firmware. See [USB-C review and checks](docs/usb-c-review.txt) and [connector contacts](docs/usb-header-pinout.csv).
