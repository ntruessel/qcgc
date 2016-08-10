#pragma once

#include "config.h"

#include <stddef.h>
#include <stdlib.h>

typedef struct bag_s {
	size_t size;
	size_t count;
	void *items[];
} bag_t;

bag_t *qcgc_bag_create(size_t size);

bag_t *qcgc_bag_add(bag_t *bag, void *item);
bag_t *qcgc_bag_remove(bag_t *bag, void *item);
bag_t *qcgc_bag_remove_index(bag_t *bag, size_t index);
