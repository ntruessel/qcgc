from support import lib,ffi
import unittest

class EventLoggerTestCase(unittest.TestCase):
    def test_minimal(self):
        "Create and destroy event log"
        lib.qcgc_initialize()
        lib.qcgc_destroy()

        try:
            logfile = open(ffi.string(lib.logfile), "rb")

            try:
                pass
            finally:
                logfile.close()
        except:
            self.fail("Logfile does not exist")
