#include "bag.h"

#include <assert.h>

#define BAG_MIN_SIZE 64

static size_t bag_size(size_t size);
static bag_t *bag_grow(bag_t *bag);
static bag_t *bag_shrink(bag_t *bag);
static void bag_check_invariant(bag_t *bag);

bag_t *qcgc_bag_create(size_t size) {
	bag_t *result = (bag_t *) malloc(bag_size(size));
	result->size = size;
	result->count = 0;
#if CHECKED
	bag_check_invariant(result);
#endif
	return result;
}

bag_t *qcgc_bag_add(bag_t *bag, void *item) {
#if CHECKED
	assert(bag != NULL);
	size_t old_count = bag->count;
	bag_check_invariant(bag);
#endif
	if (bag->count >= bag->size) {
		bag = bag_grow(bag);
	}
	bag->items[bag->count++] = item;
#if CHECKED
	assert(bag->items[bag->count - 1] == item);
	assert(old_count + 1 == bag->count);
	bag_check_invariant(bag);
#endif
	return bag;
}

bag_t *qcgc_bag_remove(bag_t *bag, void *item) {
#if CHECKED
	assert(bag != NULL);
	size_t old_count = bag->count;
	bag_check_invariant(bag);
#endif
	for (size_t i = 0; i < bag->count; i++) {
		if (bag->items[i] == item) {
			bag = qcgc_bag_remove_index(bag, i);
			break;
		}
	}
#if CHECKED
	if (old_count == bag->count) {
		for (size_t i = 0; i < bag->count; i++) {
			assert(bag->items[i] != item);
		}
	} else {
		assert(old_count = bag->count + 1);
	}
	bag_check_invariant(bag);
#endif
	return bag;
}

bag_t *qcgc_bag_remove_index(bag_t *bag, size_t index) {
#if CHECKED
	assert(bag != NULL);
	assert(index < bag->count);		// implies bag->count > 0
	size_t old_count = bag->count;
	bag_check_invariant(bag);
#endif
	if (index < bag->count - 1) {	// bag->count - 1 can't undeflow
		// Fill gap caused by removing item index with last element
		bag->items[index] = bag->items[bag->count - 1];
	}
	bag->count--;

	if (bag->count < bag->size / 4) {
		bag = bag_shrink(bag);
	}
#if CHECKED
	assert(bag->count + 1 == old_count);
	bag_check_invariant(bag);
#endif
	return bag;
}

static size_t bag_size(size_t size) {
	return sizeof(bag_t) + size * sizeof(void *);
}

static bag_t *bag_grow(bag_t *bag) {
#if CHECKED
	assert(bag != NULL);
	size_t old_size = bag->size;
	size_t old_count = bag->count;
	bag_check_invariant(bag);
#endif
	bag_t *new_bag = (bag_t *) realloc(bag, bag_size(2 * bag->size));
	assert(new_bag != NULL);
	bag = new_bag;
	bag->size *= 2;
#if CHECKED
	assert(bag != NULL);
	assert(bag->count == old_count);
	assert(bag->size = 2 * old_size);
	bag_check_invariant(bag);
#endif
	return bag;
}

static bag_t *bag_shrink(bag_t *bag) {
#if CHECKED
	assert(bag != NULL);
	assert(bag->count <= bag->size / 2);
	size_t old_size = bag->size;
	size_t old_count = bag->count;
	bag_check_invariant(bag);
#endif
	bag_t *new_bag = (bag_t *) realloc(bag, bag_size(bag->size / 2));
	assert(new_bag != NULL);
	bag = new_bag;
	bag->size /= 2;
#if CHECKED
	assert(bag->size == old_size / 2);
	assert(bag->count == old_count);
	bag_check_invariant(bag);
#endif
	return bag;
}

static void bag_check_invariant(bag_t *bag) {
	assert(bag->count <= bag->size);
}
