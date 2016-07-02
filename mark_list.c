#include "mark_list.h"

#include <stdlib.h>
#include <string.h>

static mark_list_t *qcgc_mark_list_grow(mark_list_t *list);

mark_list_t *qcgc_mark_list_create(size_t initial_size) {
	size_t length = initial_size / QCGC_MARK_LIST_SEGMENT_SIZE;
	length += (size_t) length == 0;
	mark_list_t *result = (mark_list_t *)
		malloc(sizeof(mark_list_t) + length * sizeof(object_t **));
	result->head = 0;
	result->tail = 0;
	result->length = length;
	result->insert_index = 0;
	result->segments[result->head] = (object_t **)
		calloc(QCGC_MARK_LIST_SEGMENT_SIZE, sizeof(object_t **));
	return result;
}

void qcgc_mark_list_destroy(mark_list_t *list) {
	size_t i = list->head;
	do {
		free(list->segments[i]);
		i = i + 1 % list->length;
	} while (i != list->tail);
	free(list);
}

mark_list_t *qcgc_mark_list_push(mark_list_t *list, object_t *object) {
	if (list->insert_index >= QCGC_MARK_LIST_SEGMENT_SIZE) {
		if (list->tail + 1 % list->length == list->head) {
			list = qcgc_mark_list_grow(list);
		}
		list->insert_index = 0;
		list->tail++;
		list->segments[list->tail] = (object_t **)
			calloc(QCGC_MARK_LIST_SEGMENT_SIZE, sizeof(object_t *));
	}
	list->segments[list->tail][list->insert_index] = object;
	list->insert_index++;
	return list;
}

mark_list_t *qcgc_mark_list_push_all(mark_list_t *list,
		object_t **objects, size_t count) {
	// FIXME: Optimize or remove
	for (size_t i = 0; i < count; i++) {
		list = qcgc_mark_list_push(list, objects[i]);
	}
	return list;
}

object_t **qcgc_mark_list_get_head_segment(mark_list_t *list) {
	return list->segments[list->head];
}

mark_list_t *qcgc_mark_list_drop_head_segment(mark_list_t *list) {
	free(list->segments[list->head]);
	list->segments[list->head] = NULL;
	list->head++;
	return list;
}

static mark_list_t *qcgc_mark_list_grow(mark_list_t *list) {
	mark_list_t *new_list = (mark_list_t *) realloc(list,
			sizeof(mark_list_t) + 2 * list->length * sizeof(object_t **));
	if (list->tail < list->head) {
		memcpy(new_list->segments + new_list->length,
				list->segments, list->tail * sizeof(object_t **));
		new_list->tail = list->length + list->tail;
	}
	new_list->length = 2 * list->length;
	return new_list;
}
