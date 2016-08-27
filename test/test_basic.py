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
