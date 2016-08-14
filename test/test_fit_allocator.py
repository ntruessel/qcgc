from support import lib,ffi
from qcgc_test import QCGCTest

class FitAllocatorTest(QCGCTest):
    def test_macro_consistency(self):
        self.assertEqual(2**lib.QCGC_LARGE_FREE_LIST_FIRST_EXP, lib.qcgc_small_free_lists + 1)
        last_exp = lib.QCGC_LARGE_FREE_LIST_FIRST_EXP + lib.qcgc_large_free_lists - 1
        self.assertLess(2**last_exp, 2**lib.QCGC_ARENA_SIZE_EXP)
        self.assertEqual(2**(last_exp + 1), 2**lib.QCGC_ARENA_SIZE_EXP)

    def test_small_free_list_index(self):
        for i in range(1, lib.qcgc_small_free_lists + 1):
            self.assertTrue(lib.is_small(i))
            self.assertEqual(lib.small_index(i), i - 1);

    def test_large_free_list_index(self):
        index = -1;
        for i in range(2**lib.QCGC_LARGE_FREE_LIST_FIRST_EXP, 2**lib.QCGC_ARENA_SIZE_EXP):
            if (i & (i - 1) == 0):
                # Check for power of two
                index = index + 1
            self.assertFalse(lib.is_small(i))
            self.assertEqual(index, lib.large_index(i));
