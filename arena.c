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
	if (mem != QCGC_ARENA_ADDR(mem)) {
		// align
		void *aligned_mem = (void *)(
				(intptr_t) QCGC_ARENA_ADDR(mem) + QCGC_ARENA_SIZE);
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
	result->mark_bitmap[0] = 0xf0;
	return result;
}

blocktype_t qcgc_arena_blocktype(void *ptr) {
	size_t index = QCGC_ARENA_CELL_INDEX(ptr);
	arena_t *arena = QCGC_ARENA_ADDR(ptr);
	uint8_t block_bit = QCGC_ARENA_BITMAP_ENTRY(arena->block_bitmap, index);
	uint8_t mark_bit = QCGC_ARENA_BITMAP_ENTRY(arena->mark_bitmap, index);

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
