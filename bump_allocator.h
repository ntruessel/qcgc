#pragma once

#include "config.h"

#include <stdbool.h>

#include "arena.h"

struct qcgc_balloc_state {
	cell_t *bump_ptr;
	size_t remaining_cells;
} qcgc_balloc_state;

/**
 * Assign a memory region to the bump allocator
 */
void qcgc_balloc_assign(cell_t *bump_ptr, size_t cells);

/**
 * Allocate a given amount of cells from the current memory region
 */
void *qcgc_balloc_allocate(size_t cells);

/**
 * Check whether cells many cells can be allocated
 */
bool qcgc_balloc_can_allocate(size_t cells);
