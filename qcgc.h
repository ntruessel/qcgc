#pragma once

#include "config.h"

#include <stdint.h>
#include <sys/types.h>

#include "qcgc.h"
#include "arena.h"

#define qcgc_shadowstack_push(p) (*(qcgc_state.shadow_stack++) = (void *)(p))
#define qcgc_shadowstack_pop(p) ((p) = *(--qcgc_state.shadow_stack))

typedef struct object_s {
	uint32_t flags;
} object_t;

struct qcgc_state {
	object_t **shadow_stack;
	object_t **shadow_stack_base;
	arena_t **arenas;
	size_t arena_index;
	size_t current_cell_index;
} qcgc_state;

void qcgc_initialize(void);
void qcgc_destroy(void);

object_t *qcgc_allocate(size_t bytes);
void qcgc_collect(void);

extern void qcgc_trace_cb(object_t *object, void (*visit)(object_t *object));
