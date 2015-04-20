from migen.fhdl.std import (Instance, Module, Signal)
from migen.genlib.resetsync import AsyncResetSynchronizer
from migen.genlib.io import (DifferentialInput, DifferentialOutput)


class QuartusAsyncResetSynchronizerImpl(Module):
    def __init__(self, cd, async_reset):
        rst_1 = Signal()
        self.specials += [
            Instance("DFFEA",
                     d=0,
                     clk=cd.clk,
                     clrn=1,
                     prn=1,
                     ena=1,
                     adata=1,
                     aload=async_reset,
                     q=rst_1),
            Instance("DFFEA",
                     d=rst_1,
                     clk=cd.clk,
                     clrn=1,
                     prn=1,
                     ena=1,
                     adata=1,
                     aload=async_reset,
                     q=cd.rst)]


class QuartusAsyncResetSynchronizer:
    @staticmethod
    def lower(dr):
        return QuartusAsyncResetSynchronizerImpl(dr.cd, dr.async_reset)


class QuartusDifferentialInputImpl(Module):
    def __init__(self, i_p, i_n, o):
        self.specials += Instance("ALT_INBUF_DIFF",
                                  name="ibuf_diff",
                                  i_i=i_p,
                                  i_ibar=i_n,
                                  o_o=o)


class QuartusDifferentialInput:
    @staticmethod
    def lower(dr):
        return QuartusDifferentialInputImpl(dr.i_p, dr.i_n, dr.o)


class QuartusDifferentialOutputImpl(Module):
    def __init__(self, i, o_p, o_n):
        self.specials += Instance("ALT_OUTBUF_DIFF",
                                  name="obuf_diff",
                                  i_i=i,
                                  o_o=o_p,
                                  o_obar=o_n)


class QuartusDifferentialOutput:
    @staticmethod
    def lower(dr):
        return QuartusDifferentialOutputImpl(dr.i, dr.o_p, dr.o_n)


altera_special_overrides = {
    AsyncResetSynchronizer: QuartusAsyncResetSynchronizer,
    DifferentialInput: QuartusDifferentialInput,
    DifferentialOutput: QuartusDifferentialOutput
}
