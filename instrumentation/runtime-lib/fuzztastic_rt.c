// Copyright 2026 Stephan Lipp
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include <fcntl.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <unistd.h>

#define FT_ENVVAR_SHM_NAME "FT_SHM_NAME"
#define FT_ENVVAR_BB_COUNT "FT_BB_COUNT"

// NOLINTBEGIN
static size_t shm_size = 0;
static size_t bb_count = 0;

static uint64_t *shm_data = NULL;
static uint64_t *cov_data = NULL;
// NOLINTEND

/**
 * Initializes the shared memory segment and the local coverage data array.
 */
static void ft_init(void) {
    const char *shm_name = getenv(FT_ENVVAR_SHM_NAME);

    if (shm_name == NULL) {
        fprintf(stderr, "ERROR: Environment variable '%s' not set!\n", FT_ENVVAR_SHM_NAME);  // NOLINT
        exit(EXIT_FAILURE);
    }

    const char *temp_str = getenv(FT_ENVVAR_BB_COUNT);

    if (temp_str == NULL) {
        fprintf(stderr, "ERROR: Environment variable '%s' not set!\n", FT_ENVVAR_BB_COUNT);  // NOLINT
        exit(EXIT_FAILURE);
    }

    bb_count = strtoul(temp_str, NULL, 10);  // NOLINT

    if (bb_count == 0) {
        fprintf(stderr, "ERROR: Invalid number of basic blocks specified!\n");  // NOLINT
        exit(EXIT_FAILURE);
    }

    shm_size = bb_count * sizeof(uint64_t);

    int shm_fd = shm_open(shm_name, O_RDWR, 0);

    if (shm_fd < 0) {
        fprintf(stderr, "ERROR: Could not open shared memory segment '%s'!\n", shm_name);  // NOLINT
        exit(EXIT_FAILURE);
    }

    shm_data = mmap(NULL, shm_size, PROT_READ | PROT_WRITE, MAP_SHARED, shm_fd, 0);

    close(shm_fd);

    if (shm_data == MAP_FAILED) {
        fprintf(stderr, "ERROR: Could not map shared memory segment!\n");  // NOLINT
        exit(EXIT_FAILURE);
    }

    cov_data = calloc(bb_count, sizeof(uint64_t));  // NOLINT

    if (cov_data == NULL) {
        fprintf(stderr, "ERROR: Could not allocate memory for coverage data!\n");  // NOLINT
        munmap(shm_data, shm_size);
        exit(EXIT_FAILURE);
    }
}

/**
 * Increments the hit count for a basic block.
 */
void ft_inc_cov(uint32_t bb_id) { cov_data[bb_id] += 1; }

/**
 * Stores the new coverage data into the shared memory segment.
 */
static void ft_sync_cov_data(void) {
    if (shm_data == NULL || cov_data == NULL) {
        return;
    }

    for (size_t i = 0; i < bb_count; i++) {
        shm_data[i] += cov_data[i] > 0 ? 1 : 0;
    }
}

/**
 * Cleans up the resources used by the runtime library.
 */
static void ft_cleanup(void) {
    if (cov_data != NULL) {
        free(cov_data);
        cov_data = NULL;
    }

    if (shm_data != NULL) {
        munmap(shm_data, shm_size);
        shm_data = NULL;
    }
}

__attribute__((constructor)) void ft_auto_init(void) { ft_init(); }

__attribute__((destructor)) void ft_auto_sync_and_cleanup(void) {
    ft_sync_cov_data();
    ft_cleanup();
}
