from support import lib,ffi
from qcgc_test import QCGCTest

class AllocatorTest(QCGCTest):
    def test_cells_to_bytes(self):
        for i in range(1,17):
            self.assertEqual(1, lib.bytes_to_cells(i))
        self.assertEqual(2, lib.bytes_to_cells(17))

    def test_init_values(self):
        self.assertNotEqual(ffi.NULL, lib.arenas)
        for i in range(lib.qcgc_small_free_lists):
            l = lib.small_free_list(i)
            self.assertNotEqual(ffi.NULL, l)
        for i in range(lib.qcgc_large_free_lists):
            l = lib.large_free_list(i)
            self.assertNotEqual(ffi.NULL, l)

    def test_large_allocate(self):
        p = self.allocate(2**22)
        self.assertNotEqual(ffi.NULL, p)
