import pytest
from toolz.curried import *  # noqa
from migen import *  # noqa
from migen.fhdl.structure import _Fragment
from migen.fhdl.specials import Tristate
from migen.fhdl.vhdl import _printexpr, _THint


class NameSpace():
    def get_name(self, sig):
        return sig.backtrace[-1][0]


_printexpr_ctx = comp(
    dict,
    partial(zip,
            ["f", "ns", "at", "lhs", "buffer_variables", "thint", "lhint"]))


@pytest.mark.parametrize(
    "args, expected", [
        ((Constant(1), _printexpr_ctx([
            None, NameSpace(), None, None, None, _THint.integer, None])), "1"),
        ((Constant(-1), _printexpr_ctx([
            None, NameSpace(), None, None, None, _THint.integer, None])),
            "(-1)"),
        ((Constant(42), _printexpr_ctx([
            None, NameSpace(), None, None, None, _THint.un_signed,
            "foo'length"])), "to_unsigned(42, foo'length)"),
        ((Constant(42), _printexpr_ctx([
            None, NameSpace(), None, None, None, _THint.logic, "foo'length"])),
            "std_logic_vector(to_unsigned(42, foo'length))"),
        ((Constant(-42), _printexpr_ctx([
            None, NameSpace(), None, None, None, _THint.logic, 32])),
            "std_logic_vector(to_signed(-42, 32))"),
        ((Constant(1), _printexpr_ctx([
            None, NameSpace(), None, None, None, _THint.logic, None])), "'1'"),
        ((Constant(0), _printexpr_ctx([
            None, NameSpace(), None, None, None, _THint.logic, 32])),
            "(others => '0')"),
        ((Constant(1), _printexpr_ctx([
            None, NameSpace(), None, None, None, _THint.logic, 32])),
            "(0 => '1', others => '0')")])
def test_printexpr_should_handle_constant(args, expected):
    assert _printexpr(*args) == expected


foo = Signal(32)
bar = Signal((32, True))
bar_ = Signal(32)


@pytest.mark.parametrize(
    "args, expected", [
        ((foo, _printexpr_ctx([
            _Fragment(), NameSpace(), None, None, None, None, None])), "foo"),
        ((foo, _printexpr_ctx([
            _Fragment(), NameSpace(), None, None, None, _THint.logic, None])),
            "foo"),
        ((foo, _printexpr_ctx([
            _Fragment(), NameSpace(), None, None, None, _THint.un_signed,
            None])), "unsigned(foo)"),
        ((bar, _printexpr_ctx([
            _Fragment(), NameSpace(), None, None, None, _THint.un_signed,
            None])), "signed(bar)"),
        ((bar, _printexpr_ctx([
            _Fragment(), NameSpace(), None, None, None, _THint.integer, None])),
            "to_integer(signed(bar))")
    ])
def test_printexpr_should_handle_signal(args, expected):
    assert _printexpr(*args) == expected


@pytest.mark.parametrize(
    "args, expected", [
        ((foo[:10], _printexpr_ctx([
            _Fragment(), NameSpace(), None, None, None, _THint.logic,
            None])), "foo(9 downto 0)"),
        ((foo[:10], _printexpr_ctx([
            _Fragment(), NameSpace(), None, None, None, _THint.un_signed,
            None])), "unsigned(foo(9 downto 0))"),
        ((foo[:10], _printexpr_ctx([
            _Fragment(), NameSpace(), None, None, None, _THint.integer, None])),
            "to_integer(unsigned(foo(9 downto 0)))")
    ])
def test_printexpr_should_handle_slice(args, expected):
    assert _printexpr(*args) == expected


@pytest.mark.parametrize(
    "args, expected", [
        ((Cat(foo, bar), _printexpr_ctx([
            _Fragment(), NameSpace(), None, None, None, _THint.logic, None])),
            "(bar & foo)"),
        ((Cat(foo, Constant(42)), _printexpr_ctx([
            _Fragment(), NameSpace(), None, None, None, _THint.logic, None])),
            "(std_logic_vector(to_unsigned(42, 6)) & foo)"),
        ((Cat(foo, bar), _printexpr_ctx([
            _Fragment(), NameSpace(), None, None, None, _THint.un_signed, None])),
            "unsigned((bar & foo))"),
        ((Cat(foo, bar), _printexpr_ctx([
            _Fragment(), NameSpace(), None, None, None, _THint.integer, None])),
            "to_integer(unsigned((bar & foo)))")
    ])
def test_printexpr_should_handle_cat(args, expected):
    assert _printexpr(*args) == expected


@pytest.mark.parametrize(
    "args, expected", [
        # arity 1
        ((-foo, _printexpr_ctx([
            _Fragment(), NameSpace(), None, None, None, _THint.logic, None])),
            "std_logic_vector((-signed(foo)))"),
        ((~foo, _printexpr_ctx([
            _Fragment(), NameSpace(), None, None, None, _THint.un_signed, None])),
            "unsigned(not foo)"),
        ((~Constant(42), _printexpr_ctx([
            _Fragment(), NameSpace(), None, None, None, _THint.integer, None])),
            "to_integer(unsigned(not std_logic_vector(to_unsigned(42, 6))))"),
        # arity 2
        # bitwise
        ((foo & bar, _printexpr_ctx([
            _Fragment(), NameSpace(), None, None, None, _THint.logic, None])),
            "foo and bar"),
        ((foo | bar, _printexpr_ctx([
            _Fragment(), NameSpace(), None, None, None, _THint.un_signed, None])),
            "unsigned(foo or bar)"),
        ((foo ^ bar, _printexpr_ctx([
            _Fragment(), NameSpace(), None, None, None, _THint.un_signed, None])),
            "unsigned(foo xor bar)"),
        # compare
        ((foo >= bar_, _printexpr_ctx([
            _Fragment(), NameSpace(), None, None, None, _THint.logic, None])),
            "\?>=\(unsigned(foo), unsigned(bar_))"),
        ((foo > Constant(42), _printexpr_ctx([
            _Fragment(), NameSpace(), None, None, None, _THint.logic, None])),
            "\?>\(unsigned(foo), 42)"),
        ((foo > Constant(42), _printexpr_ctx([
            _Fragment(), NameSpace(), None, None, None, None, None])),
            "unsigned(foo) > 42"),
        ((foo << Constant(2), _printexpr_ctx([
            _Fragment(), NameSpace(), None, None, None, None, None])),
            "shift_left(unsigned(foo), 2)"),
        ((foo << Constant(2), _printexpr_ctx([
            _Fragment(), NameSpace(), None, None, None, None, None])),
            "shift_left(unsigned(foo), 2)"),
        ((foo >> Constant(2), _printexpr_ctx([
            _Fragment(), NameSpace(), None, None, None, _THint.logic, None])),
            "std_logic_vector(shift_right(unsigned(foo), 2))"),
    ])
def test_printexpr_should_handle_operator(args, expected):
    assert _printexpr(*args) == expected


@pytest.mark.parametrize(
    "triple, expected",
    [((TSTriple(min=0, max=2**32 - 1)), """\
foo <= o
    when \??\(oe)
    else (others => 'Z');
i <= foo;
""")])
def test_tristate(triple, expected):
    assert Tristate.emit_vhdl(
        triple.get_tristate(foo), NameSpace(), None) == expected
