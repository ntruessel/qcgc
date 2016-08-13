#pragma once

#define CHECKED 1							// Enable runtime sanity checks

#define QCGC_INIT_ZERO 1					// Init new objects with zero bytes

#define QCGC_SHADOWSTACK_SIZE 4096
#define QCGC_ARENA_BAG_INIT_SIZE 16			// Initial size of the arena bag
#define QCGC_ARENA_SIZE_EXP 20				// Between 16 (64kB) and 20 (1MB)
#define QCGC_LARGE_ALLOC_THRESHOLD 1<<14
#define QCGC_MARK_LIST_SEGMENT_SIZE 64		// TODO: Tune for performance
#define QCGC_GRAY_STACK_INIT_SIZE 128		// TODO: Tune for performance
#define QCGC_INC_MARK_MIN 64				// TODO: Tune for performance

/**
 * Segregated allocator
 */
#define QCGC_LINEAR_FREE_LISTS 16			// Amount of small free lists with
											// size = x cells
#define QCGC_EXP_FREE_LISTS 6				// Amount of large free lists with
											// size = 2^x cells
#define QCGC_FREE_LIST_INIT_SIZE 16			// Initial size of free lists

/**
 * DO NOT MODIFY
 */

#ifdef TESTING
#define QCGC_STATIC
#else
#define QCGC_STATIC static
#endif
