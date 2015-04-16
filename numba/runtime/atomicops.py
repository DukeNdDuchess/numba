from __future__ import print_function, absolute_import, division

import re
from collections import defaultdict

from numba.config import MACHINE_BITS
from numba import cgutils
from llvmlite import ir, binding as llvm


_word_type = ir.IntType(MACHINE_BITS)


def _define_incref(module, atomic_incr):
    """
    Implement NRT_incref in the module
    """
    if "NRT_incref" not in module.globals:
        return
    fn_incref = module.get_global_variable_named("NRT_incref")
    fn_incref.linkage = 'linkonce_odr'
    builder = ir.IRBuilder(fn_incref.append_basic_block())
    [ptr] = fn_incref.args
    is_null = builder.icmp_unsigned("==", ptr, cgutils.get_null_value(ptr.type))
    with cgutils.if_unlikely(builder, is_null):
        builder.ret_void()
    builder.call(atomic_incr, [builder.bitcast(ptr, atomic_incr.args[0].type)])
    builder.ret_void()


def _define_decref(module, atomic_decr):
    """
    Implement NRT_decref in the module
    """
    if "NRT_decref" not in module.globals:
        return
    fn_decref = module.get_global_variable_named("NRT_decref")
    fn_decref.linkage = 'linkonce_odr'
    calldtor = module.add_function(ir.FunctionType(ir.VoidType(),
        [ir.IntType(8).as_pointer(), ir.IntType(32)]),
        name="NRT_MemInfo_call_dtor")

    builder = ir.IRBuilder(fn_decref.append_basic_block())
    [ptr] = fn_decref.args
    is_null = builder.icmp_unsigned("==", ptr, cgutils.get_null_value(ptr.type))
    with cgutils.if_unlikely(builder, is_null):
        builder.ret_void()
    newrefct = builder.call(atomic_decr,
                            [builder.bitcast(ptr, atomic_decr.args[0].type)])

    refct_eq_0 = builder.icmp_unsigned("==", newrefct,
                                       ir.Constant(newrefct.type, 0))
    with cgutils.if_unlikely(builder, refct_eq_0):
        do_defer = ir.Constant(ir.IntType(32), 0)
        builder.call(calldtor, [ptr, do_defer])
    builder.ret_void()


def install_atomic_refct(module):
    """
    Implement both NRT_incref and NRT_decref in the module
    """
    incref = _define_atomic_inc_dec(module, "add", ordering='monotonic')
    decref = _define_atomic_inc_dec(module, "sub", ordering='monotonic')

    # Set LinkOnce ODR linkage
    for fn in [incref, decref]:
        fn.linkage = 'linkonce_odr'
    del fn

    _define_incref(module, incref)
    _define_decref(module, decref)


def _define_atomic_inc_dec(module, op, ordering):
    """Define a llvm function for atomic increment/decrement to the given module
    Argument ``op`` is the operation "add"/"sub".  Argument ``ordering`` is
    the memory ordering.
    """
    ftype = ir.FunctionType(_word_type, [_word_type.as_pointer()])
    fn_atomic = ir.Function(module, ftype, name="nrt_atomic_{0}".format(op))

    [ptr] = fn_atomic.args
    bb = fn_atomic.append_basic_block()
    builder = ir.IRBuilder(bb)
    ONE = ir.Constant(_word_type, 1)
    builder.atomic_rmw(op, ptr, ONE, ordering=ordering)
    res = builder.load(ptr)
    builder.ret(res)

    return fn_atomic


def _define_atomic_cmpxchg(module, ordering):
    ftype = ir.FunctionType(ir.IntType(32), [_word_type.as_pointer(),
                                             _word_type, _word_type,
                                             _word_type.as_pointer()])
    fn_cas = ir.Function(module, ftype, name="nrt_atomic_cas")

    [ptr, cmp, repl, oldptr] = fn_cas.args
    bb = fn_cas.append_basic_block()
    builder = ir.IRBuilder(bb)
    outtup = builder.cmpxchg(ptr, cmp, repl, ordering=ordering)
    old, ok = cgutils.unpack_tuple(builder, outtup, 2)
    builder.store(old, oldptr)
    builder.ret(builder.zext(ok, ftype.return_type))


def define_atomic_ops():
    module = ir.Module()
    _define_atomic_inc_dec(module, "add", ordering='monotonic')
    _define_atomic_inc_dec(module, "sub", ordering='monotonic')
    _define_atomic_cmpxchg(module, ordering='monotonic')
    return module


def compile_atomic_ops():
    # Implement LLVM module with atomic ops
    mod = llvm.parse_assembly(str(define_atomic_ops()))

    # Create a target just for this module
    target = llvm.Target.from_default_triple()
    mod.triple = target.triple
    tm = target.create_target_machine(cpu=llvm.get_host_cpu_name(),
                                      codemodel='jitdefault')
    mcjit = llvm.create_mcjit_compiler(mod, tm)
    mcjit.finalize_object()
    atomic_inc = mcjit.get_pointer_to_function(mod.get_function(
        "nrt_atomic_add"))
    atomic_dec = mcjit.get_pointer_to_function(mod.get_function(
        "nrt_atomic_sub"))
    atomic_cas = mcjit.get_pointer_to_function(mod.get_function(
        "nrt_atomic_cas"))

    return mcjit, atomic_inc, atomic_dec, atomic_cas


_regex_incref = re.compile(r'call void @NRT_incref\((.*)\)')
_regex_decref = re.compile(r'call void @NRT_decref\((.*)\)')
_regex_bb = re.compile(r'[-a-zA-Z$._][-a-zA-Z$._0-9]*:')


def remove_redundant_nrt_refct(ir_module):
    """
    Remove redundant reference count operations from the llvmlite.ir.ModuleRef.
    This parses the ir_module as a string and line by line to remove the
    unnecessary nrt refct pairs within each block.

    Note
    -----
    Should replace this.  Not efficient.
    """
    # Early escape if NRT_incref is not used
    try:
        ir_module.get_function('NRT_incref')
    except NameError:
        return ir_module

    incref_map = defaultdict(list)
    decref_map = defaultdict(list)
    scopes = []

    # Parse IR module as text
    llasm = str(ir_module)
    lines = llasm.splitlines()

    # Phase 1:
    # Find all refct ops and what they are operating on
    for lineno, line in enumerate(lines):
        # Match NRT_incref calls
        m = _regex_incref.match(line.strip())
        if m is not None:
            incref_map[m.group(1)].append(lineno)
            continue

        # Match NRT_decref calls
        m = _regex_decref.match(line.strip())
        if m is not None:
            decref_map[m.group(1)].append(lineno)
            continue

        # Split at BB boundaries
        m = _regex_bb.match(line)
        if m is not None:
            # Push
            scopes.append((incref_map, decref_map))
            # Reset
            incref_map = defaultdict(list)
            decref_map = defaultdict(list)

    # Phase 2:
    # Determine which refct ops are unnecessary
    to_remove = set()
    for incref_map, decref_map in scopes:
        # For each value being refct-ed
        for val in incref_map.keys():
            increfs = incref_map[val]
            decrefs = decref_map[val]
            # Mark the incref/decref pairs from the tail for removal
            for _ in range(min(len(increfs), len(decrefs))):
                to_remove.add(increfs.pop())
                to_remove.add(decrefs.pop())

    # Phase 3
    # Remove all marked instructions
    newll = '\n'.join(ln for lno, ln in enumerate(lines) if lno not in
                      to_remove)

    # Regenerate the LLVM module
    return llvm.parse_assembly(newll)
