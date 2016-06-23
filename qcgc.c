#include "qcgc.h"

#include <stdlib.h>
#include <stdio.h>

#include "bump_allocator.h"

object_t *qcgc_bump_allocate(size_t bytes);
void qcgc_mark(void);
void qcgc_mark_object(object_t *object);
void qcgc_sweep(void);

void qcgc_initialize(void) {
	qcgc_state.shadow_stack = qcgc_state.shadow_stack_base = (object_t **) malloc(QCGC_SHADOWSTACK_SIZE); qcgc_state.arenas = (arena_t **) calloc(sizeof(arena_t *), QCGC_ARENA_COUNT);
	qcgc_state.arena_index = 0;
	qcgc_state.arenas[qcgc_state.arena_index] = qcgc_arena_create();
	qcgc_state.current_cell_index = QCGC_ARENA_FIRST_CELL_INDEX;

	qcgc_balloc_assign(
			&(qcgc_state.arenas[qcgc_state.arena_index]
				->cells[qcgc_state.current_cell_index]),
			QCGC_ARENA_CELLS_COUNT - QCGC_ARENA_FIRST_CELL_INDEX);
}

void qcgc_destroy(void) {
	free(qcgc_state.shadow_stack_base);
	for (size_t i = 0; i <= qcgc_state.arena_index; i++) {
		qcgc_arena_destroy(qcgc_state.arenas[i]);
	}
	free(qcgc_state.arenas);
}

/*******************************************************************************
 * Allocation                                                                  *
 ******************************************************************************/

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

object_t *qcgc_bump_allocate(size_t bytes) {
	size_t size_in_cells = (bytes + 15) / 16;
	if (!qcgc_balloc_can_allocate(size_in_cells)) {
		// Create a new arena and assign its memory to bump allocator
		qcgc_state.arena_index++;
		if (qcgc_state.arena_index >= QCGC_ARENA_COUNT) {
			return NULL; // No more space available
		}
		qcgc_state.arenas[qcgc_state.arena_index] = qcgc_arena_create();
		qcgc_state.current_cell_index = QCGC_ARENA_FIRST_CELL_INDEX;
		qcgc_balloc_assign(
				&(qcgc_state.arenas[qcgc_state.arena_index]
					->cells[qcgc_state.current_cell_index]),
				QCGC_ARENA_CELLS_COUNT - QCGC_ARENA_FIRST_CELL_INDEX);
	}
	return (object_t *) qcgc_balloc_allocate(size_in_cells);
}

/*******************************************************************************
 * Collection                                                                  *
 ******************************************************************************/

void qcgc_mark(void) {
	for (object_t **root = qcgc_state.shadow_stack_base;
			root != qcgc_state.shadow_stack;
			root++) {
		qcgc_mark_object(*root);
	}
}

void qcgc_mark_object(object_t *object) {
	if (qcgc_arena_get_blocktype((void *) object) != BLOCK_BLACK) {
		qcgc_arena_set_blocktype((void *) object, BLOCK_BLACK);
		qcgc_trace_cb(object, &qcgc_mark_object);
	}
}

void qcgc_sweep(void) {
	for (size_t i = 0; i <= qcgc_state.arena_index; i++) {
		qcgc_arena_sweep(qcgc_state.arenas[i]);
	}
}

void qcgc_collect(void) {
	qcgc_mark();
	qcgc_sweep();
}
