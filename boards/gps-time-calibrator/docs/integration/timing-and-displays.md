# Timing capture, receiver commands and displays

This describes the intended application for RFC v1. It is a new integration
contract, not the behavior of the incomplete predecessor firmware.

## Receiver startup and command transaction rules

U6 is MAX-M10S-00B-01. ESP GPIO43 TX goes to GPS RX; GPIO44 RX receives GPS TX.
Use USB for the console. Default UART is38400 8N1; the old firmware's9600 setting
must not be assumed correct for this receiver. Try the documented default first;
if a previously configured receiver does not respond, probe other deliberate
known baud settings using checksummed MON-VER responses rather than accepting
random readable bytes as detection.

1. Power/reset using the main guide. Install a UART RX ring buffer before sending
   configuration. Budget e.g.8KiB initially and track overflows/errors.
2. Poll **UBX-MON-VER (class0x0A,id0x04)**, zero payload:
   `B5 62 0A 04 00 00 0E 34`. Log firmware and PROTVER. The attached reference
   is [M10 SPG5.10](../../../../libraries/datasheets/M10-SPG-5.10-interface.pdf);
   select the matching manual/key support if the delivered firmware differs.
3. Configure with **UBX-CFG-VALSET (0x06,0x8A)**, RAM layer only. Wait for
   ACK-ACK `(0x05,0x01)` or fail on ACK-NAK `(0x05,0x00)` for that command.
   Sending bytes successfully is not evidence the receiver accepted them.
4. **UBX-CFG-VALGET (0x06,0x8B)** each setting and compare value/type. Send only
   one SET at a time so an ACK identifies the active transaction. Bound retries.
5. Change UART baud separately to115200, drain the transmitter, reconfigure the
   ESP UART, then confirm MON-VER and baud readback at the new rate. The ACK can
   straddle the baud transition; recovery must try old/new rates deterministically.
6. Reapply on every GPS power cycle. V_BCKP follows switched GPS power; do not
   assume nonvolatile configuration, retained epoch association or hot start.

UBX frames use `B5 62 class id length_le16 payload checksumA checksumB`.
Checksum accumulates class through payload (excluding sync). Integer payload
fields are little-endian. Put malformed-length/checksum bounds in the parser
before accessing payload fields. Maintain raw capture alongside parsed records.

The offline helper prints SET/readback packets and checksums:

```bash
# From bp-test root; this does NOT send anything to hardware.
python3 tools/hardware/calibrator_ubx_commands.py > /tmp/calibrator-ubx-recipe.json
```

There is no USB-to-GNSS bridge firmware installed by this helper. Implement
UART transport in the ESP application; do not send these bytes to the ESP USB
console and expect transparent forwarding.

### Initial receiver profile

The helper encodes these initial choices:

| Setting | Intended value |
|---|---|
| UART input/output UBX | Enabled; NMEA output disabled after detection |
| UART baud | 115200 after validated transition |
| Power management | Full operation; EXTINT wake/backup/inactivity controls disabled |
| CFG-RATE-MEAS / NAV | 1000ms /1 (1Hz epochs) |
| CFG-RATE-TIMEREF | GPS (1) |
| CFG-TP-PULSE_DEF / PULSE_LENGTH_DEF | PERIOD (0) / LENGTH (1) |
| CFG-TP-PERIOD_TP1 and PERIOD_LOCK_TP1 | 1,000,000µs |
| CFG-TP-LEN_TP1 / LEN_LOCK_TP1 | 0 /100,000µs (suppress unlocked pulses; locked pulse100ms) |
| CFG-TP-TP1_ENA / SYNC_GNSS / USE_LOCKED / ALIGN_TO_TOW | All true |
| CFG-TP-POL_TP1 | Rising edge marks second boundary |
| CFG-TP-TIMEGRID_TP1 | GPS (1), explicitly retained in log metadata |
| CFG-MSGOUT-UBX_NAV_PVT_UART1 | 1 |
| CFG-MSGOUT-UBX_NAV_TIMEGPS_UART1 | 1 |
| CFG-MSGOUT-UBX_TIM_TP_UART1 | 1 |
| CFG-MSGOUT-UBX_TIM_TM2_UART1 | 1 |

Relevant output keys respectively: NAV-PVT `0x20910007`, NAV-TIMEGPS
`0x20910048`, TIM-TP `0x2091017E`, TIM-TM2 `0x20910179` (U1 values).
These rates operate on receiver epochs/events, not “send on every UART ISR.”
Do not copy the predecessor's later1kHz PPS change: keep1Hz through first integration.

Read/log `CFG-TP-ANT_CABLEDELAY` and `CFG-TP-USER_DELAY_TP1` as part of the
profile. Do not silently program zero, accept a factory cable-delay estimate as
measured truth, or compensate the same delay twice. TIM-TM2 uses the configured
time reference and timing corrections too. Derive the final cable/input/output
calibration with a known reference and record its sign/convention/version.

## What to capture on an external trigger

The input SMA feeds R8/C75, U9 comparator, U7 translator, then **three branches**:
FPGA pin38, ESP GPIO21 and MAX-M10S EXTINT pin5. The GPS and FPGA thus observe
the same conditioned event. U7 needs GPS power even if only FPGA capture is desired.

Continuously parse GPS UART; do not start listening after an event. On each trigger:

1. FPGA synchronizes the event and latches a **64-bit free-running OCXO tick**,
   event sequence, edge polarity, current PPS sequence and validity flags into
   a FIFO. Simultaneously log each PPS with its tick and sequence. Capture both
   edges if pulse-width measurement is wanted. Define behavior at coincident
   trigger/PPS edges in HDL and test it.
2. ESP GPIO21 ISR may record a diagnostic ESP timer stamp and wake a task;
   it must not parse UART, render OLED or block on SPI. That software stamp
   is not the precision result.
3. ESP drains FPGA records in batches and keeps a queue awaiting absolute-time
   association. Save receiver NAV-PVT, NAV-TIMEGPS, TIM-TP and raw TIM-TM2 frames
   before/after the event, with monotonic UART receipt times as **transport
   metadata only**.
4. Join events by pulse order/count and measured time relative to known PPS
   epochs, respecting flags and gaps. Never join simply to the “most recent
   serial sentence.” Reset/rollover breaks continuity and starts a new session.
5. Emit a record even if GNSS data is missing, explicitly marking it relative,
   holdover or invalid. Do not fabricate an absolute time to keep the stream uniform.

### M10S event-rate limit

[Integration manual §3.8](../../../../libraries/datasheets/MAX-M10S-integration.pdf)
states that TIM-TM2 reports only the **last rising and last falling edge between
measurement epochs**. At1Hz navigation a camera can easily produce many more
triggers than individually reported timemarks. The FPGA FIFO preserves all events;
M10S timemarks anchor/cross-check selected ones. Count deltas detect omitted marks.
A rising and falling time in one TM2 message may belong to different pulses;
do not blindly subtract them for pulse width. Raising GNSS measurement rate is
not equivalent to an unlimited event queue and must be checked against receiver
capabilities/constellation configuration.

Start validation with isolated pulses comfortably below1Hz and away from epoch
boundaries. Then test bursts, count gaps and FIFO overflow. For expected peak rate
`R` and worst-case host stall `T`, allocate at least `ceil(R*T)` event slots plus
margin; use available FPGA block RAM deliberately. Overflow must latch a counter
and invalidate completeness, not silently overwrite old entries.

### Exact TIM-TM2 parsing

Class/id **0x0D/0x03**, payload28 bytes, little-endian:

| Byte offset | Type | Field |
|---|---|---|
| 0 /1 | U1 /X1 | EXTINT channel / flags |
| 2 | U2 | Rising-edge count (wraps16 bits) |
| 4 /6 | U2 /U2 | Rising/falling week |
| 8 /12 | U4 /U4 | Rising TOW milliseconds / additional nanoseconds |
| 16 /20 | U4 /U4 | Falling TOW milliseconds / additional nanoseconds |
| 24 | U4 | Accuracy estimate, nanoseconds |

Flags: bit0 mode, bit1 running/stopped state, bit2 new falling edge,
bits4:3 timebase (0 receiver,1 GNSS,2 UTC), bit5 UTC available, bit6 time valid,
bit7 new rising edge. **The old parser's `(flags & 0x02)` UTC test is wrong.**
Do not set an event globally valid merely because length/checksum passed.
Require the relevant new-edge flag and valid time/timebase, preserve accuracy,
and only unwrap16-bit count inside a continuous session with bounded gaps.

For GNSS/GPS timebase, the rising time is
`week*604800 + towMsR*1e-3 + towSubMsR*1e-9` seconds from the GPS epoch.
Keep integer week/seconds/nanoseconds for precision; do not add a large epoch
and fractional seconds in32-bit floating point. If timebase=UTC use its stated
convention, not the GPS conversion. GPS−UTC is receiver-provided valid leap-second
data, not a hard-coded constant.

### PPS absolute-time association

**TIM-TP (0x0D/0x01)** describes the **next** TIMEPULSE event, not necessarily
“the pulse when the bytes arrived.” Use its week/TOW/refInfo/lock/validity and
observed PPS records to establish the association; test ±1-second ambiguities
under delayed UART transport. Its fractional TOW is **2^-32 milliseconds**,
unlike TIM-TM2's nanoseconds. Its signed `qErr` is **picoseconds**; preserve it
and its validity flag. Apply correction only after verifying the receiver's sign
convention on a reference measurement.

NAV-TIMEGPS (0x01/0x20) supplies GPS week/TOW/leap validity; NAV-PVT (0x01/0x07)
supplies UTC calendar fields, time accuracy and resolved/valid flags. Date/time
being printable is not equivalent to calibrated time. Log raw fields and flags.
Use GPS seconds as the continuous internal epoch, converting to UTC for humans;
handle leap seconds explicitly rather than assuming every UTC minute has60seconds.

## FPGA timebase and optical encoding

OCXO is **10MHz**: one raw tick=100ns nominal. Use a free-running64-bit counter,
with captured PPS ticks; never reset the primary event counter every second.
PPS synchronization introduces a fixed pipeline delay plus sampling quantization;
record/calibrate it. A global-clock-capable PPS pin does not require treating PPS
as a separate clock: synchronize it to the OCXO domain and edge-detect there.

Measure ticks per PPS interval, filter frequency over multiple valid seconds and
track residuals. Warmup/aging/frequency error still matter even with an OCXO.
No DAC/frequency-control line is fitted to Y1: the design estimates/disciplines
**digital phase/frequency**, not a voltage-controlled oven oscillator.

For an event between accepted PPS captures `C0` and `C1`:

`time_event = epoch(C0) + (Cevent - C0)/(C1 - C0)`.

This retrospective interpolation may improve the record after the next PPS;
preserve the raw ticks. The live display must instead use an estimate available
at that instant; record frequency/phase-estimator updates so its shown word can
be reconstructed. If PPS is lost, mark holdover/uncertainty; initial policy blanks
calibrated optical output until lock requalifies.

The live optical word is `floor(fractional_second * 65536) & 0xffff`, natural
binary, bit15 leftmost. All four rows show the **same16bits**, no row multiplexing.
Rising logic turns a column on. Do not freeze the live display at a trigger:
latch a separate event record while the optical counter keeps running.

A practical fixed-point implementation uses a sufficiently wide phase accumulator
or remainder accumulator with increments corresponding to65536steps per measured
second. At nominal10MHz, intervals are152 or153clock ticks, averaging
152.587890625ticks per optical increment. Reset/reconcile the display phase at
accepted PPS according to a documented boundary policy; never let a premature
wrap create an unmarked false second. Use registered outputs, real reset logic,
and one coherent word update. Do not use the old `/732` divisor.

Each LSB spans **15.2587890625µs**. Raw FPGA capture granularity100ns does not
make the optical word1µs resolution. Camera sub-LSB inference needs calibrated
transition positions, exposure integration and row readout; binary carry edges
can change many LEDs with finite channel skew. Measure these with photodiode and
scope, use ambiguity flags near transitions, and record the optical decoding
model. Gray encoding would be a different protocol/decoder and must not be
silently substituted.

LED enable sequence: FPGA data0 → validated rails/time (or explicit test mode)
→ /OE low. Shutdown does /OE high first. Begin with `0x0001`, walking ones,
`0x8000`, `0x5555`, `0xAAAA`, all-on briefly, then dynamic time. Per-LED resistors
help current uniformity; LED binning, optical efficiency and camera response still
need measurement. Avoid asynchronous brightness PWM during calibration unless
its exact effect is included in the optical protocol.

Input RC+divider ideal latencies are approximately0.696µs rising /0.676µs falling
for low-impedance0–5V input, before comparator/translator/FPGA delay. Actual source
impedance, amplitude and slew change them. GPS tags the **conditioned** edge,
not the connector crossing. Calibrate the complete SMA-to-capture and output
paths; do not equate GPS accuracy with total system accuracy.

Output SMA is 5V AHCT through33Ω into a **high-impedance** load, not5V into50Ω.
Schedule output edges in FPGA tick space, never via a FreeRTOS delay. A loopback
cable from J7 to J6 allows end-to-end latency tests and GNSS timemark cross-checks.
There is no onboard internal output-to-EXTINT loopback without that cable.

## Human date/time screen (OLED, not LCD)

DS1 is HS96L03W2C03 / SSD1315,128×64, address0x3C, on the separateGPIO1/2bus.
Use the [module datasheet](../../../../libraries/datasheets/HS96L03W2C03.pdf),
including its sample initialization on page15. Commands use I²C control byte0x00;
framebuffer data uses0x40. Its documented page-address mode supports8pages×128bytes.

Starting command sequence transcribed from the module example (review against
received hardware, retain parameter bytes, send only after supply settles):

```text
AE 00 10 40 81 CF A1 C8 A6 A8 3F D3 00 D5 80 D9 F1 DA 12 DB 30 20 02 8D 14
```

Clear display RAM while off, then command `AF`. For each page0..7 send commands
`B0|page`, `00`, `10`, then128data bytes with the0x40data control byte. Chunk transfers
as required by the I²C driver, repeating the proper control byte. `AE` blanks it;
`AF` re-enables. Use `81,<contrast>` to reduce brightness; A1/C8 control orientation.
Confirm the module-specific power-up delays and charge-pump sequence (datasheet
pages13–15); don't rely on a generic “SSD1306 compatible” label as validation.

Display at e.g.2–5Hz from a single coherent software snapshot:

```text
2026-09-27 19:35:12 UTC
GPS VALID   OCXO READY
INPUT #1234  +0.123456 s
5V/3A   switched 0.82A
```

Replace time with `NO VALID TIME`, `WARMING`, `ACQUIRING`, or `HOLDOVER` when
appropriate. A1Hz calendar advance can be extrapolated from a validated PPS epoch,
but do not overwrite it on arbitrarily delayed NAV messages. The OLED is for
humans; its scanning/refresh is not part of the calibrated optical array.
Render outside UART/edge/SPI-critical paths; allow OLED blanking during camera tests.

## Proposed persisted event record

Implement an append-only record with at least:

- Session/boot ID, schema version, hardware tag, app/FPGA hashes, ABI, calibration ID.
- Event sequence, edge, FPGA tick64, PPS sequence and previous/next PPS ticks.
- Calculated GPS week/TOW/ns, optional UTC text, time validity/holdover and uncertainty.
- Raw TIM-TM2 payload + channel/count/flags/accuracy when matchable; explicit
  unmatched/ambiguous status otherwise. Keep raw NAV/TIM-TP messages in the log.
- Live optical word/phase-estimator version at capture, output-schedule ID if relevant.
- UART receipt timestamp, frame/parse errors, FPGA FIFO losses and host log drops.
- Power states, PD contract snapshot, switched current, OCXO warmup age.

Use bounded queues and sequence numbers so transport losses are visible. USB/Wi-Fi
logs must not block FPGA capture or ISR work. At receiver resets, OTA, changed
configuration/calibration, GNSS jumps or unwrappable counters, close the session
or explicitly record a discontinuity. Do not merge unrelated epochs by proximity.
