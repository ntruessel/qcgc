import unittest
from support import lib,ffi
from qcgc_test import QCGCTest

class FitAllocatorTest(QCGCTest):
    def test_initialization(self):
        # self.assertEqual( <config_value> ,lib.arenas().size)
        self.assertEqual(1, lib.arenas().count)
        self.assertNotEqual(ffi.NULL, lib.arenas().items)
        # self.assertEqual( <config_value> ,lib.free_arenas().size)
        self.assertEqual(0, lib.free_arenas().count)
        self.assertNotEqual(ffi.NULL, lib.free_arenas().items)
        self.assertEqual(ffi.addressof(lib.arena_cells(lib.arenas().items[0])[lib.qcgc_arena_first_cell_index]), lib._qcgc_bump_allocator.ptr)
        self.assertEqual(lib.qcgc_arena_cells_count - lib.qcgc_arena_first_cell_index, self.bump_remaining_cells())
        for i in range(lib.qcgc_small_free_lists):
            self.assertEqual(lib.QCGC_SMALL_FREE_LIST_INIT_SIZE, lib.small_free_list(i).size)
            self.assertEqual(0, lib.small_free_list(i).count)
            self.assertNotEqual(ffi.NULL, lib.small_free_list(i).items)
        for i in range(lib.qcgc_large_free_lists):
            self.assertEqual(lib.QCGC_LARGE_FREE_LIST_INIT_SIZE, lib.large_free_list(i).size)
            self.assertEqual(0, lib.large_free_list(i).count)
            self.assertNotEqual(ffi.NULL, lib.large_free_list(i).items)

    def test_macro_consistency(self):
        self.assertEqual(2**lib.QCGC_LARGE_FREE_LIST_FIRST_EXP, lib.qcgc_small_free_lists + 1)
        last_exp = lib.QCGC_LARGE_FREE_LIST_FIRST_EXP + lib.qcgc_large_free_lists - 1
        self.assertEqual(2**last_exp * 16, 2**lib.QCGC_LARGE_ALLOC_THRESHOLD_EXP)

    def test_small_free_list_index(self):
        for i in range(1, lib.qcgc_small_free_lists + 1):
            self.assertTrue(lib.is_small(i))
            self.assertEqual(lib.small_index(i), i - 1)
            self.assertTrue(lib.small_index_to_cells(i - 1), i)
            self.assertLess(lib.small_index(i), lib.qcgc_small_free_lists)

    def test_large_free_list_index(self):
        index = -1;
        for i in range(2**lib.QCGC_LARGE_FREE_LIST_FIRST_EXP, 2**lib.QCGC_LARGE_ALLOC_THRESHOLD_EXP // 16):
            if (i & (i - 1) == 0):
                # Check for power of two
                index = index + 1
            self.assertFalse(lib.is_small(i))
            self.assertEqual(index, lib.large_index(i))
            self.assertLess(lib.large_index(i), lib.qcgc_large_free_lists)

    def test_block_validity_check(self):
        arena = lib.qcgc_arena_create()
        first = ffi.addressof(lib.arena_cells(arena)[lib.qcgc_arena_first_cell_index])
        self.assertTrue(lib.valid_block(first, lib.qcgc_arena_cells_count - lib.qcgc_arena_first_cell_index))
        lib.qcgc_arena_mark_allocated(first, 10);
        self.assertFalse(lib.valid_block(first, 10));
        self.set_blocktype(first, lib.BLOCK_FREE);
        self.assertTrue(lib.valid_block(first, 10));
        self.assertFalse(lib.valid_block(first, 8));
        self.assertFalse(lib.valid_block(first + 1, 9));
        self.assertFalse(lib.valid_block(first + 1, 8));

    def test_add_small(self):
        blocks = list()
        for i in range(1, lib.qcgc_small_free_lists + 1):
            p = self.bump_allocate_cells(i)
            lib.qcgc_arena_mark_free(p)
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
            p = self.bump_allocate_cells(size)
            lib.qcgc_arena_mark_free(p)
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
            p = self.bump_allocate_cells(i)
            lib.qcgc_arena_mark_free(p)
            lib.qcgc_fit_allocator_add(p, i)
            q = self.fit_allocate(i)
            self.assertEqual(p, q)
            q = self.fit_allocate(i)
            self.assertNotEqual(p, q)

        # Large first fit
        for i in range(lib.qcgc_large_free_lists):
            size = 2**(i + lib.QCGC_LARGE_FREE_LIST_FIRST_EXP)
            p = self.bump_allocate_cells(size)
            lib.qcgc_arena_mark_free(p)
            lib.qcgc_fit_allocator_add(p, size)
            q = self.fit_allocate(size)
            self.assertEqual(p, q)
            q = self.fit_allocate(size)
            self.assertNotEqual(p, q)

    def test_allocate_no_block(self):
        "Test allocate when no block is available"

        p = self.bump_allocate_cells(1)
        lib.qcgc_arena_mark_free(p)
        lib.qcgc_fit_allocator_add(p, 1)

        q = self.fit_allocate(2)
        self.assertEqual(ffi.NULL, q)

    def test_allocate_block_splitting(self):
        "Test allocation when blocks have to be split"
        # Small block
        size = lib.qcgc_small_free_lists
        p = self.bump_allocate_cells(size)
        lib.qcgc_arena_mark_free(p)
        lib.qcgc_fit_allocator_add(p, size)

        q = self.fit_allocate(1)
        self.assertEqual(q, p)
        q = self.fit_allocate(size - 1)
        self.assertEqual(q, p + 1)

        # Large block
        size = 2**(1 + lib.QCGC_LARGE_FREE_LIST_FIRST_EXP)
        p = self.bump_allocate_cells(size)
        lib.qcgc_arena_mark_free(p)
        lib.qcgc_fit_allocator_add(p, size)

        q = self.fit_allocate(1)
        self.assertEqual(q, p)
        q = self.fit_allocate(size - 2)
        self.assertEqual(q, p + 1)
        q = self.fit_allocate(1)
        self.assertEqual(q, p + size - 1)

    @unittest.skip("Free lists do not contain invalid blocks")
    def test_allocate_coalesced_block(self):
        "Test allocation when there are invalid blocks in the free lists"
        # Small block
        # coalesced area no 1
        # ATOMIC! Invalidates internal invariant for short time
        x = self.bump_allocate(16)
        y = self.bump_allocate(16)
        self.bump_allocate(16) # Prevent non-coalesced arena
        lib.qcgc_arena_mark_free(ffi.cast("cell_t *",x))
        lib.qcgc_arena_mark_free(ffi.cast("cell_t *",y))
        lib.qcgc_fit_allocator_add(ffi.cast("cell_t *", x), 1)
        lib.qcgc_fit_allocator_add(ffi.cast("cell_t *", y), 1)
        self.set_blocktype(ffi.cast("cell_t *", y), lib.BLOCK_EXTENT)

        # only valid block
        p = self.bump_allocate_cells(1)
        lib.qcgc_arena_mark_free(p)
        lib.qcgc_fit_allocator_add(p, 1)

        # coalesced area no 2
        # ATOMIC! Invalidates internal invariant for short time
        x = self.bump_allocate(16)
        y = self.bump_allocate(16)
        self.bump_allocate(16) # Prevent non-coalesced arena
        lib.qcgc_arena_mark_free(ffi.cast("cell_t *",x))
        lib.qcgc_arena_mark_free(ffi.cast("cell_t *",y))
        lib.qcgc_fit_allocator_add(ffi.cast("cell_t *", x), 1)
        lib.qcgc_fit_allocator_add(ffi.cast("cell_t *", y), 1)
        self.set_blocktype(ffi.cast("cell_t *", y), lib.BLOCK_EXTENT)

        q = self.fit_allocate(1)
        self.assertEqual(p, q)

        # Large block
        # coalesced area no 1
        # ATOMIC! Invalidates internal invariant for short time
        x = self.bump_allocate(16 * 2**lib.QCGC_LARGE_FREE_LIST_FIRST_EXP)
        y = self.bump_allocate(16 * 2**lib.QCGC_LARGE_FREE_LIST_FIRST_EXP)
        self.bump_allocate(16) # Prevent non-coalesced arena
        lib.qcgc_arena_mark_free(ffi.cast("cell_t *",x))
        lib.qcgc_arena_mark_free(ffi.cast("cell_t *",y))
        lib.qcgc_fit_allocator_add(ffi.cast("cell_t *", x), 2**lib.QCGC_LARGE_FREE_LIST_FIRST_EXP)
        lib.qcgc_fit_allocator_add(ffi.cast("cell_t *", y), 2**lib.QCGC_LARGE_FREE_LIST_FIRST_EXP)
        self.set_blocktype(ffi.cast("cell_t *", y), lib.BLOCK_EXTENT)

        # only valid block
        p = self.bump_allocate_cells(2**lib.QCGC_LARGE_FREE_LIST_FIRST_EXP)
        lib.qcgc_arena_mark_free(p)
        lib.qcgc_fit_allocator_add(p, 2**lib.QCGC_LARGE_FREE_LIST_FIRST_EXP)

        # coalesced area no 2
        # ATOMIC! Invalidates internal invariant for short time
        x = self.bump_allocate(16 * 2**lib.QCGC_LARGE_FREE_LIST_FIRST_EXP)
        y = self.bump_allocate(16 * 2**lib.QCGC_LARGE_FREE_LIST_FIRST_EXP)
        self.bump_allocate(16) # Prevent non-coalesced arena
        lib.qcgc_arena_mark_free(ffi.cast("cell_t *",x))
        lib.qcgc_arena_mark_free(ffi.cast("cell_t *",y))
        lib.qcgc_fit_allocator_add(ffi.cast("cell_t *", x), 2**lib.QCGC_LARGE_FREE_LIST_FIRST_EXP)
        lib.qcgc_fit_allocator_add(ffi.cast("cell_t *", y), 2**lib.QCGC_LARGE_FREE_LIST_FIRST_EXP)
        self.set_blocktype(ffi.cast("cell_t *", y), lib.BLOCK_EXTENT)

        q = self.fit_allocate(2**lib.QCGC_LARGE_FREE_LIST_FIRST_EXP)
        self.assertEqual(p, q)

    def test_fit_allocate_no_double_entry(self):
        roots = list()
        x = self.bump_allocate(16 * 3)
        roots.append(x)
        self.bump_allocate(16 * 1)
        roots.append(self.bump_allocate(16 * 1))
        #
        for r in roots:
            self.push_root(r)
        lib.bump_ptr_reset()
        lib.qcgc_collect()
        for _ in roots:
            self.pop_root()
        #
        self.assertEqual(lib.small_free_list(0).count, 1)
        #
        del roots[0]
        for r in roots:
            self.push_root(r)
        lib.qcgc_collect()
        for _ in roots:
            self.pop_root()
        #
        self.assertEqual(lib.small_free_list(3).count, 1)
        #
        y = lib.qcgc_fit_allocate(16 * 3) # Create double entry
        self.assertEqual(lib.small_free_list(3).count, 0)
        self.assertEqual(lib.small_free_list(0).count, 1)
        self.assertEqual(x, y)

    def fit_allocate(self, cells):
        p = lib.qcgc_fit_allocate(cells * 16)
        return ffi.cast("cell_t *", p)

    def bump_allocate_cells(self, cells):
        p = self.bump_allocate(cells * 16)
        self.bump_allocate(16)   # Prevent non-coalseced arena
        return ffi.cast("cell_t *", p)


if __name__ == "__main__":
    unittest.main()
