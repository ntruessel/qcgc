#include "segregated_allocator.h"

#include <assert.h>
#include "bag.h"

QCGC_STATIC size_t free_list_index(size_t cells);
QCGC_STATIC cell_t *simple_free_list_allocate(simple_free_list_t *l, size_t cells);
QCGC_STATIC cell_t *free_list_allocate(free_list_t *l, size_t cells);
QCGC_STATIC void salloc_add(cell_t *ptr, size_t cells);

void qcgc_salloc_initialize(void) {
	size_t i = 0;
	while (i < QCGC_LINEAR_FREE_LISTS) {
		qcgc_salloc_state.free_lists[i] = qcgc_simple_free_list_create(16);
		i++;
	}

	while (i <= QCGC_LINEAR_FREE_LISTS + QCGC_EXP_FREE_LISTS) {
		qcgc_salloc_state.free_lists[i] = qcgc_free_list_create(16);
		i++;
	}
}

void qcgc_salloc_destroy(void) {
	for (size_t i = 0; i <= QCGC_LINEAR_FREE_LISTS + QCGC_EXP_FREE_LISTS; i++) {
		free(qcgc_salloc_state.free_lists[i]);
	}
}

void qcgc_salloc_assign(cell_t *base_ptr, size_t cells) {
	// FIXME: Switch to lazy implementation
	cell_t *free_block_start = NULL;
	size_t free_block_size = 0;
	for (size_t i = 0; i < cells; i++) {
		switch (qcgc_arena_get_blocktype(base_ptr)) {
			case BLOCK_EXTENT:
				free_block_size++;
				break;
			case BLOCK_FREE:
				if (free_block_start != NULL) {
					salloc_add(free_block_start, free_block_size);
				}

				free_block_start = base_ptr;
				free_block_size = 0;
				break;
			case BLOCK_WHITE:	// fall through
			case BLOCK_BLACK:
				if (free_block_start != NULL) {
					salloc_add(free_block_start, free_block_size);
					free_block_start = NULL;
				}
				break;
		}
		base_ptr++;
	}
}

cell_t *qcgc_salloc_allocate(size_t cells) {
	size_t index = free_list_index(cells);
	size_t free_list_count =
		((free_list_t *) (qcgc_salloc_state.free_lists[index]))->count;

	if (free_list_count = 0) {
		// FIXME: Search for new free blocks (lazy implementation)
	}

	free_list_count =
		((free_list_t *) (qcgc_salloc_state.free_lists[index]))->count;

	if (free_list_count > 0) {
		// Best fit
		if (index < QCGC_LINEAR_FREE_LISTS) {
			// Already is best fit
			simple_free_list_t *free_list =
				(simple_free_list_t *) qcgc_salloc_state.free_lists[index];

			cell_t *result = free_list->items[free_list->count - 1];
			qcgc_salloc_state.free_lists[index] =
				qcgc_simple_free_list_remove_index(free_list,
						free_list->count - 1);
			qcgc_arena_mark_allocated(result, cells);
			return result;
		} else {
			// First fit approximates best fit
			// XXX: Switch to real best fit by searching?
			free_list_t *free_list =
				(free_list_t *) qcgc_salloc_state.free_lists[index];

			struct free_list_item_s item =
				free_list->items[free_list->count - 1];
			qcgc_salloc_state.free_lists[index] =
				qcgc_free_list_remove_index(free_list, free_list->count - 1);
			qcgc_arena_mark_allocated(item.ptr, cells);
			salloc_add(item.ptr + cells, item.size - cells);
			return item.ptr;
		}
	} else {
		// First fit
		while(index < QCGC_LINEAR_FREE_LISTS) {
			simple_free_list_t *free_list =
				(simple_free_list_t *) qcgc_salloc_state.free_lists[index];
			if (free_list->count > 0) {
				cell_t *result = free_list->items[free_list->count - 1];
				qcgc_salloc_state.free_lists[index] =
					qcgc_simple_free_list_remove_index(free_list,
							free_list->count - 1);
				qcgc_arena_mark_allocated(result, cells);
				salloc_add(result + cells, index + 1 - cells);
			}
			index++;
		}

		while(index < QCGC_LINEAR_FREE_LISTS + QCGC_EXP_FREE_LISTS) {
			free_list_t *free_list =
				(free_list_t *) qcgc_salloc_state.free_lists[index];
			if (free_list->count > 0) {
				struct free_list_item_s item =
					free_list->items[free_list->count - 1];
				qcgc_salloc_state.free_lists[index] =
					qcgc_free_list_remove_index(free_list, free_list->count - 1);
				qcgc_arena_mark_allocated(item.ptr, cells);
				salloc_add(item.ptr + cells, item.size - cells);
				return item.ptr;
			}
			index++;
		}
	}

	return NULL;
}

QCGC_STATIC size_t free_list_index(size_t cells) {
#if CHECKED
	assert(cells > 0);
#endif
	// Multiple of cell size
	if (cells <= QCGC_LINEAR_FREE_LISTS) {
		return cells - 1;
	}

	// Power of two of cell size
	size_t first_exp = 32 - __builtin_clz(QCGC_LINEAR_FREE_LISTS);
	for (size_t i = 0; i < QCGC_EXP_FREE_LISTS; i++) {
		if (cells <= 1<<(first_exp + i)) {
			return QCGC_LINEAR_FREE_LISTS + i;
		}
	}

	// Remaining blocks
	return QCGC_LINEAR_FREE_LISTS + QCGC_EXP_FREE_LISTS;
}

QCGC_STATIC void salloc_add(cell_t *ptr, size_t cells) {
	if (cells > 0) {
		size_t index = free_list_index(cells);
		if (index < QCGC_LINEAR_FREE_LISTS) {
			simple_free_list_t *free_list =
				(simple_free_list_t *) qcgc_salloc_state.free_lists[index];
			qcgc_salloc_state.free_lists[index] =
				qcgc_simple_free_list_add(free_list, ptr);
		} else {
			free_list_t *free_list =
				(free_list_t *) qcgc_salloc_state.free_lists[index];
			qcgc_salloc_state.free_lists[index] = qcgc_free_list_add(
					free_list, (struct free_list_item_s) {ptr, cells});
		}
	}
}
