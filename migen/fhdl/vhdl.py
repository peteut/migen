from collections import Iterable, Hashable
try:
    from functools import singledispatch
except ImportError:
    from multimethods import singledispatch
from enum import Enum

from migen.fhdl.structure import *  # noqa

from migen.fhdl.structure import *  # noqa
from migen.fhdl.structure import _Operator,_Slice, _Assign, _Fragment
from migen.fhdl.tools import *  # noqa
from migen.fhdl.namer import build_namespace
from migen.fhdl.conv_output import ConvOutput

from mako.template import Template

from toolz.curried import *  # noqa
from toolz.compatibility import iteritems
from operator import (is_, and_, or_, and_, attrgetter, sub,
                      mul, contains)

is_, and_, mul, sub, contains = map(curry, [is_, and_, mul, sub, contains])

_isinstance = flip(isinstance)

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


def _get_sigtype(s):
    return ("std_ulogic" if len(s) is 1
            else "std_logic_vector({} downto 0)".format(len(s) - 1))

_entitytemplate = Template(
"""\
<%!
from migen.fhdl.vhdl import _get_sigtype
%><%
def _direction(sig):
    return "inout" if sig in inouts else "out" if sig in targets else "in"
%>\
-- Machine generated using Migen - experimental VHDL backend
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
library ieee_proposed;
use ieee_proposed.numeric_std_additions.all;
use ieee_proposed.std_logic_1164_additions.all;

entity ${name} is
% for sig in ios:
${"port (" if bool(loop.first) else " " * 6}\
${ns.get_name(sig)}: \
${_direction(sig)} ${_get_sigtype(sig)}${")" * bool(loop.last)};
% endfor
end entity ${name};
""")

@curry
def apply(fn, args):
    return fn(*args)


_sigs = comp(reduce(or_),
             juxt([list_signals,
                   comp(apply(list_special_ios),
                        flip(cons, [True, True, True]))]))
_inouts = comp(apply(list_special_ios), flip(cons, [False, False, True]))
_targets = comp(reduce(or_),
                juxt([list_targets,
                      comp(apply(list_special_ios),
                           flip(cons, [False, True, True]))]))


def _printentity(f, ios, name, ns):
    return _entitytemplate.render(
        name=name, sigs=_sigs(f), inouts=_inouts(f),
        targets=_targets(f), ns=ns, ios=sorted(ios, key=hash))

_get_comb, _get_sync, _get_clock_domains = map(
    attrgetter, ["comb", "sync", "clock_domains"])
_reg_typename = "{}_reg_t".format
_rin_name = "{}_rin".format
_r_name = "{}_r".format
_v_name = "{}_v".format
_sorted_sync = comp(concatv, partial(sorted, key=get(0)), iteritems, _get_sync)
_cd_regs = comp(
    map(juxt(
    [first,
     comp(list, filter(complement(is_variable)),
          filter(comp(_isinstance(Signal))), list_targets, second)])),
    _sorted_sync)
_assignment_filter_fn = comp(
    reduce(and_), juxt([comp(is_(1), len, first),
                        comp(_isinstance(_Assign), get_in([1, 0]))]))
_assignments = comp(pluck(0), pluck(1), filter(_assignment_filter_fn),
                    concatv, group_by_targets, _get_comb)
_comb = comp(concatv, group_by_targets, _get_comb)
_comb_statements = comp(pluck(1), _comb)
# _comb_sigs = comp(concat, pluck(0), _comb)


def _sensitivity_list(f, ns, ios):
    return pipe(
        (ios | _inouts(f)) -
        (_targets(f) |
         pipe(f, _get_clock_domains, map(attrgetter("clk")), set)),
        map(ns.get_name),
        flip(concatv, pipe(f, _get_clock_domains, map(attrgetter("name")),
                           map(_r_name))),
        tuple)

_indent = mul("    ")
_AT_BLOCKING, _AT_NONBLOCKING, _AT_SIGNAL = range(3)
_THint = Enum("THint", "boolean logic un_signed  integer")


@singledispatch
def _printexpr(node, f, ns, at, lhs, buffer_variables, thint, lhint):
    raise NotImplementedError("{} not implemented".format(type(node)))


_fntemplate = Template( """\
<%! from collections import Iterable

def _iterable(arg):
    return isinstance(arg, Iterable) and not isinstance(arg, str)
%>\
${name | trim}(${", ".join(map(str, args)) if _iterable(args) else args})\
""")


def _fn_call(name, *args):
    return _fntemplate.render(name=name, args=args)

_unsigned, _signed, _std_logic_vector, _to_integer = map(
    partial(partial, _fn_call),
    ["unsigned", "signed", "std_logic_vector", "to_integer"])


@_printexpr.register(Constant)
def _printexpr_constant(node, f, ns, at, lhs, buffer_variables, thint, lhint):
    if thint == _THint.integer:
        return "({})".format(node.value) if node.value < 0 \
            else "{}".format(node.value)
    elif thint == _THint.logic:
        if len(node) == 1 and not lhint:
            return "'{}'".format(node.value)
        elif node.value == 0:
            return "(others => '0')"
        elif node.value == 2 ** len(node) - 1:
            return "(others => '1')"
        else:
            return _std_logic_vector(
                _fn_call("to_signed" if node.signed else "to_unsigned",
                         node.value, lhint or len(node)))
    else:
        return _fn_call("to_signed" if node.signed else "to_unsigned",
                        node.value, lhint or len(node))


@_printexpr.register(Signal)
def _printexpr_signal(node, f, ns, at, lhs, buffer_variables, thint, lhint):
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
        casted = _unsigned(" & ".join(["\"\"", identifier]))
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
def _printexpr_slice(node, f, ns, at, lhs, buffer_variables, thint, lhint):
    if node.start + 1 == node.stop:
        sr = "" if len(node.value) == 1 else "({})".format(node.start)
    else:
        sr = "({} downto {})".format(node.stop - 1, node.start)
    expr = "".join([_printexpr(node.value, f, ns, at, lhs, buffer_variables,
                               _THint.logic, None), sr])
    if thint == _THint.un_signed:
        return _unsigned(expr)
    elif thint == _THint.integer:
        return _fn_call("to_integer", _unsigned(expr))
    elif thint == _THint.boolean:
        return _fn_call("\\??\\", expr)
    else:
        return expr


@_printexpr.register(Cat)
def _printexpr_cat(node, f, ns, at, lhs, buffer_variables, thint, lhint):
    expr = pipe(node.l, map(
        comp(partial(_printexpr, f=f, ns=ns, at=at, lhs=lhs,
                     buffer_variables=buffer_variables,
                     thint=_THint.logic, lhint=None))),
        tuple, reversed, " & ".join, "({})".format)
    if thint == _THint.un_signed:
        return _unsigned(expr)
    elif thint == _THint.integer:
        return _fn_call("to_integer", _unsigned(expr))
    else:
        return expr


def _is_op_cmp(node):
    return node.op == "==" if isinstance(node, _Operator) else False


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
def _printexpr_operator(node, f, ns, at, lhs, buffer_variables, thint, lhint):
    arity = len(node.operands)
    if arity == 1:
        r1 = _printexpr(node.operands[0], f, ns, at, False,
                        buffer_variables, _THint.logic, None)
        if node.op == "-":
            expr = "(-{})".format(_signed(r1))
            if thint == _THint.un_signed:
                return expr
            elif thint == _THint.integer:
                return _to_integer("to_integer", expr)
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
            r1, r2 = map(partial(_printexpr, f=f, ns=ns, at=at, lhs=False,
                                 buffer_variables=buffer_variables,
                                 thint=_THint.logic, lhint=None), node.operands)
            expr = " ".join([r1, _get_op(node), r2])
            if thint == _THint.un_signed:
                return _unsigned(expr)
            elif thint == _THint.integer:
                return _fn_call("to_integer", expr)
            else:
                return expr
        elif _is_comp_op(node):
            if all(map(comp(is_(1), len),node.operands)):
                r1, r2 = map(partial(_printexpr, f=f, ns=ns, at=at, lhs=False,
                                     buffer_variables=buffer_variables,
                                     thint=_THint.logic, lhint=None),
                             node.operands)
            else:
                r1, r2 = map(lambda x:
                             _printexpr(x, f, ns, at, False,
                                        buffer_variables,
                                        _THint.integer if isinstance(x, Constant)
                                        else _THint.un_signed, None),
                             node.operands)
            if thint == _THint.logic:
                return _fn_call(pipe(node, _get_op, "\\?{}\\".format), r1, r2)
            else:
                return " ".join([r1, _get_op(node), r2])
        elif _is_shift_op(node):
            r1, r2 = map(lambda x:
                         _printexpr(x, f, ns, at, False,
                                    buffer_variables,
                                    _THint.integer if isinstance(x, Constant)
                                    else _THint.un_signed, None),
                         node.operands)
            expr = _fn_call(_shift_op[node.op], r1, r2)
            if thint == _THint.integer:
                return _fn_call("to_integer", expr)
            elif thint == _THint.logic:
                return _std_logic_vector(expr)
            else:
                return expr
        elif _is_arith_op(node):
            r1, r2 = map(lambda x:
                         _printexpr(x, f, ns, at, False,
                                    buffer_variables,
                                    _THint.integer if isinstance(x, Constant)
                                    else _THint.un_signed, None),
                         node.operands)
            expr = " ".join([r1, _arith_op_map[node.op], r2])
            if thint == _THint.integer:
                return _fn_call("to_integer", expr)
            elif thint == _THint.logic:
                return _std_logic_vector(expr)
            else:
                return expr

    raise TypeError("unkown operator: {}, arity: {}".format(node, arity))


@singledispatch
def _printnode(node, f, ns, at, level, buffer_variables, thint, lhint):
    raise NotImplementedError("{} not implemented".format(type(node)))


@_printnode.register(Iterable)
def _printnode_iterable(node, f, ns, at, level, buffer_variables, thint, lhint):
    return pipe(node,
                map(partial(_printnode, f=f, ns=ns, at=at, level=level,
                            buffer_variables=buffer_variables,
                            thint=None, lhint=None)),
                ";\n".join)

_iftemplate = Template(
"""\
<%!
from migen.fhdl.vhdl import _indent, _printnode,  _printexpr, _THint
%>\
${_indent(level)}if ${_printexpr(node.cond, f, ns, at, False,
    buffer_variables, _THint.boolean, None)} then
${_printnode(node.t, f, ns, at, level + 1, buffer_variables, None, None)};
% if node.f:
${_indent(level)}else
${_printnode(node.f, f, ns, at, level + 1, buffer_variables, None, None)};
% endif
${_indent(level)}end if\
""")


@_printnode.register(If)
def _printnode_if(node, f, ns, at, level, buffer_variables, thint, lhint):
    return _iftemplate.render(f=f, node=node, ns=ns, at=at,
                              buffer_variables=buffer_variables, level=level)

_casetemplate = Template(
"""\
<%!
from migen.fhdl.vhdl import (_indent, _printnode, _printexpr, _THint, Constant,
    first, flip, filter, pipe, comp, filter, partial, get, attrgetter)
%>\
<%
css = pipe(node.cases.items(), filter(comp(flip(isinstance, Constant), first)),
    tuple, partial(sorted, key=comp(attrgetter("value"), first)))
default = get("default", node.cases, None)
%>\
${_indent(level)}case ${_printexpr(node.test, f, ns, at, False,
    buffer_variables, _THint.integer, False)} is
% for case in css:
${_indent(level)}when ${_printexpr(
    case[0], f, ns, at, False, buffer_variables, _THint.integer, None)} =>
${_printnode(case[1], f, ns, at, level + 1, buffer_variables, None, None)};
% endfor
${_indent(level)}when others =>
% if default:
${_printnode(default, f, ns, at, level + 1, buffer_variables, None, None)};
% else:
${_indent(level)}null;
% endif
${_indent(level)}end case\
""")


@_printnode.register(Case)
def _printnode_case(node, f, ns, at, level, buffer_variables, thint, lhint):
    return _casetemplate.render(node=node, f=f, ns=ns, at=at,
                                level=level, buffer_variables=buffer_variables)


@_printnode.register(None)
def _printnode_none(node, f, ns, at, level, buffer_variables, thint, lhint):
    return ""


@_printnode.register(_Assign)
def _printnode_assign(node, f, ns, at, level, buffer_variables, thint, lhint):
    lhs = _printexpr(node.l, f, ns, at, True, buffer_variables, _THint.logic,
                     None)
    rhs = _printexpr(node.r, f, ns, at, False, buffer_variables, _THint.logic,
                     "{}'length".format(lhs) if len(node.l) > 1 else None)

    return "{}{} {} {}".format(_indent(level), lhs,
                               ":=" if at == _AT_BLOCKING else "<=", rhs)


_architecturetemplate = Template(
"""\
<%!
from migen.fhdl.vhdl import (_reg_typename, _v_name, _r_name, _rin_name,
    _indent, _printnode, _get_sigtype, _Assign, _AT_BLOCKING,
    contains, map, filter, pipe, comp, first, second,
    juxt, identity, attrgetter)

_architecture_id = "two_process_{}".format
%>
architecture ${_architecture_id(name)} of ${name} is

% for cd, sigs in cd_regs:
type ${_reg_typename(cd)} is record
% for sig in sigs:
    ${ns.get_name(sig)}: ${_get_sigtype(sig)};
% endfor
end record ${_reg_typename(cd)};

signal ${_rin_name(cd)}: ${_reg_typename(cd)}; -- register input for cd "${cd}"
signal ${_r_name(cd)}: ${_reg_typename(cd)}; -- register for cd "${cd}"

% endfor
begin

% if not len(sensitivity_list):
comb: process
% else:
comb: process (${", ".join(sensitivity_list)}) is
% endif
% for cd, _ in cd_regs:
variable ${_v_name(cd)}: ${_reg_typename(cd)};  -- variable for cd "${cd}"
% endfor
% for v in variables:
variable ${ns.get_name(v)}: ${_get_sigtype(v)};
% endfor
% for v in buffer_variables:
variable ${_v_name(ns.get_name(v))}: ${_get_sigtype(v)};
% endfor

begin
-- defaults
% for cd in map(first, cd_regs):
${_indent(1)}${_v_name(cd)} := ${_r_name(cd)};
% endfor
-- comb statements
% for statement in comb_statements:
${_printnode(statement, f, ns, _AT_BLOCKING, 1, buffer_variables, None, None)};
% endfor
% for statement in filter(comp(contains(buffer_variables), attrgetter("l")),\
    assignments):
${_printnode(statement, f, ns, _AT_BLOCKING, 1, buffer_variables, None, None)};
% endfor
-- sync statements
% if len(sync_statements):
% for statement in map(second, sync_statements):
${_printnode(statement, f, ns, _AT_BLOCKING, 1, buffer_variables, None, None)};
% endfor
% endif
-- drive register input
% for cd in map(first, cd_regs):
${_indent(1)}${_rin_name(cd)} <= ${_v_name(cd)};
% endfor
-- drive outputs
% for v in buffer_variables:
${_indent(1)}${pipe(v, ns.get_name, juxt([identity, _v_name]), " <= ".join)};
% endfor
% for cd in cd_regs:
-- drive "${cd[0]}" regs
% for sig in pipe(cd, second, filter(contains(ios))):
${_indent(1)}${pipe(sig, ns.get_name,
    juxt([identity,
          comp(".".join, juxt([lambda _: _r_name(cd[0]), identity]))]),
          " <= ".join)};
% endfor
% endfor
end process comb;

% for cd in cds:
${cd.name}_seq: process (${ns.get_name(cd.clk)})
begin
${_indent(1)}if rising_edge(${ns.get_name(cd.clk)}) then
${_indent(2)}${_r_name(cd.name)} <= ${_rin_name(cd.name)};
${_indent(1)}end if;
end process;
% endfor
end architecture ${_architecture_id(name)};\
""")

def _variables(f, ios):
    return sorted(pipe(f, juxt([
        _sigs, comp(set, concat, map(second), _cd_regs)]),
        reduce(sub)) - ios, key=hash)


def _printarchitecture(f, ios, name, ns):
    return _architecturetemplate.render(
        name=name,
        ns=ns,
        f=f,
        ios=ios,
        sensitivity_list=_sensitivity_list(f, ns, ios),
        cd_regs=pipe(f, _cd_regs, list),
        variables=_variables(f, ios),
        buffer_variables=sorted(
            pipe(f, _assignments, map(attrgetter("l")),
                 filter(_isinstance(Hashable)),
                 set, and_(ios)) |
            pipe(f, juxt([_targets, comp(set, concat, map(second), _cd_regs)]),
                 reduce(sub)) - set(_variables(f, ios)), key=hash),
        groups=group_by_targets(f.comb),
        assignments=pipe(f, _assignments, list),
        sync_statements=pipe(f, _sorted_sync, list),
        comb_statements=pipe(f, _comb_statements, list),
        cds=pipe(f, _get_clock_domains,
                 partial(sorted, key=attrgetter("name"))))


def convert(f, ios=None, name="top",
            special_overrides=dict(),
            create_clock_domains=True,
            display_run=False,
            asic_syntax=False):
    r = ConvOutput()
    if not isinstance(f, _Fragment):
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

    ns = build_namespace(unique(concatv(list_signals(f),
                                        list_special_ios(f, True, True, True),
                                        ios)), _reserved_keywords)
    ns.clock_domains = f.clock_domains
    r.ns = ns
    r.set_main_source("".join([
        _printentity(f, ios, name, ns),
        _printarchitecture(f, ios, name, ns)]))

    return r
