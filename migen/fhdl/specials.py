from operator import itemgetter

from migen.fhdl.structure import *  # noqa
from migen.fhdl.structure import _Value
from migen.fhdl.bitcontainer import bits_for, value_bits_sign
from migen.fhdl.tools import *  # noqa
from migen.fhdl.tracer import get_obj_var_name
from migen.fhdl.verilog import _printexpr as verilog_printexpr


__all__ = ["TSTriple", "Instance", "Memory",
    "READ_FIRST", "WRITE_FIRST", "NO_CHANGE"]


class Special:
    def __init__(self):
        self._duid = next(duid)

    def iter_expressions(self):
        for x in []:
            yield x

    def rename_clock_domain(self, old, new):
        for obj, attr, direction in self.iter_expressions():
            rename_clock_domain_expr(getattr(obj, attr), old, new)

    def list_clock_domains(self):
        r = set()
        for obj, attr, direction in self.iter_expressions():
            r |= list_clock_domains_expr(getattr(obj, attr))
        return r

    def list_ios(self, ins, outs, inouts):
        r = set()
        for obj, attr, direction in self.iter_expressions():
            if (direction == SPECIAL_INPUT and ins) \
              or (direction == SPECIAL_OUTPUT and outs) \
              or (direction == SPECIAL_INOUT and inouts):
                signals = list_signals(getattr(obj, attr))
                r.update(signals)
        return r

    def __hash__(self):
        return self._duid


class Tristate(Special):
    def __init__(self, target, o, oe, i=None):
        super().__init__()
        self.target = wrap(target)
        self.o = wrap(o)
        self.oe = wrap(oe)
        self.i = wrap(i) if i is not None else None

    def iter_expressions(self):
        for attr, target_context in [
          ("target", SPECIAL_INOUT),
          ("o", SPECIAL_INPUT),
          ("oe", SPECIAL_INPUT),
          ("i", SPECIAL_OUTPUT)]:
            if getattr(self, attr) is not None:
                yield self, attr, target_context

    @staticmethod
    def emit_verilog(tristate, ns, add_data_file):
        def pe(e):
            return verilog_printexpr(ns, e)[0]
        w, s = value_bits_sign(tristate.target)
        r = "assign " + pe(tristate.target) + " = " \
            + pe(tristate.oe) + " ? " + pe(tristate.o) \
            + " : " + str(w) + "'bz;\n"
        if tristate.i is not None:
            r += "assign " + pe(tristate.i) + " = " + pe(tristate.target) + ";\n"
        r += "\n"
        return r


class TSTriple:
    def __init__(self, bits_sign=None, min=None, max=None, reset_o=0, reset_oe=0):
        self.o = Signal(bits_sign, min=min, max=max, reset=reset_o)
        self.oe = Signal(reset=reset_oe)
        self.i = Signal(bits_sign, min=min, max=max)

    def get_tristate(self, target):
        return Tristate(target, self.o, self.oe, self.i)


class Instance(Special):
    class _IO:
        def __init__(self, name, expr=None):
            self.name = name
            if expr is None:
                expr = Signal()
            self.expr = wrap(expr)
    class Input(_IO):
        pass
    class Output(_IO):
        pass
    class InOut(_IO):
        pass
    class Parameter:
        def __init__(self, name, value):
            self.name = name
            if isinstance(value, (int, bool)):
                value = Constant(value)
            self.value = value
    class PreformattedParam(str):
        pass

    def __init__(self, of, *items, name="", synthesis_directive=None, **kwargs):
        super().__init__()
        self.of = of
        if name:
            self.name_override = name
        else:
            self.name_override = of
        self.items = list(items)
        self.synthesis_directive = synthesis_directive
        for k, v in sorted(kwargs.items(), key=itemgetter(0)):
            item_type, item_name = k.split("_", maxsplit=1)
            item_class = {
                "i": Instance.Input,
                "o": Instance.Output,
                "io": Instance.InOut,
                "p": Instance.Parameter
            }[item_type]
            self.items.append(item_class(item_name, v))

    def get_io(self, name):
        for item in self.items:
            if isinstance(item, Instance._IO) and item.name == name:
                return item.expr

    def iter_expressions(self):
        for item in self.items:
            if isinstance(item, Instance.Input):
                yield item, "expr", SPECIAL_INPUT
            elif isinstance(item, Instance.Output):
                yield item, "expr", SPECIAL_OUTPUT
            elif isinstance(item, Instance.InOut):
                yield item, "expr", SPECIAL_INOUT

    @staticmethod
    def emit_verilog(instance, ns, add_data_file):
        r = instance.of + " "
        parameters = list(filter(lambda i: isinstance(i, Instance.Parameter), instance.items))
        if parameters:
            r += "#(\n"
            firstp = True
            for p in parameters:
                if not firstp:
                    r += ",\n"
                firstp = False
                r += "\t." + p.name + "("
                if isinstance(p.value, Constant):
                    r += verilog_printexpr(ns, p.value)[0]
                elif isinstance(p.value, float):
                    r += str(p.value)
                elif isinstance(p.value, Instance.PreformattedParam):
                    r += p.value
                elif isinstance(p.value, str):
                    r += "\"" + p.value + "\""
                else:
                    raise TypeError
                r += ")"
            r += "\n) "
        r += ns.get_name(instance)
        if parameters: r += " "
        r += "(\n"
        firstp = True
        for p in instance.items:
            if isinstance(p, Instance._IO):
                name_inst = p.name
                name_design = verilog_printexpr(ns, p.expr)[0]
                if not firstp:
                    r += ",\n"
                firstp = False
                r += "\t." + name_inst + "(" + name_design + ")"
        if not firstp:
            r += "\n"
        if instance.synthesis_directive is not None:
            synthesis_directive = "/* synthesis {} */".format(instance.synthesis_directive)
            r += ")" + synthesis_directive + ";\n\n"
        else:
            r += ");\n\n"
        return r


(READ_FIRST, WRITE_FIRST, NO_CHANGE) = range(3)


class _MemoryPort(Special):
    def __init__(self, adr, dat_r, we=None, dat_w=None,
      async_read=False, re=None, we_granularity=0, mode=WRITE_FIRST,
      clock_domain="sys"):
        super().__init__()
        self.adr = adr
        self.dat_r = dat_r
        self.we = we
        self.dat_w = dat_w
        self.async_read = async_read
        self.re = re
        self.we_granularity = we_granularity
        self.mode = mode
        self.clock = ClockSignal(clock_domain)

    def iter_expressions(self):
        for attr, target_context in [
          ("adr", SPECIAL_INPUT),
          ("we", SPECIAL_INPUT),
          ("dat_w", SPECIAL_INPUT),
          ("re", SPECIAL_INPUT),
          ("dat_r", SPECIAL_OUTPUT),
          ("clock", SPECIAL_INPUT)]:
            yield self, attr, target_context

    @staticmethod
    def emit_verilog(port, ns, add_data_file):
        return ""  # done by parent Memory object


class _MemoryLocation(_Value):
    def __init__(self, memory, index):
        _Value.__init__(self)
        self.memory = memory
        self.index = wrap(index)


class Memory(Special):
    def __init__(self, width, depth, init=None, name=None):
        super().__init__()
        self.width = width
        self.depth = depth
        self.ports = []
        self.init = init
        self.name_override = get_obj_var_name(name, "mem")

    def __getitem__(self, index):
        # simulation only
        return _MemoryLocation(self, index)

    def get_port(self, write_capable=False, async_read=False,
      has_re=False, we_granularity=0, mode=WRITE_FIRST,
      clock_domain="sys"):
        if we_granularity >= self.width:
            we_granularity = 0
        adr = Signal(max=self.depth)
        dat_r = Signal(self.width)
        if write_capable:
            if we_granularity:
                we = Signal(self.width // we_granularity)
            else:
                we = Signal()
            dat_w = Signal(self.width)
        else:
            we = None
            dat_w = None
        if has_re:
            re = Signal()
        else:
            re = None
        mp = _MemoryPort(adr, dat_r, we, dat_w,
          async_read, re, we_granularity, mode,
          clock_domain)
        self.ports.append(mp)
        return mp

    @staticmethod
    def emit_verilog(memory, ns, add_data_file):
        r = ""
        def gn(e):
            if isinstance(e, Memory):
                return ns.get_name(e)
            else:
                return verilog_printexpr(ns, e)[0]
        adrbits = bits_for(memory.depth - 1)

        r += "".join(("reg [{}:0] ".format(memory.width - 1),
                      gn(memory),
                      "[0:{}];\n".format(memory.depth - 1)))

        adr_regs = {}
        data_regs = {}
        for port in memory.ports:
            if not port.async_read:
                if port.mode == WRITE_FIRST and port.we is not None:
                    adr_reg = Signal(name_override="memadr")
                    r += "".join(("reg [{}:0] ".format(adrbits - 1),
                                  gn(adr_reg), ";\n"))
                    adr_regs[id(port)] = adr_reg
                else:
                    data_reg = Signal(name_override="memdat")
                    r += "".join(("reg [{}:0] ".format(memory.width - 1),
                                  gn(data_reg), ";\n"))
                    data_regs[id(port)] = data_reg

        for port in memory.ports:
            r += "always @(posedge {}) begin\n".format(gn(port.clock))
            if port.we is not None:
                if port.we_granularity:
                    n = memory.width // port.we_granularity
                    for i in range(n):
                        m = i * port.we_granularity
                        M = (i + 1) * port.we_granularity - 1
                        sl = "[{}:{}]".format(M, m)
                        r += "\tif ({}[{}])\n".format(gn(port.we), i)
                        r += "\t\t{}[{}]{} <= {}{};\n".format(
                            gn(memory), gn(port.adr), sl, gn(port.dat_w), sl)
                else:
                    r += "\tif ({})\n".format(gn(port.we))
                    r += "\t\t{}[{}] <= {};\n".format(
                        gn(memory), gn(port.adr), gn(port.dat_w))
            if not port.async_read:
                if port.mode == WRITE_FIRST and port.we is not None:
                    rd = "\t{} <= {};\n".format(
                        gn(adr_regs[id(port)]), gn(port.adr))
                else:
                    bassign = "{} <= {}[{}];\n".format(
                        gn(data_regs[id(port)]), gn(memory), gn(port.adr))
                    if port.mode == READ_FIRST or port.we is None:
                        rd = "\t" + bassign
                    elif port.mode == NO_CHANGE:
                        rd = ("\tif (!{})\n".format(gn(port.we))
                              + "\t\t" + bassign)
                if port.re is None:
                    r += rd
                else:
                    r += "\tif ({})\n".format(gn(port.re))
                    r += "\t" + rd.replace("\n\t", "\n\t\t")
            r += "end\n\n"

        for port in memory.ports:
            if port.async_read:
                r += "assign {} = {}[{}];\n".format(
                    gn(port.dat_r), gn(memory), gn(port.adr))
            else:
                if port.mode == WRITE_FIRST and port.we is not None:
                    r += "assign {} = {}[{}];\n".format(
                        gn(port.dat_r), gn(memory), gn(adr_regs[id(port)]))
                else:
                    r += "assign {} = {};\n".format(
                        gn(port.dat_r), gn(data_regs[id(port)]))
        r += "\n"

        if memory.init is not None:
            content = ""
            for d in memory.init:
                content += "{:x}\n".format(d)
            memory_filename = add_data_file(gn(memory) + ".init", content)

            r += "initial begin\n"
            r += "\t$readmemh(\"{}\", {});\n".format(memory_filename, gn(memory))
            r += "end\n\n"

        return r


class SynthesisDirective(Special):
    def __init__(self, template, **signals):
        super().__init__()
        self.template = template
        self.signals = signals

    @staticmethod
    def emit_verilog(directive, ns, add_data_file):
        name_dict = dict((k, ns.get_name(sig)) for k, sig in directive.signals.items())
        formatted = directive.template.format(**name_dict)
        return "// synthesis " + formatted + "\n"


class Keep(SynthesisDirective):
    def __init__(self, signal):
        super().__init__("attribute keep of {s} is true", s=signal)
