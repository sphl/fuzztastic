#!/usr/bin/env bash

set -e

function run_wdir_cmd() {
    local wdir="$1"
    shift

    (cd "$wdir" && "$@")
}

function fetch_fuzzer() {
    local wdir="$1"

    git clone "https://github.com/AFLplusplus/AFLplusplus.git" "$wdir/aflpp"
    run_wdir_cmd "$wdir/aflpp" git checkout "v4.33c"
}

function build_fuzzer() {
    local wdir="$1"

    run_wdir_cmd "$wdir/aflpp" make -j
}

function setup_fuzzer() {
    local wdir="$1"

    if [ ! -d "$wdir/aflpp" ]; then
        fetch_fuzzer "$wdir"
        build_fuzzer "$wdir"
    fi
}

function fetch_target() {
    local wdir="$1"

    git clone "https://github.com/Orc/discount.git" "$wdir/discount"
    run_wdir_cmd "$wdir/discount" git checkout "v3.0.0d"
}

function build_target() {
    local wdir="$1"

    # Extract the LLVM bitcode file from the target program (mkd2html)
    run_wdir_cmd "$wdir/discount" sh -c '
        make distclean || true
        CC=gclang CFLAGS="-g -O0 -fno-inline" ./configure.sh
        make -j
        get-bc ./mkd2html
    '

    # Apply the FuzzTastic code coverage instrumentation
    run_wdir_cmd /fuzztastic poetry run fuzztastic instrument --input-bc "$wdir/discount/mkd2html.bc" --output-bc "$wdir/discount/mkd2html.ft.bc" --output "$wdir/mkd2html.json"

    # Compile mkd2html into a fuzzable binary using the AFL++ C compiler wrapper
    AFL_USE_ASAN=1 $wdir/aflpp/afl-clang-fast -O0 -fno-inline "$wdir/discount/mkd2html.ft.bc" -lfuzztasticrt -o "$wdir/fuzz_mkd2html"
}

function setup_target() {
    local wdir="$1"

    if [ ! -d "$wdir/discount" ]; then
        fetch_target "$wdir"
    fi
    build_target "$wdir"
}

WDIR="${WDIR:-$PWD}"

setup_fuzzer "$WDIR"
setup_target "$WDIR"
