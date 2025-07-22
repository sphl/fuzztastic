# Copyright 2021-2025 Chair for Software & Systems Engineering, TUM
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#!/usr/bin/env bash

# -------------------------- FuzzTastic Demo -------------------------
#
# This script runs AFL++ on mkd2html for five minutes while FuzzTastic
# monitors the achieved code coverage in real time.
#
# Usage: ./demo.sh [--skip-setup]

set -e

# ------------------------------ Helper ------------------------------

function print_info_msg() {
    local msg="$1"

    local cyan="\e[36m"
    local light_green="\e[92m"
    local endcolor="\e[0m"

    echo -e "$(date '+%Y-%m-%d %H:%M:%S') ${cyan}FuzzTastic${endcolor}[${light_green}Demo${endcolor}]: $msg"
}

function run_cmd_in_dir() {
    local wdir="$1"
    shift

    (cd "$wdir" && "$@")
}

function run_fuzztastic() {
    run_cmd_in_dir /fuzztastic poetry run fuzztastic "$@"
}

# ------------------ Fuzzer, Target & Corpus Setup -------------------

function fetch_fuzzer() {
    local wdir="$1"

    git clone "https://github.com/AFLplusplus/AFLplusplus.git" "$wdir/aflpp"
    run_cmd_in_dir "$wdir/aflpp" git checkout "v4.33c"
}

function build_fuzzer() {
    local wdir="$1"

    run_cmd_in_dir "$wdir/aflpp" make -j
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
    run_cmd_in_dir "$wdir/discount" git checkout "v3.0.0d"
}

function build_target() {
    local wdir="$1"

    # Extract the LLVM bitcode file from the target program (mkd2html)
    run_cmd_in_dir "$wdir/discount" sh -c '
        make distclean || true
        CC=gclang CFLAGS="-g -O0 -fno-inline" ./configure.sh
        make -j
        get-bc ./mkd2html
    '

    # Apply the FuzzTastic code coverage instrumentation
    run_fuzztastic instrument --input-bc "$wdir/discount/mkd2html.bc" --output-bc "$wdir/discount/mkd2html.ft.bc" --output "$wdir/mkd2html.json"

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

function setup_corpus() {
    local wdir="$1"

    if [ ! -d "$wdir/seed_corpus" ]; then
        mkdir "$wdir/seed_corpus"
        cp /fuzztastic/README.md "$wdir/seed_corpus/sample.md"
    fi
}

# --------------------------- Main Routine ---------------------------

function main() {
    local wdir="$1"
    local flag="$2"

    local log_file="$wdir/demo.log"

    if [ ! -d "$wdir" ]; then
        mkdir -p "$wdir"
    else
        rm -f "$log_file" 2>/dev/null || true
    fi

    if [ "$flag" != "--skip-setup" ]; then
        print_info_msg "⏳ Setting up the fuzzer (AFL++), target program (mkd2html), and seed corpus (run 'tail -f $log_file' to see the progress)"

        setup_fuzzer "$wdir" &>> "$log_file"
        setup_target "$wdir" &>> "$log_file"
        setup_corpus "$wdir" &>> "$log_file"
    fi

    local fuzzing_dur="5m"
    local fuzzing_dir="$wdir/campaign_$EPOCHSECONDS"

    mkdir "$fuzzing_dir"

    local fuzzing_cmd="timeout $fuzzing_dur $wdir/aflpp/afl-fuzz -z -i $wdir/seed_corpus -o $fuzzing_dir -- $wdir/fuzz_mkd2html @@"

    print_info_msg "🚀 Launching FuzzTastic with command: $fuzzing_cmd"

    sleep 5

    export AFL_TRY_AFFINITY=1
    export AFL_NO_SYNC=1

    run_fuzztastic monitor --input "$wdir/mkd2html.json" --command "$fuzzing_cmd" --visualization --output "$fuzzing_dir/coverage"

    print_info_msg "✅ Fuzzing completed. The coverage reports are in: $fuzzing_dir/coverage"
}

demo_dir="$(dirname "$(realpath "$0")")"
flag="$1"

main "$demo_dir" "$flag"
