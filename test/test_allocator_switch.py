from support import lib,ffi
from qcgc_test import QCGCTest
import unittest

class AllocatorSwitchTest(QCGCTest):
    def test_simple_switch(self):
        objs = list()
        for _ in range(lib.qcgc_arena_cells_count - lib.qcgc_arena_first_cell_index - 1):
            o = self.allocate(1)
            self.push_root(o)
            objs.append(o)
        #
        for o in objs:
            self.assertEqual(self.get_blocktype(ffi.cast("cell_t *",o)), lib.BLOCK_WHITE)

        lib.qcgc_reset_bump_ptr()
        lib.qcgc_collect(False)
        self.assertEqual(lib._qcgc_bump_allocator.ptr, ffi.NULL)
        self.assertEqual(lib._qcgc_bump_allocator.end, ffi.NULL)
        self.allocate(1)
        self.assertEqual(lib._qcgc_bump_allocator.ptr, ffi.NULL)
        self.assertEqual(lib._qcgc_bump_allocator.end, ffi.NULL)

if __name__ == "__main__":
    unittest.main()
