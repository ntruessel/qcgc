import unittest
from support import lib,ffi
from qcgc_test import QCGCTest

class FitAllocatorTest(QCGCTest):
    def test_macro_consistency(self):
        self.assertEqual(2**lib.QCGC_LARGE_FREE_LIST_FIRST_EXP, lib.qcgc_small_free_lists + 1)
        last_exp = lib.QCGC_LARGE_FREE_LIST_FIRST_EXP + lib.qcgc_large_free_lists - 1
        self.assertLess(2**last_exp, 2**lib.QCGC_ARENA_SIZE_EXP)
        self.assertEqual(2**(last_exp + 1), lib.qcgc_arena_cells_count)

    def test_small_free_list_index(self):
        for i in range(1, lib.qcgc_small_free_lists + 1):
            self.assertTrue(lib.is_small(i))
            self.assertEqual(lib.small_index(i), i - 1)
            self.assertTrue(lib.small_index_to_cells(i - 1), i)
            self.assertLess(lib.small_index(i), lib.qcgc_small_free_lists)

    def test_large_free_list_index(self):
        index = -1;
        for i in range(2**lib.QCGC_LARGE_FREE_LIST_FIRST_EXP, lib.qcgc_arena_cells_count):
            if (i & (i - 1) == 0):
                # Check for power of two
                index = index + 1
            self.assertFalse(lib.is_small(i))
            self.assertEqual(index, lib.large_index(i))
            self.assertLess(lib.large_index(i), lib.qcgc_large_free_lists)

    def test_block_validity_check(self):
        arena = lib.qcgc_arena_create()
        first = ffi.addressof(lib.arena_cells(arena)[lib.qcgc_arena_first_cell_index])
        lib.qcgc_arena_mark_allocated(first, 10);
        self.assertFalse(lib.valid_block(first, 10));
        lib.qcgc_arena_set_blocktype(first, lib.BLOCK_FREE);
        self.assertTrue(lib.valid_block(first, 10));
        self.assertFalse(lib.valid_block(first, 8));
        self.assertFalse(lib.valid_block(first + 1, 9));
        self.assertFalse(lib.valid_block(first + 1, 8));

    def test_add_small(self):
        blocks = list()
        for i in range(1, lib.qcgc_small_free_lists + 1):
            p = lib.bump_allocator_allocate(i)
            blocks.append(p)
            lib.qcgc_fit_allocator_add(p, i)

        for i in range(lib.qcgc_small_free_lists):
            l = lib.small_free_list(i)
            self.assertEqual(l.count, 1)
            self.assertEqual(blocks[i], l.items[0])

    def test_add_large(self):
        blocks = list()
        for i in range(lib.qcgc_large_free_lists):
            size = 2**(i + lib.QCGC_LARGE_FREE_LIST_FIRST_EXP)
            p = lib.bump_allocator_allocate(size)
            blocks.append(p)
            lib.qcgc_fit_allocator_add(p, size)

        for i in range(lib.qcgc_large_free_lists):
            size = 2**(i + lib.QCGC_LARGE_FREE_LIST_FIRST_EXP)
            l = lib.large_free_list(i)
            self.assertEqual(l.count, 1)
            self.assertEqual(blocks[i], l.items[0].ptr)
            self.assertEqual(size, l.items[0].size)

if __name__ == "__main__":
    unittest.main()
