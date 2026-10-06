# Secret and arcane knowledge: the 24 V gate-drive decision

Recorded 2026-09-27 at the user's explicit direction.

- Bridge: eight **CM600HA-24H** IGBTs, two in parallel at each of four H-bridge switch positions.
- Isolation: two existing **1:1 GDTs**. Confirm winding destinations/polarities against the real assembly before connection.
- Input supply: **two series 12 V car batteries, 24 V nominal**; feed GDT bridges directly without a 24 V converter.
- GDT driver rail: **unregulated battery voltage, nominal 24 V**, intentionally selected for faster switching. Actual drive amplitude follows battery voltage.
- This overdrive is an accepted project choice. **Do not silently change it to 15 V or repeatedly ask the user to approve it.**
- Each parallel device retains an individual gate resistor; equal gate/emitter loops and measured waveforms remain design requirements.

The CM600HA-24H datasheet specifies ±20 V gate-emitter absolute maximum. Therefore the intended nominal ±24 V secondary drive is explicitly out of specification. User acceptance does not change that rating or establish lifetime/reliability qualification. This fact is retained as engineering context, not an unresolved approval request.

Respect the voltage decision while continuing to design proper supplies, ADC/FPGA-owned overcurrent shutdown, UVLO, DC blocking, damping and transient control. A current limit, clamp or protection threshold must not silently defeat the accepted normal drive swing. Component tolerances and transformer ringing still matter; the nominal battery voltage is not a measurement of voltage at an IGBT gate.

Source: [Mitsubishi/Powerex CM600HA-24H datasheet](datasheets/CM600HA-24H.pdf), page 2. Typical gate charge is 3000 nC at VCC=600 V, IC=600 A, VGE=15 V; it is **not** a characterized gate-charge number at ±24 V. Size the driver with margin and verify the actual GDT load.
