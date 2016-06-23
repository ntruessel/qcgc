from support import lib,ffi
from qcgc_test import QCGCTest
import unittest

class MarkTestCase(QCGCTest):
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

        lib.qcgc_mark()

        for p in roots:
            self.assertEqual(lib.qcgc_arena_get_blocktype(p), lib.BLOCK_BLACK)

        for p in garbage:
            self.assertEqual(lib.qcgc_arena_get_blocktype(p), lib.BLOCK_WHITE)

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

        lib.qcgc_mark()

        for p in reachable:
            self.assertEqual(lib.qcgc_arena_get_blocktype(p), lib.BLOCK_BLACK)

        for p in unreachable:
            self.assertEqual(lib.qcgc_arena_get_blocktype(p), lib.BLOCK_WHITE)

    def gen_structure_1(self):
        result = self.allocate_ref(6)
        result_list = [result]

        for i in range(5):
            p = self.allocate(1)
            result_list.append(p)
            self.set_ref(result, i, p)
        p = self.allocate_ref(1)
        result_list.append(p)
        self.set_ref(result, 5, p)

        q = self.allocate(1)
        result_list.append(q)
        self.set_ref(p, 0, q)
        return result, result_list

if __name__ == "__main__":
    unittest.main()
