#include "qcgc.h"

#include <stdlib.h>
#include <stdio.h>

object_t *qcgc_bump_allocate(size_t bytes) {
	object_t *result = NULL;
	size_t size_in_cells = (bytes + 15) / 16;
	if (qcgc_state.current_cell_index + size_in_cells > QCGC_ARENA_CELLS_COUNT) {
		// Create new arena and allocate there
		qcgc_state.arena_index++;
		if (qcgc_state.arena_index >= QCGC_ARENA_COUNT) {
			return NULL; // No more space available
		}
		qcgc_state.arenas[qcgc_state.arena_index] = qcgc_arena_create();
		qcgc_state.current_cell_index = QCGC_ARENA_FIRST_CELL_INDEX;
	}
	// Allocate in current arena
	result = (object_t *) &(qcgc_state.arenas[qcgc_state.arena_index]->cells[qcgc_state.current_cell_index]);
	qcgc_arena_mark_allocated((void *) result, bytes);
	qcgc_state.current_cell_index += size_in_cells;

	return result;
}

void qcgc_initialize(void) {
	qcgc_state.shadow_stack = qcgc_state.shadow_stack_base =
		(object_t **) malloc(QCGC_SHADOWSTACK_SIZE);
	qcgc_state.arenas = (arena_t **) calloc(sizeof(arena_t *), QCGC_ARENA_COUNT);
	qcgc_state.arena_index = 0;
	qcgc_state.arenas[qcgc_state.arena_index] = qcgc_arena_create();
	qcgc_state.current_cell_index = QCGC_ARENA_FIRST_CELL_INDEX;
}

void qcgc_destroy(void) {
	free(qcgc_state.shadow_stack_base);
	for (size_t i = 0; i <= qcgc_state.arena_index; i++) {
		qcgc_arena_destroy(qcgc_state.arenas[i]);
	}
	free(qcgc_state.arenas);
}

object_t *qcgc_allocate(size_t bytes) {
	object_t *result = NULL;
	if (bytes >= QCGC_LARGE_ALLOC_THRESHOLD) {
		// Use malloc for large objects
		result = (object_t *) malloc(bytes);
	} else {
		result = qcgc_bump_allocate(bytes);
	}
	return result;
}

void qcgc_collect(void) {
	return;
}
