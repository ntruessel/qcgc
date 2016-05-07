#pragma once

#include "config.h"

#include <stdint.h>
#include <sys/types.h>

#define qcgc_shadowstack_push(p) (*(qcgc_state.shadow_stack++) = (void *)(p))
#define qcgc_shadowstack_pop(p) ((p) = *(--qcgc_state.shadow_stack))

typedef struct object_s {
	uint32_t flags;
} object_t;

struct qcgc_state {
	object_t **shadow_stack;
	object_t **shadow_stack_base;
} qcgc_state;

void qcgc_initialize(void);
void qcgc_destroy(void);

object_t *qcgc_allocate(size_t bytes);
void qcgc_collect(void);
