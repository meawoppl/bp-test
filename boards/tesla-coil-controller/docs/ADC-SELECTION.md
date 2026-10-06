# ADC selection — 2026-09-27

## Decision

Use **AD7606C-16BSTZ**, LCSC **C5371769**, for the initial design. This is the **C-16**
generation, not AD7606BSTZ (original) or AD7606BBSTZ (B generation).
Eight independent sample-and-hold/ADC channels share one conversion-start edge.
The accessible LQFP package suits hand inspection and repair.

| Candidate | Simultaneous channels | Maximum per-channel sample rate | Relevant analog bandwidth | Decision |
|---|---:|---:|---|---|
| TI ADS8588S | 8 | 200 kSPS | 16 kHz at ±5 V; 24 kHz at ±10 V | Reject for raw 30 kHz waveform |
| AD7606B | 8 | 800 kSPS | 13.5 kHz at ±5 V; 22.5 kHz at ±10 V | Reject despite faster digital rate |
| AD7606C-16 | 8 | 1 MSPS | High mode: 220 kHz generally; **150 kHz at 0–5 V and ±2.5 V** | Selected |
| AD7606C-18 | 8 | 1 MSPS | Wide-band family alternative | More bits/data than required; not a blind substitution |

Source documents:
- [TI ADS8588S datasheet](https://www.ti.com/lit/ds/symlink/ads8588s.pdf)
- [ADI AD7606B datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/ad7606b.pdf)
- [ADI AD7606C-16 datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/ad7606c-16.pdf)
- [LCSC C5371769](https://www.lcsc.com/product-detail/C5371769.html)
- [LCSC C5240947 reel variant](https://www.lcsc.com/product-detail/C5240947.html)
- [ADI AD7606C-18](https://www.analog.com/en/products/ad7606c-18.html)

The retrieved C5371769 product-page payload reported 175 units on 2026-09-27.
This is an observation, not a reservation or evidence of JLCPCB assembly inventory.
Confirm JLCPCB availability before release; acquisition IC cost is roughly the $50–60 class.
The local PDF is the manufacturer's datasheet mirrored by LCSC; pin assignment uses Table 9,
not the older AD7606 library symbol.

## Rates, timing and aliases

30 kHz is 33.333 us per cycle. A 200 kSPS stream has 5 us spacing, 6.667 samples/cycle,
and 54 degrees between samples. This is inadequate as a sole precise switching-edge clock.
A separate low-hysteresis comparator will feed FPGA global-capable J2.22/G0.
Its offset, hysteresis, noise and propagation delay must be calibrated; fast propagation alone
is not phase accuracy. For a sine, crossing error is approximately deltaV/(2*pi*f*Vpeak).

Eight channels × 16 bits × 200 kSPS = 25.6 Mbit/s, before framing. Four data lines require
32 SCLK edges per frame; at a provisional 25 MHz this is 1.28 us of shift time.
At 200 kSPS there is ample room in a 5 us frame for conversion, BUSY handling and readout.
Final FPGA timing must use datasheet worst-case times and setup/hold, not these nominal sums.
1 MSPS is an ADC rating, not a validated carrier/FPGA throughput claim.

Prefer a higher acquisition rate and FPGA filtering/decimation if useful; sample-rate changes
must also change the anti-alias plan. The 220/150 kHz analog bandwidth exceeds the 100 kHz
Nyquist limit at 200 kSPS. **It is not sufficient anti-alias filtering by itself.** The initial
100R/1nF input RC (~1.59 MHz) is only an EMI/ringing placeholder. Specify external filtering
from the expected harmonic and interference spectrum, and measure amplitude/phase response.
A rectified 30 kHz waveform contains 60 kHz ripple and higher harmonics; decide whether CH6
is instantaneous absolute current or an envelope before choosing its smoothing bandwidth.

USB full-speed cannot stream this entire raw data rate. FPGA buffering, triggered capture,
statistics and decimation are expected. ESP32 Wi-Fi/USB transport must not determine timing.

## Electrical configuration

AVCC 4.75–5.25 V; VDRIVE 3.3 V. Do not expose FPGA pins to 5 V logic.
OS0/OS1/OS2 high selects software mode; PAR/SER high selects serial operation.
Internal reference enabled. Each AVCC pin has 100 nF; bulk 10 uF; VDRIVE 100 nF;
REGCAP36 and REGCAP39 each have separate 1 uF; REFIN42 has 100 nF;
REFCAP44/45 connect together with 10 uF. Reference outputs are not external load supplies.

Power-up sequence: hold conversion low and chip-select high, apply full ADC reset,
configure four DOUT lanes, select high analog bandwidth and channel ranges, read back
configuration, verify known test voltages and BUSY timing, then enable continuous capture.
Do not rely on reset range/bandwidth defaults. CH5/CH7 use ±2.5 V for the two CST raw paths; CH6/CH8 and CH1–CH4 use 0–5 V.
Firmware/HDL and final signal conditioning are not implemented by this draft.

## CST implementation update — 2026-09-28

See [CST-INPUT.md](CST-INPUT.md) for the implemented burden, rectifier, phase circuits. CH5/CH7 use ±2.5 V, CH6/CH8 use 0–5 V, all with high bandwidth. CH1–CH4 are auxiliary 0–5 V inputs in AUX1/AUX2/AUX3/AUX4 order; use [adc-channel-map.json](adc-channel-map.json). Overcurrent is assigned to the ADC/FPGA; see OUTPUT-STAGE.md for the implemented unrouted GDT bridges. The chosen source is now two 12 V car batteries in series (24 V nominal), directly supplying the GDT bridges.
