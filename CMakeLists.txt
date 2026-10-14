cmake_minimum_required(VERSION 3.16)

# Set the SDK path
set(ENV{IDF_PATH} "C:/Espressif/frameworks/esp-idf-v5.5.4")

# Official Python path
set(PYTHON "C:/Espressif/python_env/idf5.5_py3.11_env/Scripts/python.exe" CACHE FILEPATH "" FORCE)

# Force the language standards matching the compiler
set(CMAKE_C_STANDARD 11 CACHE INTERNAL "" FORCE)
set(CMAKE_CXX_STANDARD 17 CACHE INTERNAL "" FORCE)

# Magic commands to bypass the toolchain version blocking
set(ENV{IDF_MAINTAINER} "1")
set(CONFIG_IDF_TARGET_TOOLCHAIN_PREFIX "xtensa-esp32s3-elf-" CACHE INTERNAL "" FORCE)
add_compile_definitions(IDF_MAINTAINER=1)

# Explicit instruction to CMake to take only the essential core components (this removes esp_lcd from the build!)
set(COMPONENTS main freertos log esp_hw_support heap soc esp_rom esp_system newlib pthread esp_common driver spi_flash nvs_flash esp_timer)

include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(esp32s3_fft)

# Force long jumps in memory (mlongcalls) to fix the linker error
set(CMAKE_CXX_FLAGS "-std=gnu++17 -mlongcalls" CACHE STRING "" FORCE)
set(CMAKE_C_FLAGS "-std=gnu11 -mlongcalls" CACHE STRING "" FORCE)
