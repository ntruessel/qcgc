from support import lib,ffi
from qcgc_test import QCGCTest
import unittest

class WeakrefTestCase(QCGCTest):
    def test_weakref_to_normal(self):
        alive = self.allocate(1)
        self.push_root(alive)
        self.weakref_to_alive_and_dead(alive, self.allocate(1))

    def test_weakref_to_huge(self):
        alive = self.allocate(lib.qcgc_arena_size)
        self.push_root(alive)
        self.weakref_to_alive_and_dead(alive, self.allocate(lib.qcgc_arena_size))

    def test_weakref_to_prebuilt(self):
        prebuilt = self.allocate_prebuilt(1)
        wr = self.allocate_weakref(prebuilt)
        self.push_root(wr)
        # Collect
        lib.bump_ptr_reset()
        lib.qcgc_collect()
        #
        self.assertEqual(self.get_ref(wr, 0), prebuilt)

    def test_collected_weakref_no_err(self):
        alive = self.allocate(1)
        self.push_root(alive)
        # Collect
        lib.bump_ptr_reset()
        lib.qcgc_collect()
        # There is nothing to check besides that this does not crash

    def weakref_to_alive_and_dead(self, alive, dead):
        """Utility to reduce code duplication in test cases. Client is responsible
        that alive object remains alive"""
        wr_to_alive = self.allocate_weakref(alive)
        wr_to_dead = self.allocate_weakref(dead)
        self.push_root(wr_to_alive)
        self.push_root(wr_to_dead)
        # Collect
        lib.bump_ptr_reset()
        lib.qcgc_collect()
        #
        self.assertEqual(self.get_ref(wr_to_alive, 0), alive)
        self.assertEqual(self.get_ref(wr_to_dead, 0), ffi.NULL)

if __name__ == "__main__":
    unittest.main()
