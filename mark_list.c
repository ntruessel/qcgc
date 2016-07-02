#include "mark_list.h"

mark_list_t *qcgc_mark_list_create(size_t initial_size) {
}

void qcgc_mark_list_destroy(mark_list_t *list) {
}

mark_list_t *qcgc_mark_list_push(mark_list_t *list, object_t *object) {
}

mark_list_t *qcgc_mark_list_push_all(mark_list_t *list,
		object_t **objects, size_t count) {
}

object_t **qcgc_mark_list_get_head_segment(mark_list_t *list) {
}

mark_list_t *qcgc_mark_list_drop_head_segment(mark_list_t *list) {
}
