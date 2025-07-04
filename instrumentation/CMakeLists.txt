cmake_minimum_required(VERSION 3.13.4)
project(fuzztasticpass VERSION 1.2.0 LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(LLVM REQUIRED CONFIG)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra")

# LLVM is normally built with no C++ RTTI. We need to match that.
if(NOT LLVM_ENABLE_RTTI)
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fno-rtti")
endif()

include_directories(${LLVM_INCLUDE_DIRS})
separate_arguments(LLVM_DEFINITIONS_LIST NATIVE_COMMAND ${LLVM_DEFINITIONS})
add_definitions(${LLVM_DEFINITIONS_LIST})

if(APPLE)
    set(CMAKE_SHARED_LIBRARY_SUFFIX ".dylib")
    set(CMAKE_SHARED_LIBRARY_CREATE_CXX_FLAGS "${CMAKE_SHARED_LIBRARY_CREATE_CXX_FLAGS} -undefined dynamic_lookup")
elseif(UNIX AND NOT APPLE)
    set(CMAKE_SHARED_LIBRARY_SUFFIX ".so")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fPIC")
endif()

add_library(fuzztasticpass SHARED fuzztastic_pass.cpp bb_info.cpp utils/formatter.cpp utils/io.cpp)

llvm_map_components_to_libnames(llvm_libs support core irreader)
target_include_directories(fuzztasticpass PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}/include")
target_link_libraries(fuzztasticpass ${llvm_libs})

set_target_properties(fuzztasticpass PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
)

install(TARGETS fuzztasticpass
    LIBRARY DESTINATION lib
)

add_subdirectory(runtime-lib)
