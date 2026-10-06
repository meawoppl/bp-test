# AUX input routing

The four 0–5 V AUX channels are routed from J3/J8/J9/J10 through their
1 kΩ input resistors, RC filters and BAV199 clamps, through the OPA197 unity
buffers, and through the final 100 Ω / 1 nF filters to ADC channels 1–4.
Component values are unchanged. AUX1–4 now use the upper four ADC channels, CH1–4; CST1 raw/envelope use CH5/6 and CST2 raw/envelope use CH7/8. See [ANALOG-AND-DRIVE-CLEANUP.md](ANALOG-AND-DRIVE-CLEANUP.md) for the current placement and routing recipe.

Each input uses a straight local filter path on front copper. The two right-hand
cells have one short back-copper crossing of the 12 V supply trunk. Feedback
links use local back copper, with all vias outside the amplifier bodies and pads.
The converter pin escapes are straight, with a spaced fan-in behind the RC bank.

The −5 V branch now reaches all four buffers and their local 100 nF capacitors;
the 10 µF branch capacitor C741 is connected as well. Existing +12 V buffer and
+5 V clamp supplies are retained. Ground pours provide the returns, supplemented
by local bypass and ADC-filter return vias. The board remains two-layer.

C741 now sits directly above C733 beside U73, aligned at X=62.9 mm, with
a 2.1 mm front-copper connection to the existing negative-rail via. Its previous
isolated branch below the AUX section and its dedicated via were removed. The
capacitor remains a 10 µF bulk bypass; every amplifier retains its local 100 nF
decoupling. See `c741-placement.json` for the placement and connectivity audit.

The earlier milestone used `tools/hardware/tesla_route_aux.py` after the CST and power routing
scripts. Apply the final cleanup replay after the FPGA and H-bridge passes. Placement changes persist in `tesla_placement.json` and `docs/circuit.json`.
`check_tesla_aux_routing.py` verifies all 16 signal nets, the complete −5 V rail,
22 capacitor returns, routing angles, overlapping copper and via holes over pads.

The existing filter-response study is in `docs/aux/`; no new simulation was
needed because the circuit values did not change. This routing milestone is not
a whole-board fabrication release. See the current validation and quality reports
for remaining connections and review items.
