from migen.fhdl.std import Module, Signal, TSTriple
from migen.fhdl import verilog


class Example(Module):
    def __init__(self, n=6):
        self.pad = Signal(n)
        self.t = TSTriple(n)
        self.specials += self.t.get_tristate(self.pad)

e = Example()

if __name__ == "__main__":
    print(verilog.convert(e, ios={e.pad, e.t.o, e.t.oe, e.t.i}))
