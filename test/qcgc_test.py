from support import lib,ffi
import unittest

class QCGCTest(unittest.TestCase):
    header_size = ffi.sizeof("myobject_t")

    def setUp(self):
        lib.qcgc_initialize()

    def tearDown(self):
        lib.qcgc_destroy()

    def push_root(self, o):
        lib.qcgc_push_root(ffi.cast("object_t *", o))

    def pop_root(self):
        lib.qcgc_pop_root(1)

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

    def allocate_weakref(self, to):
        o = lib.qcgc_allocate(self.header_size + ffi.sizeof("myobject_t *"))
        self.assertNotEqual(o, ffi.NULL)
        lib._set_type_id(o, 0)  # Prevent from tracing
        ffi.cast("myobject_t *", o).refs[0] = ffi.cast("myobject_t *", to) # Ref has to be valid before registering
        lib.qcgc_register_weakref(o, ffi.cast("object_t **",
            ffi.cast("myobject_t *", o).refs)) # XXX: ffi.addressof .refs[0] does not work
        lib.qcgc_write(o)
        return o

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

    def bump_allocate(self, size):
        if lib._qcgc_bump_allocator.remaining_cells < lib.bytes_to_cells(size):
            lib.qcgc_bump_allocator_renew_block();
        return lib.qcgc_bump_allocate(size);

    def get_ref(self, obj, index):
        return ffi.cast("myobject_t *", obj).refs[index]

    def ss_size(self):
        return lib._qcgc_shadowstack.top - lib._qcgc_shadowstack.base

    def get_blocktype(self, ptr):
        return lib.qcgc_arena_get_blocktype(lib.qcgc_arena_addr(ptr),
                lib.qcgc_arena_cell_index(ptr))

    def set_blocktype(self, ptr, blocktype):
        lib.qcgc_arena_set_blocktype(lib.qcgc_arena_addr(ptr),
                lib.qcgc_arena_cell_index(ptr),
                blocktype)

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
