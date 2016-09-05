from support import lib,ffi
from qcgc_test import QCGCTest
import unittest

class ExtraRootTestCase(QCGCTest):
    def test_extra_root(self):
        # XXX: Violates the condition of the extra roots but it does not matter atm
        extra_root_obj = self.allocate_ref(2)
        # Register roots
        lib.qcgc_register_extra_root(ffi.cast("object_t **", extra_root_obj.refs))
        lib.qcgc_register_extra_root(ffi.cast("object_t **", extra_root_obj.refs) + 1)
        # Test crash with null objects
        lib.qcgc_collect()
        # Allocate objects
        reachable = list()
        objects = self.gen_circular_structure(100);
        reachable.extend(objects)
        extra_root_obj.refs[0] = objects[0] # No self.set_ref as it triggers the write barrier
        objects = self.gen_circular_structure(100);
        reachable.extend(objects)
        extra_root_obj.refs[1] = objects[1] # Same
        #
        lib.qcgc_mark_all()
        for p in reachable:
            self.assertEqual(lib.qcgc_arena_get_blocktype(ffi.cast("cell_t *", p)), lib.BLOCK_BLACK)

if __name__ == "__main__":
    unittest.main()
