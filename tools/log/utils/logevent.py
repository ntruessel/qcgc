class UnknownLogEvent:
    def __init__(self, sec, nsec, eventID):
        self.sec = sec
        self.nsec = nsec
        self.eventID = eventID

    def parse_additional_data(self, f, size):
        _ = f.read(size)

    def __str__(self):
        return "[{: 4d}.{:09d}] Unknown event (event id = {})".format(self.sec, self.nsec, self.eventID)
