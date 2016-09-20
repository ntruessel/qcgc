from support import lib,ffi
from qcgc_test import QCGCTest
import unittest

class MarkIncTestCase(QCGCTest):
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
            self.assertEqual(self.get_blocktype(ffi.cast("cell_t *", p)), lib.BLOCK_BLACK)

        for p in garbage:
            self.assertEqual(self.get_blocktype(ffi.cast("cell_t *", p)), lib.BLOCK_WHITE)

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
            self.assertEqual(self.get_blocktype(ffi.cast("cell_t *", p)), lib.BLOCK_BLACK)

        for p in unreachable:
            self.assertEqual(self.get_blocktype(ffi.cast("cell_t *", p)), lib.BLOCK_WHITE)

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
            self.assertEqual(self.get_blocktype(ffi.cast("cell_t *", p)), lib.BLOCK_BLACK)

        for p in unreachable:
            self.assertEqual(self.get_blocktype(ffi.cast("cell_t *", p)), lib.BLOCK_WHITE)

    def test_color_transitions(self):
        """Test all possible color transitions"""
        reachable = list()
        unreachable = list()

        for i in range(2 * lib.QCGC_INC_MARK_MIN):
            o = self.allocate_ref(1)
            self.push_root(o)
            reachable.append(o)
            self.assertEqual(lib.qcgc_get_mark_color(ffi.cast("object_t *",o)), lib.MARK_COLOR_LIGHT_GRAY)


        lib.qcgc_incmark() # Marks ALL root objects
        self.assertEqual(lib.qcgc_state.phase, lib.GC_MARK)

        for o in reachable:
            self.assertIn(lib.qcgc_get_mark_color(ffi.cast("object_t *", o)), [lib.MARK_COLOR_DARK_GRAY, lib.MARK_COLOR_BLACK])
            if (lib.qcgc_get_mark_color(ffi.cast("object_t *", o)) == lib.MARK_COLOR_BLACK):
                # Trigger write barrier and add object
                lib.qcgc_write(ffi.cast("object_t *", o))
                self.assertEqual(lib.qcgc_get_mark_color(ffi.cast("object_t *", o)), lib.MARK_COLOR_DARK_GRAY)

        lib.qcgc_mark()

        for o in reachable:
            self.assertEqual(lib.qcgc_get_mark_color(ffi.cast("object_t *", o)), lib.MARK_COLOR_BLACK)

        lib.bump_ptr_reset()
        lib.qcgc_sweep(False)

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
        lib.qcgc_incmark()
        #
        # Generate new roots
        objects = self.gen_circular_structure(100)
        self.push_root(objects[0])
        reachable.extend(objects)

        mark_all_inc()

        for p in reachable:
            self.assertEqual(self.get_blocktype(ffi.cast("cell_t *", p)), lib.BLOCK_BLACK)

        for p in unreachable:
            self.assertEqual(self.get_blocktype(ffi.cast("cell_t *", p)), lib.BLOCK_WHITE)

def mark_all_inc():
    lib.qcgc_incmark()
    while(lib.qcgc_state.phase == lib.GC_MARK):
        lib.qcgc_incmark()

if __name__ == "__main__":
    unittest.main()
