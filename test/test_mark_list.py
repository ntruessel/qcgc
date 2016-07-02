from support import lib,ffi
from qcgc_test import QCGCTest

class MarkListTestCase(QCGCTest):
    def test_create_destroy(self):
        """Lifetime management"""
        for i in range(100):
            l = lib.qcgc_mark_list_create(i)
            self.assertNotEqual(l, ffi.NULL)
            self.assertEqual(l.head, l.tail)
            self.assertEqual(l.insert_index, 0)
            self.assertGreater(l.length, 0)
            self.assertNotEqual(l.segments, ffi.NULL)
            self.assertNotEqual(l.segments[l.head], ffi.NULL)
            lib.qcgc_mark_list_destroy(l)

    def test_push_pop(self):
        """Single push and pop"""
        l = lib.qcgc_mark_list_create(1000)
        for i in range(1000):
            lib.qcgc_mark_list_push(l, ffi.cast("object_t *", i))

        i = 0
        while i < 1000:
            segment = lib.qcgc_mark_list_get_head_segment(l)
            self.assertNotEqual(segment, ffi.NULL)
            for j in range(lib.QCGC_MARK_LIST_SEGMENT_SIZE):
                if i < 1000:
                    self.assertEqual(ffi.cast("object_t *", i), segment[j])
                    i += 1
            lib.qcgc_mark_list_drop_head_segment(l);

    def test_grow_push(self):
        """Growing on space exhaustion when using single push"""
        l = lib.qcgc_mark_list_create(200)
        for i in range(1000):
            lib.qcgc_mark_list_push(l, ffi.cast("object_t *", i))

        i = 0
        while i < 1000:
            segment = lib.qcgc_mark_list_get_head_segment(l)
            self.assertNotEqual(segment, ffi.NULL)
            for j in range(lib.QCGC_MARK_LIST_SEGMENT_SIZE):
                if i < 1000:
                    self.assertEqual(ffi.cast("object_t *", i), segment[j])
                    i += 1
            lib.qcgc_mark_list_drop_head_segment(l);

    def test_push_all(self):
        """Push array"""
        arr_size = 2 * lib.QCGC_MARK_LIST_SEGMENT_SIZE
        list_size = arr_size + lib.QCGC_MARK_LIST_SEGMENT_SIZE
        pre_fill = lib.QCGC_MARK_LIST_SEGMENT_SIZE // 2

        arr = ffi.new('object_t *[]', arr_size)
        l = lib.qcgc_mark_list_create(list_size)
        for i in range(arr_size):
            arr[i] = ffi.cast("object_t *", i)

        for i in range(pre_fill):
            lib.qcgc_mark_list_push(l,ffi.NULL)

        lib.qcgc_mark_list_push_all(l, arr, arr_size)

        for i in range(list_size - arr_size - pre_fill):
            lib.qcgc_mark_list_push(l,ffi.NULL)

        i = 0
        while i < list_size:
            segment = lib.qcgc_mark_list_get_head_segment(l)
            self.assertNotEqual(segment, ffi.NULL)
            for j in range(lib.QCGC_MARK_LIST_SEGMENT_SIZE):
                if i >= pre_fill and i < pre_fill + arr_size:
                    self.assertEqual(segment[i], ffi.cast("object_t *", i - pre_fill))
                else:
                    self.assertEqual(segment[i], ffi.NULL)
                i += 1
            segment = lib.qcgc_mark_list_get_head_segment(l)

    def test_grow_push_all(self):
        """Grow on push array"""
        arr_size = 4 * lib.QCGC_MARK_LIST_SEGMENT_SIZE
        pre_fill = lib.QCGC_MARK_LIST_SEGMENT_SIZE // 2
        list_size = pre_fill + arr_size
        init_size = lib.QCGC_MARK_LIST_SEGMENT_SIZE

        arr = ffi.new('object_t *[]', arr_size)
        l = lib.qcgc_mark_list_create(init_size)
        for i in range(arr_size):
            arr[i] = ffi.cast("object_t *", i)

        for i in range(pre_fill):
            lib.qcgc_mark_list_push(l,ffi.NULL)

        lib.qcgc_mark_list_push_all(l, arr, arr_size)

        i = 0
        while i < list_size:
            segment = lib.qcgc_mark_list_get_head_segment(l)
            self.assertNotEqual(segment, ffi.NULL)
            for j in range(lib.QCGC_MARK_LIST_SEGMENT_SIZE):
                if i >= pre_fill and i < pre_fill + arr_size:
                    self.assertEqual(segment[i], ffi.cast("object_t *", i - pre_fill))
                else:
                    self.assertEqual(segment[i], ffi.NULL)
                i += 1
            segment = lib.qcgc_mark_list_get_head_segment(l)
