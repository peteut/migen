import subprocess
import tempfile
from os import path
from migen import *  # noqa
from migen.fhdl import vhdl
from migen.genlib import divider


@ResetInserter()
@CEInserter()
class Example(Module):
    def __init__(self, width):
        d1 = divider.Divider(width)
        d2 = divider.Divider(width)
        self.submodules += d1, d2
        self.ios = {
            d1.ready_o, d1.quotient_o, d1.remainder_o, d1.start_i,
            d1.dividend_i, d1.divisor_i,
            d2.ready_o, d2.quotient_o, d2.remainder_o, d2.start_i,
            d2.dividend_i, d2.divisor_i}


if __name__ == "__main__":
    example = Example(16)
    fname = path.join(tempfile.gettempdir(), "two_dividers.vhd")
    vhdl.convert(example, example.ios | {example.ce, example.reset}
                 ).write(fname)
    subprocess.check_call(["nvc", "--syntax", fname])
    subprocess.check_call(["nvc", "-a", fname])
