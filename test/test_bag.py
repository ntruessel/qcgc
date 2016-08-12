import unittest
from support import lib,ffi
from qcgc_test import QCGCTest

class BagTestCase(QCGCTest):
    def test_bag_create(self):
        for i in range(1,50):
            b = lib.qcgc_arena_bag_create(i)
            self.assertEqual(b.size, i)
            self.assertEqual(b.count, 0)
            q = b.items[i - 1]  # just to check whether this causes a segfault

    def test_bag_add(self):
        b = lib.qcgc_arena_bag_create(100)
        for i in range(100):
            b = lib.qcgc_arena_bag_add(b, ffi.cast("void *", i))
            self.assertEqual(b.size, 100)
            self.assertEqual(b.count, i + 1)
            self.assertEqual(b.items[i], ffi.cast("void *", i))

    def test_bag_grow(self):
        b = lib.qcgc_arena_bag_create(10)
        for i in range(10):
            b = lib.qcgc_arena_bag_add(b, ffi.cast("void *", i))

        self.assertEqual(b.count, b.size)
        b = lib.qcgc_arena_bag_add(b, ffi.cast("void *", 10))
        self.assertEqual(b.size, 20)
        self.assertEqual(b.count, 11)

        for i in range(11):
            self.assertEqual(b.items[i], ffi.cast("void *", i))

    def test_bag_remove_index(self):
        b = lib.qcgc_arena_bag_create(10)
        for i in range(10):
            b = lib.qcgc_arena_bag_add(b, ffi.cast("void *", i))

        # Remove last
        b = lib.qcgc_arena_bag_remove_index(b, b.count - 1)
        self.assertEqual(b.count, 9)

        # Remove other
        b = lib.qcgc_arena_bag_remove_index(b, 0)
        self.assertEqual(b.count, 8)

        for i in range(1,9):
            has = False
            for j in range(8):
                has = has | (b.items[j] != ffi.cast("void *", i))
            self.assertTrue(has)

        # Bag with size 1
        b = lib.qcgc_arena_bag_create(1)
        b = lib.qcgc_arena_bag_add(b, ffi.NULL)

        b = lib.qcgc_arena_bag_remove_index(b, 0)
        self.assertEqual(b.count, 0)

    def test_bag_shrink(self):
        b = lib.qcgc_arena_bag_create(12)
        for i in range(3):
            b = lib.qcgc_arena_bag_add(b, ffi.cast("void *", i))

        self.assertEqual(b.size, 12)
        b = lib.qcgc_arena_bag_remove_index(b, 2)

        self.assertEqual(b.size, 6)
        for i in range(2):
            self.assertEqual(b.items[i], ffi.cast("void *", i))

if __name__ == "__main__":
    unittest.main()
