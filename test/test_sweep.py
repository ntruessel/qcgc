from support import lib,ffi
from qcgc_test import QCGCTest
import unittest

class SweepTestCase(QCGCTest):
    def test_arena_sweep_white(self):
        arena = lib.qcgc_arena_create()
        i = lib.qcgc_arena_first_cell_index

        for j in range(10):
            lib.qcgc_arena_mark_allocated(
                    ffi.addressof(lib.arena_cells(arena)[i + j]),
                    1)
        self.assertEqual(lib.qcgc_arena_white_blocks(arena), 10)

        self.assertTrue(lib.qcgc_arena_sweep(arena))
        self.assertEqual(lib.qcgc_arena_black_blocks(arena), 0)
        self.assertEqual(lib.qcgc_arena_white_blocks(arena), 0)
        self.assertEqual(lib.qcgc_arena_free_blocks(arena), 1)

        self.assertTrue(lib.qcgc_arena_is_empty(arena))
        self.assertTrue(lib.qcgc_arena_is_coalesced(arena))
        for i in range(lib.qcgc_small_free_lists):
            self.assertEqual(0, lib.small_free_list(i).count)

        for i in range(lib.qcgc_large_free_lists):
            self.assertEqual(0, lib.large_free_list(i).count)

    def test_arena_sweep_black(self):
        arena = lib.qcgc_arena_create()
        i = lib.qcgc_arena_first_cell_index

        for j in range(10):
            p = ffi.addressof(lib.arena_cells(arena)[i + j])
            lib.qcgc_arena_mark_allocated(p, 1)
            lib.qcgc_arena_set_blocktype(p, lib.BLOCK_BLACK)

        self.assertEqual(lib.qcgc_arena_black_blocks(arena), 10)

        self.assertFalse(lib.qcgc_arena_sweep(arena))
        self.assertEqual(lib.qcgc_arena_black_blocks(arena), 0)
        self.assertEqual(lib.qcgc_arena_white_blocks(arena), 10)
        self.assertEqual(lib.qcgc_arena_free_blocks(arena), 1)

        self.assertTrue(lib.qcgc_arena_is_coalesced(arena))
        for i in range(lib.qcgc_small_free_lists):
            self.assertEqual(0, lib.small_free_list(i).count)

        # NO large free blocks, as the last block was already marked free, hence
        # it has to be registered previously
        for i in range(lib.qcgc_large_free_lists):
            self.assertEqual(0, lib.large_free_list(i).count)

    def test_arena_sweep_mixed(self):
        arena = lib.qcgc_arena_create()
        i = lib.qcgc_arena_first_cell_index

        layout = [ (0, lib.BLOCK_WHITE)
                 , (20, lib.BLOCK_BLACK)
                 , (32, lib.BLOCK_BLACK)
                 , (42, lib.BLOCK_BLACK)
                 , (43, lib.BLOCK_WHITE)
                 , (44, lib.BLOCK_WHITE)
                 ]

        for b in layout:
            p = ffi.addressof(lib.arena_cells(arena)[i + b[0]])
            lib.qcgc_arena_set_blocktype(p, b[1])

        self.assertEqual(lib.qcgc_arena_black_blocks(arena), 3)
        self.assertEqual(lib.qcgc_arena_white_blocks(arena), 3)

        self.assertFalse(lib.qcgc_arena_sweep(arena))
        self.assertEqual(lib.qcgc_arena_black_blocks(arena), 0)
        self.assertEqual(lib.qcgc_arena_white_blocks(arena), 3)
        self.assertEqual(lib.qcgc_arena_free_blocks(arena), 2)

        self.assertTrue(lib.qcgc_arena_is_coalesced(arena))

    def test_arena_sweep_mixed_2(self):
        arena = lib.qcgc_arena_create()
        i = lib.qcgc_arena_first_cell_index

        layout = [ (0, lib.BLOCK_WHITE)
                 , (5, lib.BLOCK_FREE)
                 , (20, lib.BLOCK_BLACK)
                 , (32, lib.BLOCK_BLACK)
                 , (33, lib.BLOCK_FREE)     # This block should not be registerd as free as it already was free and no changes were made
                 , (42, lib.BLOCK_BLACK)
                 , (43, lib.BLOCK_WHITE)
                 , (44, lib.BLOCK_WHITE)
                 , (49, lib.BLOCK_BLACK)
                 ]

        for b in layout:
            p = ffi.addressof(lib.arena_cells(arena)[i + b[0]])
            lib.qcgc_arena_set_blocktype(p, b[1])

        lib.qcgc_arena_sweep(arena)

        have_elems = [5,19]

        for i in range(lib.qcgc_small_free_lists):
            if (i in have_elems):
                self.assertEqual(1, lib.small_free_list(i).count)
            else:
                self.assertEqual(0, lib.small_free_list(i).count)

        for i in range(lib.qcgc_large_free_lists):
            self.assertEqual(0, lib.large_free_list(i).count)

    def test_arena_sweep_no_double_add(self):
        arena = lib.qcgc_arena_create()
        i = lib.qcgc_arena_first_cell_index

        layout = [ (0, lib.BLOCK_BLACK)
                 , (1, lib.BLOCK_WHITE)
                 , (2, lib.BLOCK_BLACK)
                 ]

        for b in layout:
            p = ffi.addressof(lib.arena_cells(arena)[i + b[0]])
            lib.qcgc_arena_set_blocktype(p, b[1])

        lib.qcgc_arena_sweep(arena)

        have_elems = [0]

        for i in range(lib.qcgc_small_free_lists):
            if (i in have_elems):
                self.assertEqual(1, lib.small_free_list(i).count)
            else:
                self.assertEqual(0, lib.small_free_list(i).count)

        for i in range(lib.qcgc_large_free_lists):
            self.assertEqual(0, lib.large_free_list(i).count)

        # Now mark the black blocks black again
        layout = [ (0, lib.BLOCK_BLACK)
                 , (2, lib.BLOCK_BLACK)
                 ]

        for b in layout:
            p = ffi.addressof(lib.arena_cells(arena)[i + b[0]])
            lib.qcgc_arena_set_blocktype(p, b[1])

        lib.qcgc_arena_sweep(arena)

        have_elems = [0]

        for i in range(lib.qcgc_small_free_lists):
            if (i in have_elems):
                self.assertEqual(1, lib.small_free_list(i).count)
            else:
                self.assertEqual(0, lib.small_free_list(i).count)

        for i in range(lib.qcgc_large_free_lists):
            self.assertEqual(0, lib.large_free_list(i).count)

    def test_arena_sweep_no_bump_ptr_coalescing(self):
        p = lib.qcgc_bump_allocate(16)
        arena = lib.qcgc_arena_addr(ffi.cast("cell_t *", p))

        lib.qcgc_arena_sweep(arena)

        self.assertEqual(lib.qcgc_arena_get_blocktype(ffi.cast("cell_t *", lib.bump_ptr())), lib.BLOCK_FREE)

    def test_write_barrier_after_sweep(self):
        o = self.allocate_ref(1)
        self.push_root(o)
        #
        lib.qcgc_collect()
        #
        p = self.allocate(1)
        self.set_ref(o, 0, p)
        #
        lib.bump_ptr_reset()
        lib.qcgc_collect()
        #
        self.assertIn(lib.qcgc_arena_get_blocktype(ffi.cast("cell_t *", p)), [lib.BLOCK_WHITE, lib.BLOCK_BLACK])

if __name__ == "__main__":
    unittest.main()
