#pragma once

#include "config.h"
#include <stdint.h>
#include <sys/types.h>

typedef union arena_u arena_t;

#define QCGC_ARENA_SIZE (1<<QCGC_ARENA_SIZE_EXP)

#define QCGC_ARENA_ADDR(x) ((arena_t *)(((intptr_t) x) & ~(QCGC_ARENA_SIZE - 1)))
#define QCGC_ARENA_BITMAP_SIZE (1<<(QCGC_ARENA_SIZE_EXP - 7)) // 1 / 128
#define QCGC_ARENA_CELLS_COUNT (1<<(QCGC_ARENA_SIZE_EXP - 4))

#define QCGC_ARENA_CELL_INDEX(x) ((size_t)(((intptr_t)(x)) & (QCGC_ARENA_SIZE - 1)))

typedef uint8_t cell_t[16];

union arena_u {
	struct {
		uint8_t block_bitmap[QCGC_ARENA_BITMAP_SIZE];
		uint8_t mark_bitmap[QCGC_ARENA_BITMAP_SIZE];
	};
	cell_t cells[QCGC_ARENA_CELLS_COUNT];
};

/**
 * Create a new arena
 */
arena_t *qcgc_arena_create(void);
