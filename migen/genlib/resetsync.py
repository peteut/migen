from migen.fhdl.structure import *  # noqa
from migen.fhdl.specials import Special


class AsyncResetSynchronizer(Special):
    def __init__(self, cd, async_reset):
        super().__init__()
        self.cd = cd
        self.async_reset = wrap(async_reset)

    def iter_expressions(self):
        yield self.cd, "clk", SPECIAL_INPUT
        yield self.cd, "rst", SPECIAL_OUTPUT
        yield self, "async_reset", SPECIAL_INPUT

    @staticmethod
    def lower(dr):
        raise NotImplementedError("Attempted to use a reset synchronizer, but platform does not support them")
