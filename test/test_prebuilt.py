import unittest
from support import lib,ffi
from qcgc_test import QCGCTest

class PrebuiltObjectTestCase(QCGCTest):
    def test_prebuilt(self):
        p = self.allocate_prebuilt(1)
        q = self.allocate_prebuilt_ref(4)
        r = self.allocate(1)
        s = self.allocate_ref(4)
        self.set_ref(q, 0, p)
        self.set_ref(q, 1, q)
        self.set_ref(q, 2, r)
        self.set_ref(q, 3, s)

        self.set_ref(s, 0, p)
        self.set_ref(s, 1, q)
        self.set_ref(s, 2, r)
        self.set_ref(s, 3, s)

        lib.bump_ptr_reset()
        lib.qcgc_collect()
        self.assertEqual(lib.qcgc_arena_get_blocktype(ffi.cast("cell_t *", r)), lib.BLOCK_WHITE)
        self.assertEqual(lib.qcgc_arena_get_blocktype(ffi.cast("cell_t *", s)), lib.BLOCK_WHITE)

    def test_incremental(self):
        o = self.allocate_prebuilt_ref(2)
        p = self.allocate(1)
        q = self.allocate(2)
        self.set_ref(o, 0, p)
        #
        lib.qcgc_mark_incremental()
        #
        self.assertEqual(lib.qcgc_arena_get_blocktype(ffi.cast("cell_t *", p)), lib.BLOCK_BLACK)
        self.assertEqual(lib.qcgc_arena_get_blocktype(ffi.cast("cell_t *", q)), lib.BLOCK_WHITE)
        #
        self.set_ref(o, 1, q)
        #
        lib.qcgc_mark_incremental()
        #
        r = self.allocate_prebuilt_ref(1)
        s = self.allocate(2)
        self.set_ref(r, 0, s)
        #
        lib.qcgc_mark_incremental()
        #
        self.assertEqual(lib.qcgc_arena_get_blocktype(ffi.cast("cell_t *", p)), lib.BLOCK_BLACK)
        self.assertEqual(lib.qcgc_arena_get_blocktype(ffi.cast("cell_t *", q)), lib.BLOCK_BLACK)
        self.assertEqual(lib.qcgc_arena_get_blocktype(ffi.cast("cell_t *", s)), lib.BLOCK_BLACK)
        

if __name__ == "__main__":
    unittest.main()
