from support import ffi, lib

p = lib.qcgc_allocate(10)
assert p != ffi.NULL
