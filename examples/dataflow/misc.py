from migen.flow.network import DataFlowGraph, CompositeActor
from migen.flow.transactions import Token
from migen.flow.actor import Source, Sink
from migen.actorlib import misc
from migen.actorlib.sim import SimActor
from migen.sim.generic import run_simulation


def source_gen():
    for i in range(10):
        v = i + 5
        print("==> " + str(v))
        yield Token("source", {"maximum": v})


class SimSource(SimActor):
    def __init__(self):
        self.source = Source([("maximum", 32)])
        super().__init__(source_gen())


def sink_gen():
    while True:
        t = Token("sink")
        yield t
        print(t.value["value"])


class SimSink(SimActor):
    def __init__(self):
        self.sink = Sink([("value", 32)])
        super().__init__(sink_gen())

if __name__ == "__main__":
    source = SimSource()
    loop = misc.IntSequence(32)
    sink = SimSink()
    g = DataFlowGraph()
    g.add_connection(source, loop)
    g.add_connection(loop, sink)
    comp = CompositeActor(g)
    run_simulation(comp, ncycles=500)
