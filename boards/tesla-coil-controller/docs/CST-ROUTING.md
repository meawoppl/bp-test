# CST routing milestone — two copper layers

Both current-transformer input chains and the shared TPS60403 negative-rail generator are locally routed on F.Cu/B.Cu. The board is now nominal 1.6 mm, **two copper layers**; the constructor preserves that choice. This is a development routing milestone, not manufacturing output.

The local routes cover the input common-mode chokes, permanent burdens, TVS/clamp networks, precision rectifiers, magnitude filters, phase comparators, bypass capacitors, and test points. The two sensor chains use the same geometry translated 23 mm vertically. The −5 V converter's capacitors were rearranged for short top-layer flying-capacitor and local input/output paths. Small comparator bias/clamp orientation changes make the signal paths more direct. No schematic connectivity or component values changed.

Signal routes are mostly on top. Bottom routes handle raw-signal distribution, selected feedback crossings and supply distribution. Ground pours on both faces now extend across the board after the positive-supply routing step; ground vias provide decoupling returns and join the pours. Zone-connected pads use thermal reliefs. The local ground network has native connectivity to every ground pad in this region; it now joins the board-wide return planes. The +5 V branches now share one feed from R20.2 in the ADC section above, with independent branches for each CST row and the charge pump. R20.1 is now connected back to the 5 V regulator output; the local +3V3 comparator network is connected directly to U2 through its own 0.35 mm F.Cu feed. The later AUX routing pass completes the −5 V feed to all four AUX amplifiers.

## Placement and supply cleanup

C401/C403 and their channel-2 equivalents now stand directly below the positive supply pins. C402/C404 remain directly beside the negative supply pins. Each has a local ground-return via outside its solder pads. R402/R403 are arranged at the rectifier summing input; R404–R406 form an aligned resistor column, and R407 exits straight into the summer input. R408 and C400 share an aligned envelope junction beside their test points. Channel 2 repeats this arrangement exactly, 23 mm lower.

The old +5 V detours were removed. One 0.5 mm entry/trunk from R20.2 feeds shorter 0.4 mm local branches, with short layer bridges at signal crossings. The −5 V branches run above the amplifier feedback networks; the second row no longer has an unused continuation beyond its branch. J4 and J30 now share the same X=27.5 mm pad-column position and orientation. Their Y positions and the board outline are unchanged.

The shared −5 V generator now sits in the middle of the gap below the AUX section and above CST 1. U44 and its five support passives moved together 17.6 mm right, preserving their local loops and ground returns. The +5 V entry and −5 V output leads are each 17.6 mm shorter; no vias were added. Adjacent silkscreen frames and labels follow the new position. See `negative-rail-placement.json` for the focused placement/connectivity audit.

## ADC handoffs completed — 2026-09-29

All four analog signals now reach their ADC input filters, using 0.25 mm copper. Channel assignments and component values are unchanged.

| Signal | Source | Input filter | ADC channel / pin |
|---|---|---|---|
| CT1_RAW | R400.1 | R5 / C15 | CH5 / U1.57 |
| CT1_ENVELOPE | C400.1 | R6 / C16 | CH6 / U1.59 |
| CT2_RAW | R600.1 | R7 / C17 | CH7 / U1.61 |
| CT2_ENVELOPE | C600.1 | R8 / C18 | CH8 / U1.63 |

CT1_RAW's existing takeoff via moved to (76.2, 122) mm for a direct approach to R5. The four final approaches use front-layer vertical trunks and 45-degree miters. CT2_ENVELOPE has a 2 mm rear-layer crossover between (87, 126.3) and (87, 124.3) mm to untangle the reversed incoming pair without changing channels. Its two through vias use 0.6 mm lands / 0.3 mm drills and are outside component pads.

The native connectivity audit verifies both the source-to-filter connection and each separate filter-to-ADC net. All four pass. Whole-board opens fell from 29 to 25; ERC, native physical DRC and schematic parity are zero. There are no remaining intentional dangling tracks, and `routing-intent.json` now has an empty open-end list.

Both comparator outputs remain connected to J2.22/G0 and J2.24/G1. The +3V3 supply now comes directly from U2/C21 on F.Cu to the existing supply via at (98.0875, 123.5) mm beside R414. This removes the previous thin feed from the ADC pull-up branch and the regulator-side layer transition. The new front-layer path clears C21 and its ground-return via.

## Front-layer 3V3 branches — 2026-09-29

The local comparator/pull-up/clamp supply branches now use 0.30 mm F.Cu copper. Three supply vias per channel were removed, six total: the R411/R611, D43/D63 and C424/C624 branches. Each channel retains the R414/R614 entry via and C413/C613 supply via for the shared rear trunk. That trunk crosses both comparator-output and zero-crossing routing; keeping the short rear portion avoids introducing signal-layer changes. Ground-return vias, signal copper, component values and net assignments are unchanged. Native checks remain zero ERC/physical DRC/parity, with the same 25 unfinished whole-board connections.

R416 is aligned above C413 at X=109 mm (3.45 mm center spacing). C413 stays at its existing bypass location; only the resistor moved 1 mm left, with local 45-degree lead adjustments and no via changes. See `r416-c413-alignment.json` for the annotation audit.

C429, the 1 nF CT1_RAW shunt capacitor, now sits at (54.7, 137) mm beside R401 and D40, clear of the rear +5V_ADC supply trunks. Its signal lead runs from TP40 on the front layer; its ground lead shares R401's existing ground-return via. The former ground via and redundant short segment were removed. The electrical netlist is unchanged, and native ERC/physical DRC/parity remain zero with 25 whole-board unfinished connections. See `c429-placement.json`.

U42's passive group now follows aligned columns. R414 moved to X=100 mm, matching D43/C410 below it. C412 remains below R415 and rotates to put its CT1_MID pad on the left for a direct vertical feed. C424 moved to (109, 136.4) mm, completing the R416/C413 column at 3.45 mm spacing. The two relocated ground vias match the adjacent return-via columns. Seven redundant trace segments were removed and no vias were added. Native connectivity, ERC, physical DRC and schematic parity pass, with the same 25 unfinished whole-board connections. See `u42-passive-alignment.json`.

D62 now sits at (65, 147) mm above D61, with the pair aligned at 3 mm pitch. Its connection to R603 and the R605/R606 branch now runs on F.Cu. The amplifier-output path around C602 was shortened, and the former lower feedback detour was removed. The two CT2 rectifier nets lose two vias and 4.23 mm of copper. Polarity and net assignments are unchanged. Native ERC, physical DRC and schematic parity are zero; local connectivity passes with the same 25 unfinished whole-board connections. See `d62-placement.json`.

D42 now sits at (65, 124.5) mm above D41, completing the matching CST1 diode move. Its 2.5 mm pitch clears C420. Both CT1_RECT_DRIVE and CT1_HALF stay on front copper, removing four vias and 12.97 mm of combined trace length. Polarity and all pad-connectivity clusters are unchanged. Native ERC, physical DRC and schematic parity are zero; six whole-board opens remain. See [placement review](d42-placement-review.txt).

## Verification and review

The following counts describe the original CST milestone. [COMMAND-AND-ADC-CLEANUP.md](COMMAND-AND-ADC-CLEANUP.md), `cst-routing-audit.json` and `validation.json` record the current state, including the completed ADC handoffs above.

- Native ERC: zero. Schematic parity: zero.
- Native physical checks: six findings, all six being the explicitly unfinished handoff ends; no shorts, clearance errors, courtyard overlaps or silkscreen conflicts.
- `check_tesla_cst_routing.py` uses KiCad's native connectivity graph, not endpoint proximity: all local pads on **35 nets** belong to their respective connected clusters. The CST work reduced whole-board unconnected count from **704 to 541**; the subsequent positive-supply/ground routing reduced it further to **284**. The JSON DRC report caps its displayed open-connection list at 499, so that display count is not the actual board total.
- All tracks are octilinear. Isolated right-angle bends use 45-degree miters; branch points and pad/via anchors remain intact. A collinear-overlap audit now catches duplicate segments that can conceal tails from native DRC; none remain in the owned CST routing.
- A separate native pad hit-test found no via drill overlapping an SMD pad. All added vias are through vias, 0.6 mm land / 0.3 mm drill.
- Native front/back copper renders were reviewed for input-pair continuity through the choke, local feedback loops, short decoupling links, return pours, testpoint access, and intentionally unfinished endpoints. Grounded cable return is after the choke; neither input conductor bypasses the choke.
- All eight rectifier/summer supply decouplers are aligned directly with their respective supply pins: 1.8000 mm for +5 V and 1.9125 mm for −5 V, measured center-to-center from IC pin to capacitor power pad. Comparator supply decouplers are also within approximately 2 mm pin-to-pad. The charge-pump output capacitor is approximately 2.8 mm pin-to-pad because of component courtyards; its switched loop remains local on the top layer. Comparator CT1_MID filter capacitors are reference filters, not supply bypass capacitors; their approximately 3.2 mm input-pin distance is intentional.

At the CST-only milestone, the **whole-board plugin quality report was not green**: 313 errors, 2582 warnings and 35 informational findings. The errors consist of 21 explanatory-silkscreen findings (the user-requested region frames/captions), 286 heuristic silk conflicts/clearances that are not reproduced by native KiCad DRC, and the six intentional route ends. The previously reported via-in-pad issue was real and was fixed. Remaining BOM, placement and decoupling warnings elsewhere on the board remain open for later work. These counts are recorded for transparency, not a release waiver.

No Gerbers or assembly outputs were published. Complete the remaining board routing, source/return connections and outstanding electrical/manufacturing reviews before publishing a fabrication set.

## Reproduction

Use `/usr/bin/python3 tools/hardware/tesla_route_reviewed.py` for the current copper and placement snapshot. It checks the electrical contract before replay, fills ground zones, and preserves project rules. The older `tesla_route_cst.py` is a historical incremental pass and must not be run over this board.

`check_tesla_cst_routing.py` checks local and ADC connectivity, layers, via/pad clearance, trace angles and collinear overlaps. `check_tesla_draft.py` checks native ERC/DRC/parity and refreshes the schematic PDF. Current placement and connection metadata live in `tools/hardware/tesla_placement.json` and `docs/circuit.json`.
