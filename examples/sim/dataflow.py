from migen.fhdl.std import Module, StopSimulation
from migen.flow.actor import Source, Sink
from migen.flow.transactions import Token
from migen.flow.network import DataFlowGraph, CompositeActor
from migen.actorlib.sim import SimActor
from migen.sim.generic import run_simulation


def source_gen():
    for i in range(10):
        print("Sending:  " + str(i))
        yield Token("source", {"value": i})


class SimSource(SimActor):
    def __init__(self):
        self.source = Source([("value", 32)])
        super().__init__(source_gen())


def sink_gen():
    while True:
        t = Token("sink")
        yield t
        print("Received: {}".format(t.value["value"]))


class SimSink(SimActor):
    def __init__(self):
        self.sink = Sink([("value", 32)])
        super().__init__(sink_gen())


class TB(Module):
    def __init__(self):
        self.source = SimSource()
        self.sink = SimSink()
        g = DataFlowGraph()
        g.add_connection(self.source, self.sink)
        self.submodules.comp = CompositeActor(g)

    def do_simulation(self, selfp):
        if self.source.token_exchanger.done:
            raise StopSimulation

if __name__ == "__main__":
    run_simulation(TB())
