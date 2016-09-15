from support import lib,ffi
from qcgc_test import QCGCTest
import unittest

class CellCountingTestCase(QCGCTest):
    arena_blocks = lib.qcgc_arena_cells_count - lib.qcgc_arena_first_cell_index

    def test_bump_all_free(self):
        for _ in range(10):
            self.push_root(self.allocate(1))
        lib.bump_ptr_reset()
        lib.qcgc_collect()
        self.assertEqual(lib.qcgc_state.free_cells, self.arena_blocks - 10)
        #
        for _ in range(10):
            self.pop_root()
        #
        lib.qcgc_collect()
        self.assertEqual(lib.qcgc_state.free_cells, 0) # As the arena is free now
        self.assertEqual(lib.qcgc_state.largest_free_block, 0)

    def test_bump_remain_allocated(self):
        for _ in range(10):
            self.push_root(self.allocate(1))
        lib.bump_ptr_reset()
        lib.qcgc_collect()
        self.assertEqual(lib.qcgc_state.free_cells, self.arena_blocks - 10)
        lib.qcgc_collect()
        self.assertEqual(lib.qcgc_state.free_cells, self.arena_blocks - 10)

    def test_fit_all_free(self):
        for _ in range(10):
            self.allocate(1)
            self.push_root(self.allocate(1)) # Make it non coalesced
        lib.bump_ptr_reset()
        lib.qcgc_collect()
        self.assertEqual(lib.qcgc_state.free_cells, self.arena_blocks - 10)

        for _ in range(10):
            self.push_root(lib.qcgc_fit_allocate(1))

        lib.qcgc_collect()
        self.assertEqual(lib.qcgc_state.free_cells, self.arena_blocks - 20)

    def test_custom_layout_full_sweep(self):
        arena = lib.qcgc_arena_create()
        i = lib.qcgc_arena_first_cell_index

        layout = [ (0, lib.BLOCK_WHITE)
                 , (19, lib.BLOCK_FREE)
                 , (20, lib.BLOCK_BLACK)
                 , (21, lib.BLOCK_FREE)
                 , (22, lib.BLOCK_WHITE)
                 , (32, lib.BLOCK_BLACK)
                 , (33, lib.BLOCK_FREE)
                 , (42, lib.BLOCK_BLACK)
                 , (43, lib.BLOCK_WHITE)
                 ]

        for b in layout:
            p = ffi.addressof(lib.arena_cells(arena)[i + b[0]])
            self.set_blocktype(p, b[1])

        lib.qcgc_state.free_cells = 0
        lib.qcgc_state.largest_free_block = 0
        lib.qcgc_arena_sweep(arena)
        self.assertEqual(lib.qcgc_state.free_cells, self.arena_blocks - 3)
        self.assertEqual(lib.qcgc_state.largest_free_block,  self.arena_blocks - 43)

    def test_bump_allocate(self):
        for _ in range(2 ** 9):
            self.push_root(self.allocate(1))

        lib.bump_ptr_reset()
        lib.qcgc_collect()

        self.assertEqual(lib.qcgc_state.free_cells, self.arena_blocks - 2 ** 9)
        self.assertEqual(lib.qcgc_state.largest_free_block, self.arena_blocks - 2 ** 9)
    
if __name__ == "__main__":
    unittest.main()
