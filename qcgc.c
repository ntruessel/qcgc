#include "qcgc.h"

#include <assert.h>

#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "allocator.h"
#include "event_logger.h"

// TODO: Eventually move to own header?
#define MAX(a,b) (((a)>(b))?(a):(b))
#define MIN(a,b) (((a)<(b))?(a):(b))

void qcgc_mark(void);
void qcgc_mark_all(void);
void qcgc_mark_incremental(void);
void qcgc_pop_object(object_t *object);
void qcgc_push_object(object_t *object);
void qcgc_sweep(void);

void qcgc_initialize(void) {
	qcgc_state.shadow_stack = qcgc_state.shadow_stack_base =
		(object_t **) malloc(QCGC_SHADOWSTACK_SIZE);
	qcgc_state.gray_stack_size = 0;
	qcgc_state.phase = GC_PAUSE;
	qcgc_allocator_initialize();
	qcgc_event_logger_initialize();
}

void qcgc_destroy(void) {
	qcgc_event_logger_destroy();
	qcgc_allocator_destroy();
	free(qcgc_state.shadow_stack_base);
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
		if (qcgc_state.phase != GC_PAUSE) {
			if (qcgc_arena_get_blocktype((cell_t *) object) == BLOCK_BLACK) {
				// This was black before, push it to gray stack again
				arena_t *arena = qcgc_arena_addr((cell_t *) object);
				arena->gray_stack = qcgc_gray_stack_push(
						arena->gray_stack, object);
			}
		}
	}
}

/*******************************************************************************
 * Allocation                                                                  *
 ******************************************************************************/

object_t *qcgc_allocate(size_t size) {
	object_t *result = (object_t *) qcgc_allocator_allocate(size);
	result->flags |= QCGC_GRAY_FLAG;
	return result;
}

/*******************************************************************************
 * Collection                                                                  *
 ******************************************************************************/

mark_color_t qcgc_get_mark_color(object_t *object) {
#if CHECKED
	assert(object != NULL);
#endif
	blocktype_t blocktype = qcgc_arena_get_blocktype((cell_t *) object);
	bool gray = (object->flags & QCGC_GRAY_FLAG) == QCGC_GRAY_FLAG;
	if (blocktype == BLOCK_WHITE) {
		if (gray) {
			return MARK_COLOR_LIGHT_GRAY;
		} else {
			return MARK_COLOR_WHITE;
		}
	} else if(blocktype == BLOCK_BLACK) {
		if (gray) {
			return MARK_COLOR_DARK_GRAY;
		} else {
			return MARK_COLOR_BLACK;
		}
	} else {
#if CHECKED
		assert(false);
#endif
	}
}

void qcgc_mark(void) {
	qcgc_mark_all();
}

void qcgc_mark_all(void) {
#if CHECKED
	assert(qcgc_state.phase == GC_PAUSE || qcgc_state.phase == GC_MARK);
#endif
	qcgc_state.phase = GC_MARK;

	// Push all roots
	for (object_t **it = qcgc_state.shadow_stack_base;
			it != qcgc_state.shadow_stack;
			it++) {
		qcgc_push_object(*it);
	}

	while(qcgc_state.gray_stack_size > 0) {
		for (size_t i = 0; i < qcgc_allocator_state.arenas->count; i++) {
			arena_t *arena = qcgc_allocator_state.arenas->items[i];
			while (arena->gray_stack->index > 0) {
				object_t *top =
					qcgc_gray_stack_top(arena->gray_stack);
				arena->gray_stack =
					qcgc_gray_stack_pop(arena->gray_stack);
				qcgc_pop_object(top);
			}
		}
	}

	qcgc_state.phase = GC_COLLECT;
}

void qcgc_mark_incremental(void) {
#if CHECKED
	assert(qcgc_state.phase == GC_PAUSE || qcgc_state.phase == GC_MARK);
#endif
	qcgc_state.phase = GC_MARK;

	// Push all roots
	for (object_t **it = qcgc_state.shadow_stack_base;
			it != qcgc_state.shadow_stack;
			it++) {
		qcgc_push_object(*it);
	}

	for (size_t i = 0; i < qcgc_allocator_state.arenas->count; i++) {
		arena_t *arena = qcgc_allocator_state.arenas->items[i];
		size_t initial_stack_size = arena->gray_stack->index;
		size_t to_process = MIN(arena->gray_stack->index,
				MAX(initial_stack_size / 2, QCGC_INC_MARK_MIN));
		while (to_process > 0) {
			object_t *top =
				qcgc_gray_stack_top(arena->gray_stack);
			arena->gray_stack =
				qcgc_gray_stack_pop(arena->gray_stack);
			qcgc_pop_object(top);
			to_process--;
		}
	}

	if (qcgc_state.gray_stack_size == 0) {
		qcgc_state.phase = GC_COLLECT;
	}
}

void qcgc_pop_object(object_t *object) {
#if CHECKED
	assert(object != NULL);
	assert((object->flags & QCGC_GRAY_FLAG) == QCGC_GRAY_FLAG);
	assert(qcgc_arena_get_blocktype((cell_t *) object) == BLOCK_BLACK);
#endif
	object->flags &= ~QCGC_GRAY_FLAG;
	qcgc_trace_cb(object, &qcgc_push_object);
#if CHECKED
	assert(qcgc_get_mark_color(object) == MARK_COLOR_BLACK);
#endif
}

void qcgc_push_object(object_t *object) {
#if CHECKED
	size_t old_stack_size = qcgc_state.gray_stack_size;
	assert(qcgc_state.phase == GC_MARK);
#endif
	if (object != NULL) {
		if (qcgc_arena_get_blocktype((cell_t *) object) == BLOCK_WHITE) {
			object->flags |= QCGC_GRAY_FLAG;
			qcgc_arena_set_blocktype((cell_t *) object, BLOCK_BLACK);
			arena_t *arena = qcgc_arena_addr((cell_t *) object);
			arena->gray_stack = qcgc_gray_stack_push(arena->gray_stack, object);
		}
	}
#if CHECKED
	if (object != NULL) {
		if (old_stack_size == qcgc_state.gray_stack_size) {
			assert(qcgc_get_mark_color(object) == MARK_COLOR_BLACK ||
					qcgc_get_mark_color(object) == MARK_COLOR_DARK_GRAY);
		} else {
			assert(qcgc_state.gray_stack_size == old_stack_size + 1);
			assert(qcgc_get_mark_color(object) == MARK_COLOR_DARK_GRAY);
		}
	} else {
		assert(old_stack_size == qcgc_state.gray_stack_size);
	}
#endif
}

void qcgc_sweep(void) {
#if CHECKED
	assert(qcgc_state.phase == GC_COLLECT);
#endif
	struct {
		unsigned arena_count;
	} __attribute__ ((packed)) sweep_info;
	sweep_info.arena_count = qcgc_allocator_state.arenas->count;
	qcgc_event_logger_log(EVENT_SWEEP_START, sizeof(sweep_info),
			(uint8_t *) &sweep_info);

	for (size_t i = 0; i < qcgc_allocator_state.arenas->count; i++) {
		qcgc_arena_sweep(qcgc_allocator_state.arenas->items[i]);
	}
	qcgc_state.phase = GC_PAUSE;

	qcgc_event_logger_log(EVENT_SWEEP_DONE, 0, NULL);
}

void qcgc_collect(void) {
	qcgc_mark();
	qcgc_sweep();
}
