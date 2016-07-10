from support import lib,ffi
from qcgc_test import QCGCTest
import unittest

class ObjectTestCase(QCGCTest):
    def test_write_barrier(self):
        o = self.allocate(16)
        arena = lib.qcgc_arena_addr(ffi.cast("cell_t *", o))
        self.assertEqual(ffi.cast("object_t *", o).flags & lib.QCGC_GRAY_FLAG, 0)
        lib.qcgc_write(ffi.cast("object_t *", o))
        self.assertEqual(ffi.cast("object_t *", o).flags & lib.QCGC_GRAY_FLAG, lib.QCGC_GRAY_FLAG)

        lib.qcgc_state.state = lib.GC_MARK
        o = self.allocate(16)
        self.assertEqual(ffi.cast("object_t *", o).flags & lib.QCGC_GRAY_FLAG, 0)
        lib.qcgc_arena_set_blocktype(ffi.cast("cell_t *", o), lib.BLOCK_BLACK)
        lib.qcgc_write(ffi.cast("object_t *", o))
        self.assertEqual(ffi.cast("object_t *", o).flags & lib.QCGC_GRAY_FLAG, lib.QCGC_GRAY_FLAG)
        self.assertEqual(lib.arena_gray_stack(arena).index, 1)
        self.assertEqual(lib.arena_gray_stack(arena).items[0], o)

if __name__ == "__main__":
    unittest.main()
