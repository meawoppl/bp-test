idf_component_register(
    SRCS "main.c" "fixture.c" "fpga_link.c" "wifi_test.c"
    INCLUDE_DIRS "."
    REQUIRES ice40 console driver nvs_flash esp_wifi esp_netif esp_event mbedtls app_update esp_app_format
)
