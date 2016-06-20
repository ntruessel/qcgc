#include "arena.h"

#include <sys/mman.h>
#include <unistd.h>

/**
 * Internal functions
 */
static blocktype_t get_blocktype(arena_t *arena, size_t index);
static void set_blocktype(arena_t *arena, size_t index, blocktype_t type);

arena_t *qcgc_arena_create(void) {
	arena_t *result;
	// Linux: MAP_ANONYMOUS is initialized to zero
	void *mem = mmap(0, 2 * QCGC_ARENA_SIZE,
			PROT_READ | PROT_WRITE,
			MAP_ANONYMOUS | MAP_PRIVATE, -1, 0);
	if (mem == MAP_FAILED) {
		// ERROR: OUT OF MEMORY
		return NULL;
	}
	if (mem != qcgc_arena_addr(mem)) {
		// align
		void *aligned_mem = (void *)(
				(intptr_t) qcgc_arena_addr(mem) + QCGC_ARENA_SIZE);
		size_t size_before = (size_t)((intptr_t) aligned_mem - (intptr_t) mem);
		size_t size_after = QCGC_ARENA_SIZE - size_before;

		munmap(mem, size_before);
		munmap((void *)((intptr_t) aligned_mem + QCGC_ARENA_SIZE), size_after);
		result = (arena_t *) aligned_mem;
	} else {
		// free second half
		munmap((void *)((intptr_t) mem + QCGC_ARENA_SIZE), QCGC_ARENA_SIZE);
		result = (arena_t *) mem;
	}

	// Init bitmaps: One large free block
	qcgc_arena_set_bitmap_entry(result->mark_bitmap, QCGC_ARENA_FIRST_CELL_INDEX, true);
	return result;
}

void qcgc_arena_destroy(arena_t *arena) {
	munmap((void *) arena, QCGC_ARENA_SIZE);
}

arena_t *qcgc_arena_addr(void *ptr) {
	return (arena_t *)((intptr_t) ptr & ~(QCGC_ARENA_SIZE - 1));
}

size_t qcgc_arena_cell_index(void *ptr) {
	return (size_t)((intptr_t) ptr & (QCGC_ARENA_SIZE - 1)) >> 4;
}

bool qcgc_arena_get_bitmap_entry(uint8_t *bitmap, size_t index) {
	return (((bitmap[index / 8] >> (index % 8)) & 0x1) == 0x01);
}

void qcgc_arena_set_bitmap_entry(uint8_t *bitmap, size_t index, bool value) {
	if (value) {
		bitmap[index / 8] |= 1<<(index % 8);
	} else {
		bitmap[index / 8] &= ~(1<<(index % 8));
	}
}

static blocktype_t get_blocktype(arena_t *arena, size_t index) {
	uint8_t block_bit = qcgc_arena_get_bitmap_entry(arena->block_bitmap, index);
	uint8_t mark_bit = qcgc_arena_get_bitmap_entry(arena->mark_bitmap, index);

	if (block_bit) {
		if (mark_bit) {
			return BLOCK_BLACK;
		} else {
			return BLOCK_WHITE;
		}
	} else {
		if (mark_bit) {
			return BLOCK_FREE;
		} else {
			return BLOCK_EXTENT;
		}
	}
}

blocktype_t qcgc_arena_get_blocktype(void *ptr) {
	size_t index = qcgc_arena_cell_index(ptr);
	arena_t *arena = qcgc_arena_addr(ptr);

	return get_blocktype(arena, index);
}

static void set_blocktype(arena_t *arena, size_t index, blocktype_t type) {
	switch(type) {
		case BLOCK_EXTENT:
			qcgc_arena_set_bitmap_entry(arena->block_bitmap, index, false);
			qcgc_arena_set_bitmap_entry(arena->mark_bitmap, index, false);
			break;
		case BLOCK_FREE:
			qcgc_arena_set_bitmap_entry(arena->block_bitmap, index, false);
			qcgc_arena_set_bitmap_entry(arena->mark_bitmap, index, true);
			break;
		case BLOCK_WHITE:
			qcgc_arena_set_bitmap_entry(arena->block_bitmap, index, true);
			qcgc_arena_set_bitmap_entry(arena->mark_bitmap, index, false);
			break;
		case BLOCK_BLACK:
			qcgc_arena_set_bitmap_entry(arena->mark_bitmap, index, true);
			qcgc_arena_set_bitmap_entry(arena->block_bitmap, index, true);
			break;
	}
}

void qcgc_arena_set_blocktype(void *ptr, blocktype_t type) {
	size_t index = qcgc_arena_cell_index(ptr);
	arena_t *arena = qcgc_arena_addr(ptr);
	set_blocktype(arena, index, type);
}

void qcgc_arena_mark_allocated(void *ptr, size_t cells) {
	size_t index = qcgc_arena_cell_index(ptr);
	arena_t *arena = qcgc_arena_addr(ptr);
	set_blocktype(arena, index, BLOCK_WHITE);
	size_t index_of_next_block = index + cells;
	if (index_of_next_block < QCGC_ARENA_CELLS_COUNT &&
			get_blocktype(arena, index_of_next_block) == BLOCK_EXTENT) {
		set_blocktype(arena, index_of_next_block, BLOCK_FREE);
	}
}

void qcgc_arena_mark_free(void *ptr) {
	qcgc_arena_set_blocktype(ptr, BLOCK_FREE);
	// No coalescing, collector will do this
}

bool qcgc_arena_sweep(arena_t *arena) {
	bool free = true;
	bool coalesce = false;
	for (size_t cell = QCGC_ARENA_FIRST_CELL_INDEX;
			cell < QCGC_ARENA_CELLS_COUNT;
			cell++) {
		switch (qcgc_arena_get_blocktype((void *) &arena->cells[cell])) {
			case BLOCK_EXTENT:
				break;
			case BLOCK_FREE:
				coalesce = true;
				break;
			case BLOCK_WHITE:
				if (coalesce) {
					set_blocktype(arena, cell, BLOCK_EXTENT);
				} else {
					set_blocktype(arena, cell, BLOCK_FREE);
				}
				coalesce = true;
				break;
			case BLOCK_BLACK:
				free = false;
				coalesce = false;
				set_blocktype(arena, cell, BLOCK_WHITE);
				break;
		}
	}
	return free;
}
