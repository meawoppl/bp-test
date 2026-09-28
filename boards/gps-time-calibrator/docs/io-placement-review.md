# Connector-side placement and PPS indicator

Reworked 2026-09-27. Canonical PCB and `circuit.json` preserve these placements;
construction/routing scripts in `tmp/` are historical and must not be replayed.

- USB protection U1 stays immediately behind J3. Always-on LDO U2/C2/C3
  moved above the eFuse into the USB/power cluster. R176/C78 now sit beside
  U14/R170, rather than beneath the daughterboard. The unfiltered eFuse
  current-mirror route is shorter; the longer ADC run is after the RC filter.
- U9 and U7 now share a horizontal input-channel axis. R8 feeds U9 directly;
  threshold divider/filter and bypass parts sit above/below the lane. R80/R81
  are beside U7 instead of near the bottom display, removing the long detour.
- U10 output pad, R162 and J7 signal pad share y70. The driver supply bypass
  is above it and its input pulldown sits directly to the left.
- GNSS RF input, controlled-impedance feed and J5 are unchanged. C8/C9 remain directly
  beside the receiver supply pins. R6/R7 now form a neat PPS fanout pair
  immediately left of U6; the GPS-enable pulldown is beside U5. Antenna
  bias resistor R5 now sits directly above the bias filter and is supplied by VCC_RF.
- D74 is a green PPS indicator above J5 at (197,81.7), driven directly through
  R179 1k following the SparkFun reference. U16/C79 and U8/C12 were removed
  in the subsequent [reference reconciliation](gps-reference-review.md).
  GPS reset now connects to GPIO40 through R180 33R.
- The indicator follows TIMEPULSE high, without a pulse stretcher. Configure
  the GNSS timepulse polarity and width for a visible 1Hz flash; no firmware
  changes are included. It is not independently a fix-valid indicator.
- Daughterboard mating connectors, display, compact OCXO thermal region,
  USB connector and all three SMA positions stay fixed. OCXO remains on
  FPGA G6 and PPS on G0. USB data routing is unchanged.

The UART runs now have a few straight sections and 45-degree bends instead
of short staircase segments. Input-to-FPGA copper is 24.04mm versus 59.68mm;
input-to-ESP copper is 45.73mm versus 85.68mm. These are total track lengths,
not timing/skew qualification. Full before/after totals are in
`io-routing-lengths.json`. Every newly drawn track is horizontal, vertical or
45 degrees. Inner-layer transitions avoid existing power/control routes.

Validation: native DRC, ERC and schematic parity; native drill-to-pad audit;
16-channel buffer/module mapping and OCXO G6 audit; visual schematic, top 3D,
pad-exit and local routing review. Broader heuristic findings are recorded
separately in `io-quality-summary.json`; they are not a production signoff.
Existing thermal, USB power-budget, RF and optical timing bring-up gates remain.

## Broader quality results

The earlier placement pass reported 53 heuristic errors, 4,750 warnings and 33 informational findings. See `gps-reference-quality-summary.json` for the latest counts.
The seven missing-bypass findings misidentify signal pins or VCC_RF
output; antenna bias filtering remains C10 after its series feed resistor.
Three heuristic via-in-pad reports name R175/J7, while the independent native
rotated-pad geometry check finds no drill intrusion (including both connector
sides). Existing optical row/bit legends account for 26 forbidden-text flags.
The native silkscreen checks pass; generic text/copper checks use different
geometry/thresholds and retain their earlier findings. The USB skew heuristic
applies its high-speed threshold to the unchanged full-speed USB pair.
Thousands of all-to-all bypass-distance comparisons are not actual component
to-supply pairings. These findings are retained transparently; thermal and
timing tests are still required on the prototype.
