#include "qcgc.h"

#include <assert.h>

#include <stdlib.h>
#include <stdio.h>

#include "bump_allocator.h"

// TODO: Eventually move to own header?
#define MAX(a,b) (((a)>(b))?(a):(b))

object_t *qcgc_bump_allocate(size_t size);
void qcgc_mark(void);
void qcgc_mark_all(void);
void qcgc_mark_incremental(void);
void qcgc_pop_object(object_t *object);
void qcgc_push_object(object_t *object);
void qcgc_sweep(void);

void qcgc_initialize(void) {
	qcgc_state.shadow_stack = qcgc_state.shadow_stack_base =
		(object_t **) malloc(QCGC_SHADOWSTACK_SIZE);
	qcgc_state.arenas = (arena_t **) calloc(sizeof(arena_t *), QCGC_ARENA_COUNT);
	qcgc_state.arena_index = 0;
	qcgc_state.arenas[qcgc_state.arena_index] = qcgc_arena_create();
	qcgc_state.current_cell_index = QCGC_ARENA_FIRST_CELL_INDEX;
	qcgc_state.gray_stack_size = 0;
	qcgc_state.state = GC_PAUSE;

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
 * Write barrier                                                               *
 ******************************************************************************/
void qcgc_write(object_t *object) {
#if CHECKED
	assert(object != NULL);
#endif
	if ((object->flags & QCGC_GRAY_FLAG) == 0) {
		object->flags |= QCGC_GRAY_FLAG;
		if (qcgc_arena_get_blocktype((cell_t *) object) == BLOCK_BLACK) {
			// This was black before, push it to gray stack again
			qcgc_state.gray_stack_size++;
			arena_t *arena = qcgc_arena_addr((cell_t *) object);
			arena->gray_stack = qcgc_gray_stack_push(
					arena->gray_stack, object);
		}
	}
}

/*******************************************************************************
 * Allocation                                                                  *
 ******************************************************************************/

object_t *qcgc_allocate(size_t size) {
	object_t *result = NULL;
	if (size >= QCGC_LARGE_ALLOC_THRESHOLD) {
		// Use malloc for large objects
		result = (object_t *) malloc(size);
	} else {
		result = qcgc_bump_allocate(size);
	}
	return result;
}

object_t *qcgc_bump_allocate(size_t size) {
	size_t size_in_cells = (size + 15) / 16;
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
	qcgc_mark_all();
}

void qcgc_mark_all(void) {
#if CHECKED
	assert(qcgc_state.state == GC_PAUSE || qcgc_state.state == GC_MARK);
#endif
	qcgc_state.state = GC_MARK;

	// Push all roots
	for (object_t **it = qcgc_state.shadow_stack_base;
			it != qcgc_state.shadow_stack;
			it++) {
		qcgc_push_object(*it);
	}

	while(qcgc_state.gray_stack_size > 0) {
		for (size_t i = 0; i <= qcgc_state.arena_index; i++) {
			while (qcgc_state.arenas[i]->gray_stack->index > 0) {
				object_t *top =
					qcgc_gray_stack_top(qcgc_state.arenas[i]->gray_stack);
				qcgc_state.arenas[i]->gray_stack =
					qcgc_gray_stack_pop(qcgc_state.arenas[i]->gray_stack);
				qcgc_pop_object(top);
			}
		}
	}

	qcgc_state.state = GC_COLLECT;
}

void qcgc_mark_incremental(void) {
#if CHECKED
	assert(qcgc_state.state == GC_PAUSE || qcgc_state.state == GC_MARK);
#endif
	qcgc_state.state = GC_MARK;

	// Push all roots
	for (object_t **it = qcgc_state.shadow_stack_base;
			it != qcgc_state.shadow_stack;
			it++) {
		qcgc_push_object(*it);
	}

	for (size_t i = 0; i <= qcgc_state.arena_index; i++) {
		arena_t *arena = qcgc_state.arenas[i];
		size_t initial_stack_size = arena->gray_stack->index;
		size_t to_process = MAX(initial_stack_size / 2, QCGC_INC_MARK_MIN);
		while (to_process > 0) {
			object_t *top =
				qcgc_gray_stack_top(qcgc_state.arenas[i]->gray_stack);
			qcgc_state.arenas[i]->gray_stack =
				qcgc_gray_stack_pop(qcgc_state.arenas[i]->gray_stack);
			qcgc_pop_object(top);
			to_process--;
		}
	}

	if (qcgc_state.gray_stack_size == 0) {
		qcgc_state.state = GC_COLLECT;
	}
}

void qcgc_pop_object(object_t *object) {
#if CHECKED
	assert(object != NULL);
	assert((object->flags & QCGC_GRAY_FLAG) == QCGC_GRAY_FLAG);
	assert(qcgc_arena_get_blocktype((cell_t *) object) == BLOCK_BLACK);
#endif
	qcgc_state.gray_stack_size--;
	object->flags &= ~QCGC_GRAY_FLAG;
	qcgc_trace_cb(object, &qcgc_push_object);
}

void qcgc_push_object(object_t *object) {
#if CHECKED
	assert(qcgc_state.state == GC_MARK);
#endif
	if (object != NULL) {
		if (qcgc_arena_get_blocktype((cell_t *) object) == BLOCK_WHITE) {
			object->flags |= QCGC_GRAY_FLAG;
			qcgc_arena_set_blocktype((cell_t *) object, BLOCK_BLACK);
			qcgc_state.gray_stack_size++;
			arena_t *arena = qcgc_arena_addr((cell_t *) object);
			arena->gray_stack = qcgc_gray_stack_push(arena->gray_stack, object);
		}
	}
}

void qcgc_sweep(void) {
#if CHECKED
	assert(qcgc_state.state == GC_COLLECT);
#endif
	for (size_t i = 0; i <= qcgc_state.arena_index; i++) {
		qcgc_arena_sweep(qcgc_state.arenas[i]);
	}
	qcgc_state.state = GC_PAUSE;
}

void qcgc_collect(void) {
	qcgc_mark();
	qcgc_sweep();
}
