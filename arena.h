#pragma once

#include "config.h"
#include <stdint.h>

#define QCGC_ARENA_SIZE 1<<QCGC_ARENA_SIZE_EXP

#define QCGC_ARENA_ADDR(x) ((void *)(((intptr_t) x) & ~(QCGC_ARENA_SIZE - 1)))
#define QCGC_ARENA_BITMAP_SIZE 1<<(QCGC_ARENA_SIZE_EXP - 7) // 1 / 128
#define QCGC_ARENA_CELLS_COUNT (1<<(QCGC_ARENA_SIZE_EXP - 4) - 1<<(QCGC_ARENA_SIZE_EXP - 10))

#define QCGC_ARENA_CELL_INDEX(x) ((void *)(((intptr_t)(x)) & (QCGC_ARENA_SIZE - 1)))

// Currently no need to pack this
typedef struct arena_s {
	uint8_t block_bitmap[QCGC_ARENA_BITMAP_SIZE];
	uint8_t mark_bitmap[QCGC_ARENA_BITMAP_SIZE];
	uint16_t cells[QCGC_ARENA_CELLS_COUNT];
} arena_t;

/**
 * Create a new arena
 */
arena_t *qcgc_arena_create(void);
