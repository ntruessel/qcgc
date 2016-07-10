from support import lib,ffi
import unittest

class QCGCTest(unittest.TestCase):
    header_size = ffi.sizeof("myobject_t")

    def setUp(self):
        lib.qcgc_initialize()

    def tearDown(self):
        lib.qcgc_destroy()

    def push_root(self, o):
        lib.qcgc_state.shadow_stack[0] = ffi.cast("void *", o)
        lib.qcgc_state.shadow_stack += 1

    def pop_root(self):
        lib.qcgc_state.shadow_stack -= 1
        return ffi.cast("void *", lib.qcgc_state.shadow_stack[0])

    def allocate(self, size):
        assert size < 2**16
        o = lib.qcgc_allocate(self.header_size + size)
        lib._set_type_id(o, size)
        return ffi.cast("myobject_t *", o)

    def allocate_ref(self, size):
        assert size < 2**16
        o = lib.qcgc_allocate(self.header_size + size * ffi.sizeof("myobject_t *"))
        lib._set_type_id(o, size + 2**16)
        return ffi.cast("myobject_t *", o)

    def set_ref(self, obj, index, ref):
        lib.qcgc_write(ffi.cast("object_t *", obj)) # Trigger write barrier
        fields = ffi.cast("myobject_t **", obj + 1)
        fields[index] = ref

    def get_ref(self, obj, index):
        fields = ffi.cast("myobject_t **", obj + 1)
        return fields[index]

    def ss_size(self):
        return lib.qcgc_state.shadow_stack - lib.qcgc_state.shadow_stack_base
