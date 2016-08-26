#include "hugeblocktable.h"

#include <assert.h>

QCGC_STATIC size_t bucket(object_t *object);

void qcgc_hbtable_initialize(void) {
	qcgc_hbtable.mark_flag_ref = false;
	qcgc_hbtable.gray_stack = qcgc_gray_stack_create(4);
	for (size_t i = 0; i < QCGC_HBTABLE_BUCKETS; i++) {
		qcgc_hbtable.bucket[i] = qcgc_hbbucket_create(4);
	}
}

void qcgc_hbtable_destroy(void) {
	free(qcgc_hbtable.gray_stack);
	for (size_t i = 0; i < QCGC_HBTABLE_BUCKETS; i++) {
		free(qcgc_hbtable.bucket[i]);
	}
}

void qcgc_hbtable_insert(object_t *object) {
	size_t i = bucket(object);
	qcgc_hbtable.bucket[i] = qcgc_hbbucket_add(qcgc_hbtable.bucket[i],
			(struct hbtable_entry_s) {
				.object = object,
				.mark_flag = !qcgc_hbtable.mark_flag_ref});
}

void qcgc_hbtable_mark(object_t *object) {
	hbbucket_t *b = qcgc_hbtable.bucket[bucket(object)];
	size_t count = b->count;
	for (size_t i = 0; i < count; i++) {
		if (b->items[i].object == object) {
			if (b->items[i].mark_flag != qcgc_hbtable.mark_flag_ref) {
				b->items[i].mark_flag = qcgc_hbtable.mark_flag_ref;
				qcgc_gray_stack_push(qcgc_hbtable.gray_stack, object);
			}
			return;
		}
	}
#if CHECKED
	assert(false);
#endif
}

void qcgc_hbtable_sweep(void) {
#if CHECKED
	assert(qcgc_hbtable.gray_stack->index == 0);
#endif
	for (size_t i = 0; i < QCGC_HBTABLE_BUCKETS; i++) {
		hbbucket_t *b = qcgc_hbtable.bucket[i];
		size_t j = 0;
		while(j < b->count) {
			if (b->items[j].mark_flag != qcgc_hbtable.mark_flag_ref) {
				// White object
				// FIXME: Leaks object (currently not clear how it will
				// be allocated)
				b = qcgc_hbbucket_remove_index(b, j);
			} else {
				// Black object
				j++;
			}
		}
		qcgc_hbtable.bucket[i] = b;
	}
	qcgc_hbtable.mark_flag_ref = !qcgc_hbtable.mark_flag_ref;
}

QCGC_STATIC size_t bucket(object_t *object) {
	return ((uintptr_t) object >> (QCGC_ARENA_SIZE_EXP)) % QCGC_HBTABLE_BUCKETS;
}
