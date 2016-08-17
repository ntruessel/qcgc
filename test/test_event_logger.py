from support import lib,ffi
from qcgc_test import QCGCTest

class EventLoggerTestCase(QCGCTest):
    def test_minimal(self):
        "Create and destroy event log"
        # Creation happens automatically (in set_up)
        # Destruction happens automatically (in tear_down)
        try:
            logfile = open(ffi.string(lib.logfile))

            try:
                pass
            finally:
                logfile.close()
        except:
            self.fail("Logfile does not exist")
