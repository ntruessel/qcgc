import unittest
from support import lib, ffi
from qcgc_test import QCGCTest

class BumpAllocatorTest(QCGCTest):
    def test_bump_allocator_internals(self):
        arena = lib.qcgc_arena_create()
        first_cell = lib.arena_cells(arena)[lib.qcgc_arena_first_cell_index]
        size = lib.qcgc_arena_cells_count - lib.qcgc_arena_first_cell_index
        lib.bump_allocator_assign(ffi.addressof(first_cell), size)

        self.assertEqual(ffi.addressof(first_cell), lib.bump_ptr())
        self.assertEqual(size, lib.remaining_cells())

        p = lib.qcgc_bump_allocate(16)
        self.assertEqual(ffi.addressof(first_cell), p)
        self.assertEqual(size - 1, lib.remaining_cells())

        q = lib.qcgc_bump_allocate((size - 1) * 16)
        self.assertEqual(ffi.addressof(lib.arena_cells(arena)[lib.qcgc_arena_first_cell_index + 1]), q)
        self.assertEqual(0, lib.remaining_cells())

    def test_many_small_allocations(self):
        objects = set()
        p = lib.qcgc_bump_allocate(16)
        arena = lib.qcgc_arena_addr(ffi.cast("cell_t *", p))
        objects.add(p)

        for _ in range(1000):
            p = lib.qcgc_bump_allocate(16)
            objects.add(p)
            self.assertEqual(arena, lib.qcgc_arena_addr(ffi.cast("cell_t *", p)))

        self.assertFalse(ffi.NULL in objects)
        self.assertEqual(len(objects), 1001)

    def test_large_alloc_overlap(self):
        p = lib.qcgc_bump_allocate(2**19)
        q = lib.qcgc_bump_allocate(2**19)
        self.assertNotEqual(lib.qcgc_arena_addr(ffi.cast("cell_t *", p)), lib.qcgc_arena_addr(ffi.cast("cell_t *", q)))

if __name__ == "__main__":
    unittest.main()
