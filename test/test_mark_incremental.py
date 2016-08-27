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

        mark_all_inc()

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

        mark_all_inc()

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

        mark_all_inc()

        for p in reachable:
            self.assertEqual(lib.qcgc_arena_get_blocktype(ffi.cast("cell_t *", p)), lib.BLOCK_BLACK)

        for p in unreachable:
            self.assertEqual(lib.qcgc_arena_get_blocktype(ffi.cast("cell_t *", p)), lib.BLOCK_WHITE)

    def test_color_transitions(self):
        """Test all possible color transitions"""
        reachable = list()
        unreachable = list()

        for i in range(2 * lib.QCGC_INC_MARK_MIN):
            o = self.allocate_ref(1)
            self.push_root(o)
            reachable.append(o)

        for o in reachable:
            self.assertEqual(lib.qcgc_get_mark_color(ffi.cast("object_t *",o)), lib.MARK_COLOR_LIGHT_GRAY)

        lib.qcgc_mark_incremental()
        self.assertEqual(lib.qcgc_state.phase, lib.GC_MARK)

        for o in reachable:
            self.assertIn(lib.qcgc_get_mark_color(ffi.cast("object_t *", o)), [lib.MARK_COLOR_BLACK, lib.MARK_COLOR_DARK_GRAY])
            if (lib.qcgc_get_mark_color(ffi.cast("object_t *", o)) == lib.MARK_COLOR_BLACK):
                # Trigger write barrier and add object
                p = self.allocate(1)
                self.set_ref(o, 0, p)
                reachable.append(o)
                self.assertEqual(lib.qcgc_get_mark_color(ffi.cast("object_t *", o)), lib.MARK_COLOR_DARK_GRAY)

        lib.qcgc_mark_all()

        for o in reachable:
            self.assertEqual(lib.qcgc_get_mark_color(ffi.cast("object_t *", o)), lib.MARK_COLOR_BLACK)

        lib.qcgc_sweep()

        for o in reachable:
            self.assertEqual(lib.qcgc_get_mark_color(ffi.cast("object_t *", o)), lib.MARK_COLOR_WHITE)

    def test_root_changes_while_marking(self):
        reachable = list()
        for _ in range(10):
            p, objs = self.gen_structure_1()
            self.push_root(p)
            reachable.extend(objs)
        #
        unreachable = list()
        for _ in range(10):
            p, objs = self.gen_structure_1()
            unreachable.extend(objs)
        #
        lib.qcgc_mark_incremental()
        #
        # Generate new roots
        objects = self.gen_circular_structure(100)
        self.push_root(objects[0])
        reachable.extend(objects)

        mark_all_inc()

        for p in reachable:
            self.assertEqual(lib.qcgc_arena_get_blocktype(ffi.cast("cell_t *", p)), lib.BLOCK_BLACK)

        for p in unreachable:
            self.assertEqual(lib.qcgc_arena_get_blocktype(ffi.cast("cell_t *", p)), lib.BLOCK_WHITE)


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

    def gen_circular_structure(self, size):
        assert size >= 1

        first = self.allocate_ref(1)
        objects = [first]
        p = first

        # Build chain
        for _ in range(size - 1):
            q = self.allocate_ref(1)
            objects.append(q)
            self.set_ref(p, 0, q)
            p = q

        # Close cycle
        self.set_ref(p, 0, first)
        return objects

def mark_all_inc():
    lib.qcgc_mark_incremental()
    while(lib.qcgc_state.phase == lib.GC_MARK):
        lib.qcgc_mark_incremental()

if __name__ == "__main__":
    unittest.main()
