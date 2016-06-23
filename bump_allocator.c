#include "bump_allocator.h"

#include <stddef.h>

void qcgc_balloc_assign(cell_t *bump_ptr, size_t cells) {
	qcgc_balloc_state.bump_ptr = bump_ptr;
	qcgc_balloc_state.remaining_cells = cells;
}

void *qcgc_balloc_allocate(size_t cells) {
	if (qcgc_balloc_can_allocate(cells)) {
		cell_t *result = qcgc_balloc_state.bump_ptr;
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
