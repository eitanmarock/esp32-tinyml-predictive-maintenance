# סריקה אוטומטית של כל קבצי הבינה המלאכותית
file(GLOB_RECURSE edge_impulse_sources
        "edge_ai_model/*.cpp"
        "edge_ai_model/*.c"
        "edge_ai_model/*.cc"
)

# רישום הרכיבים לקומפיילר (שימו לב שעכשיו כתוב main.cpp)
idf_component_register(
        SRCS "main.cpp" ${edge_impulse_sources}
        INCLUDE_DIRS "."
        "edge_ai_model"
        "edge_ai_model/edge-impulse-sdk"
        "edge_ai_model/model-parameters"
        "edge_ai_model/tflite-model"
)

# אופטימיזציה למהירות מקסימלית של המעבד
# אופטימיזציה למהירות מקסימלית + ביטול אזהרות קשוחות של הקומפיילר
target_compile_options(${COMPONENT_LIB} PRIVATE
        "-O3"
        "-Wno-error"
        "-Wno-uninitialized"
        "-Wno-maybe-uninitialized"
        "-Wno-missing-field-initializers"
)