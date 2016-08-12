#pragma once

#include <stddef.h>

#include "arena.h"
#include "bag.h"
#include "object.h"

/**
 * @typedef gc_state_t
 * Garbage collection states.
 * - GC_PAUSE	No gc in progress
 * - GC_MARK	Currently marking
 * - GC_COLLECT	Currently collecting
 */
typedef enum gc_phase {
	GC_PAUSE,
	GC_MARK,
	GC_COLLECT,
} gc_phase_t;

/**
 * @var qcgc_state
 *
 * Global state of the garbage collector
 */
struct qcgc_state {
	object_t **shadow_stack;
	object_t **shadow_stack_base;
	arena_bag_t *arenas;
	size_t gray_stack_size;
	gc_phase_t phase;
} qcgc_state;

