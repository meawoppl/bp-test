#include "fpga_link.h"

#include <stdio.h>
#include <string.h>
#include <esp_attr.h>
#include <driver/gpio.h>
#include <driver/spi_master.h>
#include <esp_log.h>
#include <mbedtls/sha256.h>

#include "ice40.h"

static const char *TAG = "fpga_link";

extern const uint8_t _binary_top_bin_start[];
extern const uint8_t _binary_top_bin_end[];

static const fpga_bin_t fpga_image = {
    .start = _binary_top_bin_start,
    .end = _binary_top_bin_end,
};

static spi_device_handle_t link_device = NULL;
static WORD_ALIGNED_ATTR uint8_t tx_buf[8];
static WORD_ALIGNED_ATTR uint8_t rx_buf[8];

bool fpga_link_ready(void)
{
    return link_device != NULL;
}

esp_err_t fpga_link_xfer(uint8_t cmd, uint32_t data, uint32_t *readback)
{
    if (link_device == NULL) {
        return ESP_ERR_INVALID_STATE;
    }

    xSemaphoreTake(master_spi_semaphore, portMAX_DELAY);
    tx_buf[0] = cmd;
    tx_buf[1] = data >> 24;
    tx_buf[2] = data >> 16;
    tx_buf[3] = data >> 8;
    tx_buf[4] = data;
    memset(rx_buf, 0, sizeof(rx_buf));

    spi_transaction_t trans = {
        .length = 40,
        .tx_buffer = tx_buf,
        .rx_buffer = rx_buf,
    };
    esp_err_t ret = spi_device_transmit(link_device, &trans);
    uint8_t preamble = rx_buf[0];
    uint32_t word = ((uint32_t)rx_buf[1] << 24) | ((uint32_t)rx_buf[2] << 16) |
                    ((uint32_t)rx_buf[3] << 8) | rx_buf[4];
    xSemaphoreGive(master_spi_semaphore);

    if (ret != ESP_OK) {
        return ret;
    }
    if (preamble != 0xAF) {
        ESP_LOGE(TAG, "bad SPI preamble 0x%02x (cmd 0x%02x)", preamble, cmd);
        return ESP_ERR_INVALID_RESPONSE;
    }
    if (readback) {
        *readback = word;
    }
    return ESP_OK;
}

esp_err_t fpga_link_apply(uint32_t mask, uint8_t rgb, bool *match)
{
    uint32_t mask_rb = 0, rgb_rb = 0;
    esp_err_t ret = fpga_link_xfer(FPGA_CMD_WRITE | FPGA_CMD_MASK, mask, NULL);
    if (ret == ESP_OK) ret = fpga_link_xfer(FPGA_CMD_WRITE | FPGA_CMD_RGB, rgb, NULL);
    if (ret == ESP_OK) ret = fpga_link_xfer(FPGA_CMD_MASK, 0, &mask_rb);
    if (ret == ESP_OK) ret = fpga_link_xfer(FPGA_CMD_RGB, 0, &rgb_rb);
    *match = (ret == ESP_OK) && mask_rb == mask && rgb_rb == rgb;
    return ret;
}

esp_err_t fpga_link_status(uint32_t *status, uint32_t *uptime_ms)
{
    esp_err_t ret = fpga_link_xfer(FPGA_CMD_STATUS, 0, status);
    if (ret == ESP_OK && uptime_ms) {
        ret = fpga_link_xfer(FPGA_CMD_UPTIME, 0, uptime_ms);
    }
    return ret;
}

void fpga_link_bitstream_info(size_t *size, char hash_hex[17])
{
    uint8_t digest[32];
    *size = fpga_image.end - fpga_image.start;
    mbedtls_sha256(fpga_image.start, *size, digest, 0);
    for (int i = 0; i < 8; i++) {
        sprintf(&hash_hex[i * 2], "%02x", digest[i]);
    }
}

esp_err_t fpga_link_init(void)
{
    esp_err_t ret = master_spi_init();
    if (ret != ESP_OK) {
        return ret;
    }
    ret = fpga_loader_init();
    if (ret != ESP_OK) {
        return ret;
    }

    ret = fpga_loader_load_from_rom(&fpga_image);
    int cdone = gpio_get_level(CONFIG_FPGA_CDONE_GPIO);
    ESP_LOGI(TAG, "loader: %s, CDONE=%d", esp_err_to_name(ret), cdone);
    if (ret != ESP_OK || !cdone) {
        // Hold the FPGA in reset so its pins stay high-impedance.
        gpio_set_level(CONFIG_FPGA_CRESET_GPIO, 0);
        return ret != ESP_OK ? ret : ESP_FAIL;
    }

    spi_device_interface_config_t devcfg = {
        .clock_speed_hz = CONFIG_FPGA_SPI_FREQ_COMMS * 1000000,
        .mode = 0,
        .spics_io_num = CONFIG_FPGA_CS_GPIO,
        .queue_size = 1,
    };
    ret = spi_bus_add_device(FSPI_HOST, &devcfg, &link_device);
    if (ret != ESP_OK) {
        return ret;
    }

    uint32_t id = 0, version = 0;
    ret = fpga_link_xfer(FPGA_CMD_ID, 0, &id);
    if (ret == ESP_OK) ret = fpga_link_xfer(FPGA_CMD_VERSION, 0, &version);
    ESP_LOGI(TAG, "runtime id=0x%08lx abi=0x%08lx", (unsigned long)id, (unsigned long)version);
    if (ret != ESP_OK || id != FPGA_FIXTURE_ID || version != FPGA_ABI_VERSION) {
        ESP_LOGE(TAG, "FPGA identity check failed (expected id 0x%08x abi 0x%08x)",
                 FPGA_FIXTURE_ID, FPGA_ABI_VERSION);
        spi_bus_remove_device(link_device);
        link_device = NULL;
        gpio_set_level(CONFIG_FPGA_CRESET_GPIO, 0);
        return ret != ESP_OK ? ret : ESP_ERR_INVALID_VERSION;
    }

    bool match = false;
    ret = fpga_link_apply(0, 0, &match);
    if (ret == ESP_OK && !match) {
        ret = ESP_ERR_INVALID_RESPONSE;
    }
    return ret;
}
