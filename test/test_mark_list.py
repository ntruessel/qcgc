from support import lib,ffi
from qcgc_test import QCGCTest
import math

class MarkListTestCase(QCGCTest):

    bias = 1

    def test_create_destroy(self):
        """Lifetime management"""
        for i in range(100):
            length = math.ceil((i * 1.0) / lib.QCGC_MARK_LIST_SEGMENT_SIZE)
            if length == 0:
                length = 1

            l = lib.qcgc_mark_list_create(i)
            self.assertNotEqual(l, ffi.NULL)
            self.assertEqual(l.head, l.tail)
            self.assertEqual(l.insert_index, 0)
            self.assertEqual(l.length, length)
            self.assertEqual(l.count, 0)
            self.assertNotEqual(l.segments, ffi.NULL)
            self.assertNotEqual(l.segments[l.head], ffi.NULL)
            lib.qcgc_mark_list_destroy(l)

    def test_destroy_full_list(self):
        """Destroy a non-empty list"""
        list_size = lib.QCGC_MARK_LIST_SEGMENT_SIZE + 1
        l = lib.qcgc_mark_list_create(list_size)
        for i in range(list_size):
            l = lib.qcgc_mark_list_push(l, ffi.cast("object_t *", i + self.bias))
            self.assertEqual(l.count, i + 1)

        lib.qcgc_mark_list_destroy(l)

    def test_single_segment_push(self):
        """Push to single segment"""
        list_size = lib.QCGC_MARK_LIST_SEGMENT_SIZE
        l = lib.qcgc_mark_list_create(list_size)
        for i in range(list_size):
            l = lib.qcgc_mark_list_push(l, ffi.cast("object_t *", i + self.bias))
            self.assertEqual(l.count, i + 1)

        i = 0
        while i < list_size:
            segment = lib.qcgc_mark_list_get_head_segment(l)
            self.assertNotEqual(segment, ffi.NULL)
            for j in range(lib.QCGC_MARK_LIST_SEGMENT_SIZE):
                if i < list_size:
                    self.assertEqual(ffi.cast("object_t *", i + self.bias), segment[j])
                i += 1
            l = lib.qcgc_mark_list_drop_head_segment(l)
            self.assertEqual(l.count, max(0,list_size - i))
        lib.qcgc_mark_list_destroy(l)

    def test_push_pop(self):
        """Push to multiple segments"""
        list_size = 10 * lib.QCGC_MARK_LIST_SEGMENT_SIZE + lib.QCGC_MARK_LIST_SEGMENT_SIZE // 2
        l = lib.qcgc_mark_list_create(list_size)
        for i in range(list_size):
            l = lib.qcgc_mark_list_push(l, ffi.cast("object_t *", i + self.bias))
            self.assertEqual(l.count, i + 1)

        i = 0
        while i < list_size:
            segment = lib.qcgc_mark_list_get_head_segment(l)
            self.assertNotEqual(segment, ffi.NULL)
            for j in range(lib.QCGC_MARK_LIST_SEGMENT_SIZE):
                if i < list_size:
                    self.assertEqual(ffi.cast("object_t *", i + self.bias), segment[j])
                i += 1
            l = lib.qcgc_mark_list_drop_head_segment(l)
            self.assertEqual(l.count, max(0,list_size - i))
        lib.qcgc_mark_list_destroy(l)

    def test_grow_push(self):
        """Growing on space exhaustion when using single push"""
        list_size = 20 * lib.QCGC_MARK_LIST_SEGMENT_SIZE
        l = lib.qcgc_mark_list_create(lib.QCGC_MARK_LIST_SEGMENT_SIZE)
        for i in range(list_size):
            l = lib.qcgc_mark_list_push(l, ffi.cast("object_t *", i + self.bias))
            self.assertEqual(l.count, i + 1)

        self.assertEqual(l.length, 32)

        i = 0
        while i < list_size:
            segment = lib.qcgc_mark_list_get_head_segment(l)
            self.assertNotEqual(segment, ffi.NULL)
            for j in range(lib.QCGC_MARK_LIST_SEGMENT_SIZE):
                if i < list_size:
                    self.assertEqual(ffi.cast("object_t *", i + self.bias), segment[j])
                i += 1
            l = lib.qcgc_mark_list_drop_head_segment(l)
            self.assertEqual(l.count, max(0,list_size - i))
        lib.qcgc_mark_list_destroy(l)

    def test_push_all_short(self):
        """Push short array"""
        arr_size = lib.QCGC_MARK_LIST_SEGMENT_SIZE // 2
        list_size = arr_size

        arr = ffi.new('object_t *[]', arr_size)
        l = lib.qcgc_mark_list_create(list_size)
        for i in range(arr_size):
            arr[i] = ffi.cast("object_t *", i + self.bias)

        l = lib.qcgc_mark_list_push_all(l, arr, arr_size)
        self.assertEqual(l.count, arr_size)

        i = 0
        while i < list_size:
            segment = lib.qcgc_mark_list_get_head_segment(l)
            self.assertNotEqual(segment, ffi.NULL)
            for j in range(lib.QCGC_MARK_LIST_SEGMENT_SIZE):
                if i < list_size:
                    self.assertEqual(segment[j], ffi.cast("object_t *", i + self.bias))
                i += 1
            l = lib.qcgc_mark_list_drop_head_segment(l)
            self.assertEqual(l.count, max(0,list_size - i))
        lib.qcgc_mark_list_destroy(l)

    def test_push_all_long(self):
        """Push long array"""
        arr_size = 2 * lib.QCGC_MARK_LIST_SEGMENT_SIZE
        pre_fill = lib.QCGC_MARK_LIST_SEGMENT_SIZE // 2
        list_size = arr_size + pre_fill

        arr = ffi.new('object_t *[]', arr_size)
        l = lib.qcgc_mark_list_create(list_size)
        for i in range(arr_size):
            arr[i] = ffi.cast("object_t *", i+ self.bias)

        for i in range(pre_fill):
            l = lib.qcgc_mark_list_push(l, ffi.cast("object_t *", -1))
            self.assertEqual(l.count, i + 1)

        l = lib.qcgc_mark_list_push_all(l, arr, arr_size)
        self.assertEqual(l.count, pre_fill + arr_size)

        i = 0
        while i < list_size:
            segment = lib.qcgc_mark_list_get_head_segment(l)
            self.assertNotEqual(segment, ffi.NULL)
            for j in range(lib.QCGC_MARK_LIST_SEGMENT_SIZE):
                if i < list_size:
                    if i >= pre_fill:
                        self.assertEqual(segment[j], ffi.cast("object_t *", i - pre_fill + self.bias))
                    else:
                        self.assertEqual(segment[j], ffi.cast("object_t *", -1))
                i += 1
            l = lib.qcgc_mark_list_drop_head_segment(l)
            self.assertEqual(l.count, max(0,list_size - i))
        lib.qcgc_mark_list_destroy(l)

    def test_grow_push_all(self):
        """Grow on push array"""
        arr_size = 4 * lib.QCGC_MARK_LIST_SEGMENT_SIZE
        pre_fill = lib.QCGC_MARK_LIST_SEGMENT_SIZE // 2
        list_size = pre_fill + arr_size
        init_size = lib.QCGC_MARK_LIST_SEGMENT_SIZE

        arr = ffi.new('object_t *[]', arr_size)
        l = lib.qcgc_mark_list_create(init_size)
        for i in range(arr_size):
            arr[i] = ffi.cast("object_t *", i + self.bias)

        for i in range(pre_fill):
            l = lib.qcgc_mark_list_push(l, ffi.cast("object_t *", -1))
            self.assertEqual(l.count, i + 1)

        l = lib.qcgc_mark_list_push_all(l, arr, arr_size)
        self.assertEqual(l.count, arr_size + pre_fill)

        i = 0
        while i < list_size:
            segment = lib.qcgc_mark_list_get_head_segment(l)
            self.assertNotEqual(segment, ffi.NULL)
            for j in range(lib.QCGC_MARK_LIST_SEGMENT_SIZE):
                if i < list_size:
                    if i >= pre_fill:
                        self.assertEqual(segment[j], ffi.cast("object_t *", i - pre_fill + self.bias))
                    else:
                        self.assertEqual(segment[j], ffi.cast("object_t *", -1))
                i += 1
            l = lib.qcgc_mark_list_drop_head_segment(l)
            self.assertEqual(l.count, max(0,list_size - i))
        lib.qcgc_mark_list_destroy(l)

    def test_partial_drop(self):
        """Test dropping a partially filled segment"""
        list_size = 2 * lib.QCGC_MARK_LIST_SEGMENT_SIZE
        l = lib.qcgc_mark_list_create(list_size)

        l = lib.qcgc_mark_list_push(l, ffi.cast("object_t *", 10))
        segment = lib.qcgc_mark_list_get_head_segment(l)
        self.assertEqual(segment[0], ffi.cast("object_t *", 10))
        self.assertEqual(segment[1], ffi.NULL)
        self.assertEqual(l.count, 1)
        l = lib.qcgc_mark_list_drop_head_segment(l)
        self.assertEqual(l.count, 0)

        l = lib.qcgc_mark_list_push(l, ffi.cast("object_t *", 20))
        segment = lib.qcgc_mark_list_get_head_segment(l)
        self.assertEqual(segment[0], ffi.cast("object_t *", 20))
        self.assertEqual(segment[1], ffi.NULL)
        self.assertEqual(l.count, 1)
        lib.qcgc_mark_list_destroy(l)

    def test_wrap(self):
        """Test circular wrapping"""
        partial_fill = lib.QCGC_MARK_LIST_SEGMENT_SIZE + 1
        list_size = 2 * lib.QCGC_MARK_LIST_SEGMENT_SIZE
        l = lib.qcgc_mark_list_create(list_size)
        for i in range(partial_fill):
            l = lib.qcgc_mark_list_push(l, ffi.cast("object_t *", i + self.bias))

        l = lib.qcgc_mark_list_drop_head_segment(l)
        l = lib.qcgc_mark_list_drop_head_segment(l)
        self.assertEqual(l.head, 1)
        self.assertEqual(l.tail, 1)

        bias = 100
        for i in range(list_size):
            l = lib.qcgc_mark_list_push(l, ffi.cast("object_t *", i + bias))
            self.assertEqual(l.count, i + 1)

        i = 0
        while i < list_size:
            segment = lib.qcgc_mark_list_get_head_segment(l)
            self.assertNotEqual(segment, ffi.NULL)
            for j in range(lib.QCGC_MARK_LIST_SEGMENT_SIZE):
                if i < list_size:
                    self.assertEqual(segment[j], ffi.cast("object_t *", i + bias))
                i += 1
            l = lib.qcgc_mark_list_drop_head_segment(l)
            self.assertEqual(l.count, max(0,list_size - i))
        lib.qcgc_mark_list_destroy(l)

    def test_wrap_grow(self):
        """Test wrapping and growing"""
        partial_fill = lib.QCGC_MARK_LIST_SEGMENT_SIZE + 1
        initial_list_size = lib.QCGC_MARK_LIST_SEGMENT_SIZE
        list_size = 10 * lib.QCGC_MARK_LIST_SEGMENT_SIZE - 1
        l = lib.qcgc_mark_list_create(initial_list_size)
        for i in range(partial_fill):
            l = lib.qcgc_mark_list_push(l, ffi.cast("object_t *", i + self.bias))

        l = lib.qcgc_mark_list_drop_head_segment(l)
        l = lib.qcgc_mark_list_drop_head_segment(l)
        self.assertEqual(l.head, 1)
        self.assertEqual(l.tail, 1)

        bias = 100
        for i in range(list_size):
            l = lib.qcgc_mark_list_push(l, ffi.cast("object_t *", i + bias))
            self.assertEqual(l.count, i + 1)

        i = 0
        while i < list_size:
            segment = lib.qcgc_mark_list_get_head_segment(l)
            self.assertNotEqual(segment, ffi.NULL)
            for j in range(lib.QCGC_MARK_LIST_SEGMENT_SIZE):
                if i < list_size:
                    self.assertEqual(segment[j], ffi.cast("object_t *", i + bias))
                i += 1
            l = lib.qcgc_mark_list_drop_head_segment(l)
            self.assertEqual(l.count, max(0,list_size - i))
        lib.qcgc_mark_list_destroy(l)
