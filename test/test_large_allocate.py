import unittest
from support import lib,ffi
from qcgc_test import QCGCTest

class LargeAllocateTestCase(QCGCTest):
    def test_arena_size_allocation(self):
        o = lib.qcgc_allocate(lib.qcgc_arena_size)
        self.assertNotEqual(ffi.NULL, o)
        self.assertTrue(self.hbtable_has(o))
        self.assertFalse(lib.qcgc_hbtable_is_marked(o))
        self.assertEqual(lib.qcgc_state.gray_stack_size, 0)

    def test_mark_large(self):
        o = ffi.cast("object_t *", self.allocate(lib.qcgc_arena_size))
        self.push_root(o)
        p = ffi.cast("object_t *", self.allocate_ref(lib.qcgc_arena_size // ffi.sizeof("myobject_t *")))
        self.push_root(p)
        q = ffi.cast("object_t *", self.allocate(lib.qcgc_arena_size))
        self.push_root(q)
        r = ffi.cast("object_t *", self.allocate(1))
        self.push_root(r)
        s = ffi.cast("object_t *", self.allocate_ref(1))
        self.push_root(s)
        t = ffi.cast("object_t *", self.allocate(lib.qcgc_arena_size))
        self.push_root(t)
        self.set_ref(p, 0, q)
        self.set_ref(p, 1, r)
        self.set_ref(p, 2, s)
        self.set_ref(s, 0, p)
        #
        for _ in range(6):
            self.pop_root()
        self.push_root(o)
        self.push_root(s)
        #
        lib.qcgc_mark()
        #
        self.assertTrue(self.hbtable_has(o))
        self.assertTrue(self.hbtable_marked(o))
        self.assertEqual(lib.qcgc_state.gray_stack_size, 0)
        #
        self.assertTrue(self.hbtable_has(p))
        self.assertTrue(self.hbtable_marked(p))
        self.assertEqual(lib.qcgc_state.gray_stack_size, 0)
        #
        self.assertTrue(self.hbtable_has(q))
        self.assertTrue(self.hbtable_marked(q))
        self.assertEqual(lib.qcgc_state.gray_stack_size, 0)
        #
        self.assertTrue(self.hbtable_has(t))
        self.assertFalse(self.hbtable_marked(t))
        self.assertEqual(lib.qcgc_state.gray_stack_size, 0)
        #
        self.assertEqual(self.get_blocktype(
            ffi.cast("cell_t *", s)), lib.BLOCK_BLACK)
        self.assertEqual(self.get_blocktype(
            ffi.cast("cell_t *", r)), lib.BLOCK_BLACK)
        #
        lib.bump_ptr_reset()
        lib.qcgc_sweep(False)
        #
        self.assertTrue(self.hbtable_has(o))
        self.assertFalse(self.hbtable_marked(o))
        self.assertEqual(lib.qcgc_state.gray_stack_size, 0)
        #
        self.assertTrue(self.hbtable_has(p))
        self.assertFalse(self.hbtable_marked(p))
        self.assertEqual(lib.qcgc_state.gray_stack_size, 0)
        #
        self.assertTrue(self.hbtable_has(q))
        self.assertFalse(self.hbtable_marked(q))
        self.assertEqual(lib.qcgc_state.gray_stack_size, 0)
        #
        self.assertFalse(self.hbtable_has(t))
        self.assertFalse(self.hbtable_marked(t))
        self.assertEqual(lib.qcgc_state.gray_stack_size, 0)
        #
        self.assertEqual(self.get_blocktype(
            ffi.cast("cell_t *", s)), lib.BLOCK_WHITE)
        self.assertEqual(self.get_blocktype(
            ffi.cast("cell_t *", r)), lib.BLOCK_WHITE)

    def test_incremenatal(self):
        o = ffi.cast("object_t *", self.allocate_ref(lib.qcgc_arena_size // ffi.sizeof("myobject_t *")))
        self.push_root(o)
        p = ffi.cast("object_t *", self.allocate(1))
        self.push_root(p)
        q = ffi.cast("object_t *", self.allocate(1))
        self.set_ref(o, 0, p)
        #
        self.pop_root()
        lib.qcgc_incmark()
        #
        self.assertTrue(self.hbtable_has(o))
        self.assertTrue(self.hbtable_marked(o))
        self.assertFalse(self.gp_gray_stack_has(o))
        #
        self.assertEqual(self.get_blocktype(
            ffi.cast("cell_t *", p)), lib.BLOCK_BLACK)
        self.assertEqual(self.get_blocktype(
            ffi.cast("cell_t *", q)), lib.BLOCK_WHITE)
        #
        self.set_ref(o, 1, q)
        self.assertTrue(self.gp_gray_stack_has(o))
        #
        lib.qcgc_incmark()
        #
        self.assertTrue(self.hbtable_has(o))
        self.assertTrue(self.hbtable_marked(o))
        self.assertFalse(self.gp_gray_stack_has(o))
        #
        self.assertEqual(self.get_blocktype(
            ffi.cast("cell_t *", p)), lib.BLOCK_BLACK)
        self.assertEqual(self.get_blocktype(
            ffi.cast("cell_t *", q)), lib.BLOCK_BLACK)

    def hbtable_has(self, o):
        b = lib.bucket(o)
        for i in range(lib.qcgc_hbtable.bucket[b].count):
            if (lib.qcgc_hbtable.bucket[b].items[i].object == o):
                return True
        return False

    def hbtable_marked(self, o):
        b = lib.bucket(o)
        for i in range(lib.qcgc_hbtable.bucket[b].count):
            if (lib.qcgc_hbtable.bucket[b].items[i].object == o):
                return (lib.qcgc_hbtable.bucket[b].items[i].mark_flag == lib.qcgc_hbtable.mark_flag_ref)
        return False

if __name__ == "__main__":
    unittest.main()
