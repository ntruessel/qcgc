#pragma once

#include "config.h"

#include "arena.h"

struct qcgc_salloc_state {
	void *free_lists[QCGC_LINEAR_FREE_LISTS + QCGC_EXP_FREE_LISTS + 1];
} qcgc_salloc_state;

void qcgc_salloc_initialize(void);
void qcgc_salloc_destroy(void);

void qcgc_salloc_assign(cell_t *base_ptr, size_t cells);
cell_t *qcgc_salloc_allocate(size_t cells);
