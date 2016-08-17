#include <qcgc.h>

#include <assert.h>

typedef struct node_s node_t;

struct node_s {
	object_t hdr;
	int value;
	node_t *next;
};

void qcgc_trace_cb(object_t *object, void (*visit)(object_t *object)) {
	node_t *node = (node_t *) object;
	visit((object_t *) node->next);
}

int main(void) {
	qcgc_initialize();
	node_t *list = (node_t *) qcgc_allocate(sizeof(node_t));
	list->value = 0;
	list->next = NULL;

	qcgc_shadowstack_push(list);
	node_t *last = list;
	for (size_t i = 1; i < 1<<22; i++) { // 4+ arenas of memory
		last->next = (node_t *) qcgc_allocate(sizeof(node_t));
		last = last->next;
		last->value = i;
		last->next = NULL;
	}

	// Check structure
	last = list;
	size_t i = 0;
	while(last != NULL) {
		assert(last->value == i);
		i++;
		last = last->next;
	}

	// Remove part of the list (by making it unreachable)
	last = list;
	for (size_t i = 0; i < 10000; i++) {
		last = last->next;
	}
	last->next = NULL;

	// Force collection
	qcgc_collect();

	qcgc_destroy();

	return 0;
}
