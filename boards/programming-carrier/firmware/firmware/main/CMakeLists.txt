idf_component_register(
    SRCS "main.c" "fixture.c" "fpga_link.c"
    INCLUDE_DIRS "."
    REQUIRES ice40 console driver nvs_flash mbedtls app_update esp_app_format
)
