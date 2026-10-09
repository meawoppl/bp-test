# Vendored ice40 component

Copied from https://github.com/meawoppl/affogato `components/ice40` at
fac90b963b3129069d10ca2db1702034210e4076 (MIT, see LICENSE), because the
affogato container only mounts the project directory.

Local changes in `fpga_loader.c`:

- The ≥1200 µs wait after CRESET_B release is a busy-wait; `vTaskDelay(pdMS_TO_TICKS(2))`
  could round to zero ticks at 100 Hz.
- A bitstream transfer error is no longer overwritten by the CDONE result, and
  CDONE is not waited for after a failed transfer.
