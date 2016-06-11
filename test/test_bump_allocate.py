from support import lib, ffi
from qcgc_test import QCGCTest

class BumpAllocatorTest(QCGCTest):
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
