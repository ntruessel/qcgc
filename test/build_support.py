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
        #define QCGC_LARGE_ALLOC_THRESHOLD_EXP 14
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
# object_stack                                                                 #
################################################################################
ffi.cdef("""
        typedef struct object_stack_s {
                size_t count;
                size_t size;
                object_t *items[];
        } object_stack_t;

        object_stack_t *qcgc_object_stack_create(size_t size);

        object_stack_t *qcgc_object_stack_push(object_stack_t *stack, object_t *item);
        object_t *qcgc_object_stack_top(object_stack_t *stack);
        object_stack_t *qcgc_object_stack_pop(object_stack_t *stack);
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
        object_stack_t *arena_gray_stack(arena_t *arena);

        arena_t *qcgc_arena_create(void);
        void qcgc_arena_destroy(arena_t *arena);

        arena_t *qcgc_arena_addr(cell_t *);
        size_t qcgc_arena_cell_index(cell_t *);

        void qcgc_arena_mark_allocated(cell_t *ptr, size_t cells);
        void qcgc_arena_mark_free(cell_t *ptr);

        blocktype_t qcgc_arena_get_blocktype(arena_t *arena, size_t index);
        void qcgc_arena_set_blocktype(arena_t *arena, size_t index, blocktype_t type);

        bool qcgc_arena_is_empty(arena_t *arena);
        bool qcgc_arena_is_coalesced(arena_t *arena);
        size_t qcgc_arena_free_blocks(arena_t *arena);
        size_t qcgc_arena_white_blocks(arena_t *arena);
        size_t qcgc_arena_black_blocks(arena_t *arena);

        bool qcgc_arena_pseudo_sweep(arena_t *arena);
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

        struct weakref_bag_item_s {
                object_t *weakrefobj;
                object_t **target;
        };

        typedef struct weakref_bag_s {
            size_t size;
            size_t count;
            struct weakref_bag_item_s items[];
        } weakref_bag_t;

        """)

################################################################################
# hugeblocktable                                                               #
################################################################################
ffi.cdef("""
        #define QCGC_HBTABLE_BUCKETS 61

        struct hbtable_s {
                bool mark_flag_ref;
                hbbucket_t *bucket[QCGC_HBTABLE_BUCKETS];
        } qcgc_hbtable;

        void qcgc_hbtable_initialize(void);
        void qcgc_hbtable_destroy(void);
        void qcgc_hbtable_insert(object_t *object);
        bool qcgc_hbtable_mark(object_t *object);
        bool qcgc_hbtable_is_marked(object_t *object);
        void qcgc_hbtable_sweep(void);
        size_t bucket(object_t *object);
        """)

################################################################################
# gc_state                                                                     #
################################################################################
ffi.cdef("""
        struct qcgc_shadowstack {
                object_t **top;
                object_t **base;
        } _qcgc_shadowstack;

        typedef enum gc_phase {
                GC_PAUSE,
                GC_MARK,
                GC_COLLECT,
        } gc_phase_t;

        struct qcgc_state {
                object_stack_t *prebuilt_objects;
                weakref_bag_t *weakrefs;
                object_stack_t *gp_gray_stack;
                size_t gray_stack_size;
                gc_phase_t phase;
                size_t cells_since_incmark;
                size_t incmark_since_sweep;
                size_t incmark_threshold;
                size_t incmark_to_sweep;
                size_t free_cells;
                size_t largest_free_block;
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
        arena_bag_t *free_arenas(void);
        linear_free_list_t *small_free_list(size_t index);
        exp_free_list_t *large_free_list(size_t index);

        void bump_ptr_reset(void);
        void qcgc_reset_bump_ptr(void);

        void qcgc_allocator_initialize(void);
        void qcgc_allocator_destroy(void);
        object_t *qcgc_fit_allocate(size_t bytes);
        void qcgc_fit_allocator_add(cell_t *ptr, size_t cells);

        // static functions
        size_t bytes_to_cells(size_t bytes);

        void bump_allocator_assign(cell_t *ptr, size_t cells);
        void qcgc_bump_allocator_renew_block(size_t size, bool force);

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
# core                                                                         #
################################################################################
ffi.cdef("""
        struct qcgc_bump_allocator {
                cell_t *ptr;
                cell_t *end;
        } _qcgc_bump_allocator;

        void qcgc_initialize(void);
        void qcgc_destroy(void);
        void qcgc_write(object_t *object);
        object_t *qcgc_allocate(size_t size);
        void qcgc_collect(void);

        void qcgc_push_root(object_t *object);
        void qcgc_pop_root(size_t count);

        object_t *_qcgc_allocate_large(size_t bytes);
        """)

################################################################################
# collector                                                                    #
################################################################################
ffi.cdef("""
        void qcgc_mark(void);
        void qcgc_incmark(void);
        void qcgc_sweep(void);
        """)

################################################################################
# weakref                                                                      #
################################################################################
ffi.cdef("""
        void qcgc_register_weakref(object_t *weakrefobj, object_t **target);
        """)

################################################################################
# utilities                                                                    #
################################################################################

ffi.cdef("""
        // prebuilt
        object_t *allocate_prebuilt(size_t bytes);

        // object
        typedef struct myobject_s myobject_t;

        struct myobject_s {
            object_t hdr;
            uint32_t type_id;
            myobject_t *refs[];
        };

        void _set_type_id(object_t *obj, uint32_t id);
        uint32_t _get_type_id(object_t *obj);

        typedef enum mark_color {
            MARK_COLOR_WHITE,
            MARK_COLOR_LIGHT_GRAY,
            MARK_COLOR_DARK_GRAY,
            MARK_COLOR_BLACK,
            MARK_COLOR_INVALID,
        } mark_color_t;

        mark_color_t qcgc_get_mark_color(object_t *object);
        object_t *qcgc_bump_allocate(size_t bytes);

        """)

################################################################################
# set_source                                                                   #
################################################################################

ffi.set_source("support",
        """
        #include "../config.h"
        #include <stddef.h>
        #include <stdbool.h>
        #include <stdint.h>

/******************************************************************************/
        // qcgc.h
        #define QCGC_GRAY_FLAG (1<<0)
        #define QCGC_PREBUILT_OBJECT (1<<1)
        #define QCGC_PREBUILT_REGISTERED (1<<2)

        typedef struct object_s {
                uint32_t flags;
        } object_t;

        typedef uint8_t cell_t[16];

        struct qcgc_shadowstack {
                object_t **top;
                object_t **base;
        } _qcgc_shadowstack;

        struct qcgc_bump_allocator {
            cell_t *ptr;
            cell_t *end;
        } _qcgc_bump_allocator;

        bool _qcgc_gray_flag_inverted;

        void qcgc_initialize(void);
        void qcgc_destroy(void);
        object_t *qcgc_allocate(size_t size);
        object_t *_qcgc_allocate_large(size_t bytes);
        void qcgc_push_root(object_t *object);
        void qcgc_pop_root(size_t count);
        void qcgc_write(object_t *object);
        void qcgc_collect(void);
        void qcgc_register_weakref(object_t *weakrefobj, object_t **target);


/******************************************************************************/
        // event_logger.h
        #include "../src/event_logger.h"

/******************************************************************************/
        // object_stack.h
        typedef struct object_stack_s {
                size_t count;
                size_t size;
                object_t *items[];
        } object_stack_t;

        __attribute__ ((warn_unused_result))
        object_stack_t *qcgc_object_stack_create(size_t size);

        __attribute__ ((warn_unused_result))
        object_stack_t *qcgc_object_stack_push(object_stack_t *stack, object_t *item);

        object_t *qcgc_object_stack_top(object_stack_t *stack);

        __attribute__ ((warn_unused_result))
        object_stack_t *qcgc_object_stack_pop(object_stack_t *stack);

/******************************************************************************/
        // arena.h
        #include <stdbool.h>
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

        arena_t *qcgc_arena_create(void);
        void qcgc_arena_destroy(arena_t *arena);
        void qcgc_arena_mark_allocated(cell_t *ptr, size_t cells);
        void qcgc_arena_mark_free(cell_t *ptr);
        bool qcgc_arena_sweep(arena_t *arena);
        bool qcgc_arena_pseudo_sweep(arena_t *arena);

        arena_t *qcgc_arena_addr(cell_t *ptr);
        size_t qcgc_arena_cell_index(cell_t *ptr);
        blocktype_t qcgc_arena_get_blocktype(arena_t *arena, size_t index);
        void qcgc_arena_set_blocktype(arena_t *arena, size_t index, blocktype_t type);

        bool qcgc_arena_is_empty(arena_t *arena);
        bool qcgc_arena_is_coalesced(arena_t *arena);
        size_t qcgc_arena_free_blocks(arena_t *arena);
        size_t qcgc_arena_white_blocks(arena_t *arena);
        size_t qcgc_arena_black_blocks(arena_t *arena);

/******************************************************************************/
        // bag.h
        #define DECLARE_BAG(name, type)					    \
        typedef struct name##_s {					    \
                size_t size;						    \
                size_t count;						    \
                type items[];						    \
        } name##_t;							    \
                                                                            \
        __attribute__ ((warn_unused_result))				    \
        name##_t *qcgc_##name##_create(size_t size);			    \
                                                                            \
        __attribute__ ((warn_unused_result))				    \
        name##_t *qcgc_##name##_add(name##_t *self, type item);		    \
                                                                            \
        __attribute__ ((warn_unused_result))				    \
        name##_t *qcgc_##name##_remove_index(name##_t *self, size_t index);

        struct exp_free_list_item_s {
            cell_t *ptr;
            size_t size;
        };

        struct hbtable_entry_s {
            object_t *object;
            bool mark_flag;
        };

        struct weakref_bag_item_s {
            object_t *weakrefobj;
            object_t **target;
        };

        DECLARE_BAG(arena_bag, arena_t *);
        DECLARE_BAG(linear_free_list, cell_t *);
        DECLARE_BAG(exp_free_list, struct exp_free_list_item_s);
        DECLARE_BAG(hbbucket, struct hbtable_entry_s);
        DECLARE_BAG(weakref_bag, struct weakref_bag_item_s);

/******************************************************************************/
        // hugeblocktable.h
        #define QCGC_HBTABLE_BUCKETS 61

        struct hbtable_s {
                bool mark_flag_ref;
                hbbucket_t *bucket[QCGC_HBTABLE_BUCKETS];
        } qcgc_hbtable;

        void qcgc_hbtable_initialize(void);
        void qcgc_hbtable_destroy(void);
        void qcgc_hbtable_insert(object_t *object);
        bool qcgc_hbtable_mark(object_t *object);
        bool qcgc_hbtable_is_marked(object_t *object);
        void qcgc_hbtable_sweep(void);
        size_t bucket(object_t *object);

/******************************************************************************/
        // gc_state.h
        typedef enum gc_phase {
                GC_PAUSE,
                GC_MARK,
                GC_COLLECT,
        } gc_phase_t;

        struct qcgc_state {
                object_stack_t *prebuilt_objects;
                weakref_bag_t *weakrefs;
                object_stack_t *gp_gray_stack;
                size_t gray_stack_size;
                gc_phase_t phase;
                size_t cells_since_incmark;
                size_t incmark_since_sweep;
                size_t incmark_threshold;
                size_t incmark_to_sweep;
                size_t free_cells;
                size_t largest_free_block;
        } qcgc_state;

/******************************************************************************/
        // allocator.h
        #define QCGC_LARGE_FREE_LISTS (QCGC_LARGE_ALLOC_THRESHOLD_EXP - QCGC_LARGE_FREE_LIST_FIRST_EXP - 4 + 1)

        #define QCGC_SMALL_FREE_LISTS ((1<<QCGC_LARGE_FREE_LIST_FIRST_EXP) - 1)

        struct qcgc_allocator_state {
            arena_bag_t *arenas;
            arena_bag_t *free_arenas;
            struct fit_state {
                linear_free_list_t *small_free_list[QCGC_SMALL_FREE_LISTS];
                exp_free_list_t *large_free_list[QCGC_LARGE_FREE_LISTS];
            } fit_state;
        } qcgc_allocator_state;

        void qcgc_allocator_initialize(void);
        void qcgc_allocator_destroy(void);
        object_t *qcgc_fit_allocate(size_t bytes);
        void qcgc_fit_allocator_empty_lists(void);
        void qcgc_fit_allocator_add(cell_t *ptr, size_t cells);
        void qcgc_bump_allocator_renew_block(size_t size, bool force);
        void qcgc_reset_bump_ptr(void);

/******************************************************************************/
        // collector.h
        void qcgc_mark(void);
        void qcgc_incmark(void);
        void qcgc_sweep(void);

/******************************************************************************/
        // weakref.h
        void qcgc_register_weakref(object_t *weakrefobj, object_t **target);

/******************************************************************************/
/******************************************************************************/
/******************************************************************************/

        // arena.h - Macro replacements
        const size_t qcgc_arena_size = QCGC_ARENA_SIZE;

        const size_t qcgc_arena_bitmap_size = QCGC_ARENA_BITMAP_SIZE;
        const size_t qcgc_arena_cells_count = QCGC_ARENA_CELLS_COUNT;
        const size_t qcgc_arena_first_cell_index = QCGC_ARENA_FIRST_CELL_INDEX;

        // event_logger.h - Macro replacements
        const char *logfile = LOGFILE;

        // hugeblocktable.c prototyes
        size_t bucket(object_t *object);

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

        bool valid_block(cell_t *ptr, size_t cells) {
#if CHECKED
            assert(ptr != NULL);
            assert(cells > 0);
#endif
            return (qcgc_arena_get_blocktype(qcgc_arena_addr(ptr), qcgc_arena_cell_index(ptr)) == BLOCK_FREE &&
                    (((qcgc_arena_addr(ptr + cells)) == (arena_t *) (ptr + cells)) ||
                        qcgc_arena_get_blocktype(qcgc_arena_addr(ptr + cells), qcgc_arena_cell_index(ptr + cells)) != BLOCK_EXTENT));
        }

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

        object_stack_t *arena_gray_stack(arena_t *arena) {
            return arena->gray_stack;
        }

        size_t qcgc_arena_sizeof(void) {
            return sizeof(arena_t);
        }

        // allocator state accessors
        arena_bag_t *arenas(void) {
            return qcgc_allocator_state.arenas;
        }

        arena_bag_t *free_arenas(void) {
            return qcgc_allocator_state.free_arenas;
        }

        linear_free_list_t *small_free_list(size_t index) {
            return qcgc_allocator_state.fit_state.small_free_list[index];
        }

        exp_free_list_t *large_free_list(size_t index) {
            return qcgc_allocator_state.fit_state.large_free_list[index];
        }

        void bump_ptr_reset(void) {
            if (_qcgc_bump_allocator.end > _qcgc_bump_allocator.ptr) {
                qcgc_arena_set_blocktype(qcgc_arena_addr(_qcgc_bump_allocator.ptr),
                        qcgc_arena_cell_index(_qcgc_bump_allocator.ptr), BLOCK_FREE);
            }
            _qcgc_bump_allocator.ptr = NULL;
            _qcgc_bump_allocator.end = NULL;
        }

        object_t *allocate_prebuilt(size_t bytes) {
            object_t *result = (object_t *) calloc(bytes, sizeof(char));
            result->flags = QCGC_PREBUILT_OBJECT;
            return result;
        }

        typedef struct myobject_s myobject_t;
        struct myobject_s {
            object_t hdr;
            uint32_t type_id;
            myobject_t *refs[];
        };

        object_t *qcgc_bump_allocate(size_t bytes);
        object_t *qcgc_bump_allocate(size_t bytes) {
            size_t cells = bytes_to_cells(bytes);

            cell_t *mem = _qcgc_bump_allocator.ptr;

            qcgc_arena_set_blocktype(qcgc_arena_addr(mem), qcgc_arena_cell_index(mem),
                            BLOCK_WHITE);

            _qcgc_bump_allocator.ptr += cells;

            object_t *result = (object_t *) mem;

        #if QCGC_INIT_ZERO
            memset(result, 0, cells * sizeof(cell_t));
        #endif

            result->flags = QCGC_GRAY_FLAG;
            return result;
        }

        void _set_type_id(object_t *obj, uint32_t id);
        uint32_t _get_type_id(object_t *obj);

        void _set_type_id(object_t *object, uint32_t id) {
            ((myobject_t *) object)->type_id = id;
        }

        uint32_t _get_type_id(object_t *object) {
            return ((myobject_t *) object)->type_id;
        }

        typedef enum mark_color {
            MARK_COLOR_WHITE,
            MARK_COLOR_LIGHT_GRAY,
            MARK_COLOR_DARK_GRAY,
            MARK_COLOR_BLACK,
            MARK_COLOR_INVALID,
        } mark_color_t;

        mark_color_t qcgc_get_mark_color(object_t *object);

        mark_color_t qcgc_get_mark_color(object_t *object) {
                blocktype_t blocktype = qcgc_arena_get_blocktype(
                        qcgc_arena_addr((cell_t *) object),
                        qcgc_arena_cell_index((cell_t *) object));
                bool gray = !(object->flags & QCGC_GRAY_FLAG) == _qcgc_gray_flag_inverted;
                if (blocktype == BLOCK_WHITE) {
                        if (gray) {
                                return MARK_COLOR_LIGHT_GRAY;
                        } else {
                                return MARK_COLOR_WHITE;
                        }
                } else if(blocktype == BLOCK_BLACK) {
                        if (gray) {
                                return MARK_COLOR_DARK_GRAY;
                        } else {
                                return MARK_COLOR_BLACK;
                        }
                } else {
                        return MARK_COLOR_INVALID;
                }
        }

        void qcgc_trace_cb(object_t *object, void (*visit)(object_t *)) {
            myobject_t *o = (myobject_t *) object;
            for (size_t i = 0; i < o->type_id; i++) {
                visit((object_t *)o->refs[i]);
            }
        }

        """, sources=['lib.c'],
        extra_compile_args=['-Wall', '-Wextra', '--coverage', '-std=gnu11',
                '-UNDEBUG', '-DTESTING', '-O0', '-g'],
        extra_link_args=['--coverage', '-lrt'])

if __name__ == "__main__":
    ffi.compile()
