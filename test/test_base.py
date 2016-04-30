from support import ffi, lib

def shadowstack_push(o):
    lib.qcgc_state.shadow_stack[0] = ffi.cast("void *", o);
    lib.qcgc_state.shadow_stack += 1;

def shadowstack_pop():
    lib.qcgc_state.shadow_stack -= 1;
    return ffi.cast("void *", lib.qcgc_state.shadow_stack[0]);

lib.qcgc_initialize()
assert lib.qcgc_state.shadow_stack == lib.qcgc_state.shadow_stack_base

p = lib.qcgc_allocate(10)
assert p != ffi.NULL

shadowstack_push(p)
assert lib.qcgc_state.shadow_stack - lib.qcgc_state.shadow_stack_base == 1

q = lib.qcgc_allocate(4)
assert q != ffi.NULL

shadowstack_push(q)
assert lib.qcgc_state.shadow_stack - lib.qcgc_state.shadow_stack_base == 2

assert shadowstack_pop() == q
assert lib.qcgc_state.shadow_stack - lib.qcgc_state.shadow_stack_base == 1

assert shadowstack_pop() == p
assert lib.qcgc_state.shadow_stack == lib.qcgc_state.shadow_stack_base

lib.qcgc_destroy()
