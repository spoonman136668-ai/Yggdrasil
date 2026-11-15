#!/usr/bin/env python3
"""F50 equal-information, lossless source-law/episode interface.

Native, conventional, and Bayesian research controls must obtain FIT source
graphs and observed FIT episodes through this identical interface. Never returns
VALIDATION law examples, target-program ASTs, or evaluator-only observations.
"""
from dataclasses import dataclass
from hashlib import sha256
import json
import f50_worlds as world

SCHEMA = "yggdrasil.qtr01.f50.public-source-parity.v1"
OPCODES = ("leaf", "not", "and", "or", "xor")
MAX_NODES = 15  # Full binary tree at source depth <=3.


class PublicSourceRejected(world.F50Rejected):
    pass


@dataclass(frozen=True)
class LawGraph:
    """Lossless rooted postorder graph, with explicit left/right child edges."""
    nodes: tuple
    root: int

    def serialize(self):
        return {"nodes": [list(x) for x in self.nodes], "root": self.root}


def encode_source_graph(ast):
    world.freeze()
    if world.ast_depth(ast) > 3:
        raise PublicSourceRejected("F50_SOURCE_GRAPH_EXCEEDS_FROZEN_DEPTH")
    nodes = []
    memo = {}
    def visit(node):
        if node in memo:
            return memo[node]
        code = OPCODES.index(node[0])
        if code == 0:
            record = (code, node[1], -1, -1)
        elif code == 1:
            record = (code, -1, visit(node[1]), -1)
        else:
            left, right = visit(node[1]), visit(node[2])
            record = (code, -1, left, right)
        index = len(nodes)
        nodes.append(record)
        memo[node] = index
        return index
    root = visit(ast)
    if len(nodes) > MAX_NODES:
        raise PublicSourceRejected("F50_SOURCE_GRAPH_TOO_MANY_NODES")
    return LawGraph(tuple(nodes), root)


def decode_source_graph(graph):
    if type(graph) is not LawGraph or type(graph.root) is not int or not graph.nodes or len(graph.nodes) > MAX_NODES:
        raise PublicSourceRejected("F50_SOURCE_GRAPH_REJECTED")
    asts = []
    for index, node in enumerate(graph.nodes):
        if type(node) is not tuple or len(node) != 4 or any(type(x) is not int for x in node):
            raise PublicSourceRejected("F50_GRAPH_NODE_BAD_TYPE")
        op, variable, left, right = node
        if not 0 <= op < len(OPCODES):
            raise PublicSourceRejected("F50_GRAPH_UNREGISTERED_OPERATOR")
        if op == 0:
            if left != -1 or right != -1:
                raise PublicSourceRejected("F50_GRAPH_BAD_LEAF_EDGES")
            ast = world.leaf(variable)
        elif op == 1:
            if variable != -1 or not 0 <= left < index or right != -1:
                raise PublicSourceRejected("F50_GRAPH_UNARY_CYCLE_OR_EDGE")
            ast = ("not", asts[left])
        else:
            if variable != -1 or not 0 <= left < index or not 0 <= right < index:
                raise PublicSourceRejected("F50_GRAPH_BINARY_CYCLE_OR_EDGE")
            ast = (OPCODES[op], asts[left], asts[right])
        asts.append(ast)
    if graph.root != len(asts)-1:
        raise PublicSourceRejected("F50_GRAPH_ROOT_NOT_TERMINAL")
    if world.ast_depth(asts[graph.root]) > 3:
        raise PublicSourceRejected("F50_GRAPH_DEPTH_DRIFT")
    if encode_source_graph(asts[graph.root]) != graph:
        raise PublicSourceRejected("F50_GRAPH_NONCANONICAL")
    return asts[graph.root]


def graph_one_hot(graph):
    """Graph neural input: node types, variable IDs, directed two-slot edges.

    This is an injective encoding of the canonical graph, not a lossy summary.
    Each node occupies 38 features (5 operators + 33 leaves), plus a 15x15
    left adjacency and a separate 15x15 right adjacency matrix.
    """
    decode_source_graph(graph)
    features = [[0]*38 for _ in range(MAX_NODES)]
    left = [[0]*MAX_NODES for _ in range(MAX_NODES)]
    right = [[0]*MAX_NODES for _ in range(MAX_NODES)]
    mask = [0]*MAX_NODES
    for i, (op, leaf_id, li, ri) in enumerate(graph.nodes):
        mask[i] = 1
        features[i][op] = 1
        if op == 0:
            features[i][5+leaf_id] = 1
        if li >= 0:
            left[i][li] = 1
        if ri >= 0:
            right[i][ri] = 1
    return tuple(tuple(z) for z in features), tuple(tuple(z) for z in left), tuple(tuple(z) for z in right), tuple(mask)


def action_features(episode):
    """3×33 bit features; exact current/lag1/lag2/context observables."""
    a,b,c,context = world.validate_trajectory(episode)
    return tuple(tuple(int((action >> bit)&1) for bit in range(10)) +
                 tuple(int((previous >> bit)&1) for bit in range(10)) +
                 tuple(int((lag2 >> bit)&1) for bit in range(10)) +
                 tuple(int((context >> bit)&1) for bit in range(3))
                 for action,previous,lag2 in ((a,0,0),(b,a,0),(c,b,a)))


def observed_episode(episode, bits):
    tr = world.validate_trajectory(episode)
    if type(bits) not in (tuple,list) or len(bits)!=3 or any(type(x) is not int or x not in (0,1) for x in bits):
        raise PublicSourceRejected("F50_PUBLIC_EPISODE_BITS_REJECTED")
    return tr,tuple(bits)


class PublicFIT:
    """Read-only logical interface; strictly FIT source law partition."""

    def __init__(self, size):
        world.freeze()
        world._check_bank_size(size)
        self.size = size
        fit,valid = world.source_split(size)
        if (fit & valid or len(fit)+len(valid)!=size or
            len(fit)!=size*4//5):
            raise PublicSourceRejected("F50_SOURCE_SPLIT_CONTAMINATED")
        self.ids = tuple(sorted(fit))
        self._fit = fit
        self._validation = valid

    def source_graph(self, law_id):
        if type(law_id) is not int or law_id not in self._fit:
            raise PublicSourceRejected("F50_NONFIT_SOURCE_GRAPH_ACCESS")
        return encode_source_graph(world.source_bank(self.size)[law_id])

    def source_episodes(self, law_id):
        if type(law_id) is not int or law_id not in self._fit:
            raise PublicSourceRejected("F50_NONFIT_SOURCE_LABEL_ACCESS")
        rows = world.source_training_row(self.size,law_id)
        if len(rows)!=world.TRAIN_EPISODES:
            raise PublicSourceRejected("F50_SOURCE_ROW_COUNT_DRIFT")
        return tuple(observed_episode(*pair) for pair in rows)

    def iter_fit_graphs(self):
        for law_id in self.ids:
            yield law_id,self.source_graph(law_id)

    def iter_fit_episodes(self):
        for law_id in self.ids:
            yield law_id,self.source_graph(law_id),self.source_episodes(law_id)

    def snapshot(self, law_id):
        """Identical FIT source graph, actions and noisy bits for all arms."""
        graph = self.source_graph(law_id)
        return {"law_id":law_id,"graph":graph.serialize(),
                "episodes":[[list(a),list(y)] for a,y in self.source_episodes(law_id)]}

    def digest_for_fit_graphs(self):
        stream = sha256(("F50/FIT-graph/v1|"+world.PREREG_BLOB+
                         "|"+str(self.size)+"|").encode("ascii"))
        for law_id,graph in self.iter_fit_graphs():
            stream.update(str(law_id).encode("ascii")+b":")
            stream.update(json.dumps(graph.serialize(),separators=(",",":"),sort_keys=True).encode("ascii"))
            stream.update(b"\n")
        return stream.hexdigest()

    @property
    def fit_count(self):
        return len(self.ids)

    @property
    def excluded_validation_count(self):
        return len(self._validation)


def assert_equal_source_access(*arms):
    """Take each arm's shared PublicFIT object and require exact identity."""
    if not arms or any(type(x) is not PublicFIT for x in arms):
        raise PublicSourceRejected("F50_PARITY_REQUIRES_IDENTICAL_PUBLICFIT")
    first = (arms[0].size,arms[0].ids,arms[0].digest_for_fit_graphs())
    if any((x.size,x.ids,x.digest_for_fit_graphs())!=first for x in arms[1:]):
        raise PublicSourceRejected("F50_SOURCE_INFO_PARITY_VIOLATED")
    return first[2]


if __name__ == "__main__":
    world.freeze()
    print("F50_PUBLIC_FIT_GRAPH_AND_EPISODE_INTERFACE_READY_NO_TARGET_FIRST_USE")
