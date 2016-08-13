#pragma once

#include "config.h"

#include <stddef.h>

#include "arena.h"
#include "bag.h"
#include "object.h"

struct qcgc_allocator_state {
	arena_bag_t *arenas;
	struct bump_state {
		cell_t *bump_ptr;
		size_t remaining_cells;
	} bump_state;
	struct fit_state {
		void *free_lists[QCGC_LINEAR_FREE_LISTS + QCGC_EXP_FREE_LISTS + 1];
	} fit_state;
} qcgc_allocator_state;

/**
 * Initialize allocator
 */
void qcgc_allocator_initialize(void);

/**
 * Destroy allocator
 */
void qcgc_allocator_destroy(void);

/**
 * Allocate new memory region
 *
 * @param	bytes	Desired size of the memory region in bytes
 * @return	Pointer to memory large enough to hold size bytes, NULL in case of
 *			errors, already zero initialized if QCGC_INIT_ZERO is set
 */
cell_t *qcgc_allocator_allocate(size_t bytes);
