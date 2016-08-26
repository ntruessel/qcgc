import unittest
from support import lib,ffi
from qcgc_test import QCGCTest

class LargeAllocateTestCase(QCGCTest):
    def test_arena_size_allocation(self):
        o = lib.qcgc_allocate(lib.qcgc_arena_size)
        self.assertNotEqual(ffi.NULL, o)
        self.assertTrue(self.hbtable_has(o))
        self.assertFalse(self.hbtable_marked(o))
        self.assertFalse(self.hbtable_gray_stack_has(o))

    def test_mark_large(self):
        o = lib.qcgc_allocate(lib.qcgc_arena_size)
        lib.qcgc_shadowstack_push(o)
        lib.qcgc_mark_all()
        self.assertTrue(self.hbtable_has(o))
        self.assertTrue(self.hbtable_marked(o))
        self.assertFalse(self.hbtable_gray_stack_has(o))

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

    def hbtable_gray_stack_has(self, o):
        for i in range(lib.qcgc_hbtable.gray_stack.index):
            if (lib.qcgc_hbtable.gray_stack.items[i] == o):
                return True
        return False

if __name__ == "__main__":
    unittest.main()
