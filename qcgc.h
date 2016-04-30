#pragma once

#include <sys/types.h>

#define SHADOW_STACK_SIZE 4096

#define qcgc_shadowstack_push(p) (*(qcgc_state.shadow_stack++) = (void *)(p))
#define qcgc_shadowstack_pop(p) ((p) = *(--qcgc_state.shadow_stack))

struct qcgc_state {
	void **shadow_stack;
	void **shadow_stack_base;
} qcgc_state;

void qcgc_initialize(void);
void qcgc_destroy(void);

void *qcgc_allocate(size_t bytes);
void qcgc_collect(void);
