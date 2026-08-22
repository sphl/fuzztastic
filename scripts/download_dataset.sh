#!/usr/bin/env bash
set -euo pipefail

ZENODO_URL="https://zenodo.org/records/21985962/files/fuzztastic_dataset.tar?download=1"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

DEST="${1:-$ROOT_DIR/data/dataset}"

mkdir -p "$DEST"

echo "Downloading dataset to '$DEST'..."
# --strip-components 2 drops the "./fuzztastic_dataset/" prefix so content lands directly in $DEST
curl -L --fail --progress-bar "$ZENODO_URL" \
    | tar -xf - --strip-components 2 -C "$DEST"

NCPUS=$(nproc 2>/dev/null || sysctl -n hw.logicalcpu 2>/dev/null || echo 1)

echo "Extracting campaign archives..."
find "$DEST" -maxdepth 1 -name '*.tar.xz' ! -name '._*' -print0 \
    | xargs -0 -r -P "$NCPUS" -I{} bash -c 'dir="${1%.tar.xz}"; mkdir -p "$dir" && tar -xJf "$1" -C "$dir" && rm "$1"' -- {}

find "$DEST" -name '._*' -delete

echo "Done."
