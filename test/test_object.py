from support import lib,ffi
from qcgc_test import QCGCTest
import unittest

class ObjectTestCase(QCGCTest):
    def test_write_barrier(self):
        arena = lib.qcgc_arena_create()
        o = self.allocate(16)
        self.assertEqual(ffi.cast("object_t *", o).flags & lib.QCGC_GRAY_FLAG, 0)
        lib.qcgc_write(ffi.cast("object_t *", o))
        self.assertEqual(ffi.cast("object_t *", o).flags & lib.QCGC_GRAY_FLAG, lib.QCGC_GRAY_FLAG)

if __name__ == "__main__":
    unittest.main()
