# programming-carrier-v1-test

Bring-up firmware and FPGA image for the ESP32-S2 + iCE40 module v1 mounted on
the programming carrier v1. It walks every carrier monitor LED that firmware
can safely drive. It's an [affogato](https://github.com/meawoppl/affogato)
project: the bitstream is linked into the ESP app and loaded over SPI at boot.

## Build and flash

```bash
cd boards/programming-carrier/firmware
python3 tools/gen_pinmap.py      # only after led-map.json or the module netlist changes
affogato test                    # SPI slave testbench
affogato build                   # yosys/nextpnr/icepack, then idf.py build
```

First flash: SW1=BOOT, press/release SW2 RESET, then flash over native USB.
The affogato CLI passes only `/dev/ttyACM0` into its container. Check the
port first (`lsusb | grep 303a`, `/dev/serial/by-id/usb-Espressif*`). Then
set SW1=RUN and press RESET. Keep SW3 (GPIO46) released during reset.

### Native build (macOS, no Docker)

This is how the first board was brought up on 2026-10-09 (log: `bringup-2026-10-09.log`).
It uses [oss-cad-suite](https://github.com/YosysHQ/oss-cad-suite-build) and ESP-IDF v5.3.2.

```bash
yosys -q -p "synth_ice40 -top top -json fpga/top.json" fpga/rtl/*.v
nextpnr-ice40 --up5k --package sg48 --json fpga/top.json --pcf fpga/project.pcf --asc fpga/top.asc
icepack fpga/top.asc fpga/top.bin
cd firmware && idf.py set-target esp32s2 && idf.py -p /dev/cu.usbmodem* flash
```

The design uses 364/5280 LCs and 34/39 I/O, and meets 48 MHz with 55.6 MHz max.
After flashing, set SW1 to RUN and press RESET. The app console then enumerates
as a new `usbmodem` port. Keep one terminal session open, or use
`tools/console.py PORT "fixture status"`, which leaves DTR/RTS deasserted.
Repeatedly opening the port with DTR/RTS asserted once made the console stop
responding. `esptool --before usb_reset --after hard_reset chip_id` recovers it
without touching the board.

## Operating

The console is USB CDC (`affogato monitor`, or any serial terminal). It boots
idle, with eligible outputs low and RGB sinks released. Nothing lights until
you arm the fixture:

```
fixture arm carrier-v1        # confirms this is the carrier, not an application board
fixture start                 # baseline, banks, walk fwd/rev, checkerboard, walking zero, RGB
fixture stop                  # works during any dwell; returns to safe idle
```

Arming is stored in NVS, so you only need to do it once per module; `fixture disarm`
clears it. Once armed, pressing **SW3** starts the full sequence when the fixture
is idle, and stops whatever is running. The sequence runs at 5× the
human-inspection dwell times (`SEQ_SPEEDUP` in `fixture.c`), about 21 s in total.
The walk dwell is 60 ms; for slower probing use `dwell 300` or `pause`/`step`.
D35 (GPIO45) and D36 (GPIO46) are not in the sequence. D36 lights while SW3 is held.

| Command | Effect |
|---|---|
| `status`, `banks` | Identity, hashes, FPGA link, readback summary; channel table |
| `bankseq`, `walk [fwd\|rev]`, `checkerboard`, `walkzero` | Single phases |
| `bank U7`, `hold FPGA_IOB_3B_G6` / `hold D44`, `rgb 0\|1\|2\|all` | Hold a pattern until `stop` |
| `pause`, `step`, `resume`, `repeat on\|off`, `dwell <ms>` | Probe a suspect joint |
| `allon [ms]` | Opt-in all-regular-on, ≤10 s; watch USB current and the LDO |
| `gpio45 [ms]` | Opt-in strap test, ≤3 s HIGH then LOW |
| `input46` | GPIO46/SW3 edges are always logged as `INPUT` lines |
| `wifi scan`, `wifi connect <ssid> [pass]`, `wifi off` | On-demand Wi-Fi check (off at boot); module v1 needs an antenna on U.FL J3 |
| `mark ok\|bad [note]` | Record an optical observation against the current step |

`f` is an alias for `fixture`. The log keeps three kinds of evidence separate:
- each step line records that the **command was applied**;
- `READBACK MISMATCH` lines report **pin readback** (ESP pad input, FPGA register);
- `OBSERVED` lines record what the operator saw (**optical**).

Only the last one proves a lamp works.

Never driven: EN (D10) and GPIO0/BOOT (D11) stay lit, and so do the D1/D2
power LEDs. GPIO46 is input-only. GPIO45 is driven only by `gpio45`. GPIO9–14,
36 and 37 (FPGA link) and 19/20 (USB) are not part of the sweep. If the FPGA
fails to load or identify, ESP-only tests still run.

## FPGA ABI v1

The 48 MHz HFOSC oversamples SPI mode 0 at 1 MHz from the ESP. Each frame is
40 bits, MSB first: `[cmd:8][data:32]`. During the frame, MISO returns `0xAF`
and then the 32-bit word selected by `cmd[3:0]` (its value before this frame).
`cmd[7]` = write. A frame is accepted only if exactly 40 bits were clocked.

| cmd[3:0] | Read | Write |
|---|---|---|
| 1 | ID `0x50435431` ("PCT1") | — |
| 2 | ABI `0x00010000` | — |
| 3 | 30-bit output mask | set mask |
| 4 | RGB sink enables [2:0] | set enables |
| 5 | `[31:16]` frame count, `[0]` watchdog tripped | clear trip flag |
| 6 | uptime, ms | — |

If no valid frame arrives for 1 s, the FPGA clears the mask and releases the
RGB sinks. The ESP sends a keepalive every 200 ms. RGB uses `SB_RGBA_DRV` in
half-current mode at 2 mA. "Off" releases the sink and never drives HIGH.

`fpga_out[n]` follows `docs/led-map.json` order (D42…D71). `fpga/project.pcf`
and `firmware/main/carrier_map.h` are generated from that map and the module v1
netlist by `tools/gen_pinmap.py`.
