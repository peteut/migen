import subprocess
from os import path
import tempfile
from migen import *  # noqa
from migen.fhdl import vhdl
from migen.genlib.divider import Divider


class CDM(Module):
    def __init__(self):
        self.submodules.divider = Divider(5)
        self.clock_domains.cd_sys = ClockDomain(reset_less=True)


class MultiMod(Module):
    def __init__(self):
        self.submodules.foo = CDM()
        self.submodules.bar = CDM()


if __name__ == "__main__":
    fname = path.join(tempfile.gettempdir(), "local_cd.vhd")
    mm = MultiMod()
    vhdl.convert(mm, {mm.foo.cd_sys.clk, mm.bar.cd_sys.clk}).write(fname)
    subprocess.check_call(["nvc", "--syntax", fname])
    subprocess.check_call(["nvc", "-a", fname])
