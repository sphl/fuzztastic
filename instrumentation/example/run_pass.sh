#!/usr/bin/env bash

# Compile the C code to LLVM bitcode
clang -g -O0 -fno-inline -emit-llvm -c ./math.c -o ./math.bc

# Run the fuzztastic pass on the bitcode to generate a instrumented LLVM IR
FT_PASS_OUTPUT_FILE=./math.json opt -load-pass-plugin=../build/libfuzztasticpass.so -passes="fuzztastic" ./math.bc -o ./math_ft.bc

# Compile the instrumented LLVM IR with the runtime library in order to create the final executable
clang ./math_ft.bc -L$(pwd)/../build/runtime-lib -Wl,-rpath,$(pwd)/../build/runtime-lib -lfuzztasticrt -o ./math
