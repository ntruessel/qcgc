#pragma once

#include "config.h"

#include <stdbool.h>

#include "arena.h"

/**
 * @var qcgc_balloc_state
 * 
 * Global state of bump allocator
 */
struct {
	cell_t *bump_ptr;
	size_t remaining_cells;
} qcgc_balloc_state;

/**
 * Assign a memory region to the bump allocator.
 *
 * @arg	bump_ptr	Pointer to the first cell of the memory region
 * @arg	cells		Size of the region in cells
 */
void qcgc_balloc_assign(cell_t *bump_ptr, size_t cells);

/**
 * Allocate a given amount of cells from the current memory region.
 *
 * @arg	cells	The amount of cells that should be allocated
 * @return	Pointer to the allocated memory
 */
void *qcgc_balloc_allocate(size_t cells);

/**
 * Check whether cells many cells can be allocated.
 *
 * @arg	cells	The amount of cells
 * @return	true iff there is enough space to allcate memory with the size of
 *			cells
 */
bool qcgc_balloc_can_allocate(size_t cells);
