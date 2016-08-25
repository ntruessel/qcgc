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

        lib.qcgc_collect()
        self.assertTrue(lib.qcgc_arena_get_blocktype(ffi.cast("cell_t *", r)) == lib.BLOCK_WHITE)
        self.assertTrue(lib.qcgc_arena_get_blocktype(ffi.cast("cell_t *", s)) == lib.BLOCK_WHITE)
