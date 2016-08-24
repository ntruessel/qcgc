#pragma once


#include "config.h"
#include <stdint.h>

#define QCGC_GRAY_FLAG (1<<0)
#define QCGC_PREBUILT_OBJECT (1<<1)
#define QCGC_HUGE_BLOCK (1<<2)

typedef struct object_s {
	uint32_t flags;
} object_t;
