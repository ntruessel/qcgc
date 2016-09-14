import struct

class EventBase:
    def __init__(self, sec, nsec):
        self.sec = sec
        self.nsec = nsec

    def time(self):
        return self.sec + self.nsec * (10 ** (-9))

    def parse_additional_data(self, f, size):
        _ = f.read(size)

class UnknownEvent(EventBase):
    def __init__(self, sec, nsec, eventID):
        super(UnknownEvent, self).__init__(sec, nsec)
        self.eventID = eventID

    def accept(self, visitor):
        visitor.visit_unknown(self)

    def __str__(self):
        return "[{: 4d}.{:09d}] Unknown event (event id = {})".format(self.sec, self.nsec, self.eventID)

class LogStartEvent(EventBase):
    def accept(self, visitor):
        visitor.visit_log_start(self)

    def __str__(self):
        return "[{: 4d}.{:09d}] Log start".format(self.sec, self.nsec)

class LogStopEvent(EventBase):
    def accept(self, visitor):
        visitor.visit_log_stop(self)

    def __str__(self):
        return "[{: 4d}.{:09d}] Log stop".format(self.sec, self.nsec)

class SweepStartEvent(EventBase):
    def parse_additional_data(self, f, size):
        buf = f.read(size)
        self.arenas, self.free_cells = struct.unpack("LL", buf)

    def accept(self, visitor):
        visitor.visit_sweep_start(self)

    def __str__(self):
        return "[{: 4d}.{:09d}] Sweep start, {} arenas".format(self.sec, self.nsec, self.arenas)

class SweepDoneEvent(EventBase):
    def parse_additional_data(self, f, size):
        buf = f.read(size)
        self.arenas, self.free_cells, self.largest_free_block = struct.unpack("LLL", buf)

    def accept(self, visitor):
        visitor.visit_sweep_done(self)

    def __str__(self):
        if (self.free_cells != 0):
            return "[{: 4d}.{:09d}] Sweep done. Fragmentation = {:.2%}".format(
                    self.sec, self.nsec,
                    1 - self.largest_free_block / self.free_cells)
        else:
            return "[{: 4d}.{:09d}] Sweep done. Fragmentation = 0%".format(
                    self.sec, self.nsec)


class AllocateStartEvent(EventBase):
    def parse_additional_data(self, f, size):
        buf = f.read(size)
        self.size, = struct.unpack("L", buf)

    def accept(self, visitor):
        visitor.visit_allocate_start(self)

    def __str__(self):
        return "[{: 4d}.{:09d}] Allocation start, {} bytes".format(self.sec, self.nsec, self.size)

class AllocateDoneEvent(EventBase):
    def parse_additional_data(self, f, size):
        buf = f.read(size)
        s = struct.unpack("P", buf)
        self.ptr = s[0]

    def accept(self, visitor):
        visitor.visit_allocate_done(self)

    def __str__(self):
        return "[{: 4d}.{:09d}] Allocation done, ptr = 0x{:x}".format(self.sec, self.nsec, self.ptr)

class NewArenaEvent(EventBase):
    def accept(self, visitor):
        visitor.visit_new_arena(self)

    def __str__(self):
        return "[{: 4d}.{:09d}] New arena created".format(self.sec, self.nsec)

class MarkStartEvent(EventBase):
    def parse_additional_data(self, f, size):
        buf = f.read(size)
        self.incremental, self.stack_size = struct.unpack("?L", buf)

    def accept(self, visitor):
        visitor.visit_mark_start(self)

    def __str__(self):
        return "[{: 4d}.{:09d}] {} mark phase start. Gray stack size = {}".format(
                self.sec, self.nsec, "Incremental" if self.incremental else "Full", self.stack_size)

class MarkDoneEvent(EventBase):
    def parse_additional_data(self, f, size):
        buf = f.read(size)
        self.incremental, self.stack_size = struct.unpack("?L", buf)

    def accept(self, visitor):
        visitor.visit_mark_done(self)

    def __str__(self):
        return "[{: 4d}.{:09d}] {} mark phase done. Gray stack size = {}".format(
                self.sec, self.nsec, "Incremental" if self.incremental else "Full", self.stack_size)

class FreelistDumpEvent(EventBase):
    def parse_additional_data(self, f, size):
        buf = f.read(size)
        self.size, self.count = struct.unpack("LL", buf)

    def accept(self, visitor):
        visitor.visit_freelist_dump(self)

    def __str__(self):
        return "[{: 4d}.{:09d}] Freelist dump. Size {}, Count {}".format(
                self.sec, self.nsec, self.size, self.count)

del EventBase
