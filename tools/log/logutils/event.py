import struct

class EventBase:
    def __init__(self, sec, nsec, eventID):
        self.sec = sec
        self.nsec = nsec
        self.eventID = eventID

    def parse_additional_data(self, f, size):
        _ = f.read(size)

class UnknownEvent(EventBase):
    def __str__(self):
        return "[{: 4d}.{:09d}] Unknown event (event id = {})".format(self.sec, self.nsec, self.eventID)

class LogStartEvent(EventBase):
    def __str__(self):
        return "[{: 4d}.{:09d}] Log start".format(self.sec, self.nsec, self.eventID)

class LogStopEvent(EventBase):
    def __str__(self):
        return "[{: 4d}.{:09d}] Log stop".format(self.sec, self.nsec, self.eventID)

class SweepStartEvent(EventBase):
    def __init__(self, sec, nsec, eventID):
        super(SweepStartEvent, self).__init__(sec, nsec, eventID)
        self.arenas = 0

    def parse_additional_data(self, f, size):
        buf = f.read(size)
        self.arenas = struct.unpack("I", buf)

    def __str__(self):
        return "[{: 4d}.{:09d}] Sweep start, {} arenas".format(self.sec, self.nsec, self.eventID, self.arenas)

class SweepDoneEvent(EventBase):
    def __str__(self):
        return "[{: 4d}.{:09d}] Sweep done".format(self.sec, self.nsec, self.eventID)

del EventBase
