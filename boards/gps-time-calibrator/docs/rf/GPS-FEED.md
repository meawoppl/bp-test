# GPS antenna feed / stackup calculation

Calculated 2026-09-26 for the GPS calibrator carrier, not the 1.0 mm daughterboard.

## Fabrication stackup

Order **nominal 1.6 mm, four-layer JLC04161H-7628**, 1 oz outer / 0.5 oz inner
copper. The selected stackup is recorded in `.kicad-pcb.json` and the PCB file.
The SMA edge-launch connector is also selected for a nominal 1.6 mm board.

| Layer | Thickness (mm) | Relative permittivity |
|---|---:|---:|
| F.Cu | 0.035 | — |
| 7628 prepreg | 0.2104 | 4.4 |
| In1.Cu (GND reference) | 0.0152 | — |
| FR4 core | 1.065 | 4.6 |
| In2.Cu | 0.0152 | — |
| 7628 prepreg | 0.2104 | 4.4 |
| B.Cu | 0.035 | — |

Copper plus dielectric sum is 1.5862 mm, consistent with nominal 1.6 mm;
mask thickness is not the reference-plane spacing. Do not substitute an arbitrary
four-layer stackup with a different outer prepreg.
Source: [JLCPCB stackups and material parameters](https://jlcpcb.com/impedance).

## Geometry and calculated result

The straight GNSS_RF feed is on F.Cu from U6.11 (188.25,90.00) to J5.1
(197.46,90.00), length **9.21 mm**, width **0.26 mm**. The bias branch joins at
(192.25,90.00). Its 1.91 mm branch terminates at L1's RF pad.

Model: JLCPCB **CoatedCoplanarWaveguideWithLowerGnd1B** (grounded coplanar,
coated), using the [manufacturer calculator](https://jlcpcb.com/pcb-impedance-calculator).
Only numeric cross-section geometry was sent; no board files were uploaded.
Inputs (API uses mil):

- H1 = 0.2104 mm (8.283465 mil), Er1 = 4.4.
- Trace base W1 = 0.26 mm; top W2 = 0.2473 mm (0.5 mil etch taper).
- Coplanar gap D1 = 0.15 mm, ground width G1 = 0.508 mm (20 mil).
- T1 = 0.035 mm nominal copper; a second case uses 0.04064 mm (1.6 mil)
  to show sensitivity to finished/plated copper thickness.
- Mask C1 = 0.03048 mm (1.2 mil) above substrate and C2 = 0.01524 mm
  (0.6 mil) above trace, mask Er = 3.8, per JLCPCB's published parameters.

| Copper | Coplanar gap | Calculated impedance |
|---|---|---:|
| 35 um | 0.15 mm (design) | **50.50 ohm** |
| 40.64 um | 0.15 mm (sensitivity) | **49.84 ohm** |
| 35 um | 0.20 mm (gap sensitivity) | 53.21 ohm |
| 40.64 um | 0.20 mm (gap sensitivity) | 52.62 ohm |

`gps-feed-jlc.json` contains the complete submitted inputs and returned results.
Reproduce with `tools/hardware/calibrator_gps_impedance.py` (requires
websocket-client and network access). The 35 um design case gives effective
permittivity 3.1411 and approximately 5.912 ps/mm propagation delay, or 54.45 ps
for the 9.21 mm uniform line approximation.

## Physical scope and limits

The custom rule sets GNSS_RF-to-GND-zone clearance to 0.15 mm. Filled copper
sampling at x190,191,193,194 mm finds ground about 0.155 mm from the trace edge
(5 um sampling resolution). In1 GND is present beneath those points. At the
receiver pad, bias tee and wide SMA signal land the geometry deliberately departs
from a uniform transmission line; the calculator does not model their reflections,
connector launch, solder, finite ground shape, via inductance or antenna performance.
The return-plane sampling report is `gps-feed-geometry.json`.

Request a 50-ohm controlled-impedance outer-layer feed using this exact stackup
and have the fabricator confirm finished copper/mask/etch geometry before release.
These are nominal cross-section calculations, not VNA measurements or an RF
sign-off. Carrier routing is complete; native electrical checks are clean. Hardware RF validation remains outstanding.

## Independent-tool discrepancy

The managed kct CPWG calculation returned 77.77 ohm for nominal width/gap.
It is preserved in `gps-feed-kct.json` for reproducibility but **not used as the
manufacturing target**: inspection of its implementation shows a sinh substrate
mapping, unlike the tanh metal-backed mapping in the documented
[scikit-rf grounded CPW implementation](https://scikit-rf.readthedocs.io/en/latest/_modules/skrf/media/cpw.html),
and it omits this soldermask/etch cross-section. The JLCPCB coated grounded model
above is the applicable calculation here.
