/**
 * @file	qcgc.h
 */

#pragma once

#include "config.h"

#include <stdint.h>
#include <sys/types.h>

#include "object.h"
#include "arena.h"
#include "gray_stack.h"

#define qcgc_shadowstack_push(p) (*(qcgc_state.shadow_stack++) = (object_t *)(p))
#define qcgc_shadowstack_pop(p) ((p) = *(--qcgc_state.shadow_stack))

/**
 * @typedef gc_state_t
 * Garbage collection states.
 * - GC_PAUSE	No gc in progress
 * - GC_MARK	Currently marking
 * - GC_COLLECT	Currently collecting
 */
typedef enum gc_state {
	GC_PAUSE,
	GC_MARK,
	GC_COLLECT,
} gc_state_t;

/**
 * @var qcgc_state
 *
 * Global state of the garbage collector
 */
struct qcgc_state {
	object_t **shadow_stack;
	object_t **shadow_stack_base;
	arena_t **arenas;
	size_t arena_index;
	size_t current_cell_index;
	size_t gray_stack_size;
	gc_state_t state;
} qcgc_state;

/**
 * Initialize the garbage collector.
 */
void qcgc_initialize(void);

/**
 * Destroy the garbage collector.
 */
void qcgc_destroy(void);

/**
 * Write barrier.
 *
 * @param	object	Object to write to
 */
void qcgc_write(object_t *object);

/**
 * Allocate new memory region
 *
 * @param	size	Desired size of the memory region
 * @return	Pointer to memory large enough to hold size bytes, NULL in case of
 *			errors
 */
object_t *qcgc_allocate(size_t size);

/**
 * Run garbage collection.
 */
void qcgc_collect(void);

/**
 * Tracing function.
 *
 * This function traces an object, i.e. calls visit on every object referenced
 * by the given object. Has to be provided by the library user.
 *
 * @param	object	The object to trace
 * @param	visit	The function to be called on the referenced objects
 */
extern void qcgc_trace_cb(object_t *object, void (*visit)(object_t *object));
