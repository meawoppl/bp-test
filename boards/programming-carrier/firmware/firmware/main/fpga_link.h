#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <esp_err.h>

// FPGA fixture ABI v1 (see fpga/rtl/top.v). Command bit 7 = write.
#define FPGA_CMD_ID 0x01
#define FPGA_CMD_VERSION 0x02
#define FPGA_CMD_MASK 0x03
#define FPGA_CMD_RGB 0x04
#define FPGA_CMD_STATUS 0x05
#define FPGA_CMD_UPTIME 0x06
#define FPGA_CMD_WRITE 0x80

#define FPGA_FIXTURE_ID 0x50435431u  // "PCT1"
#define FPGA_ABI_VERSION 0x00010000u

// Load the embedded bitstream, check CDONE, attach the runtime SPI device and
// verify the fixture identity/ABI. Leaves outputs low and RGB released.
esp_err_t fpga_link_init(void);

bool fpga_link_ready(void);

// One 40-bit frame. *readback receives the word selected by cmd's low nibble
// as it was before this frame was applied.
esp_err_t fpga_link_xfer(uint8_t cmd, uint32_t data, uint32_t *readback);

// Write mask and RGB, then read both back. *match is false on any mismatch.
esp_err_t fpga_link_apply(uint32_t mask, uint8_t rgb, bool *match);

// Read status word: [31:16] frame count, [0] watchdog tripped.
esp_err_t fpga_link_status(uint32_t *status, uint32_t *uptime_ms);

// SHA-256 prefix of the embedded bitstream, for the test report.
void fpga_link_bitstream_info(size_t *size, char hash_hex[17]);
