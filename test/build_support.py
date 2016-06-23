from cffi import FFI

ffi = FFI()

################################################################################
# config.h                                                                     #
################################################################################
ffi.cdef("""
        #define QCGC_ARENA_SIZE_EXP 20	// Between 16 (64kB) and 20 (1MB)
        """)

################################################################################
# arena                                                                        #
################################################################################
ffi.cdef(""" const size_t qcgc_arena_size;
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
        void qcgc_arena_destroy(arena_t *arena);

        arena_t *qcgc_arena_addr(void *);
        size_t qcgc_arena_cell_index(void *);
        bool qcgc_arena_get_bitmap_entry(uint8_t *, size_t);
        void qcgc_arena_set_bitmap_entry(uint8_t *, size_t, bool);

        void qcgc_arena_mark_allocated(void *ptr, size_t cells);
        void qcgc_arena_mark_free(void *ptr);

        blocktype_t qcgc_arena_get_blocktype(void *ptr);
        void qcgc_arena_set_blocktype(void *ptr, blocktype_t type);

        bool qcgc_arena_is_empty(arena_t *arena);
        bool qcgc_arena_is_coalesced(arena_t *arena);
        size_t qcgc_arena_free_blocks(arena_t *arena);
        size_t qcgc_arena_white_blocks(arena_t *arena);
        size_t qcgc_arena_black_blocks(arena_t *arena);

        bool qcgc_arena_sweep(arena_t *arena);

        size_t qcgc_arena_sizeof(void);
        """)

################################################################################
# bump_allocator                                                               #
################################################################################
ffi.cdef("""
        struct qcgc_balloc_state {
            cell_t *bump_ptr;
            size_t remaining_cells;
        } qcgc_balloc_state;

        void qcgc_balloc_assign(cell_t *bump_ptr, size_t cells);
        void *qcgc_balloc_allocate(size_t cells);
        bool qcgc_balloc_can_allocate(size_t cells);
        """)

################################################################################
# qcgc                                                                         #
################################################################################
ffi.cdef("""
        // qcgc.h
        typedef struct object_s {
            uint32_t flags;
        } object_t;

        struct qcgc_state {
                object_t **shadow_stack;
                object_t **shadow_stack_base;
                arena_t **arenas;
                size_t arena_index;
                size_t current_cell_index;
        } qcgc_state;

        void qcgc_initialize(void);
        void qcgc_destroy(void);
        object_t *qcgc_allocate(size_t bytes);
        void qcgc_collect(void);

        // qcgc.c
        object_t *qcgc_bump_allocate(size_t bytes);
        void qcgc_mark(void);
        void qcgc_mark_object(object_t *object);
        void qcgc_sweep(void);
        """)

################################################################################
# utilities                                                                    #
################################################################################

ffi.cdef("""
        // object
        typedef struct {
            object_t hdr;
            uint32_t type_id;
        } myobject_t;

        void _set_type_id(object_t *obj, uint32_t id);
        uint32_t _get_type_id(object_t *obj);
        """)

################################################################################
# set_source                                                                   #
################################################################################

ffi.set_source("support",
        """
        #include "../qcgc.h"
        #include "../arena.h"
        #include "../bump_allocator.h"

        // arena.h - Macro replacements
        const size_t qcgc_arena_size = QCGC_ARENA_SIZE;

        const size_t qcgc_arena_bitmap_size = QCGC_ARENA_BITMAP_SIZE;
        const size_t qcgc_arena_cells_count = QCGC_ARENA_CELLS_COUNT;
        const size_t qcgc_arena_first_cell_index = QCGC_ARENA_FIRST_CELL_INDEX;

        // qcgc.c prototoypes
        object_t *qcgc_bump_allocate(size_t bytes);
        void qcgc_mark(void);
        void qcgc_mark_object(object_t *object);
        void qcgc_sweep(void);

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

        // Utilites
        typedef struct {
            object_t hdr;
            uint32_t type_id;
        } myobject_t;

        void _set_type_id(object_t *obj, uint32_t id);
        uint32_t _get_type_id(object_t *obj);
        void _set_type_id(object_t *object, uint32_t id) {
            ((myobject_t *) object)->type_id = id;
        }

        uint32_t _get_type_id(object_t *object) {
            return ((myobject_t *) object)->type_id;
        }

        void qcgc_trace_cb(object_t *object, void (*visit)(object_t *)) {
            myobject_t *o = (myobject_t *) object;
            if (o->type_id < 1<<16) {
                // Default object, no references
                return;
            } else {
                // Object containing only references
                object_t **members = (object_t **) o + 1;
                size_t fields = o->type_id - (1<<16);
                for (size_t i = 0; i < fields; i++) {
                    object_t *ref = members[i];
                    visit(ref);
                }
            }
        }

        """, sources=['../qcgc.c', '../arena.c', '../bump_allocator.c'],
        extra_compile_args=['--coverage','-std=gnu99'], extra_link_args=['--coverage'])

if __name__ == "__main__":
    ffi.compile()
