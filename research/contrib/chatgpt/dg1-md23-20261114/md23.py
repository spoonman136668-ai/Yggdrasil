"""DG1-MD23 prospective tokenless causal-event graph. TOY ONLY until frozen first use.

Only public image/direction, self-history, observed actions and reward are consulted.
The inherited navigation scaffold is scripted; only event counts are learned.
"""
import hashlib
import importlib.util
import json
import statistics
import zlib
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "dg1-md22-20261114" / "md22.py"
spec = importlib.util.spec_from_file_location("md23_exact_md22", str(SOURCE))
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)
m = d.m
m.MAX_STEPS = 256
# UnlockPickup requires physically dropping a carried key to pick up the box.
# The same six legal actions are available to every teacher, learned arm and
# fully trainable conventional control; no free or simulated actions are used.
m.ACTIONS = (0, 1, 2, 3, 4, 5)

FROZEN_PREREG = "ea927ae080aee59d2dc0783f45eb703735dfb52f"
EXACT_PARENT = "155cb5c3c3f4802166ffb26695b7f7353384cb42"
ARMS = ("causal_graph", "shuffled_graph", "fixed_scripted",
        "reactive", "tabular_q", "recurrent_imitation")
TOY_SEEDS = (11, 17, 19, 23, 29, 31)
DOOR_ENV = "MiniGrid-DoorKey-6x6-v0"
BOX_ENV = "MiniGrid-UnlockPickup-v0"
REGISTERED_RANGES = ((980001, 980024), (981001, 981024),
                     (982001, 982012), (983001, 983012),
                     (984001, 984012), (985001, 985012))


def validate_toy_seeds(seeds):
    if not seeds or any(not isinstance(s, int) or s not in TOY_SEEDS for s in seeds):
        raise AssertionError("MD23_ONLY_PREREG_TOY_SEEDS_BEFORE_FIRST_USE")


def verify_prereg():
    data = json.loads(Path(__file__).with_name("prereg.json").read_text())
    if (data["experiment_id"] != "DG1-MD23-20261114"
            or data["exact_parent_sha"] != EXACT_PARENT
            or data["frozen_design"]["toy_only_development_seeds"] != list(TOY_SEEDS)
            or tuple(data["frozen_design"]["arms"]) != ARMS
            or data["status"] != "PREREGISTRATION_ONLY_NO_EXPERIMENT_EXECUTED"):
        raise AssertionError("MD23_PREREGISTRATION_DRIFT")
    for s in TOY_SEEDS:
        if any(lo <= s <= hi for lo, hi in REGISTERED_RANGES):
            raise AssertionError("MD23_TOY_PRIMARY_SEED_COLLISION")


class GraphPolicy(d.AffordancePlanner):
    """Learn conditional physical key->unlock->rewarded-box events on shared traces.

    Causal and shuffled controls use identical observations, memory capacity and
    navigation. Shuffling changes ONLY conditional subgoal use. Scripted control
    has the same navigation but ignores learned edges.
    """
    def __init__(self, kind, probe_first=False):
        if kind not in ("causal_graph", "shuffled_graph", "fixed_scripted"):
            raise ValueError("MD23_INVALID_POLICY")
        self.edges = {"key_before_unlock": 0, "unlock_before_rewarded_box": 0}
        self.train_events = {"key": 0, "unlock": 0, "rewarded_box": 0}
        self.probe_first = bool(probe_first)
        super().__init__("causal_affordance", teacher=(kind == "fixed_scripted"))
        self.kind = kind
        self.start(11)

    def start(self, seed):
        super().start(seed)
        self.episode_key = False
        self.episode_unlock = False
        self.episode_rewarded_box = False
        self.edge_uses = 0
        self.selected_learned_edge = False
        self.task_family_box = False
        self.key_dropped = False

    def feedback(self, before, action, after, reward, training=False):
        from minigrid.core.constants import OBJECT_TO_IDX
        old = m.front_type(before)
        new = m.front_type(after)
        state0 = int(before["image"][3, 5, 2])
        state1 = int(after["image"][3, 5, 2])
        key_pickup = action == 3 and old == OBJECT_TO_IDX["key"] and new != old
        door_unlock = (action == 5 and old == OBJECT_TO_IDX["door"]
                       and state0 in (1, 2) and state1 == 0)
        rewarded_box = (action == 3 and old == OBJECT_TO_IDX["box"] and reward > 0)
        key_drop = (action == 4 and old == OBJECT_TO_IDX["empty"]
                    and new == OBJECT_TO_IDX["key"])
        super().feedback(before, action, after, reward, training=training)
        if key_pickup:
            self.episode_key = True
        if key_drop:
            self.key_dropped = True
            self.has_key = False
        if door_unlock:
            if training:
                self.train_events["unlock"] += 1
                if self.episode_key:
                    self.edges["key_before_unlock"] += 1
            self.episode_unlock = True
        if rewarded_box:
            self.episode_rewarded_box = True
            if training:
                self.train_events["rewarded_box"] += 1
                if self.episode_unlock:
                    self.edges["unlock_before_rewarded_box"] += 1
        if key_pickup and training:
            self.train_events["key"] += 1

    def act(self, obs, t):
        from minigrid.core.constants import OBJECT_TO_IDX
        front = m.front_type(obs)
        if self.opened_door and self.has_key and not self.key_dropped:
            if front == OBJECT_TO_IDX["empty"]:
                return 4  # real charged key drop, then free hands for box pickup
            if front == OBJECT_TO_IDX["box"]:
                return 1  # cannot pick up a box while still carrying the key
        action = super().act(obs, t)
        # The inherited map can momentarily be stale immediately after a drop.
        # Never reacquire the key after a verified unlock: the box needs free
        # hands. This guard is based on the live public front observation.
        if self.opened_door and front == OBJECT_TO_IDX["key"] and action == 3:
            return 1
        return action

    def preferred_subgoal(self):
        from minigrid.core.constants import OBJECT_TO_IDX
        if self.opened_door:
            if OBJECT_TO_IDX["goal"] in self.tiles.values():
                return "goal"
            if self.kind == "causal_graph" and self.edges["unlock_before_rewarded_box"] >= 3:
                self.edge_uses += 1
                self.selected_learned_edge = True
                return "box"
            if self.kind == "shuffled_graph" and self.edges["unlock_before_rewarded_box"] >= 3:
                return "goal"  # fixed, edge-permuted sham decision
            return "box" if self.kind == "fixed_scripted" else "goal"
        if self.has_key:
            return "door"
        if self.probe_first and not self.probed_without_key:
            return "door"
        if self.kind == "fixed_scripted":
            return "key"
        if self.kind == "causal_graph" and self.edges["key_before_unlock"] >= 3:
            self.edge_uses += 1
            self.selected_learned_edge = True
            return "key"
        # With missing/misassigned learned condition, try door first, then key.
        return "key" if self.probed_without_key else "door"

    def dump(self):
        result = super().dump()
        result.update(kind=self.kind, edges=self.edges, train_events=self.train_events,
                      probe_first=self.probe_first)
        return result

    def load(self, data):
        super().load(data)
        if set(data["edges"]) != set(self.edges) or set(data["train_events"]) != set(self.train_events):
            raise AssertionError("MD23_EVENT_GRAPH_SCHEMA_DRIFT")
        self.edges = data["edges"]
        self.train_events = data["train_events"]
        self.probe_first = data["probe_first"]


def make_agent(name):
    if name in ARMS[:3]:
        return GraphPolicy(name)
    if name in ARMS[3:]:
        return m.make_agent(name)
    raise ValueError("MD23_UNKNOWN_ARM")


def save(agent):
    raw = m.canon(agent.dump()).encode()
    data = zlib.compress(raw, 9)
    if len(data) > 65536:
        raise AssertionError("MD23_CHECKPOINT_CAP")
    return data


def restore(data):
    state = json.loads(zlib.decompress(data))
    obj = make_agent(state["kind"])
    obj.load(state)
    if save(obj) != data:
        raise AssertionError("MD23_NONCANONICAL_CHECKPOINT")
    return obj


def teacher_episode(env_name, seed):
    validate_toy_seeds((seed,))
    # A freshly reset scripted navigator, explicitly instructed to attempt the
    # physical locked-door probe before seeking the key. No hidden world state.
    teacher = GraphPolicy("fixed_scripted", probe_first=True)
    ep = m.make_trace(env_name, seed, teacher)
    ep["no_key_probe"] = teacher.episode_failed_probes
    ep["with_key_unlock"] = teacher.episode_successful_unlocks
    ep["rewarded_box"] = int(teacher.episode_rewarded_box)
    if ep["steps"] != len(ep["transitions"]):
        raise AssertionError("MD23_UNCHARGED_PHYSICAL_ACTION")
    return ep


def train_shared(agents, episode):
    """Exactly one genuine physical teacher trajectory shared by all six arms."""
    for key in ("causal_graph", "shuffled_graph"):
        agents[key].start(episode["seed"])
        agents[key].training_episodes += 1
    seq = []
    last = 6
    for i, (before, action, reward, after, terminated) in enumerate(episode["transitions"]):
        for key in ("causal_graph", "shuffled_graph"):
            agents[key].feedback(before, action, after, reward, training=True)
        agents["tabular_q"].feedback(before, action, after, reward,
                                     training=True, terminal=terminated)
        seq.append(m.public_features(before, last, i))
        seq = seq[-m.HISTORY:]
        agents["recurrent_imitation"].learn(seq, action, 2. if episode["success"] else 1.)
        last = action


def toy_qualification(seeds=TOY_SEEDS):
    """Never touches frozen registered cohorts or writes primary science results."""
    verify_prereg()
    validate_toy_seeds(seeds)
    import gymnasium
    import minigrid
    import numpy
    if (gymnasium.__version__, minigrid.__version__, numpy.__version__) != (
            "1.4.0", "3.2.0", "2.3.4"):
        raise AssertionError("MD23_DEPENDENCY_DRIFT")
    agents = {a: make_agent(a) for a in ARMS}
    observed = {"door": {"episodes": 0, "goals": 0, "no_key_probe": 0,
                          "with_key_unlock": 0},
                "box": {"episodes": 0, "goals": 0, "rewarded_box": 0,
                         "no_key_probe": 0, "with_key_unlock": 0}}
    traces = {}
    for env, label in ((DOOR_ENV, "door"), (BOX_ENV, "box")):
        for seed in seeds:
            ep = teacher_episode(env, seed)
            part = observed[label]
            part["episodes"] += 1
            part["goals"] += ep["success"]
            part["no_key_probe"] += ep["no_key_probe"]
            part["with_key_unlock"] += ep["with_key_unlock"]
            if label == "box":
                part["rewarded_box"] += ep["rewarded_box"]
            traces[label + ":" + str(seed)] = ep["sha256"]
            train_shared(agents, ep)
    a, b = agents["causal_graph"], agents["shuffled_graph"]
    if (a.edges != b.edges or a.train_events != b.train_events
            or a.failed_without_key != b.failed_without_key
            or a.unlocked_with_key != b.unlocked_with_key
            or a.train_calls != b.train_calls):
        raise AssertionError("MD23_UNMATCHED_SHARED_TRAINING")
    checkpoints = {k: save(v) for k, v in agents.items()}
    if any(save(restore(x)) != x for x in checkpoints.values()):
        raise AssertionError("MD23_COLD_RESTORE_FAILED")
    return {"schema": "yggdrasil.dg1-md23-toy-prefirstuse.v1",
            "seeds": list(seeds), "teacher": observed, "trace_sha256": traces,
            "learned_edges": a.edges,
            "trained_counts": {"q": agents["tabular_q"].count,
                               "rnn": agents["recurrent_imitation"].count},
            "checkpoint_sha256": {k: hashlib.sha256(v).hexdigest()
                                   for k, v in checkpoints.items()},
            "checkpoint_bytes": {k: len(v) for k, v in checkpoints.items()},
            "registered_first_use": False}


if __name__ == "__main__":
    print(m.canon(toy_qualification()))
