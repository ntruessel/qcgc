import unittest
from support import lib,ffi
from qcgc_test import QCGCTest

class ShadowStackTestCase(QCGCTest):
    def test_basic(self):
        p = self.allocate(1)
        q = self.allocate(1)
        #
        self.push_root(p)
        self.assertEqual(self.ss_size(), 1)
        #
        self.push_root(q)
        self.assertEqual(self.ss_size(), 2)
        #
        self.assertEqual(lib.qcgc_shadowstack.base[1], q)
        self.pop_root()
        self.assertEqual(self.ss_size(), 1)
        #
        self.assertEqual(lib.qcgc_shadowstack.base[0], p)
        self.pop_root()
        self.assertEqual(self.ss_size(), 0)

    def test_state_modification(self):
        p = self.allocate(1)
        lib.qcgc_state.phase = lib.GC_PAUSE
        self.assertEqual(lib.qcgc_state.gray_stack_size, 0)
        #
        p = self.allocate(1)
        self.push_root(p)
        self.assertEqual(lib.qcgc_state.gray_stack_size, 0)
        self.assertEqual(lib.qcgc_state.phase, lib.GC_PAUSE)



if __name__ == "__main__":
    unittest.main()
