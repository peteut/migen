from collections import defaultdict

from migen.fhdl.std import *  # noqa
from migen.flow.actor import *  # noqa


class EndpointSimHook(Module):
    def __init__(self, endpoint):
        self.endpoint = endpoint

    def on_ack(self):
        pass

    def on_nack(self):
        pass

    def on_inactive(self):
        pass

    def do_simulation(self, selfp):
        if selfp.endpoint.stb:
            if selfp.endpoint.ack:
                self.on_ack()
            else:
                self.on_nack()
        else:
            self.on_inactive()


class DFGHook(Module):
    def __init__(self, dfg, create):
        assert(not dfg.is_abstract())
        self.nodepair_to_ep = defaultdict(dict)
        for hookn, (u, v, data) in enumerate(dfg.edges_iter(data=True)):
            ep_to_hook = self.nodepair_to_ep[(u, v)]
            ep = data["source"]
            h = create(u, ep, v)
            ep_to_hook[ep] = h
            setattr(self.submodules, "hook{}".format(hookn), h)

    def hooks_iter(self):
        for v1 in self.nodepair_to_ep.values():
            for v2 in v1.values():
                yield v2
