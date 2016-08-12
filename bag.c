#include "bag.h"

DEFINE_BAG(arena_bag, arena_t *);
DEFINE_BAG(simple_free_list, cell_t *);
DEFINE_BAG(free_list, struct free_list_item_s);
