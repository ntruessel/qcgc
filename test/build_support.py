from cffi import FFI

ffi = FFI()

ffi.set_source("support",
        """
        #include "../qcgc.h"
        """, sources=['../qcgc.c'])

ffi.cdef("""
        void *qcgc_allocate(size_t bytes);
        void qcgc_collect(void);
        """)

if __name__ == "__main__":
    ffi.compile()
