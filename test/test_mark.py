from support import lib,ffi
from qcgc_test import QCGCTest

class MarkTestCase(QCGCTest):
    def test_no_references(self):
        """Test mark for objects that don't contain refernces"""
        roots = list()
        garbage = list()

        for _ in range(100):
            p = self.allocate(10)
            self.push_root(p)
            roots.append(p)

            p = self.allocate(3)
            garbage.append(p)

        lib.qcgc_mark()

        for p in roots:
            self.assertEqual(lib.qcgc_arena_get_blocktype(p), lib.BLOCK_BLACK)

        for p in garbage:
            self.assertEqual(lib.qcgc_arena_get_blocktype(p), lib.BLOCK_WHITE)
