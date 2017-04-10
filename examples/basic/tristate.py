import subprocess
from os import path
import tempfile
from migen import *  # noqa
from migen.fhdl import vhdl


class Example(Module):
    def __init__(self, n=6):
        self.pad = Signal(n)
        self.t = TSTriple(n)
        self.specials += self.t.get_tristate(self.pad)

if __name__ == "__main__":
    e = Example()
    fname = path.join(tempfile.gettempdir(), "tristate.vhd")
    vhdl.convert(e, ios={e.pad, e.t.o, e.t.oe, e.t.i}).write(fname)
    subprocess.check_call(["nvc", "--syntax", fname])
    subprocess.check_call(["nvc", "-a", fname])
