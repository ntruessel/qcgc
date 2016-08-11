#pragma once

#include "config.h"

#include "arena.h"
#include "generic_bag.h"

struct free_list_item_s {
	cell_t *ptr;
	size_t size;
};

DECLARE_BAG(simple_free_list, cell_t *);
DECLARE_BAG(free_list, struct free_list_item_s);
