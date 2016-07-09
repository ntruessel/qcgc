#pragma once


#include "config.h"
#include <stdint.h>

#define QCGC_GRAY_FLAG 0x01

typedef struct object_s {
	uint32_t flags;
} object_t;

/**
 * Write barrier.
 *
 * @param	object	Object to write to
 */
void qcgc_write(object_t *object);
