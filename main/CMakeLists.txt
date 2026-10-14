# Automatically scan all AI model files
file(GLOB_RECURSE edge_impulse_sources
        "edge_ai_model/*.cpp"
        "edge_ai_model/*.c"
        "edge_ai_model/*.cc"
)

# Register the components with the compiler (note that it now says main.cpp)
idf_component_register(
        SRCS "main.cpp" ${edge_impulse_sources}
        INCLUDE_DIRS "."
        "edge_ai_model"
        "edge_ai_model/edge-impulse-sdk"
        "edge_ai_model/model-parameters"
        "edge_ai_model/tflite-model"
)

# Optimization for maximum CPU speed
# Optimization for maximum speed + disabling strict compiler warnings
target_compile_options(${COMPONENT_LIB} PRIVATE
        "-O3"
        "-Wno-error"
        "-Wno-uninitialized"
        "-Wno-maybe-uninitialized"
        "-Wno-missing-field-initializers"
)
