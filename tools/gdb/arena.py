import gdb

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
            bt = blocktype(arena, i)
            if (bt == Blocktype.free):
                if last_free is None:
                    last_free = i
                else:
                    print("Consecutive free blocks {} and {}".format(arena['cells'][last_free].address, arena['cells'][i].address))
                    return
            elif (bt in [Blocktype.black, Blocktype.white]):
                last_free = None



class BlocktypeLookup(gdb.Command):
    def __init__(self):
        super(BlocktypeLookup, self).__init__("blocktype-lookup", gdb.COMMAND_USER, gdb.COMPLETE_EXPRESSION)

    def invoke(self, arg, from_tty):
        ptr = gdb.parse_and_eval(arg)
        print(blocktype(ptr))

class BlocktypeWatch(gdb.Command):
    def __init__(self):
        super(BlocktypeWatch, self).__init__("blocktype-watch", gdb.COMMAND_USER, gdb.COMPLETE_EXPRESSION)

    def invoke(self, arg, from_tty):
        ptr = gdb.parse_and_eval(arg)
        arena = ptr_to_arena(ptr)
        index = ptr_to_index(ptr)
        print(index)
        mark_byte = arena['mark_bitmap'][index // 8]
        block_byte = arena['block_bitmap'][index // 8]
        mask = 0x01 << (index % 8)
        print("mark_byte:  watch *(uint8_t *){}".format(mark_byte.address))
        print("block_byte:  watch *(uint8_t *){}".format(block_byte.address))

def ptr_to_arena(ptr):
    i = int(str(ptr), 16)
    return gdb.Value(i & ~0x0fffff).cast(gdb.lookup_type("arena_t").pointer()).dereference() #XXX: Lookup arena size

def ptr_to_index(ptr):
    arena = ptr_to_arena(ptr)
    cell_ptr_t = gdb.lookup_type("cell_t").pointer()
    result = ptr.cast(cell_ptr_t) - arena.address.cast(cell_ptr_t)
    return int(result)

def blocktype(ptr):
    arena = ptr_to_arena(ptr)
    index = ptr_to_index(ptr)
    mark_bit = bitmap_entry(arena['mark_bitmap'], index)
    block_bit = bitmap_entry(arena['block_bitmap'], index)
    if block_bit:
        if mark_bit:
            return Blocktype['black']
        else:
            return Blocktype['white']
    else:
        if mark_bit:
            return Blocktype['free']
        else:
            return Blocktype['extent']

def bitmap_entry(bitmap, index):
    byte = index // 8
    mask = 0x01 << (index % 8)
    return ((bitmap[byte] & mask) == mask);


Blocktype = { 'extent': "BLOCK_EXTENT"
            , 'free': "BLOCK_FREE"
            , 'white': "BLOCK_WHITE"
            , 'black': "BLOCK_BLACK"
            }

ArenaCoalesceError()
BlocktypeLookup()
BlocktypeWatch()
