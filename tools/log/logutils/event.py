import struct

class EventBase:
    def __init__(self, sec, nsec):
        self.sec = sec
        self.nsec = nsec

    def parse_additional_data(self, f, size):
        _ = f.read(size)

class UnknownEvent(EventBase):
    def __init__(self, sec, nsec, eventID):
        super(UnknownEvent, self).__init__(sec, nsec)
        self.eventID = eventID

    def __str__(self):
        return "[{: 4d}.{:09d}] Unknown event (event id = {})".format(self.sec, self.nsec, self.eventID)

class LogStartEvent(EventBase):
    def __str__(self):
        return "[{: 4d}.{:09d}] Log start".format(self.sec, self.nsec)

class LogStopEvent(EventBase):
    def __str__(self):
        return "[{: 4d}.{:09d}] Log stop".format(self.sec, self.nsec)

class SweepStartEvent(EventBase):
    def parse_additional_data(self, f, size):
        buf = f.read(size)
        self.arenas, = struct.unpack("L", buf)

    def __str__(self):
        return "[{: 4d}.{:09d}] Sweep start, {} arenas".format(self.sec, self.nsec, self.arenas)

class SweepDoneEvent(EventBase):
    def __str__(self):
        return "[{: 4d}.{:09d}] Sweep done".format(self.sec, self.nsec)

class AllocateStartEvent(EventBase):
    def parse_additional_data(self, f, size):
        buf = f.read(size)
        s = struct.unpack("L", buf)
        self.size = s[0]

    def __str__(self):
        return "[{: 4d}.{:09d}] Allocation start, {} bytes".format(self.sec, self.nsec, self.size)

class AllocateDoneEvent(EventBase):
    def parse_additional_data(self, f, size):
        buf = f.read(size)
        s = struct.unpack("P", buf)
        self.ptr = s[0]

    def __str__(self):
        return "[{: 4d}.{:09d}] Allocation done, ptr = 0x{:x}".format(self.sec, self.nsec, self.ptr)

class NewArenaEvent(EventBase):
    def __str__(self):
        return "[{: 4d}.{:09d}] New arena created".format(self.sec, self.nsec)

class MarkStartEvent(EventBase):
    def __str__(self):
        return "[{: 4d}.{:09d}] Mark phase start".format(self.sec, self.nsec)

class IncmarkStartEvent(EventBase):
    def parse_additional_data(self, f, size):
        buf = f.read(size)
        self.stack_size, = struct.unpack("L", buf)

    def __str__(self):
        return "[{: 4d}.{:09d}] Incremenal mark phase start, current gray stack size = {}".format(self.sec, self.nsec, self.stack_size)

class MarkDoneEvent(EventBase):
    def parse_additional_data(self, f, size):
        if (size > 0):
            buf = f.read(size)
            self.stack_size, = struct.unpack("L", buf)
        else:
            self.stack_size = -1

    def __str__(self):
        if (self.stack_size == -1):
            return "[{: 4d}.{:09d}] Mark phase done".format(self.sec, self.nsec)
        else:
            return "[{: 4d}.{:09d}] Mark phase done, current gray stack size = {}".format(self.sec, self.nsec, self.stack_size)

del EventBase
