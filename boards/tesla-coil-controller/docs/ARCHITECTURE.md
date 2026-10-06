# Controller architecture

1. CST 1 → two-conductor common-mode choke and small cable/burden capacitors → permanent 10-ohm burden/clamp → raw bipolar ADC CH5.
2. Parallel two-op-amp precision rectifier → filtered magnitude ADC CH6.
3. Parallel biased TLV3501 comparator → FPGA global input G0 for phase timing.
4. Second independent CST raw/envelope → ADC CH7/8; four unity-gain-buffered, RC-filtered auxiliary 0–5 V measurements → ADC CH1–4 in AUX1/AUX2/AUX3/AUX4 order. See [adc-channel-map.json](adc-channel-map.json).
5. FPGA uses ADC current samples for overcurrent decisions, schedules phase lead and balanced bursts, and terminates drive at the selected current-zero event.
6. Eight independent FPGA gate commands → individual 33-ohm series resistors and 2.2-kohm input pull-downs → four UCC27282 half-bridge drivers → two 24 V MOSFET full bridges → two existing 1:1 GDTs.

The separate analog overcurrent window/NOR/threshold circuitry has been removed at the user's direction. There is no independent hardware overcurrent latch or watchdog implemented. Driver input interlocks and UVLO remain; FPGA logic must enforce deadtime, maximum pulse duration, data/phase validity, and intentional rearming. Input interlock is not timed deadtime.

Power comes from two series 12 V car batteries (24 V nominal). VBAT_24V directly powers both GDT bridges. U30/U31 LMZ14202H integrated-inductor modules independently convert battery power to 12 V driver bias and 5 V module/ADC power, followed by local 3.3 V logic. No 9 V rail or regulated 24 V converter remains. See POWER-DESIGN.md for module values and qualification gates.

The output follows UD2.7's differential GDT-primary drive, local energy storage, series nonpolar DC blocking and damping. It replaces the complementary N/P power stage and AC-coupled predriver gates with all-N-channel bridges and bootstrap half-bridge drivers. See [OUTPUT-STAGE.md](OUTPUT-STAGE.md) for parts, states, calculations and remaining qualification.

References: [UD2.7 explanation](https://www.loneoceans.com/labs/ud27/) and [UD27C through-hole schematic](https://github.com/profdc9/DRSSTC-PCB-Pack/tree/master/ud27c%20thru%20hole). The manufacturer's UCC27282 pinout and truth table, not the reference's older driver pinout, govern this implementation.

User-confirmed load: eight CM600HA-24H, two in parallel at each of four H-bridge positions, isolated by two existing 1:1 GDTs. The accepted 24 V drive decision remains in DRIVE-DECISION.md. Each IGBT requires its own external gate network. Transformer winding polarity, magnetics, cable parasitics and gate-network behavior remain hardware qualification items.

The PCB is a development placement with local output links and incomplete routing, not a manufacturing release. CT and GDT boundaries provide the intended isolation; USB/auxiliary/service connections share controller ground.

Dual-CST carrier mapping: CT1_ZERO → J2.22/G0, CT2_ZERO → J2.24/G1, J2.33 reassigned to GDT2_L_HI after J6 removal. The shared −5 V pump feeds both rectifiers; signal paths and phase midpoints are separate. See CST-INPUT.md.
