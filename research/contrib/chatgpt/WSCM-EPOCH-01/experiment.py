"""Frozen WSCM-EPOCH-01 source-free, DEVELOPMENT-only native A/B/A test.

No protected-world outcomes, regime labels passed to models, model API calls,
accepted ref writes, scientific qualification, source-system execution or
additional actions beyond the paired, fixed synthetic outcomes.
"""
from __future__ import annotations

import argparse
import collections
from fractions import Fraction
from hashlib import sha1, sha256
import json
import math
from pathlib import Path
import random
import resource
import time

from yggdrasil.native_episode_experience import NativeEpisodeExperience
from yggdrasil.public_causal_cells import PublicCausalCells

PREREG_COMMIT = "c8dbfb5156e3ebe2878bf518806579c311df9467"
PREREG_BLOB = "55dbc55bf9722d02bb1f5adfea537d47e055bb15"
PARENT = "86264b41a08d49f558418c0fba367f3a2636befa"
ARTIFACT_SHA = "576370a1963158f7dc43099360f491eb6a1e49355448922943b6bde374d484c8"
ORIGINAL_NATIVE_BLOB = "5a18b00a4c4131526e71f51d63dfd9eb9471c81e"
SEEDS = {"B": (92011, 92023, 92041), "C": (93011, 93023, 93041)}
A_LAW = ((5, 27), (7, 25))
B_LAW = ((27, 5), (7, 25))
C_LAW = ((5, 27), (25, 7))
STAGES = (("A_warm", 0, 16), ("changed", 16, 64), ("A_return", 64, 112))
ARMS = ("epoch", "frozen", "continuing", "fit_full", "trailing32", "bocpd32", "bayes2")


def git_blob(raw: bytes) -> str:
    return sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("ascii")


def _bit(value):
    if type(value) is not int or value not in (0, 1):
        raise ValueError("EPOCH_BIT")
    return value


def load_original(joint_path: Path) -> NativeEpisodeExperience:
    raw = joint_path.read_bytes()
    if sha256(raw).hexdigest() != ARTIFACT_SHA:
        raise ValueError("EPOCH_ARCHIVE_IDENTITY")
    d = json.loads(raw)
    native = d["native_ascii"].encode("ascii")
    checkpoint = json.loads(native)["experience_ascii"].encode("ascii")
    restored = NativeEpisodeExperience.restore(checkpoint, sha256(checkpoint).hexdigest())
    if len(restored._ledger) != 1025 or restored._projection != 0 or restored._episode_limit < 1137:
        raise ValueError("EPOCH_NATIVE_CONTRACT")
    if restored.checkpoint() != checkpoint:
        raise ValueError("EPOCH_NATIVE_COLD_DRIFT")
    return restored


def archived_events(native):
    """Only publicly witnessed (context, first action, transition) from ledger."""
    out = []
    for identifier, views, first, state, second, reward in native._ledger:
        c = native._context(views)
        if c is not None:
            out.append((c, first, state))
    return out


def new_outcomes(seed: int, changed: str):
    """Only this fixture function may access the B/C label and causal law."""
    rng = random.Random(seed)
    chosen = B_LAW if changed == "B" else C_LAW if changed == "C" else None
    if chosen is None or seed not in SEEDS[changed]:
        raise ValueError("EPOCH_SEED_OR_REGIME")
    for i in range(112):
        ctx = (i // 2) % 2
        action = i % 2
        second = (i // 4) % 2
        law = A_LAW if i < 16 or i >= 64 else chosen
        state = int(rng.randrange(32) < law[ctx][action])
        reward = rng.getrandbits(1)
        event_id = sha256(f"WSCM-EPOCH-01|{changed}|{seed}|{i}".encode("ascii")).hexdigest()
        yield {"index": i, "context": ctx, "action": action, "second": second,
               "outcome": state, "reward": reward, "event_id": event_id}


def beta_from_counts(counts):
    failures, successes = counts
    return (successes + 1) / (failures + successes + 2)


class CumulativeBeta:
    def __init__(self, history):
        self.counts = [[[0, 0] for _ in (0, 1)] for _ in (0, 1)]
        for c, a, y in history:
            self.observe(c, a, y)

    def predict(self, c, a):
        return beta_from_counts(self.counts[c][a])

    def observe(self, c, a, y):
        self.counts[c][a][y] += 1


class TrailingBeta:
    def __init__(self, history):
        self.events = collections.deque(history[-32:], maxlen=32)

    def predict(self, c, a):
        matched = [y for cc, aa, y in self.events if (cc, aa) == (c, a)]
        return (sum(matched) + 1) / (len(matched) + 2)

    def observe(self, c, a, y):
        self.events.append((c, a, y))


class BayesianChangePoint32:
    """Conventional hazard-weighted Beta/Bernoulli run-length model, fixed cap."""

    def __init__(self, history):
        self.events = collections.deque(history[-32:], maxlen=32)

    @staticmethod
    def log_marginal(segment):
        counts = [[0, 0] for _ in range(4)]
        for c, a, y in segment:
            counts[c * 2 + a][y] += 1
        return sum(math.lgamma(f + 1) + math.lgamma(s + 1) - math.lgamma(f + s + 2)
                   for f, s in counts)

    def predict(self, c, a):
        history = list(self.events)
        kmax = len(history)
        predictions, logs = [], []
        for run in range(kmax + 1):
            suffix = history[-run:] if run else []
            fs = [0, 0]
            for cc, aa, y in suffix:
                if cc == c and aa == a:
                    fs[y] += 1
            predictions.append(beta_from_counts(fs))
            # A Bayesian hazard prior for a change at each candidate run length.
            # Segment likelihood is integrated under independent Beta(1,1) priors.
            logs.append(math.log(1 / 32) + run * math.log(31 / 32)
                        + self.log_marginal(suffix))
        shift = max(logs)
        weights = [math.exp(v - shift) for v in logs]
        return sum(p * w for p, w in zip(predictions, weights)) / sum(weights)

    def observe(self, c, a, y):
        self.events.append((c, a, y))


class EpochMemory:
    """Public-context-local, fixed 2-epoch candidate; archived A never updated."""

    def __init__(self, old_prediction, *, probabilistic=False):
        self.old = tuple(tuple(float(old_prediction(c, a)) for a in (0, 1)) for c in (0, 1))
        self.alternate = PublicCausalCells()
        self.activated = [False, False]
        self.surprises = [collections.deque(maxlen=4) for _ in (0, 1)]
        self.paired = [collections.deque(maxlen=8) for _ in (0, 1)]
        self.activation_count = 0
        self.mode_switch_count = 0
        self.using_alternate = [False, False]
        self.probabilistic = probabilistic
        self.observations = 0

    def _alternate_p(self, c, a):
        return float(Fraction(*self.alternate.outcome_probability(c, a)))

    def _weight(self, c):
        if not self.activated[c] or len(self.paired[c]) < 4:
            return 0.0
        pairs = list(self.paired[c])[-8:]
        if self.probabilistic:
            # Conventional equal-prior Bayesian likelihood ratio over
            # prequential evidence, with numerical clipping to avoid overflow.
            delta = sum(y - x for x, y in pairs)
            return 1 / (1 + math.exp(max(-40, min(40, 8 * delta))))
        return float(sum(a - b for a, b in pairs) / len(pairs) >= .01)

    def predict(self, c, a):
        p_old, p_alt = self.old[c][a], self._alternate_p(c, a)
        w = self._weight(c)
        if self.probabilistic:
            return p_old * (1 - w) + p_alt * w
        return p_alt if w >= 0.5 else p_old

    def observe(self, c, a, y):
        old_p = self.old[c][a]
        alt_p = self._alternate_p(c, a)
        w = self._weight(c)
        selected = w >= .5
        if self.activated[c]:
            self.paired[c].append(((old_p - y) ** 2, (alt_p - y) ** 2))
            if selected != self.using_alternate[c]:
                self.mode_switch_count += 1
            self.using_alternate[c] = selected
            if selected:
                self.alternate.observe(c, a, y)
        else:
            true_prob = old_p if y else 1 - old_p
            self.surprises[c].append(true_prob < .25)
            if len(self.surprises[c]) == 4 and sum(self.surprises[c]) >= 3:
                self.activated[c] = True
                self.activation_count += 1
                self.paired[c].clear()
        self.observations += 1

    def snapshot(self) -> bytes:
        return canonical({"old": self.old, "alternate": self.alternate.snapshot().hex(),
                          "activated": self.activated,
                          "surprises": [list(x) for x in self.surprises],
                          "paired": [list(x) for x in self.paired],
                          "using_alternate": self.using_alternate,
                          "activation_count": self.activation_count,
                          "mode_switch_count": self.mode_switch_count,
                          "probabilistic": self.probabilistic,
                          "observations": self.observations})

    @classmethod
    def restore(cls, data: bytes):
        record = json.loads(data)
        obj = cls(lambda c, a: record["old"][c][a],
                  probabilistic=record["probabilistic"])
        obj.alternate = PublicCausalCells.restore(bytes.fromhex(record["alternate"]))
        obj.activated = list(record["activated"])
        obj.surprises = [collections.deque(x, maxlen=4) for x in record["surprises"]]
        obj.paired = [collections.deque((tuple(p) for p in x), maxlen=8)
                      for x in record["paired"]]
        obj.using_alternate = list(record["using_alternate"])
        obj.activation_count = record["activation_count"]
        obj.mode_switch_count = record["mode_switch_count"]
        obj.observations = record["observations"]
        if obj.snapshot() != data:
            raise ValueError("EPOCH_MEMORY_COLD_DRIFT")
        return obj


def run_seed(original, seed, altered):
    # Each model gets the same previous archived evidence and paired public outcomes.
    x = NativeEpisodeExperience.restore(original.checkpoint(),
                                        sha256(original.checkpoint()).hexdigest())
    initial = archived_events(original)
    frozen = lambda c, a: float(original.context_forecast((c, 0), a))
    fitted = CumulativeBeta(initial)
    trailing = TrailingBeta(initial)
    cp = BayesianChangePoint32(initial)
    candidate = EpochMemory(frozen)
    bayes2 = EpochMemory(frozen, probabilistic=True)
    sums = {stage: {name: 0.0 for name in ARMS} for stage, _, _ in STAGES}
    stage_count = collections.Counter()
    stage_trigger = {stage: 0 for stage, _, _ in STAGES}
    native_snapshots = []
    old_snap = original.checkpoint()
    fixture = list(new_outcomes(seed, altered))
    # Check labels are not present inside the learner inputs.
    if len(fixture) != 112 or any("stage" in x or "regime" in x for x in fixture):
        raise ValueError("EPOCH_GENERATOR_CONTRACT")
    for event in fixture:
        i, c, a, outcome = (event[k] for k in ("index", "context", "action", "outcome"))
        stage = "A_warm" if i < 16 else "changed" if i < 64 else "A_return"
        predictions = {
            "epoch": candidate.predict(c, a),
            "frozen": frozen(c, a),
            "continuing": float(x.context_forecast((c, 0), a)),
            "fit_full": fitted.predict(c, a),
            "trailing32": trailing.predict(c, a),
            "bocpd32": cp.predict(c, a),
            "bayes2": bayes2.predict(c, a),
        }
        for name, p in predictions.items():
            if not 0 <= p <= 1:
                raise ValueError("EPOCH_FORECAST_RANGE")
            sums[stage][name] += (p - outcome) ** 2
        stage_count[stage] += 1
        # All arms see the same revealed result after prequential prediction.
        before_activations = candidate.activation_count
        candidate.observe(c, a, outcome)
        stage_trigger[stage] += candidate.activation_count - before_activations
        bayes2.observe(c, a, outcome)
        fitted.observe(c, a, outcome)
        trailing.observe(c, a, outcome)
        cp.observe(c, a, outcome)
        row = {"s1": c, "x1": a, "s2": outcome,
               "x2": event["second"], "y": event["reward"]}
        x = x.observe(event["event_id"], ((c, 0), (c, 1)), row)
        if i in (15, 63, 111):
            before = x.checkpoint()
            x = NativeEpisodeExperience.restore(before, sha256(before).hexdigest())
            if x.checkpoint() != before:
                raise ValueError("EPOCH_NATIVE_RESTORE_MISMATCH")
            shadow_before = candidate.snapshot()
            candidate = EpochMemory.restore(shadow_before)
            if candidate.snapshot() != shadow_before:
                raise ValueError("EPOCH_SHADOW_RESTORE_MISMATCH")
            b_before = bayes2.snapshot()
            bayes2 = EpochMemory.restore(b_before)
            if bayes2.snapshot() != b_before:
                raise ValueError("EPOCH_BAYES_RESTORE_MISMATCH")
            native_snapshots.append({"after_event": i, "native_sha256": sha256(before).hexdigest(),
                                     "shadow_sha256": sha256(shadow_before).hexdigest()})
    if original.checkpoint() != old_snap:
        raise ValueError("EPOCH_ORIGINAL_ANCHOR_MUTATED")
    stage_scores = {stage:{n: round(v / stage_count[stage], 9) for n, v in scores.items()}
                    for stage, scores in sums.items()}
    return {"seed": seed, "altered": altered,
            "source_outcomes_sha256": sha256(canonical(fixture)).hexdigest(),
            "episodes": len(fixture), "transition_brier": stage_scores,
            "activations": candidate.activation_count,
            "stage_activations": stage_trigger,
            "mode_switches": candidate.mode_switch_count,
            "alternate_active_end": candidate.using_alternate,
            "stage_end_checkpoints": native_snapshots,
            "epoch_state_bytes": len(candidate.snapshot())}


def run(joint: Path, prereg: Path):
    prereg_bytes = prereg.read_bytes()
    if git_blob(prereg_bytes) != PREREG_BLOB:
        raise ValueError("EPOCH_PREREG_BLOB_DRIFT")
    native_source = Path(NativeEpisodeExperience.__module__.replace(".", "/") + ".py")
    # Verify the original pinned source file when invoked from repository root;
    # the minimal dependency shims are explicitly documented, not certified.
    if native_source.exists() and git_blob(native_source.read_bytes()) != ORIGINAL_NATIVE_BLOB:
        raise ValueError("EPOCH_NATIVE_GIT_BLOB_DRIFT")
    t0 = time.perf_counter()
    original = load_original(joint)
    inputs = []
    for altered, seeds in SEEDS.items():
        for seed in seeds:
            inputs.append(run_seed(original, seed, altered))
    means = {}
    for altered in SEEDS:
        subset = [x for x in inputs if x["altered"] == altered]
        means[altered] = {stage:{arm:round(sum(x["transition_brier"][stage][arm] for x in subset) / len(subset),9)
                                for arm in ARMS} for stage,_,_ in STAGES}
    # Compare only to the strongest equal-information control, even when that
    # control is selected post hoc. This is deliberately conservative for GO.
    controls = ("frozen", "continuing", "fit_full", "trailing32", "bocpd32", "bayes2")
    margins = {a:{stage:round(means[a][stage]["epoch"] - min(means[a][stage][c] for c in controls),9)
                  for stage,_,_ in STAGES} for a in SEEDS}
    no_spurious = all(x["stage_activations"]["A_warm"] == 0 for x in inputs)
    # Use the frozen stringent gate; per-seed return must also satisfy bound.
    all_seed_return = all(x["transition_brier"]["A_return"]["epoch"] <=
                          x["transition_brier"]["A_return"]["frozen"] + .01
                          for x in inputs)
    all_changed = all(x["transition_brier"]["changed"]["epoch"] <=
                      min(x["transition_brier"]["changed"][c] for c in controls) - .005
                      for x in inputs)
    candidate_promising = all_seed_return and all_changed and no_spurious
    return {"schema":"yggdrasil.wscm.epoch01.source-free-dev.v1",
            "preregistration_commit": PREREG_COMMIT, "preregistration_git_blob":PREREG_BLOB,
            "source_original_amalgam":PARENT, "joint_artifact_sha256":ARTIFACT_SHA,
            "scope":"single preregistered source-free development pass; not original-world science",
            "classification":"DEV_PROMISING_ONLY" if candidate_promising else "DEV_NO_GO",
            "scientific_gain_verified":False, "new_protected_world_actions":0,
            "synthetic_public_observations":sum(x["episodes"] for x in inputs),
            "per_seed":inputs,"scenario_mean":means,
            "candidate_minus_best_control":margins,
            "all_seed_return_pass":all_seed_return,
            "all_seed_changed_pass":all_changed,
            "no_spurious_A_warm_activations":no_spurious,
            "wall_seconds":round(time.perf_counter()-t0,6),
            "peak_rss_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--joint",type=Path,required=True)
    parser.add_argument("--prereg",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    opts=parser.parse_args()
    result=run(opts.joint,opts.prereg)
    opts.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(result["classification"],"synthetic_outcomes",result["synthetic_public_observations"],
          "wall_seconds",result["wall_seconds"])


if __name__=="__main__":
    main()
