cmake_minimum_required(VERSION 3.16)

# components/ice40 is vendored from affogato (see components/ice40/VENDORED.md).
set(PROJECT_VER "1.0.0")
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(programming-carrier-v1-test)

# Embed the FPGA bitstream into the firmware
target_add_binary_data(${CMAKE_PROJECT_NAME}.elf "../fpga/top.bin" BINARY)
