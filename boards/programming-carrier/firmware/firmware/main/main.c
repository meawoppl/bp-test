#include <stdio.h>
#include <esp_app_desc.h>
#include <esp_console.h>
#include <esp_log.h>
#include <nvs_flash.h>

#include "fixture.h"
#include "fpga_link.h"

static const char *TAG = "main";

void app_main(void)
{
    const esp_app_desc_t *app = esp_app_get_description();
    char elf_sha[17];
    esp_app_get_elf_sha256(elf_sha, sizeof(elf_sha));
    size_t bin_size;
    char bin_hash[17];
    fpga_link_bitstream_info(&bin_size, bin_hash);

    ESP_LOGI(TAG, "%s %s (app %s, elf %s, bitstream %u bytes sha256 %s…)", FIXTURE_IDENTITY,
             app->version, app->project_name, elf_sha, (unsigned)bin_size, bin_hash);

    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    ret = fpga_link_init();
    if (ret == ESP_OK) {
        ESP_LOGI(TAG, "FPGA fixture image loaded and identified");
    } else {
        ESP_LOGE(TAG, "FPGA unavailable (%s); FPGA/RGB channels disabled", esp_err_to_name(ret));
    }
    ESP_ERROR_CHECK(fixture_init(ret == ESP_OK));

    esp_console_repl_t *repl = NULL;
    esp_console_repl_config_t repl_config = ESP_CONSOLE_REPL_CONFIG_DEFAULT();
    repl_config.prompt = "carrier> ";
    esp_console_dev_usb_cdc_config_t cdc_config = ESP_CONSOLE_DEV_CDC_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_console_new_repl_usb_cdc(&cdc_config, &repl_config, &repl));
    esp_console_register_help_command();
    fixture_register_commands();

    printf("\n%s idle: eligible outputs low, RGB sinks released.\n"
           "Confirm the module is on programming carrier v1, then:\n"
           "  fixture arm " FIXTURE_ARM_TOKEN "   (once; persists)\n"
           "  fixture start      (or press SW3; SW3/`fixture stop` stops)\n"
           "  fixture            (all commands)\n\n",
           FIXTURE_IDENTITY);
    ESP_ERROR_CHECK(esp_console_start_repl(repl));
}
