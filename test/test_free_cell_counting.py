from support import lib,ffi
from qcgc_test import QCGCTest
import unittest

class FreeCellCountingTestCase(QCGCTest):
    arena_blocks = lib.qcgc_arena_cells_count - lib.qcgc_arena_first_cell_index

    def test_bump_all_free(self):
        for _ in range(10):
            self.allocate(1)
        self.assertEqual(lib.free_cells(), self.arena_blocks - 10)
        lib.bump_ptr_reset()
        lib.qcgc_collect()
        self.assertEqual(lib.free_cells(), self.arena_blocks)

    def test_bump_remain_allocated(self):
        for _ in range(10):
            self.push_root(self.allocate(1))
        self.assertEqual(lib.free_cells(), self.arena_blocks - 10)
        lib.bump_ptr_reset()
        lib.qcgc_collect()
        self.assertEqual(lib.free_cells(), self.arena_blocks - 10)

    def test_fit_all_free(self):
        obj = list()
        for _ in range(10):
            o = self.allocate(1)
            self.push_root(self.allocate(1)) # Make it non coalesced
            obj.append(o)
        self.assertEqual(lib.free_cells(), self.arena_blocks - 20)
        lib.bump_ptr_reset()
        lib.qcgc_collect()
        self.assertEqual(lib.free_cells(), self.arena_blocks - 10)

        for o in obj:
            lib.qcgc_fit_allocator_add(ffi.cast("cell_t *", o), 1)

        for _ in range(10):
            self.push_root(lib.qcgc_fit_allocate(1))

        self.assertEqual(lib.free_cells(), self.arena_blocks - 20)
        lib.bump_ptr_reset()
        lib.qcgc_collect()
        self.assertEqual(lib.free_cells(), self.arena_blocks - 20)



if __name__ == "__main__":
    unittest.main()
