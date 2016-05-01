from support import lib,ffi
import unittest

class QCGCTest(unittest.TestCase):
    def setUp(self):
        lib.qcgc_initialize()

    def tearDown(self):
        lib.qcgc_destroy()

    def push_root(self, o):
        lib.qcgc_state.shadow_stack[0] = ffi.cast("void *", o)
        lib.qcgc_state.shadow_stack += 1

    def pop_root(self):
        lib.qcgc_state.shadow_stack -= 1
        return ffi.cast("void *", lib.qcgc_state.shadow_stack[0])

    def ss_size(self):
        return lib.qcgc_state.shadow_stack - lib.qcgc_state.shadow_stack_base
