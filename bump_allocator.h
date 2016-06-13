#pragma once

#include "config.h"

#include <stdbool.h>

#include "arena.h"

struct qcgc_balloc_state {
	cell_t *bump_ptr;
	size_t remaining_cells;
} qcgc_balloc_state;

void qcgc_balloc_assign(cell_t *bump_ptr, size_t cells);
void *qcgc_balloc_allocate(size_t cells);
bool qcgc_balloc_can_allocate(size_t cells);
size_t qcgc_balloc_remaining_cells(void);
