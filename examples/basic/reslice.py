import subprocess
import tempfile
from os import path
from migen import *  # noqa
from migen.fhdl import vhdl


class Example(Module):
    def __init__(self):
        a = Signal(3)
        b = Signal(4)
        c = Signal(5)
        d = Signal(7)
        s1 = c[:3][:2]
        s2 = Cat(a, b)[:6]
        s3 = Cat(s1, s2)[-5:]
        self.comb += s3.eq(0)
        self.comb += d.eq(Cat(d[::-1][3:], Cat(s1[:1], s3[-4:])[:3]))


if __name__ == "__main__":
    fname = path.join(tempfile.gettempdir(), "reslice.vhd")
    vhdl.convert(Example()).write(fname)
    subprocess.check_call(["nvc", "--syntax", fname])
    subprocess.check_call(["nvc", "--std=2008", "-a", fname])
