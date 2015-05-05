# Simple Processor Interface

from migen.fhdl.std import Module, Signal, If, Memory, bits_for, flen
from migen.bank.description import CSR, AutoCSR, CSRStorage, CSRStatus
from migen.flow.network import (AbstractActor, CompositeActor, DataFlowGraph,
                                Source, Sink)
from migen.flow import plumbing
from migen.actorlib import misc


# layout is a list of tuples, either:
# - (name, nbits, [reset value], [alignment bits])
# - (name, sublayout)

def _convert_layout(layout):
    r = []
    for element in layout:
        if isinstance(element[1], list):
            r.append((element[0], _convert_layout(element[1])))
        else:
            r.append((element[0], element[1]))
    return r

(MODE_EXTERNAL, MODE_SINGLE_SHOT, MODE_CONTINUOUS) = range(3)


class SingleGenerator(Module, AutoCSR):
    def __init__(self, layout, mode):
        self.source = Source(_convert_layout(layout))
        self.busy = Signal()

        self.comb += self.busy.eq(self.source.stb)

        if mode == MODE_EXTERNAL:
            self.trigger = Signal()
            trigger = self.trigger
        elif mode == MODE_SINGLE_SHOT:
            self._shoot = CSR()
            trigger = self._shoot.re
        elif mode == MODE_CONTINUOUS:
            self._enable = CSRStorage()
            trigger = self._enable.storage
        else:
            raise ValueError
        self.sync += If(self.source.ack | ~self.source.stb,
                        self.source.stb.eq(trigger))

        self._create_csrs(layout, self.source.payload,
                          mode != MODE_SINGLE_SHOT)

    def _create_csrs(self, layout, target, atomic, prefix=""):
        for element in layout:
            if isinstance(element[1], list):
                self._create_csrs(element[1], atomic,
                                  getattr(target, element[0]),
                                  element[0] + "_")
            else:
                name = element[0]
                nbits = element[1]
                if len(element) > 2:
                    reset = element[2]
                else:
                    reset = 0

                if len(element) > 3:
                    alignment = element[3]
                else:
                    alignment = 0

                regname = prefix + name
                reg = CSRStorage(nbits + alignment, reset=reset,
                                 atomic_write=atomic,
                                 alignment_bits=alignment, name=regname)
                setattr(self, "r_" + regname, reg)
                self.sync += If(self.source.ack | ~self.source.stb,
                                getattr(target, name).eq(reg.storage))


class Collector(Module, AutoCSR):
    def __init__(self, layout, depth=1024):
        self.sink = Sink(layout)
        self.busy = Signal()
        dw = sum(len(s) for s in self.sink.payload.flatten())

        self._wa = CSRStorage(bits_for(depth - 1), write_from_dev=True)
        self._wc = CSRStorage(bits_for(depth), write_from_dev=True,
                              atomic_write=True)
        self._ra = CSRStorage(bits_for(depth - 1))
        self._rd = CSRStatus(dw)

        ###

        mem = Memory(dw, depth)
        self.specials += mem
        wp = mem.get_port(write_capable=True)
        rp = mem.get_port()
        self.specials += wp, rp

        self.comb += [
            self.busy.eq(0),

            If(self._wc.r != 0,
                self.sink.ack.eq(1),
                If(self.sink.stb,
                    self._wa.we.eq(1),
                    self._wc.we.eq(1),
                    wp.we.eq(1)
                   )
               ),
            self._wa.dat_w.eq(self._wa.storage + 1),
            self._wc.dat_w.eq(self._wc.storage - 1),

            wp.adr.eq(self._wa.storage),
            wp.dat_w.eq(self.sink.payload.raw_bits()),

            rp.adr.eq(self._ra.storage),
            self._rd.status.eq(rp.dat_r)
        ]


class _DMAController(Module):
    def __init__(self, bus_accessor, bus_aw, bus_dw, mode, base_reset=0,
                 length_reset=0):
        self.alignment_bits = bits_for(bus_dw // 8) - 1
        layout = [
            ("length", bus_aw + self.alignment_bits, length_reset,
             self.alignment_bits),
            ("base", bus_aw + self.alignment_bits, base_reset,
             self.alignment_bits)
        ]
        self.generator = SingleGenerator(layout, mode)
        self.r_busy = CSRStatus()

        self.length = self.generator.r_length.storage
        self.base = self.generator.r_base.storage
        if hasattr(self.generator, "trigger"):
            self.trigger = self.generator.trigger

    def get_csrs(self):
        return self.generator.get_csrs() + [self.r_busy]


class DMAReadController(_DMAController):
    def __init__(self, bus_accessor, *args, **kwargs):
        bus_aw = flen(bus_accessor.address.a)
        bus_dw = flen(bus_accessor.data.d)
        super().__init__(bus_accessor, bus_aw, bus_dw, *args, **kwargs)

        g = DataFlowGraph()
        g.add_pipeline(self.generator,
                       misc.IntSequence(bus_aw, bus_aw),
                       AbstractActor(plumbing.Buffer),
                       bus_accessor,
                       AbstractActor(plumbing.Buffer))
        comp_actor = CompositeActor(g)
        self.submodules += comp_actor

        self.data = comp_actor.q
        self.busy = comp_actor.busy
        self.comb += self.r_busy.status.eq(self.busy)


class DMAWriteController(_DMAController):
    def __init__(self, bus_accessor, *args, ack_when_inactive=False, **kwargs):
        bus_aw = flen(bus_accessor.address_data.a)
        bus_dw = flen(bus_accessor.address_data.d)
        super().__init__(bus_accessor, bus_aw, bus_dw, *args, **kwargs)

        g = DataFlowGraph()
        adr_buffer = AbstractActor(plumbing.Buffer)
        int_sequence = misc.IntSequence(bus_aw, bus_aw)
        g.add_pipeline(self.generator,
                       int_sequence,
                       adr_buffer)
        g.add_connection(adr_buffer, bus_accessor, sink_subr=["a"])
        g.add_connection(AbstractActor(plumbing.Buffer), bus_accessor,
                         sink_subr=["d"])
        comp_actor = CompositeActor(g)
        self.submodules += comp_actor

        if ack_when_inactive:
            demultiplexer = plumbing.Demultiplexer([("d", bus_dw)], 2)
            self.comb += [
                demultiplexer.sel.eq(~adr_buffer.busy),
                demultiplexer.source0.connect(comp_actor.d),
                demultiplexer.source1.ack.eq(1),
            ]
            self.submodules += demultiplexer
            self.data = demultiplexer.sink
        else:
            self.data = comp_actor.d

        self.busy = comp_actor.busy
        self.comb += self.r_busy.status.eq(self.busy)
