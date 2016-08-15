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
            p = self.bump_allocate(i)
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
            p = self.bump_allocate(size)
            blocks.append(p)
            lib.qcgc_fit_allocator_add(p, size)

        for i in range(lib.qcgc_large_free_lists):
            size = 2**(i + lib.QCGC_LARGE_FREE_LIST_FIRST_EXP)
            l = lib.large_free_list(i)
            self.assertEqual(l.count, 1)
            self.assertEqual(blocks[i], l.items[0].ptr)
            self.assertEqual(size, l.items[0].size)

    def test_allocate_exact(self):
        "Test allocate when there is always exactly the size needed"

        # Small first fit
        for i in range(1, lib.qcgc_small_free_lists + 1):
            p = self.bump_allocate(i)
            lib.qcgc_arena_mark_free(p)
            lib.qcgc_fit_allocator_add(p, i)
            q = self.fit_allocate(i)
            self.assertEqual(p, q)
            q = self.fit_allocate(i)
            self.assertNotEqual(p, q)

        # Large first fit
        for i in range(lib.qcgc_large_free_lists):
            size = 2**(i + lib.QCGC_LARGE_FREE_LIST_FIRST_EXP)
            p = self.bump_allocate(size)
            lib.qcgc_arena_mark_free(p)
            lib.qcgc_fit_allocator_add(p, size)
            q = self.fit_allocate(size)
            self.assertEqual(p, q)
            q = self.fit_allocate(size)
            self.assertNotEqual(p, q)

    def test_allocate_no_block(self):
        "Test allocate when no block is available"

        p = self.bump_allocate(1)
        lib.qcgc_arena_mark_free(p)
        lib.qcgc_fit_allocator_add(p, 1)

        old_bump_ptr = lib.bump_ptr()
        q = self.fit_allocate(2)
        self.assertEqual(old_bump_ptr, q)

    def test_allocate_block_splitting(self):
        "Test alloation when blocks have to be split"
        # Small block
        size = lib.qcgc_small_free_lists
        p = self.bump_allocate(size)
        lib.qcgc_arena_mark_free(p)
        lib.qcgc_fit_allocator_add(p, size)

        q = self.fit_allocate(1)
        self.assertEqual(q, p)
        q = self.fit_allocate(size - 1)
        self.assertEqual(q, p + 1)

        # Large block
        size = 2**(1 + lib.QCGC_LARGE_FREE_LIST_FIRST_EXP)
        p = self.bump_allocate(size)
        lib.qcgc_arena_mark_free(p)
        lib.qcgc_fit_allocator_add(p, size)

        q = self.fit_allocate(1)
        self.assertEqual(q, p)
        q = self.fit_allocate(size - 2)
        self.assertEqual(q, p + 1)
        q = self.fit_allocate(1)
        self.assertEqual(q, p + size - 1)

    def test_allocate_coalesced_block(self):
        "Test allocation when there are invalid blocks in the free lists"
        # Small block
        p = self.bump_allocate(1)
        lib.qcgc_arena_mark_free(p)
        lib.qcgc_fit_allocator_add(p, 1)

        q = self.bump_allocate(1)
        lib.qcgc_arena_mark_free(q)
        lib.qcgc_fit_allocator_add(q, 1)

        r = self.bump_allocate(1)
        lib.qcgc_arena_mark_free(r)
        lib.qcgc_fit_allocator_add(r, 1)

        lib.qcgc_arena_set_blocktype(q, lib.BLOCK_EXTENT)

        s = self.fit_allocate(1)
        self.assertEqual(s, r)

        # Large block
        p = self.bump_allocate(2**lib.QCGC_LARGE_FREE_LIST_FIRST_EXP)
        lib.qcgc_arena_mark_free(p)
        lib.qcgc_fit_allocator_add(p, 2**lib.QCGC_LARGE_FREE_LIST_FIRST_EXP)

        q = self.bump_allocate(2**lib.QCGC_LARGE_FREE_LIST_FIRST_EXP)
        lib.qcgc_arena_mark_free(q)
        lib.qcgc_fit_allocator_add(q, 2**lib.QCGC_LARGE_FREE_LIST_FIRST_EXP)

        r = self.bump_allocate(2**lib.QCGC_LARGE_FREE_LIST_FIRST_EXP)
        lib.qcgc_arena_mark_free(r)
        lib.qcgc_fit_allocator_add(r, 2**lib.QCGC_LARGE_FREE_LIST_FIRST_EXP)

        lib.qcgc_arena_set_blocktype(q, lib.BLOCK_EXTENT)

        s = self.fit_allocate(2**lib.QCGC_LARGE_FREE_LIST_FIRST_EXP)
        self.assertEqual(s, r)

    def fit_allocate(self, size):
        p = lib.fit_allocator_allocate(size)
        lib.qcgc_arena_mark_allocated(p, size)
        return p

    def bump_allocate(self, size):
        p = lib.bump_allocator_allocate(size)
        lib.qcgc_arena_mark_allocated(p, size)
        return p


if __name__ == "__main__":
    unittest.main()
