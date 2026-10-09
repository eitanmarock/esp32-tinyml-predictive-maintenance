cmake_minimum_required(VERSION 3.16)

# הגדרת נתיב ה-SDK
set(ENV{IDF_PATH} "C:/Espressif/frameworks/esp-idf-v5.5.4")

# נתיב הפייתון הרשמי
set(PYTHON "C:/Espressif/python_env/idf5.5_py3.11_env/Scripts/python.exe" CACHE FILEPATH "" FORCE)

# אילוץ מוחלט של תקן השפה המתאים לקומפיילר
set(CMAKE_C_STANDARD 11 CACHE INTERNAL "" FORCE)
set(CMAKE_CXX_STANDARD 17 CACHE INTERNAL "" FORCE)

# פקודות הקסם לביטול חסימת הגרסאות של הכלים
set(ENV{IDF_MAINTAINER} "1")
set(CONFIG_IDF_TARGET_TOOLCHAIN_PREFIX "xtensa-esp32s3-elf-" CACHE INTERNAL "" FORCE)
add_compile_definitions(IDF_MAINTAINER=1)

# הוראה מפורשת ל-CMake לקחת רק את רכיבי הליבה ההכרחיים (זה יוריד את ה-esp_lcd מהבנייה!)
set(COMPONENTS main freertos log esp_hw_support heap soc esp_rom esp_system newlib pthread esp_common driver spi_flash nvs_flash esp_timer)

include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(esp32s3_fft)

# כפיית קפיצות ארוכות בזיכרון (mlongcalls) כדי לפתור את שגיאת הלינקר
set(CMAKE_CXX_FLAGS "-std=gnu++17 -mlongcalls" CACHE STRING "" FORCE)
set(CMAKE_C_FLAGS "-std=gnu11 -mlongcalls" CACHE STRING "" FORCE)