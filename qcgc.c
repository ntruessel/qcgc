#include "qcgc.h"

#include <stdlib.h>
#include <stdio.h>

void qcgc_initialize(void) {
	qcgc_state.shadow_stack = qcgc_state.shadow_stack_base =
		(object_t **) malloc(QCGC_SHADOWSTACK_SIZE);
	qcgc_state.current_arena = qcgc_arena_create();
	qcgc_state.current_cell_index = QCGC_ARENA_FIRST_CELL_INDEX;
}

void qcgc_destroy(void) {
	free(qcgc_state.shadow_stack_base);
}

object_t *qcgc_allocate(size_t bytes) {
	object_t *result = NULL;
	if (bytes >= 1<<14) { // XXX: REPLACE BY MACRO
		// Use malloc for large objects
		result = (object_t *) malloc(bytes);
	} else {
		size_t size_in_cells = (bytes + 15) / 16;
		if (qcgc_state.current_cell_index + size_in_cells > QCGC_ARENA_CELLS_COUNT) {
			// Create new arena and allocate there
			qcgc_state.current_arena = qcgc_arena_create();
			qcgc_state.current_cell_index = QCGC_ARENA_FIRST_CELL_INDEX;
		}
		// Allocate in current arena
		result = (object_t *) &(qcgc_state.current_arena->cells[qcgc_state.current_cell_index]);
		qcgc_arena_mark_allocated((void *) result, bytes);
	}
	return result;
}

void qcgc_collect(void) {
	return;
}
