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
        o = lib.allocate_prebuilt(self.header_size + size)
        self.assertNotEqual(o, ffi.NULL)
        lib._set_type_id(o, 0)
        lib.qcgc_write(o) # Register object
        return ffi.cast("myobject_t *", o)

    def allocate_prebuilt_ref(self, size):
        o = lib.allocate_prebuilt(self.header_size + size * ffi.sizeof("myobject_t *"))
        self.assertNotEqual(o, ffi.NULL)
        lib._set_type_id(o, size)
        lib.qcgc_write(o) # Register object
        return ffi.cast("myobject_t *", o)

    def set_ref(self, obj, index, ref):
        lib.qcgc_write(ffi.cast("object_t *", obj)) # Trigger write barrier
        assert index >= 0
        assert ffi.cast("myobject_t *", obj).type_id > index
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

    # Utilities for mark/sweep testing
    def gen_structure_1(self):
        result = self.allocate_ref(6)
        result_list = [result]

        for i in range(5):
            p = self.allocate(1)
            result_list.append(p)
            self.set_ref(result, i, p)
        p = self.allocate_ref(1)
        result_list.append(p)
        self.set_ref(result, 5, p)

        q = self.allocate(1)
        result_list.append(q)
        self.set_ref(p, 0, q)
        return result, result_list

    def gen_circular_structure(self, size):
        assert size >= 1

        first = self.allocate_ref(1)
        objects = [first]
        p = first

        # Build chain
        for _ in range(size - 1):
            q = self.allocate_ref(1)
            objects.append(q)
            self.set_ref(p, 0, q)
            p = q

        # Close cycle
        self.set_ref(p, 0, first)
        return objects
