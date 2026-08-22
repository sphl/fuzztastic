set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

set(CMAKE_SHARED_LIBRARY_SUFFIX ".so")

add_library(fuzztasticrt SHARED fuzztastic_rt.c)

target_compile_options(fuzztasticrt PRIVATE
    -Wall
    -fPIC
    -fno-omit-frame-pointer
    $<$<CONFIG:Debug>:-g -O0>
    $<$<CONFIG:Release>:-O2>
)

set_target_properties(fuzztasticrt PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
)

install(TARGETS fuzztasticrt
    LIBRARY DESTINATION lib
)
