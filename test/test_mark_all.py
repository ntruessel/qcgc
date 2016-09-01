from support import lib,ffi
from qcgc_test import QCGCTest
import unittest

class MarkAllTestCase(QCGCTest):
    def test_no_references(self):
        """No references"""
        roots = list()
        garbage = list()

        for _ in range(100):
            p = self.allocate(10)
            self.push_root(p)
            roots.append(p)

            p = self.allocate(3)
            garbage.append(p)

        lib.qcgc_mark_all()

        for p in roots:
            self.assertEqual(lib.qcgc_arena_get_blocktype(ffi.cast("cell_t *", p)), lib.BLOCK_BLACK)

        for p in garbage:
            self.assertEqual(lib.qcgc_arena_get_blocktype(ffi.cast("cell_t *", p)), lib.BLOCK_WHITE)

    def test_ref_1(self):
        """Tree shaped reference struct"""

        # Generate reachable objects
        reachable = list()
        for _ in range(10):
            p, objs = self.gen_structure_1()
            self.push_root(p)
            reachable.extend(objs)

        # Generate unreachable objects
        unreachable = list()
        for _ in range(10):
            p, objs = self.gen_structure_1()
            unreachable.extend(objs)

        lib.qcgc_mark_all()

        for p in reachable:
            self.assertEqual(lib.qcgc_arena_get_blocktype(ffi.cast("cell_t *", p)), lib.BLOCK_BLACK)

        for p in unreachable:
            self.assertEqual(lib.qcgc_arena_get_blocktype(ffi.cast("cell_t *", p)), lib.BLOCK_WHITE)

    def test_circular(self):
        """Circular references"""
        reachable = list()
        unreachable = list()

        for i in range(10):
            objects = self.gen_circular_structure(i + 1)
            self.push_root(objects[0])
            reachable.extend(objects)

        for i in range(10):
            objects = self.gen_circular_structure(i + 1)
            unreachable.extend(objects)

        lib.qcgc_mark_all()

        for p in reachable:
            self.assertEqual(lib.qcgc_arena_get_blocktype(ffi.cast("cell_t *", p)), lib.BLOCK_BLACK)

        for p in unreachable:
            self.assertEqual(lib.qcgc_arena_get_blocktype(ffi.cast("cell_t *", p)), lib.BLOCK_WHITE)

if __name__ == "__main__":
    unittest.main()
