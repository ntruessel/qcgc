from support import lib, ffi
from qcgc_test import QCGCTest

class BumpAllocatorTest(QCGCTest):
    def test_bump_allocator_interface(self):
        arena = lib.qcgc_arena_create()
        first_cell = lib.arena_cells(arena)[lib.qcgc_arena_first_cell_index]
        size = lib.qcgc_arena_cells_count - lib.qcgc_arena_first_cell_index
        lib.qcgc_balloc_assign(ffi.addressof(first_cell), size)

        self.assertEqual(ffi.addressof(first_cell), lib.qcgc_balloc_state.bump_ptr)
        self.assertEqual(size, lib.qcgc_balloc_state.remaining_cells)

        self.assertTrue(lib.qcgc_balloc_can_allocate(size))
        self.assertFalse(lib.qcgc_balloc_can_allocate(size + 1))

        p = lib.qcgc_balloc_allocate(1)
        self.assertEqual(ffi.addressof(first_cell), p)
        self.assertEqual(size - 1, lib.qcgc_balloc_state.remaining_cells)

        q = lib.qcgc_balloc_allocate(size)
        self.assertEqual(q, ffi.NULL)
        self.assertEqual(size - 1, lib.qcgc_balloc_state.remaining_cells)

        self.assertTrue(lib.qcgc_balloc_can_allocate(size - 1))
        self.assertFalse(lib.qcgc_balloc_can_allocate(size))

        q = lib.qcgc_balloc_allocate(size - 1)
        self.assertEqual(ffi.addressof(lib.arena_cells(arena)[lib.qcgc_arena_first_cell_index + 1]), q)
        self.assertEqual(0, lib.qcgc_balloc_state.remaining_cells)

        self.assertEqual(lib.qcgc_balloc_state.remaining_cells, 0)
        self.assertFalse(lib.qcgc_balloc_can_allocate(1))

        r = lib.qcgc_balloc_allocate(1)
        self.assertEqual(r, ffi.NULL)

    def test_many_small_allocations(self):
        p = lib.qcgc_bump_allocate(16)
        self.assertNotEqual(p, ffi.NULL)
        arena = lib.qcgc_arena_addr(p)
        for i in range(1, 1000):
            q = lib.qcgc_bump_allocate(16)
            self.assertNotEqual(p, q)
            p = q
            self.assertEqual(arena, lib.qcgc_arena_addr(p))

    def test_large_alloc_overlap(self):
        p = lib.qcgc_bump_allocate(2**19)
        q = lib.qcgc_bump_allocate(2**19)
        self.assertNotEqual(lib.qcgc_arena_addr(p), lib.qcgc_arena_addr(q))
