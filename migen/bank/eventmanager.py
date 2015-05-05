from migen.util.misc import xdir
from migen.fhdl.std import HUID, Module, Signal, If, FinalizeError
from migen.bank.description import AutoCSR, CSR, CSRStorage
from migen.genlib.misc import optree


class _EventSource(HUID):
    def __init__(self):
        super().__init__()
        # value in the status register
        self.status = Signal()
        # value in the pending register + assert irq if unmasked
        self.pending = Signal()
        # trigger signal interface to the user design
        self.trigger = Signal()
        # clearing attempt by W1C to pending register,
        # ignored by some event sources
        self.clear = Signal()


# set on a positive trigger pulse
class EventSourcePulse(Module, _EventSource):
    def __init__(self):
        super().__init__()
        self.comb += self.status.eq(0)
        self.sync += [
            If(self.clear, self.pending.eq(0)),
            If(self.trigger, self.pending.eq(1))
        ]


# set on the falling edge of the trigger, status = trigger
class EventSourceProcess(Module, _EventSource):
    def __init__(self):
        super().__init__()
        self.comb += self.status.eq(self.trigger)
        old_trigger = Signal()
        self.sync += [
            If(self.clear, self.pending.eq(0)),
            old_trigger.eq(self.trigger),
            If(~self.trigger & old_trigger, self.pending.eq(1))
        ]


# all status set by external trigger
class EventSourceLevel(Module, _EventSource):
    def __init__(self):
        super().__init__()
        self.comb += [
            self.status.eq(self.trigger),
            self.pending.eq(self.trigger)
        ]


class EventManager(Module, AutoCSR):
    def __init__(self):
        self.irq = Signal()

    def do_finalize(self):
        sources_u = [v for k, v in xdir(self, True)
                     if isinstance(v, _EventSource)]
        sources = sorted(sources_u, key=lambda x: x.huid)
        n = len(sources)
        self.status = CSR(n)
        self.pending = CSR(n)
        self.enable = CSRStorage(n)

        for i, source in enumerate(sources):
            self.comb += [
                self.status.w[i].eq(source.status),
                If(self.pending.re & self.pending.r[i], source.clear.eq(1)),
                self.pending.w[i].eq(source.pending)
            ]

        irqs = [self.pending.w[i] & self.enable.storage[i] for i in range(n)]
        self.comb += self.irq.eq(optree("|", irqs))

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        if isinstance(value, _EventSource):
            if self.finalized:
                raise FinalizeError
            self.submodules += value


class SharedIRQ(Module):
    def __init__(self, *event_managers):
        self.irq = Signal()
        self.comb += self.irq.eq(optree("|",
                                        [ev.irq for ev in event_managers]))
