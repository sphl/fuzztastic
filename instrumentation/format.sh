#!/usr/bin/env bash

find . -path "./build" -prune -o -type f \( -name "*.cpp" -o -name "*.h" -o -name "*.c" -o -name "*.hpp" \) -exec clang-format -i {} \;
