#pragma once

#include <sys/types.h>

void *qcgc_allocate(size_t bytes);
void qcgc_collect(void);
