from cffi import FFI

ffi = FFI()

ffi.set_source("support",
        """
        #include "../qcgc.h"
        #include "../arena.h"

        // arena.h - Macro replacements
        // TODO: use macros here
        const size_t qcgc_arena_size = 1<<QCGC_ARENA_SIZE_EXP;

        const size_t qcgc_arena_bitmap_size = 1<<(QCGC_ARENA_SIZE_EXP - 7); // 1 / 128
        const size_t qcgc_arena_cells_count = (1<<(QCGC_ARENA_SIZE_EXP - 4)) - (1<<(QCGC_ARENA_SIZE_EXP - 10));

        arena_t *qcgc_arena_addr(void *x) {
            return (arena_t *) ((intptr_t) x & ~(QCGC_ARENA_SIZE - 1));
        }

        size_t qcgc_arena_cell_index(void *x) {
            return (size_t) ((intptr_t) x & (QCGC_ARENA_SIZE - 1));
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

        // cffi forces these values to be hardcoded
        typedef struct arena_s {
                uint8_t block_bitmap[8192]; //  2^(QCGC_ARENA_SIZE_EXP - 7) = 2^13
                uint8_t mark_bitmap[8192];
                cell_t cells[64512]; // 2^(QCGC_ARENA_SIZE_EXP - 4) - 2^(QCGC_ARENA_SIZE_EXP - 10) = 2^16 - 2^10
        } arena_t;

        arena_t *qcgc_arena_create(void);

        arena_t *qcgc_arena_addr(void *x);

        size_t qcgc_arena_cell_index(void *x);

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
