import subprocess
import tempfile
from os import path

from migen import *  # noqa
from migen.fhdl import vhdl


L = [
    ("position", [
        ("x", 10, DIR_M_TO_S),
        ("y", 10, DIR_M_TO_S),
    ]),
    ("color", 32, DIR_M_TO_S),
    ("stb", 1, DIR_M_TO_S),
    ("ack", 1, DIR_S_TO_M)
]


class Test(Module):
    def __init__(self):
        master = Record(L)
        slave = Record(L)
        self.comb += master.connect(slave)


if __name__ == "__main__":
    fname = path.join(tempfile.gettempdir(), "record.vhd")
    vhdl.convert(Test()).write(fname)
    subprocess.check_call(["nvc", "--syntax", fname])
    subprocess.check_call(["nvc", "--std=2008", "-a", fname])
    print(layout_len(L))
    print(layout_partial(L, "position/x", "color"))
