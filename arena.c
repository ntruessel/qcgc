#include "arena.h"

#include <sys/mman.h>
#include <unistd.h>

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
	size_t first_cell_index = qcgc_arena_cell_index((void *)((intptr_t) result) + 2 * QCGC_ARENA_BITMAP_SIZE);
	qcgc_arena_set_bitmap_entry(result->mark_bitmap, first_cell_index, true);
	return result;
}

arena_t *qcgc_arena_addr(void *ptr) {
	return (arena_t *)((intptr_t) ptr & ~(QCGC_ARENA_SIZE - 1));
}

size_t qcgc_arena_cell_index(void *ptr) {
	return (size_t)((intptr_t) ptr & (QCGC_ARENA_SIZE - 1));
}

bool qcgc_arena_get_bitmap_entry(uint8_t *bitmap, size_t index) {
	return (bitmap[index / 8] >> (index % 8) == 0x01);
}

void qcgc_arena_set_bitmap_entry(uint8_t *bitmap, size_t index, bool value) {
	if (value) {
		bitmap[index / 8] |= value << (index % 8);
	} else {
		bitmap[index / 8] &= ~(value << (index % 8));
	}
}

blocktype_t qcgc_arena_blocktype(void *ptr) {
	size_t index = qcgc_arena_cell_index(ptr);
	arena_t *arena = qcgc_arena_addr(ptr);
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
