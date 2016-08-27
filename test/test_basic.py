from support import lib, ffi
from qcgc_test import QCGCTest

class BasicTestCase(QCGCTest):
    def test_single_allocate(self):
        p = lib.qcgc_allocate(10)
        self.assertNotEqual(p, ffi.NULL)

    def test_ref_set(self):
        p = self.allocate_ref(1)
        q = self.allocate(1)
        self.set_ref(p, 0, q)
        self.assertEqual(self.get_ref(p, 0),  q)

    def test_self_allocate(self):
        p = self.allocate(1)
        self.assertEqual(lib._get_type_id(ffi.cast("object_t *", p)), 0)
        p = self.allocate_ref(1)
        self.assertEqual(lib._get_type_id(ffi.cast("object_t *", p)), 1)

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
