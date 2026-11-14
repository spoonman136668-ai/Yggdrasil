"""DG1-MD34: partial-observation three-stage consequential causal routes.

External physics-only fixture, separate from frozen MD29/30/31/32/33.
One physically charged binary diagnostic is shared across THREE irreversible
steps; observing a bit can never reveal a 4-way target. No native learner.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOCK = json.loads((HERE / "prereg.json").read_text("utf-8"))
assert LOCK["schema"] == "yggdrasil.dg1-md34-partially-observed-causal-routes-prereg.v1"
assert LOCK["status"] == "TASK_ONLY_FROZEN_BEFORE_GENERATOR_OR_OUTCOMES"
LAWS = {
    name: {k: tuple(v) for k, v in law.items()}
    for name, law in LOCK["mechanisms"]["law_contract"].items()
}
MOTIFS = tuple(LOCK["mechanisms"]["types"])
TRAIN = tuple(LOCK["mechanisms"]["train_mechanisms"])
TRANSFER = tuple(LOCK["mechanisms"]["transfer_mechanisms"])
FIRST, LAST = LOCK["fixture"]["synthetic_only_seed_range"]
ZERO = [0, 0]
N = 4


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def sensor_bit(bit):
    if type(bit) is not int or bit not in (0, 1):
        raise AssertionError("MD34_ONLY_ONE_PHYSICAL_BIT")
    return [int(bit == 0), int(bit == 1)]


def paid_bit(observation):
    sensor = observation["sensor_vector"]
    if (type(sensor) is not list or len(sensor) != 2 or
            any(type(x) is not int or x not in (0, 1) for x in sensor) or
            sum(sensor) != 1):
        raise AssertionError("MD34_NO_ONE_BIT_PHYSICAL_DIAGNOSTIC")
    return sensor.index(1)


def fixture_spec(seed):
    """Fixture harness only, NEVER a policy input or scientific seed."""
    if type(seed) is not int or not FIRST <= seed <= LAST:
        raise AssertionError("MD34_OFFICIAL_FIRST_USE_OR_UNALLOCATED_SEED_FORBIDDEN")
    block, context = divmod(seed - FIRST, 4)
    name = MOTIFS[block % len(MOTIFS)]
    law = LAWS[name]
    return {
        "context": context,
        "E": law["E"],
        "G0": law["G0"],
        "G1": tuple((x + 1) % N for x in law["G0"]),
        "D": law["D"],
        "offset": block // len(MOTIFS),
    }


class PartialRouteWorld:
    """Only observe/step/receipt are permissible policy interactions."""

    def __init__(self, spec, *, rewire):
        if type(rewire) is not bool:
            raise AssertionError("MD34_INVALID_HIDDEN_REWIRE_CONDITION")
        self._spec = dict(spec)
        self._rewire = rewire
        self._phase = 0
        self._hidden_h = None
        self._hidden_x = None
        self._route = None
        self._sensors = ZERO[:]
        self._paid_probe = False
        self._history = []
        self._utility = []

    def observe(self):
        if self._phase == 0:
            menu = [{"mechanism": "encoder_parity",
                     "channel": self._spec["context"]}]
        elif self._phase == 1:
            menu = [{"mechanism": "route_parity", "channel": r}
                    for r in (0, 1)]
        elif self._phase == 2:
            menu = [{"mechanism": "terminal_parity"}]
        else:
            menu = []
        return {
            "phase": self._phase if self._phase < 3 else "done",
            "required_context": self._spec["context"],
            "sensor_vector": list(self._sensors),
            "remaining_diagnostics": int(
                self._phase < 3 and not self._paid_probe),
            "diagnostic_menu": menu,
            "charged_history": deepcopy(self._history),
        }

    def _terminal(self):
        if self._hidden_x is None:
            raise AssertionError("MD34_LATENT_TERMINAL_NOT_CAUSED")
        return ((self._spec["D"][self._hidden_x] +
                 self._spec["offset"] + int(self._rewire)) % N)

    def step(self, action):
        if self._phase == 3:
            raise AssertionError("MD34_ACTION_AFTER_TERMINAL_DONE")
        if type(action) is not dict:
            raise AssertionError("MD34_PHYSICAL_ACTION_SHAPE_INVALID")
        stage = self._phase
        kind = action.get("kind")
        if kind == "diagnostic":
            if self._paid_probe or self._phase > 2:
                raise AssertionError("MD34_GLOBAL_PAID_DIAGNOSTIC_CAP")
            if stage == 0:
                if action != {
                    "kind": "diagnostic", "mechanism": "encoder_parity",
                    "channel": self._spec["context"],
                }:
                    raise AssertionError("MD34_UNAUTHORIZED_ENCODER_QUERY")
                bit = self._spec["E"][self._spec["context"]] % 2
            elif stage == 1:
                if (set(action) != {"kind", "mechanism", "channel"} or
                        action["mechanism"] != "route_parity" or
                        type(action["channel"]) is not int or
                        action["channel"] not in (0, 1)):
                    raise AssertionError("MD34_UNAUTHORIZED_PAID_ROUTE_QUERY")
                route = action["channel"]
                bit = self._spec["G0" if route == 0 else "G1"][
                    self._hidden_h] % 2
            else:
                if action != {
                    "kind": "diagnostic", "mechanism": "terminal_parity",
                }:
                    raise AssertionError("MD34_UNAUTHORIZED_TERMINAL_QUERY")
                bit = self._terminal() % 2
            self._paid_probe = True
            self._sensors = sensor_bit(bit)
            reward = -0.09
        elif kind == "actuator" and stage == 0:
            if action != {
                "kind": "actuator", "channel": self._spec["context"],
            }:
                raise AssertionError("MD34_WRONG_PUBLIC_CONTEXT")
            self._hidden_h = self._spec["E"][self._spec["context"]]
            self._phase = 1
            self._sensors = ZERO[:]
            reward = -0.02
        elif kind == "route" and stage == 1:
            if (set(action) != {"kind", "choice"} or
                    type(action["choice"]) is not int or
                    action["choice"] not in (0, 1)):
                raise AssertionError("MD34_INVALID_IRREVERSIBLE_ROUTE")
            self._route = action["choice"]
            self._hidden_x = self._spec[
                "G0" if self._route == 0 else "G1"][self._hidden_h]
            self._phase = 2
            self._sensors = ZERO[:]
            reward = -0.02 if self._route == 0 else -0.05
        elif kind == "terminal" and stage == 2:
            if (set(action) != {"kind", "guess"} or
                    type(action["guess"]) is not int or
                    action["guess"] not in range(N)):
                raise AssertionError("MD34_INVALID_TERMINAL_GUESS")
            reward = 0.98 if action["guess"] == self._terminal() else -0.52
            self._phase = 3
            self._sensors = ZERO[:]
        else:
            raise AssertionError("MD34_WRONG_ACTION_FOR_CAUSAL_PHASE")
        self._history.append({
            "phase": stage,
            "action": dict(action),
            "sensor_vector": self._sensors[:],
            "reward": reward,
        })
        self._utility.append(reward)
        if len(self._history) > 4:
            raise AssertionError("MD34_PAID_ACTION_CAP_EXCEEDED")
        return self.observe(), reward, self._phase == 3

    def receipt(self):
        if self._phase != 3:
            raise AssertionError("MD34_INCOMPLETE_PHYSICAL_EPISODE")
        trace = deepcopy(self._history)
        return {
            "schema": "md34.public-three-stage-paid-physical-receipt.v1",
            "paid_steps": len(trace),
            "charged_diagnostics": int(self._paid_probe),
            "net_utility": round(sum(self._utility), 6),
            "trace": trace,
            "public_trace_sha256": digest(trace),
        }


def fixture_world(seed, *, rewire):
    return PartialRouteWorld(fixture_spec(seed), rewire=rewire)


def public_blind(world):
    """No private mechanism/label: 3 real irreversible physical steps."""
    context = world.observe()["required_context"]
    world.step({"kind": "actuator", "channel": context})
    world.step({"kind": "route", "choice": 0})
    world.step({"kind": "terminal", "guess": 0})
    return world.receipt()


def public_parity_only(world):
    """Exactly one real paid bit: can disambiguate at most two classes."""
    context = world.observe()["required_context"]
    world.step({"kind": "actuator", "channel": context})
    world.step({"kind": "route", "choice": 0})
    before = world.observe()
    action = {"kind": "diagnostic", "mechanism": "terminal_parity"}
    after, reward, done = world.step(action)
    if (done or reward != -0.09 or
            len(after["charged_history"]) !=
            len(before["charged_history"]) + 1 or
            after["charged_history"][-1]["action"] != action):
        raise AssertionError("MD34_UNPAID_OR_FAKE_TERMINAL_PROBE")
    bit = paid_bit(after)
    world.step({"kind": "terminal", "guess": bit})
    return world.receipt()


def privileged_physics_oracle(world, spec, rewire):
    """Privileged harness ceiling ONLY; must never be used as learner."""
    context = world.observe()["required_context"]
    h = spec["E"][context]
    x = spec["G0"][h]
    answer = (spec["D"][x] + spec["offset"] + int(rewire)) % N
    world.step({"kind": "actuator", "channel": context})
    world.step({"kind": "route", "choice": 0})
    world.step({"kind": "terminal", "guess": answer})
    return world.receipt()


def manifest():
    hashes = {name: digest({"E": law["E"], "G0": law["G0"], "D": law["D"]})
              for name, law in sorted(LAWS.items())}
    if (len(LAWS) != 6 or len(set(hashes.values())) != 6 or
            len(TRAIN) != 3 or len(TRANSFER) != 3 or
            set(TRAIN) & set(TRANSFER) or set(TRAIN + TRANSFER) != set(LAWS)):
        raise AssertionError("MD34_CAUSAL_MECHANISM_FAMILY_COLLISION")
    for law in LAWS.values():
        if any(set(law[key]) != set(range(N)) for key in ("E", "G0", "D")):
            raise AssertionError("MD34_NONBIJECTIVE_OR_UNFROZEN_COVERAGE")
    return {
        "trained_family": list(TRAIN),
        "unfamiliar_family": list(TRANSFER),
        "six_mechanism_sha256": hashes,
        "family_sha256": digest(hashes),
    }


def task_preflight():
    """Fixture-only; exact physical interventions, NO trained learner."""
    law_manifest = manifest()
    rows = []
    for seed in range(FIRST, LAST + 1):
        spec = fixture_spec(seed)
        for changed in (False, True):
            oracle = privileged_physics_oracle(
                fixture_world(seed, rewire=changed), spec, changed)
            blind = public_blind(fixture_world(seed, rewire=changed))
            parity = public_parity_only(fixture_world(seed, rewire=changed))
            a = {
                "seed": seed,
                "motif": MOTIFS[((seed - FIRST) // 4) % 6],
                "rewire": changed,
                "oracle": oracle["net_utility"],
                "blind": blind["net_utility"],
                "parity": parity["net_utility"],
                "blind_correct": blind["trace"][-1]["reward"] == 0.98,
                "parity_correct": parity["trace"][-1]["reward"] == 0.98,
                "oracle_trace_sha256": oracle["public_trace_sha256"],
                "blind_trace_sha256": blind["public_trace_sha256"],
                "parity_trace_sha256": parity["public_trace_sha256"],
            }
            if (oracle["paid_steps"] != 3 or blind["paid_steps"] != 3 or
                    parity["paid_steps"] != 4 or
                    parity["charged_diagnostics"] != 1):
                raise AssertionError("MD34_UNCHARGED_TASK_REFERENCE")
            rows.append(a)
    if len(rows) != 192:
        raise AssertionError("MD34_WRONG_SYNTHETIC_FIXTURE_COVERAGE")
    by_motif = {}
    for motif in MOTIFS:
        examples = [x for x in rows if x["motif"] == motif]
        stable = [x for x in examples if not x["rewire"]]
        rewired = [x for x in examples if x["rewire"]]
        if (len(stable) != 16 or len(rewired) != 16 or
                sum(x["blind_correct"] for x in examples) != 8 or
                sum(x["parity_correct"] for x in examples) != 16 or
                sum(x["blind_correct"] for x in stable) != 4 or
                sum(x["parity_correct"] for x in stable) != 8):
            raise AssertionError("MD34_PARTIAL_INFORMATION_ALLOCATION_SHORTCUT")
        by_motif[motif] = {
            "physical_worlds": 32,
            "blind_correct": 8,
            "one_bit_correct": 16,
        }

    # Counterfactual intervention really changes future causal consequences
    # and stable/rewire worlds stay observationally identical until a paid
    # terminal parity probe, with no free hidden-law announcement.
    for seed in range(FIRST, LAST + 1):
        spec = fixture_spec(seed)
        h = spec["E"][spec["context"]]
        x0, x1 = spec["G0"][h], spec["G1"][h]
        if (x0 == x1 or
                spec["D"][x0] == spec["D"][x1]):
            raise AssertionError("MD34_IRREVERSIBLE_ROUTE_HAS_NO_EFFECT")
        w0 = fixture_world(seed, rewire=False)
        w1 = fixture_world(seed, rewire=True)
        if w0.observe() != w1.observe():
            raise AssertionError("MD34_FUTURE_REWIRE_ANNOUNCED")
        context = w0.observe()["required_context"]
        for action in ({"kind": "actuator", "channel": context},
                       {"kind": "route", "choice": 0}):
            b0, _, done0 = w0.step(action)
            b1, _, done1 = w1.step(action)
            if done0 or done1 or b0 != b1 or b0["sensor_vector"] != ZERO:
                raise AssertionError("MD34_FREE_CHANGED_CAUSAL_STATE_LEAK")
        diag = {"kind": "diagnostic", "mechanism": "terminal_parity"}
        post0, cost0, _ = w0.step(diag)
        post1, cost1, _ = w1.step(diag)
        if (cost0 != -0.09 or cost1 != -0.09 or
                post0["sensor_vector"] == post1["sensor_vector"]):
            raise AssertionError("MD34_REWIRE_NOT_PHYSICALLY_DETECTABLE")

    def mean(key):
        return round(sum(x[key] for x in rows) / len(rows), 6)
    oracle, blind, parity = (mean("oracle"), mean("blind"), mean("parity"))
    if (oracle != 0.94 or blind != -0.185 or parity != 0.1 or
            sum(x["blind_correct"] for x in rows) != 48 or
            sum(x["parity_correct"] for x in rows) != 96):
        raise AssertionError("MD34_FROZEN_ORACLE_BLIND_PARTIAL_GAP_DRIFT")
    return {
        "schema": "md34.partial-information-task-physics-v1",
        "status": "TASK_PHYSICS_PREFLIGHT_ONLY_NOT_MODEL_SCIENCE",
        "official_first_use": False,
        "trained_agent_evaluated": False,
        "fixture_seed_range": [FIRST, LAST],
        "fixture_physical_worlds": len(rows),
        "four_episode_law_blocks": (LAST - FIRST + 1) // 4,
        "six_family_structural_manifest": law_manifest,
        "per_motif": by_motif,
        "oracle_mean_reward": oracle,
        "blind_mean_reward": blind,
        "one_paid_bit_mean_reward": parity,
        "oracle_minus_blind": round(oracle - blind, 6),
        "oracle_minus_one_bit": round(oracle - parity, 6),
        "blind_success_fraction": 0.25,
        "one_paid_bit_success_fraction": 0.50,
        "stable_rewire_observationally_equal_until_paid_probe": "96/96",
        "route_causal_consequence_distinct": "96/96",
        "physical_trace_sha256": digest(rows),
        "conventional_training_headroom": "UNVERIFIED",
    }


if __name__ == "__main__":
    print(canonical(task_preflight()))
