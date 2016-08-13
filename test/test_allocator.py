from support import lib,ffi
from qcgc_test import QCGCTest

class AllocatorTest(QCGCTest):
    def test_cells_to_bytes(self):
        for i in range(1,17):
            self.assertEqual(1, lib.bytes_to_cells(i))
        self.assertEqual(2, lib.bytes_to_cells(17))
