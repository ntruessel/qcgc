#include "bump_allocator.h"

#include <stddef.h>

/**
 * Assign a memory region to the bump allocator
 */
void qcgc_balloc_assign(cell_t *bump_ptr, size_t cells) {
	qcgc_balloc_state.bump_ptr = bump_ptr;
	qcgc_balloc_state.remaining_cells = cells;
}

/**
 * Allocate a given amount of cells from the current memory region
 */
void *qcgc_balloc_allocate(size_t cells) {
	if (qcgc_balloc_can_allocate(cells)) {
		void *result = qcgc_balloc_state.bump_ptr;
		qcgc_arena_mark_allocated(result, cells);

		qcgc_balloc_state.bump_ptr += cells;
		qcgc_balloc_state.remaining_cells -= cells;

		return result;
	} else {
		return NULL;
	}
}

bool qcgc_balloc_can_allocate(size_t cells) {
	return cells <= qcgc_balloc_state.remaining_cells;
}

size_t qcgc_balloc_remaining_cells(void) {
	return qcgc_balloc_state.remaining_cells;
}
