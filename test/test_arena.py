from support import lib,ffi
from qcgc_test import QCGCTest

class ArenaTestCase(QCGCTest):
    ############################################################################
    # Size, Layout                                                             #
    ############################################################################
    def test_arena_size_calculations(self):
        exp = lib.QCGC_ARENA_SIZE_EXP
        size = 2**exp
        bitmap = size / 128
        cells = size / 16
        first_cell_index = 2 * bitmap / 16
        self.assertEqual(size, lib.qcgc_arena_size)
        self.assertEqual(bitmap, lib.qcgc_arena_bitmap_size)
        self.assertEqual(cells, lib.qcgc_arena_cells_count)
        self.assertEqual(first_cell_index, lib.qcgc_arena_first_cell_index)

    def test_arena_size(self):
        self.assertEqual(lib.qcgc_arena_sizeof(), lib.qcgc_arena_size)

    def test_arena_layout(self):
        arena = lib.qcgc_arena_create()

        lib.arena_cells(arena)[0][0] = 15
        self.assertEqual(lib.arena_block_bitmap(arena)[0], 15)

        lib.arena_cells(arena)[lib.qcgc_arena_bitmap_size // 16][lib.qcgc_arena_bitmap_size % 16] = 3
        self.assertEqual(lib.arena_mark_bitmap(arena)[0], 3)

        lib.arena_cells(arena)[lib.qcgc_arena_cells_count - 1][15] = 12

    ############################################################################
    # Utilites                                                                 #
    ############################################################################
    def test_index_calculation(self):
        p = lib.qcgc_arena_create()
        self.assertEqual(lib.qcgc_arena_first_cell_index,
                lib.qcgc_arena_cell_index(ffi.addressof(lib.arena_cells(p)[lib.qcgc_arena_first_cell_index])))

    def test_bitmap_manipulation(self):
        p = lib.qcgc_arena_create()
        for i in range(0, 7):
            index = i + lib.qcgc_arena_first_cell_index + 8
            lib.qcgc_arena_set_bitmap_entry(lib.arena_mark_bitmap(p), index, True)
            for j in range(0, 7):
                jndex = j + lib.qcgc_arena_first_cell_index + 8
                if (j <= i):
                    self.assertEqual(True, lib.qcgc_arena_get_bitmap_entry(lib.arena_mark_bitmap(p), jndex))
                else:
                    self.assertEqual(False, lib.qcgc_arena_get_bitmap_entry(lib.arena_mark_bitmap(p), jndex))

    def test_blocktype_manipulation(self):
        p = lib.qcgc_arena_create()
        block = ffi.addressof(lib.arena_cells(p)[lib.qcgc_arena_first_cell_index])
        for t in [lib.BLOCK_EXTENT, lib.BLOCK_FREE, lib.BLOCK_WHITE, lib.BLOCK_BLACK]:
            lib.qcgc_arena_set_blocktype(block, t)
            self.assertEqual(t, lib.qcgc_arena_get_blocktype(block))

    def test_block_counting(self):
        arena = lib.qcgc_arena_create()
        i = lib.qcgc_arena_first_cell_index

        layout = [ (0, lib.BLOCK_WHITE)
                 , (20, lib.BLOCK_BLACK)
                 , (32, lib.BLOCK_BLACK)
                 , (42, lib.BLOCK_BLACK)
                 , (43, lib.BLOCK_WHITE)
                 , (44, lib.BLOCK_WHITE)
                 ]

        for b in layout:
            p = ffi.addressof(lib.arena_cells(arena)[i + b[0]])
            if b[1] == lib.BLOCK_BLACK:
                lib.qcgc_arena_mark_allocated(p, 1)
                lib.qcgc_mark_object(ffi.cast("object_t *", p))
            elif b[1] == lib.BLOCK_WHITE:
                lib.qcgc_arena_mark_allocated(p, 1)

        self.assertEqual(lib.qcgc_arena_black_blocks(arena), 3)
        self.assertEqual(lib.qcgc_arena_white_blocks(arena), 3)
        self.assertEqual(lib.qcgc_arena_free_blocks(arena), 4)

    def test_is_empty(self):
        arena = lib.qcgc_arena_create()
        i = lib.qcgc_arena_first_cell_index

        self.assertTrue(lib.qcgc_arena_is_empty(arena))

        p = ffi.addressof(lib.arena_cells(arena)[i])

        lib.qcgc_arena_mark_allocated(p, 1)
        self.assertFalse(lib.qcgc_arena_is_empty(arena))

        lib.qcgc_mark_object(ffi.cast("object_t *", p))
        self.assertFalse(lib.qcgc_arena_is_empty(arena))

    def test_is_coalesced(self):
        arena = lib.qcgc_arena_create()
        i = lib.qcgc_arena_first_cell_index

        self.assertTrue(lib.qcgc_arena_is_coalesced(arena))

        p = ffi.addressof(lib.arena_cells(arena)[i])

        lib.qcgc_arena_mark_allocated(p, 1)
        self.assertTrue(lib.qcgc_arena_is_coalesced(arena))

        lib.qcgc_mark_object(ffi.cast("object_t *", p))
        self.assertTrue(lib.qcgc_arena_is_coalesced(arena))

        lib.qcgc_arena_mark_free(p)
        self.assertFalse(lib.qcgc_arena_is_coalesced(arena))

    ############################################################################
    # Sweep                                                                    #
    ############################################################################
    def test_arena_sweep_white(self):
        arena = lib.qcgc_arena_create()
        i = lib.qcgc_arena_first_cell_index

        for j in range(10):
            lib.qcgc_arena_mark_allocated(
                    ffi.addressof(lib.arena_cells(arena)[i + j]),
                    1)
        self.assertEqual(lib.qcgc_arena_white_blocks(arena), 10)

        self.assertTrue(lib.qcgc_arena_sweep(arena))
        self.assertEqual(lib.qcgc_arena_black_blocks(arena), 0)
        self.assertEqual(lib.qcgc_arena_white_blocks(arena), 0)
        self.assertEqual(lib.qcgc_arena_free_blocks(arena), 1)

        self.assertTrue(lib.qcgc_arena_is_empty(arena))
        self.assertTrue(lib.qcgc_arena_is_coalesced(arena))

    def test_arena_sweep_black(self):
        arena = lib.qcgc_arena_create()
        i = lib.qcgc_arena_first_cell_index

        for j in range(10):
            p = ffi.addressof(lib.arena_cells(arena)[i + j])
            lib.qcgc_arena_mark_allocated(p, 1)
            lib.qcgc_mark_object(ffi.cast("object_t *", p))

        self.assertEqual(lib.qcgc_arena_black_blocks(arena), 10)

        self.assertFalse(lib.qcgc_arena_sweep(arena))
        self.assertEqual(lib.qcgc_arena_black_blocks(arena), 0)
        self.assertEqual(lib.qcgc_arena_white_blocks(arena), 10)
        self.assertEqual(lib.qcgc_arena_free_blocks(arena), 1)

        self.assertTrue(lib.qcgc_arena_is_coalesced(arena))

    def test_arena_sweep_mixed(self):
        arena = lib.qcgc_arena_create()
        i = lib.qcgc_arena_first_cell_index

        layout = [ (0, lib.BLOCK_WHITE)
                 , (20, lib.BLOCK_BLACK)
                 , (32, lib.BLOCK_BLACK)
                 , (42, lib.BLOCK_BLACK)
                 , (43, lib.BLOCK_WHITE)
                 , (44, lib.BLOCK_WHITE)
                 ]

        for b in layout:
            p = ffi.addressof(lib.arena_cells(arena)[i + b[0]])
            if b[1] == lib.BLOCK_BLACK:
                lib.qcgc_arena_mark_allocated(p, 1)
                lib.qcgc_mark_object(ffi.cast("object_t *", p))
            elif b[1] == lib.BLOCK_WHITE:
                lib.qcgc_arena_mark_allocated(p, 1)

        self.assertEqual(lib.qcgc_arena_black_blocks(arena), 3)
        self.assertEqual(lib.qcgc_arena_white_blocks(arena), 3)

        self.assertFalse(lib.qcgc_arena_sweep(arena))
        self.assertEqual(lib.qcgc_arena_black_blocks(arena), 0)
        self.assertEqual(lib.qcgc_arena_white_blocks(arena), 3)
        self.assertEqual(lib.qcgc_arena_free_blocks(arena), 4)

        self.assertTrue(lib.qcgc_arena_is_coalesced(arena))

    ############################################################################
    # Misc                                                                     #
    ############################################################################
    def test_arena_create(self):
        p = lib.qcgc_arena_create()
        self.assertEqual(p, lib.qcgc_arena_addr(p))
        self.assertEqual(0, lib.qcgc_arena_cell_index(p))
        self.assertEqual(int(ffi.cast("uint64_t", p)),
                int(ffi.cast("uint64_t", p))
                    << lib.QCGC_ARENA_SIZE_EXP
                    >> lib.QCGC_ARENA_SIZE_EXP)
        self.assertEqual(lib.BLOCK_FREE, lib.qcgc_arena_get_blocktype(ffi.addressof(lib.arena_cells(p)[lib.qcgc_arena_first_cell_index])))
