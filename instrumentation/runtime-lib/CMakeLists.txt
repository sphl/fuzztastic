set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall")

set(CMAKE_SHARED_LIBRARY_SUFFIX ".so")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fPIC")

add_library(fuzztasticrt SHARED fuzztastic_rt.c)

target_compile_options(fuzztasticrt PRIVATE -O2 -fno-omit-frame-pointer)

set_target_properties(fuzztasticrt PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
)

install(TARGETS fuzztasticrt
    LIBRARY DESTINATION lib
)
