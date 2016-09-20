import unittest
from support import lib,ffi
from qcgc_test import QCGCTest

class HugeBlockTableTestCase(QCGCTest):
    def test_create_destroy(self):
        for i in range(lib.QCGC_HBTABLE_BUCKETS):
            self.assertNotEqual(ffi.NULL, lib.qcgc_hbtable.bucket[i])

    def test_add(self):
        o = lib._qcgc_allocate_large(2**lib.QCGC_LARGE_ALLOC_THRESHOLD_EXP)
        #
        b = lib.bucket(o)
        self.assertTrue(self.hbtable_has(o))
        self.assertFalse(lib.qcgc_hbtable_is_marked(o))

    def test_mark(self):
        o = lib._qcgc_allocate_large(2**lib.QCGC_LARGE_ALLOC_THRESHOLD_EXP)
        lib.qcgc_hbtable_mark(o)
        #
        b = lib.bucket(o)
        self.assertTrue(self.hbtable_has(o))
        self.assertTrue(lib.qcgc_hbtable_is_marked(o))

    def test_sweep(self):
        o = lib._qcgc_allocate_large(2**lib.QCGC_LARGE_ALLOC_THRESHOLD_EXP)
        lib.qcgc_hbtable_mark(o)
        p = lib._qcgc_allocate_large(2**lib.QCGC_LARGE_ALLOC_THRESHOLD_EXP)
        #
        lib.qcgc_hbtable_sweep(False)
        #
        b = lib.bucket(o)
        self.assertTrue(self.hbtable_has(o))
        self.assertFalse(lib.qcgc_hbtable_is_marked(o))

    def test_mark_twice(self):
        o = lib._qcgc_allocate_large(2**lib.QCGC_LARGE_ALLOC_THRESHOLD_EXP)
        self.assertFalse(lib.qcgc_hbtable_is_marked(o))
        self.assertTrue(lib.qcgc_hbtable_mark(o))
        self.assertFalse(lib.qcgc_hbtable_mark(o))
        self.assertTrue(lib.qcgc_hbtable_is_marked(o))

    def hbtable_has(self, o):
        b = lib.bucket(o)
        for i in range(lib.qcgc_hbtable.bucket[b].count):
            if (lib.qcgc_hbtable.bucket[b].items[i].object == o):
                return True
        return False

if __name__ == "__main__":
    unittest.main()
