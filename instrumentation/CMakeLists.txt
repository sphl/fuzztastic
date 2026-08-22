cmake_minimum_required(VERSION 3.13.4)
project(fuzztasticpass VERSION 2.0.0 LANGUAGES C CXX)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE "Debug" CACHE STRING "Build type (Debug or Release)" FORCE)
endif()
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")

find_package(LLVM REQUIRED CONFIG)

include_directories(${LLVM_INCLUDE_DIRS})
separate_arguments(LLVM_DEFINITIONS_LIST NATIVE_COMMAND ${LLVM_DEFINITIONS})
add_definitions(${LLVM_DEFINITIONS_LIST})

set(CMAKE_SHARED_LIBRARY_SUFFIX ".so")

add_library(fuzztasticpass SHARED fuzztastic_pass.cpp bb_info.cpp utils/formatter.cpp utils/io.cpp)

target_include_directories(fuzztasticpass PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}/include")
target_link_libraries(fuzztasticpass PRIVATE ${LLVM_LIBRARIES})

target_compile_options(fuzztasticpass PRIVATE
    -Wall
    -fPIC
    # LLVM is normally built without RTTI; match that to avoid ABI issues
    $<$<BOOL:${LLVM_ENABLE_RTTI}>:>$<$<NOT:$<BOOL:${LLVM_ENABLE_RTTI}>>:-fno-rtti>
    $<$<CONFIG:Debug>:-g -O0>
    $<$<CONFIG:Release>:-O2>
)

set_target_properties(fuzztasticpass PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
)

install(TARGETS fuzztasticpass
    LIBRARY DESTINATION lib
)

add_subdirectory(runtime-lib)
