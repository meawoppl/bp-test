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

## Operating

The console is USB CDC (`affogato monitor`, or any serial terminal). It boots
idle, with eligible outputs low and RGB sinks released. Nothing lights until
you arm the fixture:

```
fixture arm carrier-v1        # confirms this is the carrier, not an application board
fixture start                 # baseline, banks, walk fwd/rev, checkerboard, walking zero, RGB
fixture stop                  # works during any dwell; returns to safe idle
```

| Command | Effect |
|---|---|
| `status`, `banks` | Identity, hashes, FPGA link, readback summary; channel table |
| `bankseq`, `walk [fwd\|rev]`, `checkerboard`, `walkzero` | Single phases |
| `bank U7`, `hold FPGA_IOB_3B_G6` / `hold D44`, `rgb 0\|1\|2\|all` | Hold a pattern until `stop` |
| `pause`, `step`, `resume`, `repeat on\|off`, `dwell <ms>` | Probe a suspect joint |
| `allon [ms]` | Opt-in all-regular-on, ≤10 s; watch USB current and the LDO |
| `gpio45 [ms]` | Opt-in strap test, ≤3 s HIGH then LOW |
| `input46` | GPIO46/SW3 edges are always logged as `INPUT` lines |
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
