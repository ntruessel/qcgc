import unittest
from support import lib,ffi
from qcgc_test import QCGCTest

class HugeBlockTableTestCase(QCGCTest):
    def test_create_destroy(self):
        for i in range(lib.QCGC_HBTABLE_BUCKETS):
            self.assertNotEqual(ffi.NULL, lib.qcgc_hbtable.bucket[i])

    def test_add(self):
        o = lib.qcgc_large_allocate(1)
        #
        b = lib.bucket(o)
        self.assertTrue(self.hbtable_has(o))
        self.assertFalse(self.hbtable_marked(o))
        self.assertFalse(self.hbtable_gray_stack_has(o))

    def test_mark(self):
        o = lib.qcgc_large_allocate(1)
        lib.qcgc_hbtable_mark(o)
        #
        b = lib.bucket(o)
        self.assertTrue(self.hbtable_has(o))
        self.assertTrue(self.hbtable_marked(o))
        self.assertTrue(self.hbtable_gray_stack_has(o))
        pass

    def test_sweep(self):
        o = lib.qcgc_large_allocate(1)
        lib.qcgc_hbtable_mark(o)
        p = lib.qcgc_large_allocate(1)
        #
        lib.qcgc_gray_stack_pop(lib.qcgc_hbtable.gray_stack)
        #
        lib.qcgc_hbtable_sweep()
        #
        b = lib.bucket(o)
        self.assertTrue(self.hbtable_has(o))
        self.assertFalse(self.hbtable_marked(o))
        self.assertFalse(self.hbtable_has(p))

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
