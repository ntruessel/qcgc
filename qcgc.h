/**
 * @file	qcgc.h
 */

#ifndef __QCGC_H
#define __QCGC_H

#include "config.h"

#include <assert.h>
#include <stddef.h>
#include <stdint.h>

/*******************************************************************************
 * Types and global state                                                      *
 ******************************************************************************/

/**
 * Object Layout.
 */
typedef struct object_s {
	uint32_t flags;
} object_t;

#define QCGC_GRAY_FLAG (1<<0)
#define QCGC_PREBUILT_OBJECT (1<<1)
#define QCGC_PREBUILT_REGISTERED (1<<2)

/**
 * Shadow stack
 */
struct qcgc_shadowstack {
	object_t **top;
	object_t **base;
} _qcgc_shadowstack;

/**
 * The smallest unit of memory that can be addressed and allocated.
 */
typedef uint8_t cell_t[16];

/**
 * Bump allocator
 */
struct qcgc_bump_allocator {
	cell_t *ptr;
	size_t remaining_cells;
} _qcgc_bump_allocator;

/**
 * Object stack
 */
typedef struct object_stack_s {
	size_t count;
	size_t size;
	object_t *items[];
} object_stack_t;

/**
 * Arena
 */

#define QCGC_ARENA_SIZE (1<<QCGC_ARENA_SIZE_EXP)

#define QCGC_ARENA_BITMAP_SIZE (1<<(QCGC_ARENA_SIZE_EXP - 7)) // 1 / 128
#define QCGC_ARENA_CELLS_COUNT (1<<(QCGC_ARENA_SIZE_EXP - 4))

#define QCGC_ARENA_FIRST_CELL_INDEX (1<<(QCGC_ARENA_SIZE_EXP - 10))

typedef union {
	struct {
		union {
			object_stack_t *gray_stack;
			uint8_t block_bitmap[QCGC_ARENA_BITMAP_SIZE];
		};
		uint8_t mark_bitmap[QCGC_ARENA_BITMAP_SIZE];
	};
	cell_t cells[QCGC_ARENA_CELLS_COUNT];
} arena_t;

typedef enum blocktype {
	BLOCK_EXTENT,
	BLOCK_FREE,
	BLOCK_WHITE,
	BLOCK_BLACK,
} blocktype_t;

/*******************************************************************************
 * Internal functions                                                          *
 ******************************************************************************/

/**
 * Allocate large block. May trigger garbage collection.
 *
 * @param	size	Object size in bytes
 * @return	Pointer to memory region large enough to hold size bytes or NULL in
 *			case of errros
 */
object_t *_qcgc_allocate_large(size_t size);

/**
 * Allocator slowpath. May trigger garabge collection.
 *
 * @param	size	Object size in bytes
 * @return	Pointer to memory region large enough to hold size bytes or NULL in
 *			case of errros
 */
object_t *_qcgc_allocate_slowpath(size_t size);

/**
 * Turns bytes to cells.
 */
QCGC_STATIC QCGC_INLINE size_t bytes_to_cells(size_t bytes) {
	return (bytes + sizeof(cell_t) - 1) / sizeof(cell_t);
}

/*******************************************************************************
 * Public functions                                                            *
 ******************************************************************************/

/**
 * Initialize the garbage collector.
 */
void qcgc_initialize(void);

/**
 * Destroy the garbage collector.
 */
void qcgc_destroy(void);

/**
 * Allocate a new object. May trigger garabge collection.
 *
 * @param	size	Object size in bytes
 * @return	Pointer to memory region large enough to hold size bytes or NULL in
 *			case of errros
 */
QCGC_STATIC QCGC_INLINE object_t *qcgc_allocate(size_t size) {
	// FIXME: Create a fastpath
	if (UNLIKELY(size >= 1<<QCGC_LARGE_ALLOC_THRESHOLD_EXP)) {
		return _qcgc_allocate_large(size);
	}
	return _qcgc_allocate_slowpath(size);
}

/**
 * Push root object.
 *
 * @param	object	The root object
 */
QCGC_STATIC QCGC_INLINE void qcgc_push_root(object_t *object) {
	*_qcgc_shadowstack.top = object;
	_qcgc_shadowstack.top++;
}

/**
 * Pop root objects.
 *
 * @param	count	Number of object to pop
 */
QCGC_STATIC QCGC_INLINE void qcgc_pop_root(size_t count) {
	_qcgc_shadowstack.top -= count;
	assert(_qcgc_shadowstack.base <= _qcgc_shadowstack.top);
}

/**
 * Write barrier. Has to be called whenever a reference to another object is
 * updated.
 *
 * @param	object	Object that is updated
 */
void qcgc_write(object_t *object);

/**
 * Run garbage collection.
 */
void qcgc_collect(void);

/**
 * Weakref registration.
 *
 * @param	weakrefobj	Pointer to the weakref itself
 * @param	target		Doublepointer to referenced object.
 *						The referenced object must be a valid object.
 */
void qcgc_register_weakref(object_t *weakrefobj, object_t **target);

/**
 * Tracing function.
 *
 * This used provided function has to call visit on every object the given
 * argument references.
 *
 * @param	object	The object to trace
 * @param	visit	The function to be called on the referenced objects
 */
extern void qcgc_trace_cb(object_t *object, void (*visit)(object_t *object));

#endif
