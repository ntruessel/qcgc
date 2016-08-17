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
        return "[{: 4d}.{:09d}] Log Start".format(self.sec, self.nsec, self.eventID)

class LogStopEvent(EventBase):
    def __str__(self):
        return "[{: 4d}.{:09d}] Log Stop".format(self.sec, self.nsec, self.eventID)

del EventBase
