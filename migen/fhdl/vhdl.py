from collections import Iterable
import os
try:
    from functools import singledispatch
except ImportError:
    from multimethods import singledispatch
from enum import Enum
from itertools import repeat
from operator import and_, or_, attrgetter, sub, mul, contains, methodcaller
from toolz.curried import *  # noqa
from toolz.compatibility import iteritems
import pyramda as R
from mako.lookup import TemplateLookup

from migen.fhdl.structure import *  # noqa
from migen.fhdl.structure import _Operator, _Slice, _Assign, _Fragment
from migen.fhdl.tools import *  # noqa
from migen.fhdl.namer import build_namespace
from migen.fhdl.conv_output import ConvOutput


and_, mul, sub, contains = map(curry, [and_, mul, sub, contains])


__all__ = ["convert"]


# VHDL-2008 reserved words
_reserved_keywords = {
    "abs", "access", "after", "alias", "all", "and", "architecture", "array",
    "assert", "assume", "assume_guarantee", "attribute", "begin", "block",
    "body", "buffer", "bus", "case", "component", "configuration", "constant",
    "context", "cover", "default", "disconnect", "downto", "else", "elsif",
    "end", "entity", "exit", "fairness", "file", "for", "force", "function",
    "generate", "generic", "group", "guarded", "if", "impure", "in", "inertial",
    "inout", "is", "label", "library", "linkage", "literal", "loop", "map",
    "mod", "nand", "new", "next", "nor", "not", "null", "of", "on", "open",
    "or", "others", "out", "package", "parameter", "port", "postponed",
    "procedure", "process", "property", "protected", "pure", "range", "record",
    "register", "reject", "release", "rem", "report", "restruct",
    "restrict_guarantee", "return", "rol", "ror", "select", "sequence",
    "severity", "shared", "signal", "sla", "sll", "sra", "srl", "strong",
    "subtype", "then", "to", "transport", "type", "unaffected", "units",
    "until", "use", "variable", "vmode", "vprop", "vunit", "wait", "when",
    "while", "whith", "xnor", "xor"}


_get_sigtype = R.if_else(
    comp(R.equals(1), len),
    R.always("std_ulogic"),
    comp("std_logic_vector({} downto 0)".format, R.dec, len))

_sort_by_hash = partial(sorted, key=hash)

_sigs = comp(
    R.apply(or_),
    juxt([
        list_signals,
        partial(list_special_ios, ins=True, outs=True, inouts=True)]))

_inouts = partial(list_special_ios, ins=False, outs=False, inouts=True)

_targets = comp(
    R.apply(or_),
    juxt([
        list_targets,
        partial(list_special_ios, ins=False, outs=True, inouts=True)]))

lookup = TemplateLookup(directories=[
    os.path.abspath(os.path.join(os.path.dirname(__file__), "./templates"))])


def _printentity(f, ios, name, ns):
    return lookup.get_template("entity.mako").render(
        name=name, inouts=_inouts(f),
        targets=_targets(f), ns=ns, ios=sorted(ios, key=hash))


_get_comb, _get_sync, _get_clock_domains = map(
    attrgetter, ["comb", "sync", "clock_domains"])

_reg_typename = "{}_reg_t".format

_rin_name = "{}_rin".format

_r_name = "{}_r".format

_v_name = "{}_v".format

_sorted_sync = comp(concatv, partial(sorted, key=get(0)), iteritems, _get_sync)

_cd_regs = comp(
    map(juxt([
        first,
        comp(list, filter(complement(is_variable)),
             filter(comp(R.isinstance(Signal))), list_targets, second)])),
    _sorted_sync)

_assignment_filter_fn = comp(
    R.apply(and_), juxt([
        comp(R.equals(1), len, first),
        comp(R.isinstance(_Assign), get_in([1, 0]))]))

_comb = comp(concatv, group_by_targets, _get_comb)

_assignments = comp(map(get_in([1, 0])), filter(_assignment_filter_fn), _comb)

_comb_statements = comp(pluck(1), _comb)

# _comb_sigs = comp(concat, pluck(0), _comb)


def _sensitivity_list(f, ns, ios):
    ios = pipe(
        (ios | _inouts(f)) - (
            _targets(f) |
            pipe(f, _get_clock_domains, map(attrgetter("clk")), set)),
        map(ns.get_name))
    regs = pipe(f, _cd_regs, map(first), map(_r_name))
    return concatv(ios, regs)


_indent = R.curry_n(
    2,
    comp(
        "\n".join,
        R.apply(map),
        R.unapply(juxt([
            comp(R.add, R.multiply("    "), first),
            comp(methodcaller("split", "\n"), second)]))))

_AT_BLOCKING, _AT_NONBLOCKING, _AT_SIGNAL = range(3)

_THint = Enum("THint", "boolean logic un_signed  integer")


@singledispatch
def _printexpr(node, ctx):
    raise NotImplementedError("{} not implemented".format(type(node)))


def _fn_call(name, *args):
    return pipe(args, map(str), ", ".join,
                partial("{}({})".format, name.strip()))


_unsigned, _signed, _std_logic_vector, _to_integer = map(
    partial(partial, _fn_call),
    ["unsigned", "signed", "std_logic_vector", "to_integer"])


@_printexpr.register(Constant)
def _printexpr_constant(node, ctx):
    lhint, thint = get(["lhint", "thint"], ctx)
    if thint == _THint.integer:
        return "({})".format(node.value) if node.value < 0 else \
            "{}".format(node.value)
    elif thint == _THint.logic:
        if len(node) == 1:
            if not lhint or lhint == 1:
                return "'{}'".format(node.value)
            return "(others => '0')" if node.value == 0 else \
                "(0 => '1', others => '0')"
        elif node.value == 0:
            return "(others => '0')"
        elif node.value == 2 ** len(node) - 1:
            return "(others => '1')"
        else:
            return _std_logic_vector(
                _fn_call("to_signed" if node.signed else "to_unsigned",
                         node.value, lhint or len(node)))
    else:
        return "'{}'".format(node.value) if len(node) == 1 \
            else _fn_call("to_signed" if node.signed else "to_unsigned",
                          node.value, lhint or len(node))


@_printexpr.register(Signal)
def _printexpr_signal(node, ctx):
    f, ns, buffer_variables, thint, lhint, lhs = get(
        ["f", "ns", "buffer_variables", "thint", "lhint", "lhs"], ctx)
    cd = pipe(f, _cd_regs, map(juxt(
        [first, comp(flip(contains, node), second)])),
        filter(second), map(first), list)
    if buffer_variables and node in buffer_variables:
        identifier = pipe(node, ns.get_name, _v_name)
    else:
        identifier = ns.get_name(node) if len(cd) == 0 else \
            ".".join([_v_name(cd[0]) if lhs else _r_name(cd[0]),
                      ns.get_name(node)])
    if len(node) == 1:
        casted = _unsigned(_fn_call("std_logic_vector'",
                                    " & ".join(["\"\"", identifier])))
    else:
        casted = _signed(identifier) if node.signed else _unsigned(identifier)
    if thint == _THint.boolean:
        assert len(node) == 1
        return _fn_call("\\??\\", identifier)
    if thint == _THint.un_signed:
        return casted
    elif thint == _THint.integer:
        return _fn_call("to_integer", casted)
    elif thint == _THint.logic and lhint:
        return _std_logic_vector(
            _fn_call("to_unsigned",
                     _fn_call("to_integer", _unsigned(identifier)), lhint))
    else:
        return identifier


@_printexpr.register(_Slice)
def _printexpr_slice(node, ctx):
    thint = get("thint", ctx)
    if node.start + 1 == node.stop:
        sr = "" if len(node.value) == 1 else "({})".format(node.start)
    else:
        sr = "({} downto {})".format(node.stop - 1, node.start)
    expr = pipe(_printexpr(
        node.value,
        merge(ctx, dict(thint=_THint.logic, rhint=None))),
        flip(R.add, sr))
    if thint == _THint.un_signed:
        return _unsigned(expr)
    elif thint == _THint.integer:
        return _fn_call("to_integer", _unsigned(expr))
    elif thint == _THint.boolean:
        return _fn_call("\\??\\", expr)
    else:
        return expr


@_printexpr.register(Cat)
def _printexpr_cat(node, ctx):
    thint = get("thint", ctx)
    expr = pipe(node.l, map(
        flip(_printexpr, merge(ctx, dict(thint=_THint.logic, lhint=None)))),
        tuple, reversed, " & ".join, "({})".format)
    if thint == _THint.un_signed:
        return _unsigned(expr)
    elif thint == _THint.integer:
        return _fn_call("to_integer", _unsigned(expr))
    else:
        return expr


def _is_op_cmp(node):
    return node.op == "==" if R.isinstance(_Operator, node) else False


_bitwise_op_map = {"~": "not", "&": "and", "|": "or", "^": "xor"}

_arith_op_map = {"+": "+", "-": "-", "*": "*", "/": "/", "%": "rem"}

_is_arith_op = comp(contains(_arith_op_map.keys()), attrgetter("op"))

_comp_map = {"==": "=", "!=": "/=", "<": "<", "<=": "<=", ">": ">", ">=": ">="}

_is_bitwise_op = comp(contains(_bitwise_op_map.keys()), attrgetter("op"))

_is_comp_op = comp(contains(_comp_map.keys()), attrgetter("op"))

_get_op = comp(flip(get, merge(_bitwise_op_map, _arith_op_map, _comp_map)),
               attrgetter("op"))

_shift_op = {"<<<": "shift_left", ">>>": "shift_right"}

_is_shift_op = comp(contains(_shift_op.keys()), attrgetter("op"))


@_printexpr.register(_Operator)
def _printexpr_operator(node, ctx):
    thint = get("thint", ctx)
    arity = len(node.operands)
    if arity == 1:
        r1 = _printexpr(node.operands[0],
                        merge(ctx, dict(lhs=False,
                                        thint=_THint.logic,
                                        lhint=None)))
        if node.op == "-":
            expr = "(-{})".format(_signed(r1))
            if thint == _THint.un_signed:
                return expr
            elif thint == _THint.integer:
                return _to_integer(expr)
            elif thint == _THint.logic:
                return _std_logic_vector(expr)
            else:
                return expr
        else:
            expr = "{} {}".format(_get_op(node), r1)
            if thint == _THint.un_signed:
                return _unsigned(expr)
            elif thint == _THint.integer:
                return _fn_call("to_integer", _unsigned(expr))
            elif thint == _THint.boolean:
                return _fn_call("\\??\\", expr)
            else:
                return "({})".format(expr)
    elif arity == 2:
        if _is_bitwise_op(node):
            r1, r2 = pipe(
                [node, ctx],
                juxt([
                    comp(attrgetter("operands"), first),
                    comp(repeat, flip(merge, dict(lhs=False,
                                                  thint=_THint.logic,
                                                  lhint=None)), second),
                ]), R.apply(zip), map(R.apply(_printexpr)))
            expr = pipe([r1, _get_op(node), r2], " ".join)
            if thint == _THint.un_signed:
                return _unsigned(expr)
            elif thint == _THint.integer:
                return _fn_call("to_integer", expr)
            else:
                return expr
        elif _is_comp_op(node):
            if pipe(node.operands, R.all_satisfy(comp(R.equals(1), len))):
                r1, r2 = pipe(
                    [node, ctx],
                    juxt([
                        comp(attrgetter("operands"), first),
                        comp(repeat, flip(merge, dict(lhs=False,
                                                      thint=_THint.logic,
                                                      lhint=None)), second),
                    ]), R.apply(zip), R.map(R.apply(_printexpr)))
            else:
                r1, r2 = pipe(
                    [node, ctx],
                    juxt([
                        comp(attrgetter("operands"), first),
                        comp(repeat, second)]), R.apply(zip),
                    map(juxt([
                        first,
                        comp(
                            R.apply(merge),
                            juxt([
                                second,
                                R.always(dict(lhs=False, lhint=None)),
                                R.if_else(
                                    comp(R.isinstance(Constant), first),
                                    R.always(dict(thint=_THint.integer)),
                                    R.always(dict(thint=_THint.un_signed)))
                            ]))])),
                    map(R.apply(_printexpr)))
            if thint == _THint.logic:
                return _fn_call(pipe(node, _get_op, "\\?{}\\".format), r1, r2)
            else:
                return pipe([r1, _get_op(node), r2], " ".join)
        elif _is_shift_op(node):
            r1, r2 = pipe(
                [node, ctx],
                juxt([
                    comp(attrgetter("operands"), first),
                    comp(repeat, second)]), R.apply(zip),
                map(juxt([
                    first,
                    comp(
                        R.apply(merge),
                        juxt([
                            second,
                            R.always(dict(lhs=False, lhint=None)),
                            R.if_else(
                                comp(R.isinstance(Constant), first),
                                R.always(dict(thint=_THint.integer)),
                                R.always(dict(thint=_THint.un_signed)))
                        ]))])),
                map(R.apply(_printexpr)))
            expr = _fn_call(_shift_op[node.op], r1, r2)
            if thint == _THint.integer:
                return _fn_call("to_integer", expr)
            elif thint == _THint.logic:
                return _std_logic_vector(expr)
            else:
                return expr
        elif _is_arith_op(node):
            r1, r2 = pipe(
                node.operands,
                map(lambda x:
                    _printexpr(x,
                               merge(ctx,
                                     dict(lhs=False,
                                          thint=_THint.integer
                                          if R.isinstance(Constant, x)
                                          else _THint.un_signed,
                                          lhint=None)))))
            expr = pipe([r1, _arith_op_map[node.op], r2], " ".join)
            if thint == _THint.integer:
                return _fn_call("to_integer", expr)
            elif thint == _THint.logic:
                return _std_logic_vector(expr)
            else:
                return expr

    raise TypeError("unkown operator: {}, arity: {}".format(node, arity))


@singledispatch
def _printnode(node, ctx):
    raise NotImplementedError("{} not implemented".format(type(node)))


@_printnode.register(Iterable)
def _printnode_iterable(node, ctx):
    return pipe(
        node, map(flip(_printnode, merge(ctx, dict(thint=None, lhint=None)))), ";\n".join)


@_printnode.register(If)
def _printnode_if(node, ctx):
    return lookup.get_template("if.mako").render(**(assoc(ctx, "node", node)))


@_printnode.register(Case)
def _printnode_case(node, ctx):
    return lookup.get_template("case.mako").render(**(assoc(ctx, "node", node)))


@_printnode.register(None)
def _printnode_none(node, ctx):
    return ""


@_printnode.register(_Assign)
def _printnode_assign(node, ctx):
    at = get("at", ctx)
    if R.isinstance(Cat, node.l):
        return pipe(
            node.l.l,
            reversed,
            map(juxt([identity, len])),
            list,
            juxt([identity, comp(sum, map(second))]),
            juxt([first,
                  comp(reduce(partial(accumulate, sub)),
                       juxt([comp(map(second), first),
                             second]))]),
            R.apply(zip),
            map(lambda x: _printnode(
                x[0][0].eq(node.r[x[1] - x[0][1]: x[1]]), ctx)),
            ";\n".join)

    lhs = _printexpr(node.l, merge(ctx,
                                   dict(lhs=True,
                                        thint=_THint.logic,
                                        lhint=None)))
    rhs = _printexpr(node.r, merge(ctx,
                                   dict(
                                       lhs=False,
                                       thint=_THint.logic,
                                       lhint=len(node.l)
                                       if R.isinstance(Constant, node.r) or
                                       len(node.l) > len(node.r)
                                       else None)))

    return pipe([lhs, ":=" if at == _AT_BLOCKING else "<=", rhs], " ".join)


@singledispatch
def _printgeneric(param, ns):
    from migen.fhdl.specials import Instance

    if R.isinstance(Instance.PreformattedParam, param):
        return param

    raise NotImplementedError("{} not implemented".format(type(param)))


@_printgeneric.register(Constant)
def _printgeneric_constant(param, ns):
    return "{}".format(param.value)


@_printgeneric.register(float)
def _printgeneric_float(param, ns):
    return "{}".format(param)


@_printgeneric.register(str)
def _printgeneric_str(param, ns):
    return "\"{}\"".format(param)


def _variables(f, specials, ios):
    return pipe(
        f,
        juxt([
            _sigs,
            comp(partial(or_, ios), set, concat, map(second), _cd_regs),
            flip(_wires, ios)]),
        reduce(sub))


def _wires(f, ios):
    return pipe(
        f,
        partial(list_special_ios, ins=True, outs=True, inouts=True),
        flip(sub, ios))


def _buffer_variables(f, ios):
    return pipe(
        f,
        juxt([
            comp(and_(ios), list_targets),
            comp(set, concat, map(second), _cd_regs),
            partial(list_special_ios, ins=False, outs=True, inouts=True)]),
        reduce(sub))


def _printarchitecture(f, ios, name, ns, overrides, specials, add_data_file):
    ctx = dict(
        name=name,
        ns=ns,
        f=f,
        ios=ios,
        sensitivity_list=list(_sensitivity_list(f, ns, ios)),
        cd_regs=pipe(f, _cd_regs, list),
        variables=pipe(_variables(f, specials, ios), _sort_by_hash),
        wires=pipe(_wires(f, ios), _sort_by_hash),
        buffer_variables=pipe(_buffer_variables(f, ios), _sort_by_hash),
        groups=group_by_targets(f.comb),
        assignments=pipe(f, _assignments),
        sync_statements=pipe(f, _sorted_sync),
        comb_statements=pipe(f, _comb_statements),
        cds=pipe(
            f, _get_clock_domains, partial(sorted, key=attrgetter("name"))),
        specials=pipe(
            specials,
            _sort_by_hash,
            map(partial(call_special_classmethod, overrides,
                        method="emit_vhdl", ns=ns,
                        add_data_file=add_data_file))))
    return lookup.get_template("architecture.mako").render(**ctx)


def convert(f, ios=None, name="top",
            special_overrides=dict(),
            attr_translate=None,
            create_clock_domains=True,
            display_run=False,
            asic_syntax=False):
    r = ConvOutput()
    if R.complement(R.isinstance(_Fragment))(f):
        f = f.get_fragment()
    if ios is None:
        ios = set()

    for cd_name in sorted(list_clock_domains(f)):
        try:
            f.clock_domains[cd_name]
        except KeyError:
            if create_clock_domains:
                cd = ClockDomain(cd_name)
                f.clock_domains.append(cd)
                ios |= {cd.clk, cd.rst}
            else:
                raise KeyError("Unresolved clock domain: '{}'".format(cd_name))

    f = lower_complex_slices(f)
    insert_resets(f)
    f = lower_basics(f)
    fs, lowered_specials = lower_specials(special_overrides, f.specials)
    f += lower_basics(fs)

    ns = build_namespace(
        list_signals(f) | list_special_ios(f, True, True, True) | ios,
        _reserved_keywords)
    ns.clock_domains = f.clock_domains
    r.ns = ns
    specials = f.specials - lowered_specials
    r.set_main_source("".join([
        _printentity(f, ios, name, ns),
        _printarchitecture(
            f, ios, name, ns, special_overrides, specials, r.add_data_file)]))

    return r
