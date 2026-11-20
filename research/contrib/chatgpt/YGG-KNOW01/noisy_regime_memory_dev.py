"""KNOW20: frozen synthetic single-world noisy action-consequence learning.

This is an isolated *research proposal*, not an accepted Yggdrasil native
sublearner or canonical checkpoint. See know20_protocol.json, prereg commit
1015bac86eecf675b3d563da1a5b64f4b8cacc5a. No model-owner actions.
Only the private evaluator (never the policies) knows the hidden causal regime.
"""
from __future__ import annotations

import copy
import hashlib
import json
import time
from pathlib import Path

TRAIN_A = (6011, 6121)
TRAIN_B = (6247, 6337)
HELD = (6451, 6581, 6703, 6823, 6947, 7069)
SEEDS = TRAIN_A + TRAIN_B + HELD
SCHEMA = "yggdrasil.know20.native-sparse-regime-memory.dev.v1"
PREREG = "1015bac86eecf675b3d563da1a5b64f4b8cacc5a"
MAX_BYTES = 131072
SOURCE_MODE = "engineering_fixture_only"
STEPS = 48


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def require(ok, code):
    if not ok:
        raise ValueError("YGG_KNOW20_" + code)


def check_scene(scene):
    require(type(scene) is int and scene in SEEDS, "SCENE")


def check_action(action):
    require(type(action) is int and action in (0, 1), "ACTION")


def public_source(scene):
    """Identical for both possible private roles, no private-state feature."""
    check_scene(scene)
    opaque = hashlib.sha256(f"know20:public:scene:{scene}".encode()).digest()
    return {"scene_id": scene,
            "opaque_source_id": int.from_bytes(opaque[:4], "big"),
            "source_mode": SOURCE_MODE, "native_accepted": False}


def optimal_private_action(initial_role, step):
    require(type(initial_role) is int and initial_role in (0, 1)
            and type(step) is int and 0 <= step < STEPS, "PRIVATE_LAW")
    return initial_role ^ int(16 <= step < 32)


def private_noise(scene, step):
    """One frozen exogenous coin for *both* arms, hidden from every policy."""
    check_scene(scene)
    require(type(step) is int and 0 <= step < STEPS, "NOISE_STEP")
    raw = f"know20:private:counterfactual-coupling:v1:{scene}:{step}".encode()
    return int.from_bytes(hashlib.sha256(raw).digest()[:8], "big") / (1 << 64)


def private_consequence(scene, initial_role, step, action):
    check_action(action)
    best = optimal_private_action(initial_role, step)
    p = 0.8 if action == best else 0.2
    return int(private_noise(scene, step) < p)


def beta(counts):
    success, trials = counts
    return (1 + success) / (2 + trials)


class NativeSparseRegimeMemory:
    """Bounded two-slot local outcome counts with reversible regime selection.

    Candidate research-only memory. One action/outcome input per update.
    No hidden label, cross-world counterfactual or symbolic utility oracle.
    """
    def __init__(self, scenes=None):
        self._scenes = {} if scenes is None else scenes

    @staticmethod
    def _fresh():
        return {"active": 0, "slots": [[[0, 0], [0, 0]],
                                       [[0, 0], [0, 0]]],
                "recent": [], "since_switch": 0, "next_step": 0,
                "switches": 0}

    def _get(self, scene):
        check_scene(scene)
        return self._scenes.get(scene, self._fresh())

    def predict(self, scene, action):
        check_action(action)
        s = self._get(scene)
        return beta(s["slots"][s["active"]][action])

    def choose(self, scene):
        return int(self.predict(scene, 1) > self.predict(scene, 0))

    def stage(self, scene, step, action, witnessed,
              *, source_mode=SOURCE_MODE):
        check_scene(scene)
        check_action(action)
        require(source_mode == SOURCE_MODE, "FORGED_SOURCE_MODE")
        require(type(step) is int and 0 <= step < STEPS
                and type(witnessed) is int and witnessed in (0, 1),
                "WITNESSED_BINARY")
        scenes = copy.deepcopy(self._scenes)
        s = scenes.setdefault(scene, self._fresh())
        require(step == s["next_step"], "REPLAY_OR_OUT_OF_ORDER")
        forecast = beta(s["slots"][s["active"]][action])
        anomaly = int((forecast >= 0.65 and witnessed == 0)
                      or (forecast <= 0.35 and witnessed == 1))
        s["slots"][s["active"]][action][0] += witnessed
        s["slots"][s["active"]][action][1] += 1
        s["next_step"] += 1
        s["since_switch"] += 1
        s["recent"].append(anomaly)
        s["recent"] = s["recent"][-6:]
        if s["since_switch"] >= 8 and sum(s["recent"]) >= 3:
            s["active"] ^= 1
            s["switches"] += 1
            s["since_switch"] = 0
            s["recent"] = []
        return NativeSparseRegimeMemory(scenes)

    def switches(self, scene):
        return self._get(scene)["switches"]

    def checkpoint(self):
        rows = [{"scene": seed, **copy.deepcopy(self._scenes[seed])}
                for seed in sorted(self._scenes)]
        raw = canonical({"schema": SCHEMA, "source_mode": SOURCE_MODE,
                         "accepted_native": False, "scientific_pass": False,
                         "scenes": rows})
        require(len(raw) <= MAX_BYTES, "CHECKPOINT_CAPACITY")
        return raw

    @classmethod
    def restore(cls, raw, expected_sha256):
        require(type(raw) is bytes and 0 < len(raw) <= MAX_BYTES
                and type(expected_sha256) is str
                and len(expected_sha256) == 64
                and all(c in "0123456789abcdef" for c in expected_sha256)
                and digest(raw) == expected_sha256, "CHECKPOINT_PIN")
        def unique(pairs):
            out = {}
            for k, v in pairs:
                require(k not in out, "DUPLICATE_JSON_KEY")
                out[k] = v
            return out
        try:
            d = json.loads(raw.decode("ascii"), object_pairs_hook=unique)
            require(type(d) is dict and set(d) == {
                "schema", "source_mode", "accepted_native",
                "scientific_pass", "scenes"}, "CHECKPOINT_FIELDS")
            require(d["schema"] == SCHEMA and d["source_mode"] == SOURCE_MODE
                    and d["accepted_native"] is False and
                    d["scientific_pass"] is False
                    and type(d["scenes"]) is list
                    and canonical(d) == raw, "CHECKPOINT_CONTRACT")
            state = {}
            for s in d["scenes"]:
                require(type(s) is dict and set(s) == {
                    "scene", "active", "slots", "recent", "since_switch",
                    "next_step", "switches"}, "SCENE_FIELDS")
                key = s["scene"]
                check_scene(key)
                require(key not in state and type(s["active"]) is int
                        and s["active"] in (0, 1), "SCENE_DUPLICATE_OR_ACTIVE")
                require(type(s["slots"]) is list and len(s["slots"]) == 2
                        and all(type(slot) is list and len(slot) == 2
                                and all(type(pair) is list and len(pair) == 2
                                        and all(type(v) is int and
                                                0 <= v <= STEPS for v in pair)
                                        and pair[0] <= pair[1]
                                        for pair in slot)
                                for slot in s["slots"]), "SLOT_COUNTS")
                require(type(s["next_step"]) is int
                        and 1 <= s["next_step"] <= STEPS
                        and sum(p[1] for slot in s["slots"] for p in slot)
                        == s["next_step"], "SLOT_HISTORY")
                require(type(s["since_switch"]) is int
                        and 0 <= s["since_switch"] <= s["next_step"]
                        and type(s["switches"]) is int
                        and 0 <= s["switches"] <= s["next_step"] // 8,
                        "SWITCH_COUNT")
                require(type(s["recent"]) is list
                        and len(s["recent"]) <= min(6, s["since_switch"])
                        and all(type(x) is int and x in (0, 1)
                                for x in s["recent"]), "RECENT")
                state[key] = {k: copy.deepcopy(v) for k, v in s.items()
                              if k != "scene"}
            result = cls(state)
            require(result.checkpoint() == raw, "CHECKPOINT_REPLAY")
            return result
        except (ValueError, TypeError, KeyError, UnicodeError,
                AttributeError, OverflowError) as exc:
            raise ValueError("YGG_KNOW20_CHECKPOINT_REJECTED") from exc


class StationaryBeta:
    def __init__(self):
        self.counts = [[0, 0], [0, 0]]

    def predict(self, action):
        return beta(self.counts[action])

    def choose(self):
        return int(self.predict(1) > self.predict(0))

    def observe(self, action, result):
        self.counts[action][0] += result
        self.counts[action][1] += 1


class RollingBeta:
    def __init__(self):
        self.history = []

    def predict(self, action):
        seen = [y for a, y in self.history if a == action]
        return (sum(seen) + 1) / (len(seen) + 2)

    def choose(self):
        return int(self.predict(1) > self.predict(0))

    def observe(self, action, result):
        self.history.append((action, result))
        self.history = self.history[-8:]


class ResetBeta:
    """Same anomaly detector as native, but irreversible reset destroys older regime."""
    def __init__(self):
        self.counts = [[0, 0], [0, 0]]
        self.recent = []
        self.since_switch = 0
        self.switch_count = 0

    def predict(self, action):
        return beta(self.counts[action])

    def choose(self):
        return int(self.predict(1) > self.predict(0))

    def observe(self, action, result):
        p = self.predict(action)
        anomaly = int((p >= 0.65 and result == 0)
                      or (p <= 0.35 and result == 1))
        self.counts[action][0] += result
        self.counts[action][1] += 1
        self.since_switch += 1
        self.recent = (self.recent + [anomaly])[-6:]
        if self.since_switch >= 8 and sum(self.recent) >= 3:
            self.counts = [[0, 0], [0, 0]]
            self.recent = []
            self.since_switch = 0
            self.switch_count += 1


class BayesianHMM:
    """Strong conventional known-family comparator; role remains hidden."""
    def __init__(self):
        self.p_role1 = 0.5

    def predict(self, action):
        role_probability = self.p_role1 if action == 1 else 1 - self.p_role1
        return 0.2 + 0.6 * role_probability

    def choose(self):
        return int(self.predict(1) > self.predict(0))

    def observe(self, action, result):
        p1 = 0.8 if action == 1 else 0.2
        p0 = 0.8 if action == 0 else 0.2
        l1 = p1 if result == 1 else 1 - p1
        l0 = p0 if result == 1 else 1 - p0
        numer = self.p_role1 * l1
        posterior = numer / (numer + (1 - self.p_role1) * l0)
        # Preregistered hazard, not a hidden changepoint oracle.
        self.p_role1 = (15 / 16) * posterior + (1 / 16) * (1 - posterior)


class DeterministicRandom:
    def __init__(self, scene):
        import random
        self.rng = random.Random(scene * 139 + 53)

    def predict(self, action):
        return 0.5

    def choose(self):
        return self.rng.randrange(2)

    def observe(self, action, result):
        pass


class PassiveZero:
    def predict(self, action):
        return 0.5

    def choose(self):
        return 0

    def observe(self, action, result):
        pass


POLICIES = ("native", "stationary_beta", "rolling_8",
            "gated_reset", "bayes_hmm", "seeded_random",
            "passive_zero", "truth_oracle")


def evaluate_world(scene, role, policy):
    check_scene(scene)
    require(scene in HELD and type(role) is int and role in (0, 1)
            and policy in POLICIES, "HELD_WORLD")
    if policy == "native":
        state = NativeSparseRegimeMemory()
    else:
        ctor = {"stationary_beta": StationaryBeta, "rolling_8": RollingBeta,
                "gated_reset": ResetBeta, "bayes_hmm": BayesianHMM,
                "seeded_random": lambda: DeterministicRandom(scene),
                "passive_zero": PassiveZero}.get(policy)
        state = ctor() if ctor is not None else None
    wrong = 0
    return_wrong = 0
    reward_sum = 0
    brier = 0.0
    actions = []
    for step in range(STEPS):
        best = optimal_private_action(role, step)  # EVALUATOR ONLY
        if policy == "native":
            action = state.choose(scene)
            p = state.predict(scene, action)
        elif policy == "truth_oracle":
            action, p = best, 0.8
        else:
            action = state.choose()
            p = state.predict(action)
        check_action(action)
        observed = private_consequence(scene, role, step, action)
        wrong += int(action != best)
        if step >= 32:
            return_wrong += int(action != best)
        reward_sum += observed
        brier += (p - observed) ** 2
        actions.append(action)
        if policy == "native":
            state = state.stage(scene, step, action, observed)
        elif policy != "truth_oracle":
            state.observe(action, observed)
    return {"steps": STEPS, "wrong_actions": wrong,
            "return_wrong_actions": return_wrong, "rewards": reward_sum,
            "brier_sum": brier,
            "switches": (state.switches(scene) if policy == "native"
                         else state.switch_count if policy == "gated_reset" else None),
            "actions": tuple(actions)}


def score_policies():
    result = {}
    for name in POLICIES:
        worlds = [evaluate_world(scene, role, name)
                  for scene in HELD for role in (0, 1)]
        n = len(worlds) * STEPS
        total_wrong = sum(x["wrong_actions"] for x in worlds)
        return_wrong = sum(x["return_wrong_actions"] for x in worlds)
        result[name] = {
            "worlds": len(worlds), "witnessed_actions": n,
            "correct_optimal_action_rate": round(1 - total_wrong / n, 8),
            "expected_regret_per_action": round(0.6 * total_wrong / n, 8),
            "return_expected_regret_per_action": round(
                0.6 * return_wrong / (16 * len(worlds)), 8),
            "realized_reward_rate": round(
                sum(x["rewards"] for x in worlds) / n, 8),
            "prequential_brier": round(
                sum(x["brier_sum"] for x in worlds) / n, 8),
            "switches": (sum(x["switches"] for x in worlds)
                         if name in ("native", "gated_reset") else None),
        }
    return result


def proof():
    started = time.monotonic()
    prereg = json.loads(Path(__file__).with_name(
        "know20_protocol.json").read_text(encoding="utf-8"))
    require(prereg.get("schema") ==
            "yggdrasil.know20.noisy-action-consequence-regime-memory-frozen-dev.v1"
            and prereg.get("seeds", {}).get("fit_A") == list(TRAIN_A)
            and prereg.get("seeds", {}).get("fit_B") == list(TRAIN_B)
            and prereg.get("seeds", {}).get("held_scenes") == list(HELD),
            "PREREG_DRIFT")
    model = NativeSparseRegimeMemory()
    for scene, role in zip(TRAIN_A, (0, 1)):
        for t in range(STEPS):
            action = t % 2  # blinded, fixed, equal-action factual training
            model = model.stage(scene, t, action,
                                private_consequence(scene, role, t, action))
    old = tuple((scene, action, model.predict(scene, action))
                for scene in TRAIN_A for action in (0, 1))
    before_bytes = model.checkpoint()
    for scene, role in zip(TRAIN_B, (0, 1)):
        for t in range(STEPS):
            action = t % 2
            model = model.stage(scene, t, action,
                                private_consequence(scene, role, t, action))
    after = tuple((scene, action, model.predict(scene, action))
                  for scene in TRAIN_A for action in (0, 1))
    drift = sum(x != y for x, y in zip(old, after))
    chk = model.checkpoint()
    cold = NativeSparseRegimeMemory.restore(chk, digest(chk))
    require(drift == 0 and cold.checkpoint() == chk
            and tuple((scene, action, cold.predict(scene, action))
                      for scene in TRAIN_A for action in (0, 1)) == old,
            "COLD_RETENTION")
    require(all(cold.predict(scene, action) == 0.5
                for scene in HELD for action in (0, 1)),
            "UNSEEN_SCENE_MUST_NOT_LEAK_ROLE")
    held = score_policies()
    require(all(x["worlds"] == 12 and x["witnessed_actions"] == 576
                for x in held.values()), "BUDGET")
    native = held["native"]
    fixed = held["stationary_beta"]
    reset = held["gated_reset"]
    best_control = min(
        held[x]["expected_regret_per_action"]
        for x in ("stationary_beta", "rolling_8",
                  "gated_reset", "bayes_hmm"))
    improvement = round(
        fixed["expected_regret_per_action"] -
        native["expected_regret_per_action"], 8)
    supported = (
        improvement >= 0.03 and
        native["return_expected_regret_per_action"]
        <= reset["return_expected_regret_per_action"]
    )
    return {
        "schema": "yggdrasil.know20.noisy-action-dev-result.v1",
        "prereg_commit": PREREG,
        "native_architecture": "research_only_sparse_two_regime_bernoulli_memory",
        "no_accepted_model_or_training_owner_change": True,
        "fit_witnessed_actions": 192, "fit_A_actions": 96,
        "fit_B_actions": 96, "held_actions_per_policy": 576,
        "old_A_prediction_drift": drift,
        "cold_checkpoint_bytes": len(chk),
        "cold_checkpoint_sha256": digest(chk),
        "A_checkpoint_bytes": len(before_bytes),
        "held_policies": held,
        "native_vs_stationary_regret_improvement": improvement,
        "native_vs_strongest_regret_improvement": round(
            best_control - native["expected_regret_per_action"], 8),
        "development_hypothesis": ("MECHANISM_SUPPORTED_DEVELOPMENT"
                                   if supported else "DEV_NO_GO_OR_MIXED"),
        "engineering_gate": "PASS",
        "scientific_gate": "NOT_QUALIFIED_SYNTHETIC_DEVELOPMENT_ONLY",
        "protected_original_first_use": False, "deployment": "NONE",
        "isolated_wall_seconds": round(time.monotonic() - started, 6),
    }


if __name__ == "__main__":
    print(json.dumps(proof(), indent=2, sort_keys=True))
