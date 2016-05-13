from support import lib,ffi
from qcgc_test import QCGCTest

class ArenaTestCase(QCGCTest):
    def test_size_calculations(self):
        exp = lib.QCGC_ARENA_SIZE_EXP
        size = 2**exp
        bitmap = size / 128
        effective_cells = (size - 2 * bitmap) / 16
        self.assertEqual(size, lib.qcgc_arena_size)
        self.assertEqual(bitmap, lib.qcgc_arena_bitmap_size)
        self.assertEqual(effective_cells, lib.qcgc_arena_cells_count)
