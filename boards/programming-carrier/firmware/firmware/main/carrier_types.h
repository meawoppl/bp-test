#pragma once

#include <stdbool.h>
#include <stdint.h>

typedef enum {
    KIND_ESP,
    KIND_FPGA,
    KIND_RGB,
} channel_kind_t;

typedef enum {
    CH_OUTPUT,   // ordinary push-pull test output
    CH_OBSERVE,  // EN / GPIO0: never driven, indicator observed only
    CH_OPT_IN,   // GPIO45 strap: only via the explicit gpio45 command
    CH_INPUT,    // GPIO46: input only
    CH_RGB,      // FPGA RGB current sink (SB_RGBA_DRV)
} channel_class_t;

typedef struct {
    const char *signal;
    const char *led;
    const char *buffer;
    channel_kind_t kind;
    channel_class_t cls;
    int index;  // ESP: GPIO number; FPGA: fpga_out bit; RGB: sink number
    const char *conn;
    int conn_pin;
    int pkg_pin;
    bool active_low;
} carrier_channel_t;
