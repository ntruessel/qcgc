from cffi import FFI

ffi = FFI()

ffi.set_source("support",
        """
        #include "../qcgc.h"
        """, sources=['../qcgc.c'])

ffi.cdef("""
        struct qcgc_state {
                void **shadow_stack;
                void **shadow_stack_base;
        } qcgc_state;

        void qcgc_initialize(void);
        void qcgc_destroy(void);
        void *qcgc_allocate(size_t bytes);
        void qcgc_collect(void);
        """)

if __name__ == "__main__":
    ffi.compile()
