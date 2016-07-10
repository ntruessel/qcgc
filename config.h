#pragma once

#define QCGC_SHADOWSTACK_SIZE 4096
#define QCGC_ARENA_COUNT 4096				// Space for 4096 arenas (up to 4GB)
#define QCGC_ARENA_SIZE_EXP 20				// Between 16 (64kB) and 20 (1MB)
#define QCGC_LARGE_ALLOC_THRESHOLD 1<<14
#define QCGC_MARK_LIST_SEGMENT_SIZE 64		// TODO: Tune for performance
#define QCGC_GRAY_STACK_INIT_SIZE 128		// TODO: Tune for performance
#define QCGC_INC_MARK_MIN 64				// TODO: Tune for performance

#define CHECKED 1							// Set to 0 to disable all checks
