from cffi import FFI

ffi = FFI()

ffi.set_source("support",
        """
        #include "../qcgc.h"
        #include "../arena.h"

        // arena.h - Macro replacements
        const size_t qcgc_arena_size = QCGC_ARENA_SIZE;

        const size_t qcgc_arena_bitmap_size = QCGC_ARENA_BITMAP_SIZE;
        const size_t qcgc_arena_cells_count = QCGC_ARENA_CELLS_COUNT;

        cell_t *arena_cells(arena_t *arena) {
            return arena->cells;
        }

        uint8_t *arena_mark_bitmap(arena_t *arena) {
            return arena->mark_bitmap;
        }

        uint8_t *arena_block_bitmap(arena_t *arena) {
            return arena->block_bitmap;
        }

        arena_t *qcgc_arena_addr(void *x) {
            return QCGC_ARENA_ADDR(x);
        }

        size_t qcgc_arena_cell_index(void *x) {
            return QCGC_ARENA_CELL_INDEX(x);
        }

        size_t qcgc_arena_sizeof(void) {
            return sizeof(arena_t);
        }

        """, sources=['../qcgc.c', '../arena.c'])

ffi.cdef("""
        // config.h
        #define QCGC_SHADOWSTACK_SIZE 4096
        #define QCGC_ARENA_SIZE_EXP 20		// Between 16 (64kB) and 20 (1MB)

        // arena.h
        const size_t qcgc_arena_size;
        const size_t qcgc_arena_bitmap_size;
        const size_t qcgc_arena_cells_count;

        typedef uint8_t cell_t[16];

        typedef union arena_u arena_t;

        cell_t *arena_cells(arena_t *arena);
        uint8_t *arena_mark_bitmap(arena_t *arena);
        uint8_t *arena_block_bitmap(arena_t *arena);

        arena_t *qcgc_arena_create(void);

        arena_t *qcgc_arena_addr(void *x);

        size_t qcgc_arena_cell_index(void *x);

        size_t qcgc_arena_sizeof(void);

        // qcgc.h
        typedef struct object_s {
            uint16_t flags;
        } object_t;

        struct qcgc_state {
                object_t **shadow_stack;
                object_t **shadow_stack_base;
        } qcgc_state;

        void qcgc_initialize(void);
        void qcgc_destroy(void);
        object_t *qcgc_allocate(size_t bytes);
        void qcgc_collect(void);
        """)

if __name__ == "__main__":
    ffi.compile()
