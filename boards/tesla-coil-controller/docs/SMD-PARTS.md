# Surface-mount-only component policy

All fitted non-connector components are SMD. Mechanical mounting holes remain NPTH; only connectors may have plated through-hole pads.

The three former electrolytic reservoirs are now 24 TDK CGA9P3X7R1H226MT0Y0N MLCCs (LCSC C49297044), eight per location. Each is 22uF/50V X7R, ±20%, 2220 (5750 metric), nominal 5.7 × 5.0 × 2.5mm. Project-local KiCad C_2220_5750Metric footprints and standard STEP models are used. See [CERAMIC-RESERVOIRS.md](CERAMIC-RESERVOIRS.md) for references, bias/temperature qualification and pulse-load sensitivity. The old Panasonic library assets/datasheet are retained only as design history; no can capacitor remains populated.

Q50–Q57 are STD80N10F7, 100V DPAK, LCSC C2832811; pins 1 G, 2/tab D, 3 S. Q30/Q31 belonged to the removed main converter.

Native ERC, physical DRC and schematic parity pass. Pad-type audit confirms no non-connector plated through-hole pads. Board remains unrouted.
