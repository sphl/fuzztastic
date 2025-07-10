#!/usr/bin/env bash

# FuzzTastic demo
#
# This script runs AFL++ on mkd2html for 5 minutes while FuzzTastic tracks the achieved code coverage in real time.
#
# Usage: ./run_fuzztastic.sh

set -e

CYAN="\e[36m"
LIGHT_GREEN="\e[92m"
ENDCOLOR="\e[0m"

function log_info() {
    local msg="$1"

    echo -e "$(date '+%Y-%m-%d %H:%M:%S') ${CYAN}FuzzTastic${ENDCOLOR}[${LIGHT_GREEN}Demo${ENDCOLOR}]: $msg"
}

export WDIR="$PWD"

log_info "⏳ Setting up fuzzer (AFL++) and target program (mkd2html)"

. "$WDIR/setup.sh"

fuzzing_dur="5m"
fuzzing_dir="$WDIR/campaign_$EPOCHSECONDS"

mkdir "$fuzzing_dir"

fuzzing_cmd="timeout $fuzzing_dur $WDIR/aflpp/afl-fuzz -z -i $WDIR/seed_corpus -o $fuzzing_dir -- $WDIR/fuzz_mkd2html @@"

log_info "🚀 Launching FuzzTastic with command: $fuzzing_cmd"

sleep 5

export AFL_TRY_AFFINITY=1
export AFL_NO_SYNC=1

run_wdir_cmd /fuzztastic poetry run fuzztastic track --input "$WDIR/mkd2html.json" --command "$fuzzing_cmd" --output "$fuzzing_dir/coverage"

log_info "✅ Fuzzing completed. Coverage reports stored in: $fuzzing_dir/coverage"
