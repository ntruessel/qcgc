import struct
from .event import *

class LogIterator:
    def __init__(self, filename):
        self.f = open(filename, "rb")

    def __iter__(self):
        return self

    def __next__(self):
        fmt = "=IIBI"
        buf = self.f.read(struct.calcsize(fmt))
        if (len(buf) == struct.calcsize(fmt)):
            sec, nsec, eventID, additional_bytes = struct.unpack(fmt, buf);

            if (eventID == 0):
                result = LogStartEvent(sec, nsec)
            elif (eventID == 1):
                result = LogStopEvent(sec, nsec)
            elif (eventID == 2):
                result = SweepStartEvent(sec, nsec)
            elif (eventID == 3):
                result = SweepDoneEvent(sec, nsec)
            elif (eventID == 4):
                result = AllocateStartEvent(sec, nsec)
            elif (eventID == 5):
                result = AllocateDoneEvent(sec, nsec)
            elif (eventID == 6):
                result = NewArenaEvent(sec, nsec)
            else:
                result = UnknownEvent(sec, nsec, eventID)

            result.parse_additional_data(self.f, additional_bytes)
            return result
        else:
            self.f.close()
            raise StopIteration()
        pass
