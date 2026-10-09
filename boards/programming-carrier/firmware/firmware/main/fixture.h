#pragma once

#include <stdbool.h>
#include <esp_err.h>

#define FIXTURE_IDENTITY "programming-carrier-v1-test"
#define FIXTURE_ARM_TOKEN "carrier-v1"

// Put every eligible output in its safe state and start the scheduler task.
// fpga_ok selects whether FPGA/RGB channels may be used.
esp_err_t fixture_init(bool fpga_ok);

// Register the `fixture` console command.
void fixture_register_commands(void);
