import gdb
from enum import Enum

class ArenaCoalesceError(gdb.Command):
    def __init__(self):
        super(ArenaCoalesceError, self).__init__("arena-coalesce-error", gdb.COMMAND_USER, gdb.COMPLETE_EXPRESSION)

    def invoke(self, arg, from_tty):
        arena_addr = gdb.parse_and_eval(arg)
        print("Analyzing arena {} for non-coalesced blocks".format(arena_addr))
        self._test_coalesced(arena_addr.dereference())

    def _test_coalesced(self, arena):
        l, h = arena['cells'].type.range()
        cells = h - l + 1
        first_cell = cells // 64
        last_free = None
        for i in range(first_cell, cells):
            bt = self._blocktype(arena, i)
            if (bt == Blocktype.free):
                if last_free is None:
                    last_free = i
                else:
                    print("Consecutive free blocks {} and {}".format(arena['cells'][last_free].address, arena['cells'][i].address))
                    return
            elif (bt in [Blocktype.black, Blocktype.white]):
                last_free = None


    def _blocktype(self, arena, index):
        mark_bit = self._bitmap_entry(arena['mark_bitmap'], index)
        block_bit = self._bitmap_entry(arena['block_bitmap'], index)
        if block_bit:
            if mark_bit:
                return Blocktype.black
            else:
                return Blocktype.white
        else:
            if mark_bit:
                return Blocktype.free
            else:
                return Blocktype.extent

    def _bitmap_entry(self, bitmap, index):
        return (((bitmap[index // 8] >> (index % 8)) & 0x1) == 0x1);


class Blocktype(Enum):
    extent  = "BLOCK_EXTENT"
    free    = "BLOCK_FREE"
    white   = "BLOCK_WHITE"
    black   = "BLOCK_BLACK"

    def __str__(self):
        return (self.value)

ArenaCoalesceError()
