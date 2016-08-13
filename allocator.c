#include "allocator.h"

#include <assert.h>
#include <string.h>

QCGC_STATIC void bump_allocator_assign(cell_t *ptr, size_t cells);
QCGC_STATIC cell_t *bump_allocator_allocate(size_t cells);
QCGC_STATIC void bump_allocator_advance(size_t cells);
QCGC_STATIC size_t bytes_to_cells(size_t bytes);

void qcgc_allocator_initialize(void) {
	qcgc_allocator_state.arenas =
		qcgc_arena_bag_create(QCGC_ARENA_BAG_INIT_SIZE);

	// Bump Allocator
	qcgc_allocator_state.bump_state.bump_ptr = NULL;
	qcgc_allocator_state.bump_state.remaining_cells = 0;

	// Fit Allocator
	size_t index = 0;
	while (index < QCGC_LINEAR_FREE_LISTS) {
		qcgc_allocator_state.fit_state.free_lists[index] =
			qcgc_simple_free_list_create(QCGC_FREE_LIST_INIT_SIZE);
		index++;
	}

	while (index <= QCGC_LINEAR_FREE_LISTS + QCGC_EXP_FREE_LISTS) {
		qcgc_allocator_state.fit_state.free_lists[index] =
			qcgc_free_list_create(QCGC_FREE_LIST_INIT_SIZE);
		index++;
	}
}

void qcgc_allocator_destroy(void) {
	// Fit Allocator
	for (size_t i = 0; i <= QCGC_LINEAR_FREE_LISTS + QCGC_EXP_FREE_LISTS; i++) {
		free(qcgc_allocator_state.fit_state.free_lists[i]);
	}

	// Arenas
	size_t arena_count = qcgc_allocator_state.arenas->count;
	for (size_t i = 0; i < arena_count; i++) {
		qcgc_arena_destroy(qcgc_allocator_state.arenas->items[i]);
	}

	free(qcgc_allocator_state.arenas);
}

cell_t *qcgc_allocator_allocate(size_t bytes) {
	size_t size_in_cells = bytes_to_cells(bytes);
	cell_t *result;

	// TODO: Implement switch for bump/fit allocator
	if (true) {
		result = bump_allocator_allocate(size_in_cells);
	} else {
		result = NULL;
	}

	qcgc_arena_mark_allocated(result, size_in_cells);
#if QCGC_INIT_ZERO
	memset(result, 0, bytes);
#endif
	return result;
}

QCGC_STATIC void bump_allocator_assign(cell_t *ptr, size_t cells) {
	qcgc_allocator_state.bump_state.bump_ptr = ptr;
	qcgc_allocator_state.bump_state.remaining_cells = cells;
}

QCGC_STATIC void bump_allocator_advance(size_t cells) {
	qcgc_allocator_state.bump_state.bump_ptr += cells;
	qcgc_allocator_state.bump_state.remaining_cells -= cells;
}

QCGC_STATIC cell_t *bump_allocator_allocate(size_t cells) {
#if CHECKED
	assert(cells <= QCGC_ARENA_CELLS_COUNT - QCGC_ARENA_FIRST_CELL_INDEX);
#endif
	if (cells > qcgc_allocator_state.bump_state.remaining_cells) {
		// Grab a new arena
		arena_t *arena = qcgc_arena_create();
		bump_allocator_assign(&(arena->cells[QCGC_ARENA_FIRST_CELL_INDEX]),
				QCGC_ARENA_CELLS_COUNT - QCGC_ARENA_FIRST_CELL_INDEX);
		qcgc_allocator_state.arenas =
			qcgc_arena_bag_add(qcgc_allocator_state.arenas, arena);
	}
	cell_t *result = qcgc_allocator_state.bump_state.bump_ptr;
	bump_allocator_advance(cells);
	return result;
}

QCGC_STATIC size_t bytes_to_cells(size_t bytes) {
	return (bytes + sizeof(cell_t) - 1) / sizeof(cell_t);
}
