<div align="center">

# FuzzTastic

**A Fuzzer-Agnostic Real-Time Coverage Analyzer**

<img src="treemap.png" width=800>

</div>

FuzzTastic is a code coverage analyzer primarily designed for fuzzing campaigns. It comes with the following **features**:

- Compatible with any available fuzzer.

- Monitors line, basic block, and function coverage in parallel with the campaign.

- Tracks the exact number of fuzz inputs exercising each code region.

- Dynamic tracking schedule to adjust the coverage sampling rate during the campaign.

- Interactive visualization that shows the current code coverage in a treemap.

## Contents

- :clapper: [Demo](#demo)

- :package: [Installation](#installation)

- :rocket: [Usage](#usage)

- :bar_chart: [Visualization](#visualization)

- :floppy_disk: [Dataset](#dataset)

- :man_technologist: [Development](#development)

## Demo

The quickest way to try out FuzzTastic is by running its demo in the Docker container:

```bash
git clone <REPO_LINK>
cd fuzztastic

docker-compose run --service-ports fuzztastic ./scripts/run_demo.sh
```

In this demo, AFL++ fuzzes the `mkd2html` program of the [Discount project](https://github.com/Orc/discount) for **10 minutes** while FuzzTastic tracks and visualizes the code coverage. It first generates a basic block metadata file (`mkd2html.json`), followed by periodic coverage reports (`ft_cov_<epoch>.json`) at one-minute intervals (all files are stored in the `data/demo` directory). Moreover, it launches the treemap visualization, which can be viewed in the browser at `http://127.0.0.1:8050` (updated every 30 seconds).

## Installation

Please refer to the [`Dockerfile`](Dockerfile) for the required software dependencies.

### Setup

```bash
git clone <REPO_LINK>
cd fuzztastic

# Install the Python dependencies
poetry install

# Build the LLVM instrumentation pass (Debug by default)
cmake -B instrumentation/build -S instrumentation \
    -DCMAKE_BUILD_TYPE=Release

cmake --build instrumentation/build --parallel
```

### Configuration

Please take a look at the [`config.yaml`](config.yaml) file to view and edit the FuzzTastic configuration options.

## Usage

### Step 1: Extract Bitcode

Extract the LLVM bitcode of the target program using, e.g., [`gllvm`](https://github.com/SRI-CSL/gllvm).

### Step 2: Instrument

Instrument the extracted bitcode (`<TARGET_BITCODE_FILE>`) with FuzzTastic's coverage tracking:

```bash
poetry run fuzztastic instrument \
    --input-bc <TARGET_BITCODE_FILE> \
    --output-bc <INSTRUMENTED_BITCODE_FILE> \
    --output <BB_METADATA_JSON_FILE>
```

This also generates a basic block (BB) metadata file (`<BB_METADATA_JSON_FILE>`) containing code properties of all (instrumented) BBs in the target program.

#### Example: Basic Block Metadata

```json
[
    {
        "id": 0,
        "function": "main",
        "file": "/path/to/target.c",
        "program": "target",
        "lines": [1, 2, 3]
    },
    {
        "id": 1,
        "function": "main",
        "file": "/path/to/target.c",
        "program": "target",
        "lines": [4]
    },
    {
        "id": 2,
        "function": "main",
        "file": "/path/to/target.c",
        "program": "target",
        "lines": [5, 6, 7, 8, 9]
    },
    ...
]
```

**Fields:**

- `id`: Unique BB identifier (index in the coverage arrays).

- `function`: Name of the function containing this BB.

- `file`: Absolute source file path where the BB is located.

- `program`: Name of the program.

- `lines`: Line numbers spanned by the BB.

### Step 3: Compile

Compile the instrumented bitcode (`<INSTRUMENTED_BITCODE_FILE>`) into a fuzzable binary using, e.g., the AFL++ compiler wrapper:

```bash
afl-clang-fast <INSTRUMENTED_BITCODE_FILE> -lfuzztasticrt -o <FUZZ_BINARY_FILE>
```

> **Note:** The binary must be linked against the FuzzTastic runtime library (`libfuzztasticrt.so`) using the `-lfuzztasticrt` flag. This library is located in the `instrumentation/build/runtime-lib` directory, and its path must be included in the `LIBRARY_PATH` and `LD_LIBRARY_PATH` environment variables.

### Step 4: Monitor Coverage

Track the code coverage achieved during the campaign:

```bash
poetry run fuzztastic monitor \
    --input <BB_METADATA_JSON_FILE> \
    --command "afl-fuzz -i <SEED_CORPUS_DIR> -o <OUTPUT_DIR> -- <FUZZ_BINARY_FILE> @@" \
    --output <COVERAGE_DIR_OR_FILE>
```

The `--output` argument can be either

- a **directory**, in which case each coverage report is written as a separate file (`ft_cov_<epoch>.json`), or

- a **file** (with `.lst` extension), in which case all coverage reports are appended as JSON strings to a single file, separated by newline characters.

Optionally, pass `--visualization <NAME>` to launch a real-time coverage visualization alongside the campaign (see [Visualization](#visualization)).

#### Example: Coverage Report

```json
{
    "elapsed_time": 60.003,
    "coverage": [
        0,     // BB 0: Not covered (0 hits)
        1128,  // BB 1: Covered by 1128 different inputs
        0,     // BB 2: Not covered
        ...
    ]
}
```

**Fields:**

- `elapsed_time`: Seconds elapsed since the campaign started.

- `coverage`: Array of BB coverage data, with indices matching the BB IDs in the metadata file.

## Visualization

FuzzTastic supports interactive visualizations that display real-time code coverage during a fuzzing campaign. Pass one or more `--visualization <NAME>` options to `fuzztastic monitor` to enable them. The visualizations can be accessed in the browser at `http://127.0.0.1:8050`.

For a guide on adding new visualizations, see [Integrating a New Visualization](#integrating-a-new-visualization).

### Treemap

The treemap visualization (`--visualization treemap`) displays the current code coverage of the target program, organized hierarchically from **programs** down to **source files**, **functions**, and individual **basic blocks**.

Each node is color-coded by the number of distinct fuzz inputs that hit the corresponding BB - ranging from white (not covered) through yellow, orange, red, and dark red to black (maximum hit count) - and hovering over a node shows its exact input hit count. For non-leaf nodes (programs, files, functions), the hit count is the average over all contained BBs. The visualization is updated at a configurable interval (default: every 30 seconds).

## Dataset

A dataset of 4,320 fuzzing campaigns - covering multiple subject programs and fuzzers - is available for download on [Zenodo](https://zenodo.org/records/21985962) (**~114 GB** uncompressed). Each campaign includes the coverage reports produced by FuzzTastic as well as all fuzzer-generated artifacts. For full details on the dataset, see the [FuzzTastic paper](https://dl.acm.org/doi/10.1145/3510454.3516847).

The entire dataset can be downloaded and extracted automatically by running:

```bash
./scripts/download_dataset.sh [<DATASET_DIR>]
```

If no directory is specified, the default destination is `data/dataset/`.

> **Note:** BB hit counts in the dataset are **execution counts**: a BB executed *N* times by a single input contributes *N* to its count, not 1 as in the current FuzzTastic version.

## Development

FuzzTastic comes with a development Docker container (`fuzztastic-dev`), which can be used with the [VS Code Dev Container plugin](https://code.visualstudio.com/docs/devcontainers/containers) for developing the FuzzTastic tool (Python) and LLVM instrumentation pass (C/C++).

> **Note:** The dev container forwards port `8050` to `http://127.0.0.1:8051` (instead of `8050`) to avoid colliding with a running production container.

### Code Quality and Testing

- Format the code:

    ```bash
    # Python
    poetry run ruff format .

    # C/C++
    find instrumentation \( -name "*.cpp" -o -name "*.c" -o -name "*.h" \) -not -path "instrumentation/build/*" | xargs clang-format -i --style=file
    ```

- Run static checks and linting:

    ```bash
    # Python
    poetry run ruff check .
    poetry run mypy fuzztastic

    # C/C++
    clang-tidy -p instrumentation/build $(find instrumentation \( -name "*.cpp" -o -name "*.c" \) -not -path "instrumentation/build/*")
    ```

- Run tests:

    ```bash
    poetry run pytest
    ```

- Run tests with coverage:

    ```bash
    poetry run pytest --cov fuzztastic
    ```

### Integrating a New Visualization

Adding support for a new visualization requires the following changes:

1. [`config.yaml`](config.yaml) and [`fuzztastic/__init__.py`](fuzztastic/__init__.py): Add a configuration entry under `monitoring.visualization` for the new visualization's settings (e.g., update interval) and parse it in `Config.from_yaml`.

2. [`fuzztastic/visualization/`](fuzztastic/visualization/): Create a new module and subclass `Visualization`. Implement the constructor - calling `super().__init__(start_time, interval, label="<LABEL>")` to set the label - and implement `update_figure(bb_metadata, bb_cov_data)` to return a Plotly `go.Figure`. The `_get_fuzzing_duration()` helper is inherited from the base class.

3. [`fuzztastic/visualization/base.py`](fuzztastic/visualization/base.py): Add a new entry to the `VisualizationType` enum, using the CLI option name as the value (e.g., `MY_VIZ = "my-viz"`).

4. [`fuzztastic/visualization/factory.py`](fuzztastic/visualization/factory.py): Handle the new `VisualizationType` value in `get_visualization` by instantiating the new visualization class.

5. [`fuzztastic/commands/monitor.py`](fuzztastic/commands/monitor.py): Add an entry to the `type_to_intervals` dict mapping the new `VisualizationType` to its configured interval (e.g., `VisualizationType.MY_VIZ: config.visualization.my_viz.interval`).

The new visualization can now be launched via `--visualization my-viz`.
