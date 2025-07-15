<div align="center">

# FuzzTastic

**A Fuzzer-Agnostic Real-Time Coverage Analyzer**

</div>

FuzzTastic is a code coverage analyzer primarily designed for fuzzing campaigns. It is compatible with any available fuzzer and tracks - in parallel with the campaign - line, basic block, and function coverage, along with the number of fuzz inputs exercising each code region. Additionally, it supports dynamic tracking intervals, adjusting the coverage sampling rate during the campaign based on a user-defined schedule.

## :clapper: Demo

The quickest way to try out FuzzTastic is by running its demo in the Docker container:

```bash
git clone <repo-link>
cd fuzztastic

docker-compose run fuzztastic bash ./scripts/demo.sh
```

In this demo, AFL++ fuzzes the `mkd2html` program of the [Discount project](https://github.com/Orc/discount) for **five minutes** while FuzzTastic tracks code coverage. It first generates a basic block metadata file (`mkd2html.json`), followed by periodic coverage reports (`ft_cov_<epoch>.json`) at one-minute intervals. All files are stored in the `scripts/demo` directory.

## :package: Installation

Please refer to the [`Dockerfile`](Dockerfile) for the required software dependencies.

### Setup

```bash
git clone <repo-link>
cd fuzztastic

# Install the Python dependencies
poetry install

# Build the LLVM instrumentation pass
cd instrumentation
mkdir build && cd build
cmake ..
make -j
```

### Configuration

To configure the coverage tracking interval and specify the required tool and library paths, edit the [`config.yaml`](config.yaml) file.

## :rocket: Usage

### Step 1: Extract Bitcode

Use e.g. [`gllvm`](https://github.com/SRI-CSL/gllvm) to extract the LLVM bitcode of the target program.

### Step 2: Instrument

Instrument the extracted bitcode (`target.bc`) with FuzzTastic's coverage tracking:

```bash
poetry run fuzztastic instrument --input-bc target.bc --output-bc target.ft.bc --output target.json
```

This also generates a basic block (BB) metadata file (`target.json`) containing code properties of all (instrumented) BBs in the target program.

<details>

<summary><b>Example: Basic Block Metadata</b></summary>

```json
{
  "basic_blocks": [
    {
      "id": 0,
      "function": "main",
      "file": "target.c",
      "lines": [1, 2, 3]
    },
    {
      "id": 1,
      "function": "main",
      "file": "target.c",
      "lines": [4]
    },
    {
      "id": 2,
      "function": "main",
      "file": "target.c",
      "lines": [5, 6, 7, 8, 9]
    }
  ]
}
```

- **`id`:** Unique BB identifier (index in the coverage arrays).

- **`function`:** Name of the function containing this BB.

- **`file`:** Source file name where the BB is located.

- **`lines`:** Line numbers spanned by the BB.

</details>

### Step 3: Compile

Compile the instrumented bitcode (`target.ft.bc`) into a fuzzable binary using e.g. the AFL++ compiler wrapper:

```bash
afl-clang-fast target.ft.bc -lfuzztasticrt -o fuzz_target
```

**Note:** The binary must be linked against the FuzzTastic runtime library (`libfuzztasticrt.so`) using the `-lfuzztasticrt` flag. This library is located in the `instrumentation/build/runtime-lib` directory, and its path must be included in the `LIBRARY_PATH` and `LD_LIBRARY_PATH` environment variables.

### Step 4: Track Coverage

Track the code coverage achieved during the campaign:

```bash
poetry run fuzztastic track --input target.json --command "afl-fuzz -i <input-dir> -o <output-dir> -- fuzz_target @@" --output coverage[.lst]
```

**Note:** The `--output` argument can either be

- a **directory**, in which case each coverage report is written as a separate file (`ft_cov_<epoch>.json`), or

- a **file**, in which case all coverage reports are appended as JSON strings to a single file, separated by newline characters.

<details>

<summary><b>Example: Coverage Report</b></summary>

```json
{
  "elapsed_time": 60.003,
  "coverage": [
    0,     // BB 0: Not covered (0 hits)
    1128,  // BB 1: Covered by 1128 different inputs
    0      // BB 2: Not covered
  ]
}
```

- **`elapsed_time`:** Seconds elapsed since the campaign started.

- **`coverage`:** Array of BB coverage data, with indices matching the BB IDs in the metadata file.

</details>

## :man_technologist: Development

FuzzTastic includes a development Docker container (`fuzztastic-dev`) that can be used with the [VS Code Dev Container plugin](https://code.visualstudio.com/docs/devcontainers/containers) for developing both the FuzzTastic tool (Python) and its LLVM instrumentation pass (C/C++).

## :books: Citation

If you use FuzzTastic in your research, please cite:

> Stephan Lipp, Daniel Elsner, Thomas Hutzelmann, Sebastian Banescu, Alexander Pretschner, and Marcel Böhme. 2022. FuzzTastic: A Fine-Grained, Fuzzer-Agnostic Coverage Analyzer. In Companion Proceedings of the International Conference on Software Engineering. ACM, 75-79. DOI: [10.1145/3510454.3516847](https://dl.acm.org/doi/10.1145/3510454.3516847)

<details>

<summary><b>BibTeX Entry</b></summary>

```bibtex
@inproceedings{fuzztastic,
  title        = {FuzzTastic: A Fine-Grained, Fuzzer-Agnostic Coverage Analyzer},
  author       = {Stephan Lipp and Daniel Elsner and Thomas Hutzelmann and Sebastian Banescu and Alexander Pretschner and Marcel B\"{o}hme},
  year         = {2022},
  booktitle    = {Companion Proceedings of the International Conference on Software Engineering},
  organization = {ACM},
  pages        = {75--79},
  doi          = {10.1145/3510454.3516847}
}
```

</details>
