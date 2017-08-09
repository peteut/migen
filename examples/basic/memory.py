import tempfile
from os import path
from migen import *  # noqa
from migen.fhdl import verilog


class Example(Module):
    def __init__(self):
        self.specials.mem = Memory(32, 100, init=[5, 18, 32])
        p1 = self.mem.get_port(write_capable=True, we_granularity=8)
        p2 = self.mem.get_port(has_re=True, clock_domain="rd")
        self.specials += p1, p2
        self.ios = {p1.adr, p1.dat_r, p1.we, p1.dat_w,
                    p2.adr, p2.dat_r, p2.re}


if __name__ == "__main__":
    example = Example()
    fname = path.join(tempfile.gettempdir(), "memory.v")
    verilog.convert(example, example.ios).write(fname)
