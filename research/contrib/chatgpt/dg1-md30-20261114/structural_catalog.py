"""MD30 deterministic structural catalog: synthetic PHYSICS preflight only.

No official cohort first use. The generator is for task construction only:
never pass private structural objects, seeds, or topology labels to a policy.
"""
from functools import lru_cache
import hashlib
import itertools

from structural_rewire import Graph, Node, World, canonical, digest

TOPOLOGIES = {
    "chain": (
        ((0,), (2, 1), (3, 0), (4,)),
        ((1,), (2, 0), (3, 1), (4,))),
    "fork": (
        ((0,), (0, 1), (2, 3), (4,)),
        ((1,), (0, 1), (2, 3), (4,))),
    "collider": (
        ((0, 1), (0,), (2, 3), (4,)),
        ((0, 1), (1,), (2, 3), (4,))),
    "braided": (
        ((0, 1), (0, 2), (1, 3), (2, 4)),
        ((0, 1), (1, 2), (0, 3), (2, 4))),
    "crossfork": (
        ((0,), (2, 1), (0, 3), (2, 4)),
        ((1,), (2, 0), (1, 3), (2, 4))),
    "doublecollider": (
        ((0, 1), (0, 2), (1, 2), (3, 4)),
        ((0, 1), (1, 2), (0, 2), (3, 4))),
}
TRAIN_MOTIFS = ("chain", "fork", "collider")
TRANSFER_MOTIFS = ("braided", "crossfork", "doublecollider")
DIAGNOSTIC_NODES = (2, 3, 4)  # no root-actuator action previews
SYNTHETIC_SEEDS = tuple(range(1201, 1249))


def _rank(seed: int, label: str, count: int) -> int:
    value = hashlib.sha256(("StructuralRewire-v1|catalog-v1|" + str(seed) +
                            "|" + label).encode("utf-8")).digest()
    return int.from_bytes(value[:8], "big") % count


@lru_cache(maxsize=None)
def _eligible(motif: str, variant: int, winner: int):
    """Frozen exhaustive gate/inhibition combinations for a DAG template."""
    parents = TOPOLOGIES[motif][variant]
    choices = [
        tuple(Node(p, gate, inv)
              for gate in (("PASS",) if len(p) == 1 else ("AND", "OR", "XOR"))
              for inv in itertools.product((0, 1), repeat=len(p)))
        for p in parents
    ]
    matches = []
    for nodes in itertools.product(*choices):
        graph = Graph(tuple(nodes))
        if graph.respond((0, 0)) != (0,) * 6:
            continue
        effects = (graph.respond((1, 0))[5], graph.respond((0, 1))[5])
        if effects == ((1, 0) if winner == 0 else (0, 1)):
            matches.append(graph)
    if not matches:
        raise AssertionError("MD30_EMPTY_STRUCTURAL_CLASS_" + motif)
    return tuple(matches)


def _distinguishing_probes(a: Graph, b: Graph):
    return tuple((node, val) for node in DIAGNOSTIC_NODES
                 for val in (0, 1)
                 if a.respond((0, 0), (node, val)) !=
                    b.respond((0, 0), (node, val)))


def synthetic_pair(seed: int, motif: str):
    """Task constructor only; official first-use seed ranges all rejected."""
    if type(seed) is not int or seed < 0 or seed >= 1000000:
        raise AssertionError("MD30_OFFICIAL_COHORT_FIRST_USE_FORBIDDEN")
    if motif not in TOPOLOGIES:
        raise ValueError("MD30_UNKNOWN_MOTIF")
    first_winner = _rank(seed, motif + "|winner", 2)
    left = _eligible(motif, 0, first_winner)
    right = _eligible(motif, 1, 1 - first_winner)
    start_a = _rank(seed, motif + "|first_graph", len(left))
    start_b = _rank(seed, motif + "|second_graph", len(right))
    for i in range(len(left)):
        first = left[(start_a + i) % len(left)]
        for j in range(len(right)):
            second = right[(start_b + j) % len(right)]
            if (any(x.gate != y.gate for x, y in zip(first.nodes, second.nodes))
                    and _distinguishing_probes(first, second)):
                return first, second
    raise AssertionError("MD30_NO_STRUCTURALLY_IDENTIFIABLE_PAIR_" + motif)


def synthetic_world(seed: int, motif: str, *, rewire: bool):
    """Public task with only internal paid diagnostics, not actuator previews."""
    before, after = synthetic_pair(seed, motif)
    return World(before, next_graph=after if rewire else None, roots=(0, 0),
                 target=5, desired=1, diagnostic_nodes=DIAGNOSTIC_NODES)


def topology_manifest():
    signatures = {motif: digest({"name": motif, "parents": TOPOLOGIES[motif]})
                  for motif in sorted(TOPOLOGIES)}
    train = {signatures[x] for x in TRAIN_MOTIFS}
    transfer = {signatures[x] for x in TRANSFER_MOTIFS}
    if len(train) != 3 or len(transfer) != 3 or not train.isdisjoint(transfer):
        raise AssertionError("MD30_TOPOLOGY_SPLIT_COLLISION")
    a = {canonical(x) for motif in TRAIN_MOTIFS for x in TOPOLOGIES[motif]}
    b = {canonical(x) for motif in TRANSFER_MOTIFS for x in TOPOLOGIES[motif]}
    if len(a) != 6 or len(b) != 6 or not a.isdisjoint(b):
        raise AssertionError("MD30_GRAPH_TOPOLOGY_LEAK")
    return {"train": list(TRAIN_MOTIFS), "transfer": list(TRANSFER_MOTIFS),
            "topology_sha256": signatures,
            "all_structure_sha256": digest(signatures)}


def preflight_distribution():
    """Analytic preflight on synthetic seeds, never a learner evaluation."""
    summary = {}
    for motif in TRAIN_MOTIFS + TRANSFER_MOTIFS:
        pairs = [synthetic_pair(seed, motif) for seed in SYNTHETIC_SEEDS]
        outcomes = []
        unique = set()
        gate_coverage = set()
        win_counts = [0, 0]
        first_probes = set()
        for first, second in pairs:
            for graph in (first, second):
                unique.add(graph.fingerprint())
                gate_coverage.update(n.gate for n in graph.nodes)
            diff = _distinguishing_probes(first, second)
            if not diff:
                raise AssertionError("MD30_UNIDENTIFIABLE_INTERNAL_CLAIMS")
            first_probes.add(diff[0])
            if first.respond((0, 0)) != second.respond((0, 0)):
                raise AssertionError("MD30_INITIAL_PUBLIC_LEAKAGE")
            p = (first.respond((1, 0))[5], first.respond((0, 1))[5])
            q = (second.respond((1, 0))[5], second.respond((0, 1))[5])
            if sorted((p, q)) != [(0, 1), (1, 0)]:
                raise AssertionError("MD30_OPPOSITE_ACTIONS_INVALID")
            win_counts[p.index(1)] += 1
            outcomes.append(p)
        # A deliberately privileged blind comparator is allowed to know its
        # motif, but cannot inspect the hidden DAG or buy a diagnostic.
        blind = max(sum(row[i] for row in outcomes) for i in (0, 1)) / len(outcomes)
        headroom = (1 - blind) * 1.5
        summary[motif] = {
            "synthetic_pairs": len(pairs),
            "distinct_hidden_graphs": len(unique),
            "gate_types": sorted(gate_coverage),
            "distinct_first_internal_probes": len(first_probes),
            "blind_success_fraction": round(blind, 6),
            "oracle_blind_utility_headroom": round(headroom, 6),
            "actuator_a_wins": win_counts[0],
            "actuator_b_wins": win_counts[1],
        }
        if headroom < 0.35 or len(unique) < 8 or len(first_probes) < 2:
            raise AssertionError("MD30_PREFLIGHT_TASK_NO_GO_" + motif)
    return {
        "schema": "yggdrasil.dg1-md30-structural-distribution-preflight.v1",
        "status": "SYNTHETIC_PHYSICS_PREFLIGHT_ONLY_NO_SCIENTIFIC_EVALUATION",
        "seed_range": [SYNTHETIC_SEEDS[0], SYNTHETIC_SEEDS[-1]],
        "registered_first_use": False,
        "topology_manifest": topology_manifest(),
        "motifs": summary,
    }
