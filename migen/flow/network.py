from collections import defaultdict

from migen.fhdl.std import *  # noqa
from migen.genlib.misc import optree
from migen.flow.actor import *  # noqa
from migen.flow import plumbing

# Abstract actors mean that the actor class should be instantiated with the parameters
# from the dictionary. They are needed to enable actor duplication or sharing during
# elaboration, and automatic parametrization of plumbing actors.


class AbstractActor:
    def __init__(self, actor_class, parameters=dict(), name=None):
        self.actor_class = actor_class
        self.parameters = parameters
        self.name = name
        self.busy = Signal()

    def create_instance(self):
        return self.actor_class(**self.parameters)

    def __repr__(self):
        r = "<abstract " + self.actor_class.__name__
        if self.name is not None:
            r += ": " + self.name
        r += ">"
        return r


class MultiDiGraph:
    def __init__(self):
        self.edges = defaultdict(list)
        self.incoming = defaultdict(set)
        self.outgoing = defaultdict(set)
        self.nodes = set()

    def add_edge(self, a, b, **edge):
        self.edges[(a, b)].append(edge)
        self.incoming[b].add(a)
        self.outgoing[a].add(b)
        self.nodes |= {a, b}

    def __iter__(self):
        return iter(self.nodes)

    def __len__(self):
        return len(self.nodes)

    def edges_iter(self, data=True):
        assert data
        for (a, b), edges in self.edges.items():
            for edge in edges:
                yield a, b, edge

    def get_edge_data(self, a, b):
        return dict(enumerate(self.edges[(a, b)]))

    def add_node(self, node):
        self.nodes.add(node)

    def remove_node(self, node):
        for i in self.incoming.pop(node):
            del self.edges[(i, node)]
            self.outgoing[i].remove(node)
        for i in self.outgoing.pop(node):
            del self.edges[(node, i)]
            self.incoming[i].remove(node)
        self.nodes.remove(node)

    def remove_edge(self, a, b, key):
        e = self.edges[(a, b)]
        del e[key]
        if not e:
            self.incoming[b].remove(a)
            self.outgoing[a].remove(b)

    def in_edges(self, sink, data=True):
        assert data
        e = []
        for source in self.incoming[sink]:
            for edge in self.edges[(source, sink)]:
                e.append((source, sink, edge))
        return e

    def out_edges(self, source, data=True):
        assert data
        e = []
        for sink in self.outgoing[source]:
            for edge in self.edges[(source, sink)]:
                e.append((source, sink, edge))
        return e


# TODO: rewrite this without non-determinism
class DataFlowGraph(MultiDiGraph):
    def __init__(self):
        super().__init__()
        self.elaborated = False
        self.abstract_busy_signals = dict()

    def add_connection(self, source_node, sink_node,
      source_ep=None, sink_ep=None,        # default: assume nodes have 1 source/sink and use that one
      source_subr=None, sink_subr=None):    # default: use whole record
        self.add_edge(source_node, sink_node,
            source=source_ep, sink=sink_ep,
            source_subr=source_subr, sink_subr=sink_subr)

    def add_buffered_connection(self, source_node, sink_node,
      source_ep=None, sink_ep=None,
      source_subr=None, sink_subr=None):
        buf = AbstractActor(plumbing.Buffer)
        self.add_connection(source_node, buf, source_ep=source_ep, source_subr=source_subr)
        self.add_connection(buf, sink_node, sink_ep=sink_ep, sink_subr=sink_subr)

    def add_pipeline(self, *nodes):
        for n1, n2 in zip(nodes, nodes[1:]):
            self.add_connection(n1, n2)

    def del_connections(self, source_node, sink_node, data_requirements):
        edges_to_delete = []
        edge_data = self.get_edge_data(source_node, sink_node)
        if edge_data is None:
            # the two nodes are already completely disconnected
            return
        for key, data in edge_data.items():
            if all(k not in data_requirements or data_requirements[k] == v
              for k, v in data.items()):
                edges_to_delete.append(key)
        for key in edges_to_delete:
            self.remove_edge(source_node, sink_node, key)

    def replace_actor(self, old, new):
        self.add_node(new)
        for xold, v, data in self.out_edges(old, data=True):
            self.add_edge(new, v, **data)
        for u, xold, data in self.in_edges(old, data=True):
            self.add_edge(u, new, **data)
        self.remove_node(old)

    def instantiate(self, actor):
        inst = actor.create_instance()
        self.abstract_busy_signals[id(inst)] = actor.busy
        self.replace_actor(actor, inst)

    # Returns a dictionary
    #   source -> [sink1, ..., sinkn]
    # source element is a (node, endpoint) pair.
    # sink elements are (node, endpoint, source subrecord, sink subrecord) triples.
    def _source_to_sinks(self):
        d = dict()
        for u, v, data in self.edges_iter(data=True):
            el_src = (u, data["source"])
            el_dst = (v, data["sink"], data["source_subr"], data["sink_subr"])
            if el_src in d:
                d[el_src].append(el_dst)
            else:
                d[el_src] = [el_dst]
        return d

    # Returns a dictionary
    #   sink -> [source1, ... sourcen]
    # sink element is a (node, endpoint) pair.
    # source elements are (node, endpoint, sink subrecord, source subrecord) triples.
    def _sink_to_sources(self):
        d = dict()
        for u, v, data in self.edges_iter(data=True):
            el_src = (u, data["source"], data["sink_subr"], data["source_subr"])
            el_dst = (v, data["sink"])
            if el_dst in d:
                d[el_dst].append(el_src)
            else:
                d[el_dst] = [el_src]
        return d

    # List sources that feed more than one sink.
    def _list_divergences(self):
        d = self._source_to_sinks()
        return dict((k, v) for k, v in d.items() if len(v) > 1)

    # A graph is abstract if any of these conditions is met:
    #  (1) A node is an abstract actor.
    #  (2) A subrecord is used.
    #  (3) A single source feeds more than one sink.
    # NB: It is not allowed for a single sink to be fed by more than one source
    # (except with subrecords, i.e. when a combinator is used)
    def is_abstract(self):
        return any(isinstance(x, AbstractActor) for x in self) \
            or any(d["source_subr"] is not None or d["sink_subr"] is not None
                for u, v, d in self.edges_iter(data=True)) \
            or bool(self._list_divergences())

    def _eliminate_subrecords_and_divergences(self):
        # Insert combinators.
        for (dst_node, dst_endpoint), sources in self._sink_to_sources().items():
            if len(sources) > 1 or sources[0][2] is not None:
                # build combinator
                # "layout" is filled in during instantiation
                subrecords = [dst_subrecord for src_node, src_endpoint, dst_subrecord, src_subrecord in sources]
                combinator = AbstractActor(plumbing.Combinator, {"subrecords": subrecords})
                # disconnect source1 -> sink ... sourcen -> sink
                # connect source1 -> combinator_sink1 ... sourcen -> combinator_sinkn
                for n, (src_node, src_endpoint, dst_subrecord, src_subrecord) in enumerate(sources):
                    self.del_connections(src_node, dst_node,
                        {"source": src_endpoint, "sink": dst_endpoint})
                    self.add_connection(src_node, combinator,
                        src_endpoint, "sink{0}".format(n), source_subr=src_subrecord)
                # connect combinator_source -> sink
                self.add_connection(combinator, dst_node, "source", dst_endpoint)
        # Insert splitters.
        for (src_node, src_endpoint), sinks in self._source_to_sinks().items():
            if len(sinks) > 1 or sinks[0][2] is not None:
                subrecords = [src_subrecord for dst_node, dst_endpoint, src_subrecord, dst_subrecord in sinks]
                splitter = AbstractActor(plumbing.Splitter, {"subrecords": subrecords})
                # disconnect source -> sink1 ... source -> sinkn
                # connect splitter_source1 -> sink1 ... splitter_sourcen -> sinkn
                for n, (dst_node, dst_endpoint, src_subrecord, dst_subrecord) in enumerate(sinks):
                    self.del_connections(src_node, dst_node,
                        {"source": src_endpoint, "sink": dst_endpoint})
                    self.add_connection(splitter, dst_node,
                        "source{0}".format(n), dst_endpoint)
                # connect source -> splitter_sink
                self.add_connection(src_node, splitter, src_endpoint, "sink")

    def _infer_plumbing_layout(self):
        while True:
            ap = [a for a in self if isinstance(a, AbstractActor) and a.actor_class in plumbing.actors]
            if not ap:
                break
            for a in ap:
                in_edges = self.in_edges(a, data=True)
                out_edges = self.out_edges(a, data=True)
                if a.actor_class in plumbing.layout_sink and len(in_edges) == 1:
                    other, me, data = in_edges[0]
                    if isinstance(other, AbstractActor):
                        continue
                    other_ep = data["source"]
                    if other_ep is None:
                        other_ep = get_single_ep(other, Source)[1]
                    else:
                        other_ep = getattr(other, other_ep)
                elif a.actor_class in plumbing.layout_source and len(out_edges) == 1:
                    me, other, data = out_edges[0]
                    if isinstance(other, AbstractActor):
                        continue
                    other_ep = data["sink"]
                    if other_ep is None:
                        other_ep = get_single_ep(other, Sink)[1]
                    else:
                        other_ep = getattr(other, other_ep)
                else:
                    raise AssertionError
                layout = other_ep.payload.layout
                a.parameters["layout"] = layout
                self.instantiate(a)

    def _instantiate_actors(self):
        # 1. instantiate all abstract non-plumbing actors
        for actor in list(self):
            if isinstance(actor, AbstractActor) and actor.actor_class not in plumbing.actors:
                self.instantiate(actor)
        # 2. infer plumbing layout and instantiate plumbing
        self._infer_plumbing_layout()
        # 3. resolve default eps
        for u, v, d in self.edges_iter(data=True):
            if d["source"] is None:
                d["source"] = get_single_ep(u, Source)[0]
            if d["sink"] is None:
                d["sink"] = get_single_ep(v, Sink)[0]

    # Elaboration turns an abstract DFG into a physical one.
    #   Pass 1: eliminate subrecords and divergences
    #           by inserting Combinator/Splitter actors
    #   Pass 2: run optimizer (e.g. share and duplicate actors)
    #   Pass 3: instantiate all abstract actors and explicit "None" endpoints
    def elaborate(self, optimizer=None):
        if self.elaborated:
            return
        self.elaborated = True

        self._eliminate_subrecords_and_divergences()
        if optimizer is not None:
            optimizer(self)
        self._instantiate_actors()


class CompositeActor(Module):
    def __init__(self, dfg):
        dfg.elaborate()

        # expose unconnected endpoints
        uc_eps_by_node = dict((node, get_endpoints(node)) for node in dfg)
        for u, v, d in dfg.edges_iter(data=True):
            uc_eps_u = uc_eps_by_node[u]
            source = d["source"]
            try:
                del uc_eps_u[source]
            except KeyError:
                pass
            uc_eps_v = uc_eps_by_node[v]
            sink = d["sink"]
            try:
                del uc_eps_v[sink]
            except KeyError:
                pass
        for node, uc_eps in uc_eps_by_node.items():
            for k, v in uc_eps.items():
                assert(not hasattr(self, k))
                setattr(self, k, v)

        # connect abstract busy signals
        for node in dfg:
            try:
                abstract_busy_signal = dfg.abstract_busy_signals[id(node)]
            except KeyError:
                pass
            else:
                self.comb += abstract_busy_signal.eq(node.busy)

        # generate busy signal
        self.busy = Signal()
        self.comb += self.busy.eq(optree("|", [node.busy for node in dfg]))

        # claim ownership of sub-actors and establish connections
        for node in dfg:
            self.submodules += node
        for u, v, d in dfg.edges_iter(data=True):
            ep_src = getattr(u, d["source"])
            ep_dst = getattr(v, d["sink"])
            self.comb += ep_src.connect_flat(ep_dst)
