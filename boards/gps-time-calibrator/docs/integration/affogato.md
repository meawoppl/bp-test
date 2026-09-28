# Affogato integration, flash and runtime link

Inspected [meawoppl/affogato](https://github.com/meawoppl/affogato) at
[`530849ef2530967e09bf593597e0dd1b97ef824d`](https://github.com/meawoppl/affogato/tree/530849ef2530967e09bf593597e0dd1b97ef824d),
and the predecessor [gps-time-calibrator](https://github.com/Exclosure/gps-time-calibrator)
local checkout at `6354c0c9489a353109c27ee37584bb7b6f79b064`.
These observations describe those source revisions, not a hardware-tested release.

## What is present and what still needs implementing

| Feature | Inspected implementation | Calibrator integration work |
|---|---|---|
| FPGA build | Yosys → nextpnr-ice40 → icepack, UP5K/SG48 | New top-level ports/PCF, 10MHz clock constraints and timing closure |
| ESP build/USB flash | Docker ESP-IDF, `build`, `flash -p`, `monitor -p` | Carrier firmware/services and recovery testing |
| FPGA image storage | `top.bin` linked into ESP application | Keep app and FPGA ABI versioned as a pair |
| FPGA programming | `ice40` component loads from embedded image or VFS file | SRAM configuration every boot; verify CDONE plus runtime ABI |
| SPI runtime | Bulk-status and register RTL modules | Choose/fix/test one protocol; add event FIFO and coherent CDC |
| ESP OTA partitions | **No custom dual-OTA table in Affogato template** | Add partition CSV + ESP-IDF OTA/rollback implementation |
| OTA service | Not supplied by the basic template | Implement authenticated update transport, acceptance and rollback |
| New project app | `cli/src/project.rs` emits a loader TODO | Wire in component, loader, drivers, state machine and safe outputs |
| Calibrator timing | Not provided by Affogato | GNSS parsing, PPS discipline, trigger timestamps, optical encoding |

The `flash` command programs the **ESP flash** using `idf.py`; FPGA loading then
configures its volatile SRAM from the embedded image. There is no separate FPGA
configuration-flash IC on module v1, and no persistent standalone FPGA flash bank
to update. `fpga_loader_load_from_file()` needs an explicitly mounted filesystem;
it does not itself add storage or an updater.

## Development setup and actual CLI commands

The following are actual Affogato command names. Run them in a firmware project,
not in this PCB repository's root. Do not run `affogato init` over the existing
predecessor project: it rejects existing firmware/fpga directories.

```bash
# Install from the separately cloned Affogato checkout; Docker must be available.
cargo install --path ../affogato/cli

# New application workspace, if not continuing the old firmware repo:
affogato new gps-calibrator-rfc
cd gps-calibrator-rfc

# AFTER adapting the project as described below:
affogato fpga
affogato test
affogato lint
affogato build
affogato flash -p /dev/ttyACM0
affogato monitor -p /dev/ttyACM0
```

`affogato run -p /dev/ttyACM0` flashes and monitors; it is not a substitute for
`build`. Serial port is an example; verify the actual device. The USB carrier
has no BOOT/RUN or RESET switch, so provision and validate USB/OTA recovery on
the programmer first. TP65 can expose GPIO0, but J1.11/ESP_EN is not connected
on the carrier. Do not design the updater around an automatic hardware boot override.

Pin the Affogato git revision and Docker **image digest**, rather than relying on
`latest`. Use the CLI global `--image` option or `AFFOGATO_IMAGE`. Record Yosys,
nextpnr and ESP-IDF versions with each firmware build.

Vendor the inspected `components/ice40/` into `firmware/components/ice40/` (include
its license) or provide a pinned component path **inside the Docker mount**.
The generated CLI project does not automatically include it. Add `ice40` to
`idf_component_register(REQUIRES ...)` for the application. Actual CLI generation
embeds `../fpga/top.bin`; use that path relative to `firmware/`, rather than the
older static template's `firmware/fpga/top.bin` path. Check the resulting linker
symbols match `_binary_top_bin_start` / `_binary_top_bin_end`.

Apply these to `firmware/sdkconfig.defaults` and check the generated sdkconfig:

```ini
CONFIG_IDF_TARGET="esp32s2"
CONFIG_ESP_CONSOLE_USB_CDC=y
CONFIG_ESPTOOLPY_FLASHSIZE_4MB=y
CONFIG_PARTITION_TABLE_CUSTOM=y
CONFIG_PARTITION_TABLE_CUSTOM_FILENAME="partitions_4mb.csv"
CONFIG_BOOTLOADER_APP_ROLLBACK_ENABLE=y
CONFIG_FPGA_CS_GPIO=10
CONFIG_FPGA_SCLK_GPIO=12
CONFIG_FPGA_MOSI_GPIO=11
CONFIG_FPGA_MISO_GPIO=13
CONFIG_FPGA_WP_GPIO=-1
CONFIG_FPGA_HD_GPIO=-1
CONFIG_FPGA_CRESET_GPIO=36
CONFIG_FPGA_CDONE_GPIO=37
CONFIG_FPGA_SPI_FREQ_PROGRAMMING=10
CONFIG_FPGA_SPI_FREQ_COMMS=1
```

Programming10MHz and runtime1MHz are conservative bring-up choices, not hardware
maxima. The comms Kconfig setting must actually be consumed by the application's
runtime SPI device; setting it alone does not create that device. Remove UART
console/log routing from GPIO43/44. Disabling application UART logs does not prove
ROM never drives TX43 while GPS is off; scope cold boot and reset before accepting
power-domain isolation.

## Proposed partition layout and update ownership

Module U1 is **ESP32-S2FH4 (4MB embedded flash)**. Verify detected flash size on
the physical modules before installing a partition table. The old calibrator's
`partitions_two_ota.csv` is explicitly a **2MB** layout with 960KiB application
slots; it is a starting reference, not this module's required capacity.

[partitions_4mb.csv](partitions_4mb.csv) proposes:

| Partition | Offset | Size | Purpose |
|---|---|---|---|
| nvs | 0x9000 | 0x4000 | Settings, small calibration records |
| otadata | 0xD000 | 0x2000 | ESP-IDF OTA selection/state |
| phy_init | 0xF000 | 0x1000 | PHY init reservation |
| ota_0 | 0x10000 | 0x1E0000 | App + embedded matching FPGA image |
| ota_1 | 0x1F0000 | 0x1E0000 | App + embedded matching FPGA image |
| Unallocated | 0x3D0000 | 0x30000 | Reserve, not an existing filesystem |

This table is a **proposal**, not flashed or enabled by this documentation.
Validate with ESP-IDF's partition generator and image-size check. Do not move
partitions over an installed product as though this were an ordinary OTA image.
There is no factory application in this example. Keep bulk trigger logs in RAM
and stream them over USB/Wi-Fi; do not erase/write NVS per trigger.

Recommended update unit: **one app image containing its FPGA bitstream**.
On OTA: disarm/blank, switch loads off, receive/verify inactive-slot image,
select it, reboot, configure its bundled FPGA, verify IDs/ABI/self-tests, then
call `esp_ota_mark_app_valid_cancel_rollback()`. Use the ESP-IDF OTA APIs and
rollback state machine; no `affogato ota` command exists at the inspected revision.
Do not require satellite lock to confirm basic boot health (indoors is legitimate),
but do require loader/comms and safe-power behavior. Keep measurements invalid
until timing reacquires. An FPGA bitstream loaded independently from a VFS file
requires its own A/B/hash/ABI/rollback policy; avoid that complexity initially.

See [Espressif OTA documentation](https://docs.espressif.com/projects/esp-idf/en/v5.3.4/esp32s2/api-reference/system/ota.html)
and [ESP32-S2 family/flash variants](https://documentation.espressif.com/esp32-s2_datasheet_en.html).

## Loader sequence and source-review issues to resolve

Application sequence:

1. All switched-load enables low; set safe GPIOs as specified in the main guide.
2. `fpga_loader_init()` asserts CRESET_N; `master_spi_init()` creates the FSPI bus.
3. `fpga_loader_load_from_rom(&image)` configures FPGA; check its return value.
4. Create a **runtime** SPI device with the chosen mode/rate; perform ID, ABI,
   known-pattern and safe-output readbacks before enabling external loads.
5. Serialize runtime access, suspend all transactions for reconfiguration, remove
   the runtime device as necessary, then reload. Hold an application-level lock
   across the entire process, not merely individual SPI chunks.

The existing loader is useful but needs review before production:

- `vTaskDelay(pdMS_TO_TICKS(2))` can become zero at a coarse FreeRTOS tick rate;
  it must satisfy Lattice's ≥1200µs initialization wait with a guaranteed delay.
- A transfer-loop error is subsequently overwritten by the CDONE wait result;
  post-configuration dummy-clock writes also ignore errors. Preserve the first
  failure and fail closed; CDONE alone must not hide a failed stream.
- Manual CS/reset and SPI-device cleanup must restore known safe states on every
  failure. Use timeouts for CDONE-low and CDONE-high, validate source length/hash,
  and only release loads after a matching runtime handshake.
- Do not infer power-on reset state from Affogato's prose saying CRESET is low
  “or floating.” The module uses its own pull circuitry; software asserts reset.

## Clocking and pin constraints

[calibrator.pcf](calibrator.pcf) maps this carrier, including optical columns,
OCXO44/G6, PPS35/G0, input38, output42 and /OE34. These port names are the proposed
new top-level interface. They must match the HDL; the PCF alone is not an application.
Use `SB_GB_IO` or a verified equivalent to put the OCXO pad on the global network.
Constrain external clock to **10MHz /100ns** and the separate HFOSC control domain
at its actual chosen rate. Add proper asynchronous input and CDC constraints.

Affogato's TOML build path currently supplies no clock-frequency/pre-pack options.
Add a reviewed pre-pack timing script/build extension or use a project-specific
Makefile; do not invent a TOML `frequency` key that the CLI silently ignores.
Inspect the nextpnr report for global routing, clock rates and timing closure.
If using a Makefile, note that the CLI chooses it only when no TOML config exists.

Keep an internal-clock domain alive for SPI control, heartbeat, OCXO-edge watchdog,
and fail-safe /OE/output control. Transfer captures over an asynchronous FIFO
or explicit request/acknowledge snapshot handshake. Do not two-flop-synchronize
individual bits of a free-running multi-bit timestamp and call that coherent.

## Runtime SPI: proposed application ABI, not an existing driver

Affogato offers two **incompatible** building blocks: bulk status (mode0) and
register access (documented mode3). The predecessor ESP driver currently reads
10 bulk bytes despite its `SPI_REGISTERS.md` describing an address protocol.
Choose one and implement host/HDL tests together; do not mix their framing.

For this application, propose a versioned register/FIFO ABI based on the register
framing: `[command8][address16][dummy8][data16...]`, MSB first, word addresses.
Read register=0x02, write register=0x03, memory read/write=0x00/0x01. Hold CS low
for the complete transaction. Start at1MHz. These opcodes are Affogato's stated
contract, **not proof that its RTL implements them correctly**.

Audit the RTL first: `spi_slave_reg.v` samples MOSI on rising SCK and changes MISO
on falling SCK; verify first-bit, dummy-cycle and CS setup behavior in mode3 with waveforms.
Its single-register commands are not separately bounded, bus CDC is not a complete
coherency handshake, and multi-bit reads can tear. The bulk implementation also
needs first-bit/CDC verification. Pass a self-checking simulation and logic-analyzer
round trip before selecting the runtime `spi_device_interface_config_t.mode`.
Configuration loading retains its separate mode3 device per the loader.

Suggested **new** register allocation (implement both endpoints):

| Word address | Access | Proposed meaning |
|---|---|---|
| 0x0000–0001 | R | Magic=0x43414C31 (CAL1) |
| 0x0002 | R | ABI version=1 |
| 0x0003 | R | Flags: clock/PPS/time valid, FIFO overflow, watchdog fault |
| 0x0004 | W | Control: blank, arm input, arm output; reset is safe/blank |
| 0x0005 | R | Event FIFO count |
| 0x0006 | R | Lost-event count (saturating; clear only explicit command) |
| 0x0010–0013 | R | Latched 64-bit tick counter, high word first |
| 0x0014–0015 | R | Last measured ticks/PPS interval |
| 0x0016–0017 | R | PPS sequence number |
| 0x0020 | W | Manual16-bit display pattern (test mode only) |
| 0x0021 | W | Display mode (blank/test/time) |
| 0x0030–0037 | R | Latched FIFO head: seq32, ticks64, PPSseq32 |
| 0x0038 | R | Event type/edge/validity flags |
| 0x0039 | W | ACK/pop the latched event only after complete receipt |
| 0x0040–0043 | W | Output target absolute tick64 |
| 0x0044–0045 | W | Output pulse width32 |
| 0x0046 | W | Atomic commit of scheduled output; reject if late/disarmed |

Specify atomic snapshot/latch behavior before coding: ID/status reads have no
FIFO side effects, a record stays frozen until acknowledged, and multiword
writes take effect only on COMMIT. Add a host heartbeat with a tested timeout
(e.g.500ms initially) that blanks LEDs/disarms output on loss. This table is a
starting interface contract; bump ABI whenever its semantics change.

## Migration checklist from the old application

- Keep the UART transport/parser idea, but replace its9600 default with detected
  M10S settings, ACK/readback configuration and proper TIM-TM2 flags.
- Remove automatic1kHz PPS transition. Keep1Hz for initial absolute-second
  association, TIM-TP and10MHz frequency estimation.
- Replace48MHz HFOSC timekeeping and `counter/732` optical scaling. At10MHz that
  divisor is wrong; even at48MHz it is only approximate.
- Add real resets, clock-presence detection, event FIFO, timestamp coherency,
  receiver/time validity, power-state services, OLED driver and OTA rollback.
- Do not rely on the old NTP/HTTP infrastructure for microsecond capture latency.
  Preserve raw measurements; NTP is an auxiliary network service if retained.
