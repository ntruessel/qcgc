#include "qcgc.h"

#include <stdlib.h>
#include <stdio.h>

void *qcgc_allocate(size_t bytes) {
	printf("Allocating %lu bytes\n", bytes);
	return malloc(bytes);
}

void qcgc_collect(void) {
	return;
}
