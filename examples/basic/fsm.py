import subprocess
from os import path
import tempfile
from migen import *  # noqa
from migen.fhdl import vhdl


class Example(Module):
    def __init__(self):
        self.s = Signal()
        self.counter = Signal(8)
        x = Array(Signal(name="a") for i in range(7))

        myfsm = FSM()
        self.submodules += myfsm

        myfsm.act("FOO",
                  self.s.eq(1),
                  NextState("BAR")
                  )
        myfsm.act("BAR",
                  self.s.eq(0),
                  NextValue(self.counter, self.counter + 1),
                  NextValue(x[self.counter], 1),
                  NextState("FOO")
                  )

        self.be = myfsm.before_entering("FOO")
        self.ae = myfsm.after_entering("FOO")
        self.bl = myfsm.before_leaving("FOO")
        self.al = myfsm.after_leaving("FOO")


if __name__ == "__main__":
    fname = path.join(tempfile.gettempdir(), "fsm.vhd")
    example = Example()
    vhdl.convert(
        example,
        {example.s, example.counter, example.be, example.ae, example.bl,
         example.al}
    ).write(fname)
    subprocess.check_call(["nvc", "--syntax", fname])
    subprocess.check_call(["nvc", "-a", fname])
