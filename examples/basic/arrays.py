import subprocess
from os import path
import tempfile
from migen import *  # noqa
from migen.fhdl import vhdl


class Example(Module):
    def __init__(self):
        dx = 2
        dy = 2

        x = Signal(max=dx)
        y = Signal(max=dy)
        out = Signal()

        my_2d_array = Array(Array(Signal() for a in range(dx)) for b in
                            range(dy))
        self.comb += out.eq(my_2d_array[x][y])

        we = Signal()
        inp = Signal()
        self.sync += If(we,
                        my_2d_array[x][y].eq(inp)
                        )

        ina = Array(Signal() for a in range(dx))
        outa = Array(Signal() for a in range(dy))
        self.specials += Instance("test", o_O=outa[y], i_I=ina[x])
        self.specials += Instance("test", o_O=outa[y], i_I=ina[x])


if __name__ == "__main__":
    fname = path.join(tempfile.gettempdir(), "array.vhd")
    vhdl.convert(Example()).write(fname)
    subprocess.check_call(["nvc", "--syntax", fname])
