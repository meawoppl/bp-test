# Ceramic battery and GDT reservoirs

The user requested large SMD **ceramics**, replacing the three 470uF electrolytic cans. Each location now has eight 22uF/50V X7R 2220 capacitors, wired in parallel. Nominal capacitance is **176uF per bank**; this is a pulse-load redesign, not an electrically identical 470uF substitution.

| Location | References | Placement |
|---|---|---|
| Battery input | C335–C342 | 2 columns × 4 rows beside J4 |
| GDT 1 | C526, C531–C537 | 4 columns × 2 rows beside bridge 1 |
| GDT 2 | C566, C571–C577 | Same arrangement beside bridge 2 |

The 2.2uF series DC-block capacitors and their 15-ohm/1uF damping branches are unchanged. Those are separate from the supply reservoir.

## Selected component

- TDK **CGA9P3X7R1H226MT0Y0N**, [LCSC C49297044](https://www.lcsc.com/product-detail/C49297044.html).
- 22uF ±20%, 50V, X7R; 2220/5750, nominal 5.7 × 5.0 × 2.5mm. X7R specifies ±15% temperature change at the specified test conditions, not a combined biased capacitance guarantee.
- 500 units listed in stock on 2026-09-28, $3.7019 each at 10 / $3.3704 at 30. About $89 of reservoir capacitors at the 10-piece tier for one board; inventory is not reserved and JLC assembly stock is not independently confirmed.
- [Local manufacturer catalog PDF](datasheets/TDK-CGA-MLCC.pdf), [Markdown extraction](datasheets/TDK-CGA-MLCC.md). Catalog family CGA9P3X7R1H226M250KB / CGA9P3X7R1H226MT****. Project-local standard KiCad C_2220_5750Metric lands and STEP envelope.
- [TDK family characterization](https://product.tdk.com/en/system/files/dam/doc/product/capacitor/ceramic/mlcc/charasheet/cga9p3x7r1h226m250kb.pdf) includes DC-bias, biased temperature, ESR and ripple curves. The characterization PDF download was blocked locally; the catalog was archived successfully. Do not represent estimated curve points as guaranteed minimum capacitance.

## Sizing and simulation

`tools/hardware/check_tesla_reservoirs.py` produces [results](gdt/reservoir-results.json), reproducible ngspice decks and [plot](gdt/reservoir-response.png). It models two synchronized bridges using charge pulses: a 0.8uF equivalent reflected gate capacitance moved through 48V consumes 38.4uC per reversal at 24V. The nominal pulse is 20A with 1.92us effective area, repeated at 60kHz during a 30kHz burst. This is an engineering sensitivity model, not an IGBT switching simulation.

We sweep **12uF and 4uF effective per 22uF part** (96uF and 32uF per bank) to expose loss of capacitance from bias, tolerance, temperature and aging. These are simulation assumptions, **not** manufacturer-guaranteed corner values. Exact biased capacitance across the intended operating temperature range remains a qualification gate. Bank ESR is assumed 5mOhm including connections; it also needs measurement/characterization.

| Case | Supply | Bridge rail min / max |
|---|---:|---:|
| 96uF effective bank, nominal pulse, 1uH leads | 24V | 23.31 / 24.10V |
| 32uF effective bank, nominal pulse, 1uH leads | 24V | 22.71 / 24.36V |
| 32uF, twice reflected load, 5uH leads | 30V | 25.28 / 32.09V |

The low-capacitance nominal model gives about 7.33Arms bank ripple during the burst, or roughly 0.92Arms per part with ideal sharing. The stressed case reaches 18.35Arms per bank / 2.29Arms per part. Do not extrapolate this to a continuous rating: measure temperature rise, actual duty cycle and current sharing. The former-can comparison uses its maximum impedance as an illustrative series-resistance assumption, not a precise ESR model.

## Required before fabrication / energizing

1. Confirm effective capacitance and ripple heating on the selected part across battery voltage, temperature, aging and pulse spectrum. Increase bank count or revise load/duty limits if the measured rail droop is unacceptable.
2. Complete input damping, inrush and transient protection. An idealized 30V hot-plug into 96uF total effective capacitance through 5uH/50mOhm estimates **51.2V unclamped peak**. It is a warning calculation, not a predicted protected waveform. The existing SMBJ30A maximum clamp of 48.4V does not protect the 42V-input modules adequately. This was already open and is more important with ceramic-only reservoirs.
3. Route short wide paired power/return paths from each bank to its bridge. The floorplan is not a routed-current-sharing guarantee. The former 2.2uF/100nF bypass pairs beside each bridge were removed on 2026-10-07; the paralleled bank is the only local bypass, so its placement against the bridge loop matters. Avoid strain near large MLCCs; verify assembly/board-flex suitability.
4. Validate with actual GDTs, gates, cable lengths and synchronized/independent command patterns. Models omit nonlinear Miller behavior, core saturation, PCB parasitics and regulator input dynamics.

Circuit contract, symbols and native ERC/physical DRC/parity are checked. The board remains an **unrouted development draft**, not an approved fabrication package.
