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
        const size_t qcgc_arena_first_cell_index = QCGC_ARENA_FIRST_CELL_INDEX;

        cell_t *arena_cells(arena_t *arena) {
            return arena->cells;
        }

        uint8_t *arena_mark_bitmap(arena_t *arena) {
            return arena->mark_bitmap;
        }

        uint8_t *arena_block_bitmap(arena_t *arena) {
            return arena->block_bitmap;
        }

        size_t qcgc_arena_sizeof(void) {
            return sizeof(arena_t);
        }

        """, sources=['../qcgc.c', '../arena.c'])

ffi.cdef("""
        // config.h
        #define QCGC_SHADOWSTACK_SIZE 4096
        #define QCGC_ARENA_SIZE_EXP 20	    // Between 16 (64kB) and 20 (1MB)

        // arena.h
        const size_t qcgc_arena_size;
        const size_t qcgc_arena_bitmap_size;
        const size_t qcgc_arena_cells_count;
        const size_t qcgc_arena_first_cell_index;

        typedef uint8_t cell_t[16];

        typedef union arena_u arena_t;

        typedef enum blocktype {
                BLOCK_EXTENT,
                BLOCK_FREE,
                BLOCK_WHITE,
                BLOCK_BLACK,
        } blocktype_t;

        cell_t *arena_cells(arena_t *arena);
        uint8_t *arena_mark_bitmap(arena_t *arena);
        uint8_t *arena_block_bitmap(arena_t *arena);

        arena_t *qcgc_arena_create(void);

        arena_t *qcgc_arena_addr(void *);
        size_t qcgc_arena_cell_index(void *);
        bool qcgc_arena_get_bitmap_entry(uint8_t *, size_t);
        void qcgc_arena_set_bitmap_entry(uint8_t *, size_t, bool);

        blocktype_t qcgc_arena_get_blocktype(void *ptr);
        void qcgc_arena_set_blocktype(void *ptr, blocktype_t type);

        size_t qcgc_arena_sizeof(void);

        // qcgc.h
        typedef struct object_s {
            uint16_t flags;
        } object_t;

        struct qcgc_state {
                object_t **shadow_stack;
                object_t **shadow_stack_base;
                arena_t *current_arena;
                size_t current_arena_used;
        } qcgc_state;

        void qcgc_initialize(void);
        void qcgc_destroy(void);
        object_t *qcgc_allocate(size_t bytes);
        void qcgc_collect(void);
        """)

if __name__ == "__main__":
    ffi.compile()
