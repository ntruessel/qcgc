import struct
from .logevent import *

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
            result = BasicLogEvent(sec, nsec, eventID)
            result.parse_additional_data(self.f, additional_bytes)
            return result
        else:
            self.f.close()
            raise StopIteration()
        pass
