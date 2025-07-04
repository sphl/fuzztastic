#!/usr/bin/env bash

# Compile the C code to LLVM bitcode
clang -g -O0 -fno-inline -emit-llvm -c ./math.c -o ./math.bc

# Run the fuzztastic pass on the bitcode to generate a coverage-instrumented LLVM IR
opt -load-pass-plugin=../build/libfuzztasticpass.dylib -passes="fuzztastic" -output-file=./output.json ./math.bc -S -o ./math.ll

# Convert the instrumented LLVM IR to assembly (to avoid LLVM version compatibility issues)
llc ./math.ll -o ./math.s

# Compile the assembly with the runtime library to create the final executable
clang ./math.s -L$(pwd)/../build/runtime-lib -Wl,-rpath,$(pwd)/../build/runtime-lib -lfuzztasticrt -o ./math
