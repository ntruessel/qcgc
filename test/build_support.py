from cffi import FFI

ffi = FFI()

################################################################################
# config.h                                                                     #
################################################################################
ffi.cdef("""
        #define QCGC_ARENA_SIZE_EXP 20	// Between 16 (64kB) and 20 (1MB)
        #define QCGC_MARK_LIST_SEGMENT_SIZE 64
        #define QCGC_INC_MARK_MIN 64	// TODO: Tune for performance
        #define QCGC_LARGE_FREE_LIST_FIRST_EXP 5
        #define QCGC_LARGE_FREE_LIST_INIT_SIZE 4
        #define QCGC_SMALL_FREE_LIST_INIT_SIZE 16
        """)

################################################################################
# event_logger                                                                 #
################################################################################
ffi.cdef("""
        const char *logfile;

        enum event_e {
                EVENT_LOG_START,
                EVENT_LOG_STOP,

                EVENT_SWEEP_START,
                EVENT_SWEEP_DONE,
        };

        void qcgc_event_logger_initialize(void);
        void qcgc_event_logger_destroy(void);
        void qcgc_event_logger_log(enum event_e event,
                        uint32_t additional_data_size,
                        uint8_t *additional_data);
        """)


################################################################################
# object                                                                       #
################################################################################
ffi.cdef("""
        #define QCGC_GRAY_FLAG 0x1
        #define QCGC_PREBUILT_OBJECT 0x2

        typedef struct object_s {
                uint32_t flags;
        } object_t;
        """)

################################################################################
# gray_stack                                                                   #
################################################################################
ffi.cdef("""
        typedef struct gray_stack_s {
                size_t index;
                size_t size;
                object_t *items[];
        } gray_stack_t;

        gray_stack_t *qcgc_gray_stack_create(size_t size);

        gray_stack_t *qcgc_gray_stack_push(gray_stack_t *stack, object_t *item);
        object_t *qcgc_gray_stack_top(gray_stack_t *stack);
        gray_stack_t *qcgc_gray_stack_pop(gray_stack_t *stack);
        """)

################################################################################
# shadow_stack                                                                 #
################################################################################
ffi.cdef("""
        typedef struct shadow_stack_s {
                size_t count;
                size_t size;
                object_t *items[];
        } shadow_stack_t;

        shadow_stack_t *qcgc_shadow_stack_create(size_t size);

        shadow_stack_t *qcgc_shadow_stack_push(shadow_stack_t *stack,
                    object_t *item);
        object_t *qcgc_shadow_stack_top(shadow_stack_t *stack);
        shadow_stack_t *qcgc_shadow_stack_pop(shadow_stack_t *stack);
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
        gray_stack_t *arena_gray_stack(arena_t *arena);

        arena_t *qcgc_arena_create(void);
        void qcgc_arena_destroy(arena_t *arena);

        arena_t *qcgc_arena_addr(cell_t *);
        size_t qcgc_arena_cell_index(cell_t *);
        bool qcgc_arena_get_bitmap_entry(uint8_t *, size_t);
        void qcgc_arena_set_bitmap_entry(uint8_t *, size_t, bool);

        void qcgc_arena_mark_allocated(cell_t *ptr, size_t cells);
        void qcgc_arena_mark_free(cell_t *ptr);

        blocktype_t qcgc_arena_get_blocktype(cell_t *ptr);
        void qcgc_arena_set_blocktype(cell_t *ptr, blocktype_t type);

        bool qcgc_arena_is_empty(arena_t *arena);
        bool qcgc_arena_is_coalesced(arena_t *arena);
        size_t qcgc_arena_free_blocks(arena_t *arena);
        size_t qcgc_arena_white_blocks(arena_t *arena);
        size_t qcgc_arena_black_blocks(arena_t *arena);

        bool qcgc_arena_sweep(arena_t *arena);

        size_t qcgc_arena_sizeof(void);
        """)

################################################################################
# bag (only arena_bag_t is tested)                                             #
################################################################################
ffi.cdef("""
        typedef struct arena_bag_s {
            size_t size;
            size_t count;
            arena_t *items[];
        } arena_bag_t;

        arena_bag_t *qcgc_arena_bag_create(size_t size);
        arena_bag_t *qcgc_arena_bag_add(arena_bag_t *self, arena_t *item);
        arena_bag_t *qcgc_arena_bag_remove_index(arena_bag_t *self,
                size_t index);

        typedef struct linear_free_list_s {
            size_t size;
            size_t count;
            cell_t *items[];
        } linear_free_list_t;

        linear_free_list_t *qcgc_linear_free_list_create(size_t size);
        linear_free_list_t *qcgc_linear_free_list_add(linear_free_list_t *self,
                cell_t *item);
        linear_free_list_t *qcgc_linear_free_list_remove_index(
                linear_free_list_t *self, size_t index);

        struct exp_free_list_item_s {
                cell_t *ptr;
                size_t size;
        };

        typedef struct exp_free_list_s {
            size_t size;
            size_t count;
            struct exp_free_list_item_s items[];
        } exp_free_list_t;

        exp_free_list_t *qcgc_exp_free_list_create(size_t size);
        exp_free_list_t *qcgc_exp_free_list_add(exp_free_list_t *self,
                struct exp_free_list_item_s item);
        exp_free_list_t *qcgc_exp_free_list_remove_index(
                exp_free_list_t *self, size_t index);

        struct hbtable_entry_s {
            object_t *object;
            bool mark_flag;
        };

        typedef struct hbbucket_s {
            size_t size;
            size_t count;
            struct hbtable_entry_s items[];
        } hbbucket_t;

        hbbucket_t *qcgc_hbbucket_create(size_t size);
        hbbucket_t *qcgc_hbbucket_add(hbbucket_t *self,
                struct hbtable_entry_s item);
        hbbucket_t *qcgc_hbbucket_remove_index(
                hbbucket_t *self, size_t index);

        """)

################################################################################
# hugeblocktable                                                               #
################################################################################
ffi.cdef("""
        #define QCGC_HBTABLE_BUCKETS 61

        struct hbtable_s {
                bool mark_flag_ref;
                hbbucket_t *bucket[QCGC_HBTABLE_BUCKETS];
                gray_stack_t *gray_stack;
        } qcgc_hbtable;

        void qcgc_hbtable_initialize(void);
        void qcgc_hbtable_destroy(void);
        void qcgc_hbtable_insert(object_t *object);
        void qcgc_hbtable_mark(object_t *object);
        void qcgc_hbtable_sweep(void);
        size_t bucket(object_t *object);
        """)

################################################################################
# gc_state                                                                     #
################################################################################
ffi.cdef("""
        typedef enum gc_phase {
                GC_PAUSE,
                GC_MARK,
                GC_COLLECT,
        } gc_phase_t;

        struct qcgc_state {
                shadow_stack_t *shadow_stack;
                shadow_stack_t *prebuilt_objects;
                size_t gray_stack_size;
                gc_phase_t phase;
        } qcgc_state;

        """)

################################################################################
# allocator                                                                    #
################################################################################
ffi.cdef("""
        //
        const size_t qcgc_small_free_lists;
        const size_t qcgc_large_free_lists;

        // Access functions for state
        arena_bag_t *arenas(void);
        cell_t *bump_ptr(void);
        size_t remaining_cells(void);
        linear_free_list_t *small_free_list(size_t index);
        exp_free_list_t *large_free_list(size_t index);

        void qcgc_allocator_initialize(void);
        void qcgc_allocator_destroy(void);
        object_t *qcgc_fit_allocate(size_t bytes);
        object_t *qcgc_bump_allocate(size_t bytes);
        object_t *qcgc_large_allocate(size_t bytes);
        void qcgc_fit_allocator_add(cell_t *ptr, size_t cells);

        // static functions
        size_t bytes_to_cells(size_t bytes);

        void bump_allocator_assign(cell_t *ptr, size_t cells);
        void bump_allocator_advance(size_t cells);

        bool is_small(size_t cells);
        size_t small_index(size_t cells);
        size_t large_index(size_t cells);
        size_t small_index_to_cells(size_t index);

        cell_t *fit_allocator_small_first_fit(size_t index, size_t cells);
        cell_t *fit_allocator_large_fit(size_t index, size_t cells);
        cell_t *fit_allocator_large_first_fit(size_t index, size_t cells);

        bool valid_block(cell_t *ptr, size_t cells);
        """)

################################################################################
# mark_list                                                                    #
################################################################################
ffi.cdef("""
        typedef struct mark_list_s {
                size_t head;
                size_t tail;
                size_t length;
                size_t count;
                size_t insert_index;
                object_t **segments[];
        } mark_list_t;

        mark_list_t *qcgc_mark_list_create(size_t initial_size);
        void qcgc_mark_list_destroy(mark_list_t *list);

        mark_list_t *qcgc_mark_list_push(mark_list_t *list, object_t *object);
        mark_list_t *qcgc_mark_list_push_all(mark_list_t *list,
                        object_t **objects, size_t count);

        object_t **qcgc_mark_list_get_head_segment(mark_list_t *list);
        mark_list_t *qcgc_mark_list_drop_head_segment(mark_list_t *list);
        """)


################################################################################
# qcgc                                                                         #
################################################################################
ffi.cdef("""
        typedef enum mark_color {
                MARK_COLOR_WHITE,
                MARK_COLOR_LIGHT_GRAY,
                MARK_COLOR_DARK_GRAY,
                MARK_COLOR_BLACK,
        } mark_color_t;

        void qcgc_initialize(void);
        void qcgc_destroy(void);
        void qcgc_write(object_t *object);
        object_t *qcgc_allocate(size_t size);
        void qcgc_collect(void);
        mark_color_t qcgc_get_mark_color(object_t *object);

        void qcgc_shadowstack_push(object_t *object);
        object_t *qcgc_shadowstack_pop(void);

        // qcgc.c
        void qcgc_mark(void);
        void qcgc_mark_all(void);
        void qcgc_mark_incremental(void);
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
        #include "../config.h"
        #include "../object.h"
        #include "../qcgc.h"
        #include "../arena.h"
        #include "../mark_list.h"
        #include "../gray_stack.h"
        #include "../bag.h"
        #include "../allocator.h"
        #include "../event_logger.h"
        #include "../shadow_stack.h"
        #include "../hugeblocktable.h"

        // arena.h - Macro replacements
        const size_t qcgc_arena_size = QCGC_ARENA_SIZE;

        const size_t qcgc_arena_bitmap_size = QCGC_ARENA_BITMAP_SIZE;
        const size_t qcgc_arena_cells_count = QCGC_ARENA_CELLS_COUNT;
        const size_t qcgc_arena_first_cell_index = QCGC_ARENA_FIRST_CELL_INDEX;

        // event_logger.h - Macro replacements
        const char *logfile = LOGFILE;

        // hugeblocktable.c prototyes
        size_t bucket(object_t *object);

        // qcgc.c prototoypes
        object_t *qcgc_bump_allocate(size_t size);
        void qcgc_mark(void);
        void qcgc_mark_all(void);
        void qcgc_mark_incremental(void);
        void qcgc_sweep(void);

        // allocator.h - Macro replacements
        const size_t qcgc_small_free_lists = QCGC_SMALL_FREE_LISTS;
        const size_t qcgc_large_free_lists = QCGC_LARGE_FREE_LISTS;

        // allocator.c internals prototypes
        size_t bytes_to_cells(size_t bytes);

        void bump_allocator_assign(cell_t *ptr, size_t cells);
        void bump_allocator_advance(size_t cells);

        bool is_small(size_t cells);
        size_t small_index(size_t cells);
        size_t large_index(size_t cells);
        size_t small_index_to_cells(size_t index);

        cell_t *fit_allocator_small_first_fit(size_t index, size_t cells);
        cell_t *fit_allocator_large_fit(size_t index, size_t cells);
        cell_t *fit_allocator_large_first_fit(size_t index, size_t cells);

        bool valid_block(cell_t *ptr, size_t cells);

        // arena_t accessors
        cell_t *arena_cells(arena_t *arena) {
            return arena->cells;
        }

        uint8_t *arena_mark_bitmap(arena_t *arena) {
            return arena->mark_bitmap;
        }

        uint8_t *arena_block_bitmap(arena_t *arena) {
            return arena->block_bitmap;
        }

        gray_stack_t *arena_gray_stack(arena_t *arena) {
            return arena->gray_stack;
        }

        size_t qcgc_arena_sizeof(void) {
            return sizeof(arena_t);
        }

        // allocator state accessors
        arena_bag_t *arenas(void) {
            return qcgc_allocator_state.arenas;
        }

        cell_t *bump_ptr(void) {
            return qcgc_allocator_state.bump_state.bump_ptr;
        }

        size_t remaining_cells(void) {
            return qcgc_allocator_state.bump_state.remaining_cells;
        }

        linear_free_list_t *small_free_list(size_t index) {
            return qcgc_allocator_state.fit_state.small_free_list[index];
        }

        exp_free_list_t *large_free_list(size_t index) {
            return qcgc_allocator_state.fit_state.large_free_list[index];
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

        """, sources=['../qcgc.c', '../arena.c', '../allocator.c',
                '../mark_list.c', '../gray_stack.c', '../bag.c',
                '../event_logger.c', '../shadow_stack.c',
                '../hugeblocktable.c'],
        extra_compile_args=['--coverage', '-std=gnu11', '-UNDEBUG', '-DTESTING',
                '-O0', '-g'],
        extra_link_args=['--coverage', '-lrt'])

if __name__ == "__main__":
    ffi.compile()
