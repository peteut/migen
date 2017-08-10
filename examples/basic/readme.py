import subprocess
from os import path
import tempfile
from migen import *  # noqa
from migen.fhdl import vhdl


def get_readme_module():
    m = Module()
    led = Signal()
    counter = Signal(26)
    m.comb += led.eq(counter[25])
    m.sync += counter.eq(counter + 1)
    return m, {led}


if __name__ == "__main__":
    fname = path.join(tempfile.gettempdir(), "readme.vhd")
    example, ios = get_readme_module()
    vhdl.convert(example, ios).write(fname)
    subprocess.check_call(["nvc", "--syntax", fname])
    subprocess.check_call(["nvc", "-a", fname])
