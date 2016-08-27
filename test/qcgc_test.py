from support import lib,ffi
import unittest

class QCGCTest(unittest.TestCase):
    header_size = ffi.sizeof("myobject_t")

    def setUp(self):
        lib.qcgc_initialize()

    def tearDown(self):
        lib.qcgc_destroy()

    def push_root(self, o):
        lib.qcgc_shadowstack_push(ffi.cast("object_t *", o))

    def pop_root(self):
        return lib.qcgc_shadowstack_pop()

    def allocate(self, size):
        o = lib.qcgc_allocate(self.header_size + size)
        self.assertNotEqual(o, ffi.NULL)
        lib._set_type_id(o, 0)
        return ffi.cast("myobject_t *", o)

    def allocate_ref(self, size):
        o = lib.qcgc_allocate(self.header_size + size * ffi.sizeof("myobject_t *"))
        self.assertNotEqual(o, ffi.NULL)
        lib._set_type_id(o, size)
        return ffi.cast("myobject_t *", o)

    def allocate_prebuilt(self, size):
        o = ffi.cast("object_t *", ffi.new("char[]", self.header_size + size))
        self.assertNotEqual(o, ffi.NULL)
        lib._set_type_id(o, 0)
        o.flags = lib.QCGC_PREBUILT_OBJECT
        lib.qcgc_write(o) # Register object
        return ffi.cast("myobject_t *", o)

    def allocate_prebuilt_ref(self, size):
        o = ffi.cast("object_t *", ffi.new("char[]", self.header_size + size * ffi.sizeof("myobject_t *")))
        self.assertNotEqual(o, ffi.NULL)
        lib._set_type_id(o, size)
        o.flags = lib.QCGC_PREBUILT_OBJECT
        lib.qcgc_write(o) # Register object
        return ffi.cast("myobject_t *", o)

    def set_ref(self, obj, index, ref):
        lib.qcgc_write(ffi.cast("object_t *", obj)) # Trigger write barrier
        ffi.cast("myobject_t *", obj).refs[index] = ffi.cast("myobject_t *", ref)

    def gp_gray_stack_has(self, obj):
        for i in range(lib.qcgc_state.gp_gray_stack.index):
            if (lib.qcgc_state.gp_gray_stack.items[i] == obj):
                return True
        return False


    def get_ref(self, obj, index):
        return ffi.cast("myobject_t *", obj).refs[index]

    def ss_size(self):
        return lib.qcgc_state.shadow_stack.count;
