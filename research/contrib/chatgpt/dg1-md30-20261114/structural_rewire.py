"""DG1-MD30 StructuralRewire-v1 physical task and preflight fixtures only.

Research-only, deterministic stdlib implementation. No trained policies, official
cohort access, scientific scoring, oracle interface to policy, or first-use path.
Every public consequence requires a charged world.step pulse. Diagnostics are
physical pulse-and-release clamps; irreversible actuations alone earn target
rewards. Each pulse starts from the same stage ambient roots. Stage transitions
may change causal structure without announcing the change.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import itertools
import json

NAME = "StructuralRewire-v1"
SENSORS = ("A", "B", "C", "D", "E", "F")
PROBE_COST = 0.05
ACTUATE_COST = 0.02
WIN = 1.0
LOSE = -0.5
STAGES = 2
MAX_DIAGNOSTICS = 3
MAX_STEPS = 8
# Explicitly locked preregistration ranges. No official cohort can be
# constructed through the fixture-only API, including by calling it "fixture".
FORBIDDEN = ((1080001, 1080768), (2080001, 2080128),
             (3080001, 3080064), (4080001, 4080256),
             (1070001, 1070096))
GATES = ("AND", "OR", "XOR")
FAMILIES = {
    "chain": ((0,), (2, 1), (3,), (4,)),
    "fork": ((0,), (0, 1), (2, 3), (4,)),
    "collider": ((0, 1), (0,), (2, 3), (4,)),
    "composed": ((0, 1), (2, 1), (3, 0), (4, 2)),
}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def sample_bit(seed: int, label: str) -> int:
    if type(seed) is not int or seed < 0 or not label:
        raise ValueError("MD30_INVALID_SEED_OR_LABEL")
    raw = f"{NAME}|preflight-v1|{seed}|{label}".encode("utf-8")
    return hashlib.sha256(raw).digest()[0] & 1


@dataclass(frozen=True)
class Node:
    parents: tuple[int, ...]
    gate: str
    invert: tuple[int, ...]

    def __post_init__(self):
        if (len(self.parents) not in (1, 2) or
            len(self.invert) != len(self.parents) or
            any(type(x) is not int or x not in (0, 1) for x in self.invert) or
            self.gate not in (("PASS",) if len(self.parents) == 1 else GATES)):
            raise ValueError("MD30_INVALID_NODE")


def eval_gate(node: Node, values: tuple[int, ...]) -> int:
    inputs = tuple(values[p] ^ n for p, n in zip(node.parents, node.invert))
    if node.gate == "PASS":
        return inputs[0]
    if node.gate == "AND":
        return inputs[0] & inputs[1]
    if node.gate == "OR":
        return inputs[0] | inputs[1]
    if node.gate == "XOR":
        return inputs[0] ^ inputs[1]
    raise AssertionError("MD30_UNKNOWN_GATE")


@dataclass(frozen=True)
class Graph:
    # Nodes 0 and 1 are exogenous roots; DAG nodes 2 through 5 are listed.
    nodes: tuple[Node, Node, Node, Node]

    def __post_init__(self):
        if len(self.nodes) != 4:
            raise ValueError("MD30_SIX_NODES_REQUIRED")
        for index, node in enumerate(self.nodes, start=2):
            if (not isinstance(node, Node) or len(set(node.parents)) != len(node.parents)
                or any(type(p) is not int or p < 0 or p >= index for p in node.parents)):
                raise ValueError("MD30_NON_DAG_OR_INVALID_PARENT")

    def fingerprint(self):
        return digest([{"parents": n.parents, "gate": n.gate, "invert": n.invert}
                       for n in self.nodes])

    def respond(self, roots: tuple[int, int], clamp: tuple[int, int] | None = None):
        if len(roots) != 2 or any(type(x) is not int or x not in (0, 1) for x in roots):
            raise ValueError("MD30_INVALID_ROOTS")
        if clamp is not None and (len(clamp) != 2 or
                                  type(clamp[0]) is not int or
                                  type(clamp[1]) is not int or
                                  clamp[0] not in range(6) or clamp[1] not in (0, 1)):
            raise ValueError("MD30_INVALID_CLAMP")
        values = [*roots]
        for i in range(2):
            if clamp is not None and clamp[0] == i:
                values[i] = clamp[1]
        for i, node in enumerate(self.nodes, start=2):
            value = eval_gate(node, tuple(values))
            values.append(clamp[1] if clamp is not None and clamp[0] == i else value)
        return tuple(values)


def reference_enumerate(graph: Graph, roots: tuple[int, int],
                        clamp: tuple[int, int] | None = None):
    """Independent constraint-enumeration physics used only by preflight tests."""
    solutions = []
    for bits in itertools.product((0, 1), repeat=6):
        if any(bits[i] != roots[i] for i in range(2)
               if clamp is None or clamp[0] != i):
            continue
        if clamp is not None and bits[clamp[0]] != clamp[1]:
            continue
        if any(bits[i] != eval_gate(node, bits)
               for i, node in enumerate(graph.nodes, start=2)
               if clamp is None or clamp[0] != i):
            continue
        solutions.append(bits)
    if len(solutions) != 1:
        raise AssertionError("MD30_REFERENCE_PHYSICS_NOT_UNIQUE")
    return solutions[0]


def fixture_graph(seed: int, family: str):
    """Synthetic preflight only; all MD30 official cohorts are blocked."""
    if type(seed) is not int or seed < 0 or any(lo <= seed <= hi for lo, hi in FORBIDDEN):
        raise AssertionError("MD30_OFFICIAL_COHORT_ACCESS_DENIED")
    if family not in FAMILIES:
        raise ValueError("MD30_UNKNOWN_MOTIF")
    nodes = []
    for i, parents in enumerate(FAMILIES[family], start=2):
        invert = tuple(sample_bit(seed, f"{family}|node{i}|invert{j}")
                       for j in range(len(parents)))
        gate = (GATES[(sample_bit(seed, f"{family}|node{i}|gate0") * 2 +
                       sample_bit(seed, f"{family}|node{i}|gate1")) % 3]
                if len(parents) == 2 else "PASS")
        nodes.append(Node(tuple(parents), gate, invert))
    return Graph(tuple(nodes))


# Distinct structural explanations of the *same* six-bit public baseline.
# The right graph relocates an edge from C to D and changes C/D gate arity.
# Identical public histories require opposite irreversible choices for F=0.
LEFT = Graph((Node((0, 1), "OR", (0, 1)), Node((2,), "PASS", (0,)),
              Node((3,), "PASS", (0,)), Node((4,), "PASS", (0,))))
RIGHT = Graph((Node((0,), "PASS", (1,)), Node((2, 1), "OR", (0, 0)),
               Node((3,), "PASS", (0,)), Node((4,), "PASS", (0,))))


class World:
    """Private physics; policy gets *only* observe() and step() in tests."""

    def __init__(self, graph: Graph, *, next_graph: Graph | None = None,
                 roots: tuple[int, int] = (0, 0), target: int = 5,
                 desired: int = 0, available: tuple[int, int] = (1, 1),
                 diagnostic_nodes: tuple[int, ...] = (0, 1, 2, 3, 4)):
        if not isinstance(graph, Graph) or (next_graph is not None and
                                           not isinstance(next_graph, Graph)):
            raise ValueError("MD30_INVALID_GRAPH")
        if type(target) is not int or target not in (4, 5) or desired not in (0, 1):
            raise ValueError("MD30_BAD_TARGET")
        if (len(available) != 2 or any(type(v) is not int or v not in (0, 1)
                                      for v in available) or not any(available)):
            raise ValueError("MD30_INVALID_AVAILABILITY")
        if (not isinstance(diagnostic_nodes, tuple) or not diagnostic_nodes or
            len(set(diagnostic_nodes)) != len(diagnostic_nodes) or
            any(type(n) is not int or n not in range(5) for n in diagnostic_nodes)):
            raise ValueError("MD30_INVALID_DIAGNOSTIC_MENU")
        self._diagnostic_nodes = diagnostic_nodes
        self._graph = graph
        self._next_graph = next_graph
        self._roots = roots
        self._target = target
        self._desired = desired
        self._available = available
        self._phase = 0
        self._probes = 0
        self._sensor = graph.respond(roots)
        self._ledger = []
        self._reward = 0.0

    def observe(self):
        return {"phase": self._phase if self._phase < STAGES else "done",
                "sensor_vector": list(self._sensor),
                "actuator_availability": list(self._available),
                "diagnostic_nodes": list(self._diagnostic_nodes),
                "target_sensor": self._target, "desired_value": self._desired,
                "remaining_diagnostics": MAX_DIAGNOSTICS - self._probes if self._phase < STAGES else 0,
                "remaining_physical_steps": MAX_STEPS - len(self._ledger),
                "action_costs": {"diagnostic": PROBE_COST, "actuator": ACTUATE_COST},
                "charged_history": json.loads(canonical(self._ledger))}

    def step(self, action):
        if self._phase >= STAGES or len(self._ledger) >= MAX_STEPS:
            raise AssertionError("MD30_STEP_AFTER_DONE_OR_OVER_BUDGET")
        if not isinstance(action, dict) or set(action) != {"kind", "node", "value"}:
            raise AssertionError("MD30_INVALID_ACTION_FIELDS")
        kind, node, value = action["kind"], action["node"], action["value"]
        if type(node) is not int or type(value) is not int or value not in (0, 1):
            raise AssertionError("MD30_INVALID_ACTION_TYPES")
        if kind == "diagnostic":
            if self._probes >= MAX_DIAGNOSTICS or node not in self._diagnostic_nodes:
                raise AssertionError("MD30_DIAGNOSTIC_CAP_OR_NODE")
            self._sensor = self._graph.respond(self._roots, (node, value))
            reward = -PROBE_COST
            self._probes += 1
        elif kind == "actuator":
            if node not in (0, 1) or not self._available[node]:
                raise AssertionError("MD30_ACTUATOR_UNAVAILABLE")
            self._sensor = self._graph.respond(self._roots, (node, value))
            reward = (WIN if self._sensor[self._target] == self._desired
                      else LOSE) - ACTUATE_COST
        else:
            raise AssertionError("MD30_UNKNOWN_ACTION_KIND")
        self._reward = round(self._reward + reward, 8)
        # The physically observed response is committed before any rewire.
        self._ledger.append({"phase": self._phase, "action": dict(action),
                             "sensor_vector": list(self._sensor),
                             "reward": round(reward, 8)})
        if kind == "actuator":
            self._phase += 1
            self._probes = 0
            if self._phase == 1:
                if self._next_graph is not None:
                    self._graph = self._next_graph
                # A stage boundary releases the pulse, then the new ambient
                # state is physically visible; no graph ID or change flag.
                self._sensor = self._graph.respond(self._roots)
        obs = self.observe()
        return obs, round(reward, 8), self._phase == STAGES

    def receipt(self):
        if self._phase != STAGES:
            raise AssertionError("MD30_INCOMPLETE_TWO_STAGE_EPISODE")
        if len(self._ledger) > MAX_STEPS or sum(
                row["action"]["kind"] == "actuator" for row in self._ledger) != 2:
            raise AssertionError("MD30_INVALID_PHYSICAL_CUSTODY")
        return {"paid_steps": len(self._ledger),
                "net_utility": self._reward,
                "physical_sha256": digest(self._ledger),
                "trace": json.loads(canonical(self._ledger))}


def preflight_headroom():
    """Analytic fixture only; never an official cohort or policy evaluation."""
    first = LEFT.respond((0, 0))
    second = RIGHT.respond((0, 0))
    if first != second:
        raise AssertionError("MD30_OBSERVATIONAL_AMBIGUITY_FAILED")
    actions = ((node, 1) for node in (0, 1))
    scores = {graph.fingerprint(): {} for graph in (LEFT, RIGHT)}
    for graph in (LEFT, RIGHT):
        for node, value in ((0, 1), (1, 1)):
            scores[graph.fingerprint()][node] = (
                WIN if graph.respond((0, 0), (node, value))[5] == 0 else LOSE
            ) - ACTUATE_COST
    oracle = sum(max(s.values()) for s in scores.values()) / 2
    blind = max(sum(s[node] for s in scores.values()) / 2 for node in (0, 1))
    if oracle - blind < 0.5:
        raise AssertionError("MD30_NO_DECISION_HEADROOM")
    if LEFT.respond((0, 0), (0, 1)) == RIGHT.respond((0, 0), (0, 1)):
        raise AssertionError("MD30_PAID_PROBE_NOT_IDENTIFYING")
    return {"identical_initial_public_sensors": first,
            "left_best": max(scores[LEFT.fingerprint()], key=scores[LEFT.fingerprint()].get),
            "right_best": max(scores[RIGHT.fingerprint()], key=scores[RIGHT.fingerprint()].get),
            "oracle_one_stage": oracle, "blind_one_stage": blind,
            "headroom": round(oracle - blind, 8),
            "fixture_graph_hashes": (LEFT.fingerprint(), RIGHT.fingerprint())}
