#pragma once

#include "config.h"
#include <stdbool.h>
#include <stdint.h>
#include <sys/types.h>

typedef union arena_u arena_t;

#define QCGC_ARENA_SIZE (1<<QCGC_ARENA_SIZE_EXP)

#define QCGC_ARENA_BITMAP_SIZE (1<<(QCGC_ARENA_SIZE_EXP - 7)) // 1 / 128
#define QCGC_ARENA_CELLS_COUNT (1<<(QCGC_ARENA_SIZE_EXP - 4))

typedef uint8_t cell_t[16];

union arena_u {
	struct {
		uint8_t block_bitmap[QCGC_ARENA_BITMAP_SIZE];
		uint8_t mark_bitmap[QCGC_ARENA_BITMAP_SIZE];
	};
	cell_t cells[QCGC_ARENA_CELLS_COUNT];
};

typedef enum blocktype {
	BLOCK_EXTENT,
	BLOCK_FREE,
	BLOCK_WHITE,
	BLOCK_BLACK,
} blocktype_t;

/**
 * Create a new arena
 */
arena_t *qcgc_arena_create(void);

/* Utility functions */

arena_t *qcgc_arena_addr(void *ptr);
size_t qcgc_arena_cell_index(void *ptr);

bool qcgc_arena_get_bitmap_entry(uint8_t *bitmap, size_t index);
void qcgc_arena_set_bitmap_entry(uint8_t *bitmap, size_t index, bool value);

/**
 * Get blocktype, no validation of ptr
 */
blocktype_t qcgc_arena_blocktype(void *ptr);
