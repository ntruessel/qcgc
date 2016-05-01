from support import lib, ffi
from qcgc_test import QCGCTest

class BasicTestCase(QCGCTest):
    def test_single_allocate(self):
        p = lib.qcgc_allocate(10)
        self.assertNotEqual(p, ffi.NULL)

    def test_shadow_stack(self):
        p = ffi.cast("void *", 0x0123456789abcdef)
        q = ffi.cast("void *", 0xfedcba9876543210)

        self.push_root(p)
        self.assertEqual(self.ss_size(), 1)

        self.push_root(q)
        self.assertEqual(self.ss_size(), 2)

        self.assertEqual(self.pop_root(), q)
        self.assertEqual(self.ss_size(), 1)

        self.assertEqual(self.pop_root(), p)
        self.assertEqual(self.ss_size(), 0)
