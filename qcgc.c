#include "qcgc.h"

#include <stdlib.h>
#include <stdio.h>

void qcgc_initialize(void) {
	qcgc_state.shadow_stack = qcgc_state.shadow_stack_base =
		(void **) malloc(SHADOW_STACK_SIZE);
}

void qcgc_destroy(void) {
	free(qcgc_state.shadow_stack_base);
}

void *qcgc_allocate(size_t bytes) {
	printf("Allocating %lu bytes\n", bytes);
	return malloc(bytes);
}

void qcgc_collect(void) {
	return;
}
