"""MH-01: source-free meta-selection of local Hebbian rules. NOT accepted science.

Uses unchanged unmerged ITD-01 R7 public generator, source and control. No
original-world first use, reward-free-within-lifetime claim, or promotion.
Run: python research/native/itd01/mh01/study.py
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
import pathlib
import subprocess
import sys
import time
from dataclasses import asdict, dataclass

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "r7"))
from native_cells import Colony, PublicDevGenerator  # noqa: E402

FIT = (181, 191, 193)
VALID = (197,)
HELD = (211, 223, 227)
CHECKPOINTS = (0, 8, 32, 64, 96)
LESION = (("A", 0), ("A", 2), ("B", 1))
EVAL_COUNT = 160


@dataclass(frozen=True)
class Genome:
    fast_gain: float
    decay: float
    slow_gain: float
    neighbor_gain: float


def genomes():
    return [Genome(*args) for args in itertools.product(
        (0.5, 1.0, 2.0, 4.0), (0.0, 0.01),
        (0.005, 0.02), (0.0, 0.03))]


class MetaColony(Colony):
    def __init__(self, genome: Genome):
        if genome not in genomes():
            raise ValueError("MH01_GENOME_OUT_OF_FROZEN_GRID")
        super().__init__()
        self.genome = genome

    def predict(self, context, sensors):
        self._validate(context, sensors)
        local = [cell.signal(sensors[i]) for i, cell in enumerate(self.cells[context])]
        gain = self.genome.neighbor_gain
        return sum(local[i] + gain * (local[(i - 1) % 4]
                       + local[(i + 1) % 4]) / 2 for i in range(4)) > 0

    def learn_completed_public_feedback(self, context, sensors, public_outcome, delay_steps):
        self._validate(context, sensors)
        if type(delay_steps) is not int or delay_steps < 2:
            raise ValueError("MH01_EARLY_FEEDBACK")
        if type(public_outcome) is not bool:
            raise ValueError("MH01_OUTCOME_INVALID")
        g = self.genome
        for bit, cell in zip(sensors, self.cells[context]):
            pre = 1 if bit else -1
            post = 1 if public_outcome else -1
            cell.fast = max(-512.0, min(512.0, (1.0 - g.decay) *
                                     cell.fast + g.fast_gain * pre * post))
            cell.slow = (1 - g.slow_gain) * cell.slow + g.slow_gain * cell.fast
            cell.updates += 1
        self.feedback_updates += 1
        self.neighbor_messages += 8

    def checkpoint(self) -> bytes:
        # Existing R7 checkpoint is unchanged; nest its signed canonical bytes.
        body = {"schema": "ygg.mh01.dev.v1",
                "genome": asdict(self.genome),
                "r7": super().checkpoint().decode("utf-8")}
        packed = json.dumps(body, sort_keys=True, separators=(",", ":"), allow_nan=False)
        outer = {"payload": body, "sha256": hashlib.sha256(packed.encode()).hexdigest()}
        result = json.dumps(outer, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
        if len(result) > 32768:
            raise ValueError("MH01_MODEL_MEMORY_CAP_EXCEEDED")
        return result

    @classmethod
    def restore(cls, raw: bytes):
        if type(raw) is not bytes or len(raw) > 32768 or not raw:
            raise ValueError("MH01_INVALID_CHECKPOINT")
        try:
            envelope = json.loads(raw)
            if type(envelope) is not dict or set(envelope) != {"payload", "sha256"}:
                raise ValueError("MH01_INVALID_ENVELOPE")
            body = envelope["payload"]
            if type(body) is not dict or set(body) != {"schema", "genome", "r7"}:
                raise ValueError("MH01_INVALID_PAYLOAD")
            expected = hashlib.sha256(json.dumps(body, sort_keys=True,
                        separators=(",", ":"), allow_nan=False).encode()).hexdigest()
            if envelope["sha256"] != expected or body["schema"] != "ygg.mh01.dev.v1":
                raise ValueError("MH01_CHECKPOINT_CORRUPT")
            if type(body["genome"]) is not dict or set(body["genome"]) != set(asdict(genomes()[0])):
                raise ValueError("MH01_GENOME_FIELDS")
            genome = Genome(**body["genome"])
            restored = Colony.restore(body["r7"].encode("utf-8"))
        except (KeyError, TypeError, UnicodeError, AttributeError, json.JSONDecodeError,
                OverflowError, ValueError) as exc:
            raise ValueError("MH01_RESTORE_REJECTED") from exc
        model = cls(genome)
        model.cells = restored.cells
        model.feedback_updates = restored.feedback_updates
        model.neighbor_messages = restored.neighbor_messages
        return model


class LogisticControl:
    """Matched 8 learned parameters, completed-public-feedback online SGD."""
    def __init__(self):
        self.weights = {"A": [0.0] * 4, "B": [0.0] * 4}
        self.feedback_updates = 0

    def predict(self, context, sensors):
        return sum((1 if b else -1) * w for b, w in
                   zip(sensors, self.weights[context])) > 0

    def learn_completed_public_feedback(self, context, sensors, outcome, delay_steps):
        if context not in ("A", "B") or type(sensors) not in (tuple, list) or len(sensors) != 4 or any(type(b) is not bool for b in sensors) or type(outcome) is not bool or type(delay_steps) is not int or delay_steps < 2:
            raise ValueError("MH01_BAD_PUBLIC_FEEDBACK")
        x = [1 if b else -1 for b in sensors]
        z = max(-24., min(24., sum(w * xi for w, xi in zip(self.weights[context], x))))
        error = (1. if outcome else 0.) - 1. / (1. + math.exp(-z))
        self.weights[context] = [max(-512., min(512., w + .2 * error * xi))
                                 for w, xi in zip(self.weights[context], x)]
        self.feedback_updates += 1


def lesion(model):
    # Same named A0/A2/B1 weight coordinates in all arms; no saved-weight copy.
    for context, index in LESION:
        if isinstance(model, LogisticControl):
            model.weights[context][index] = 0.0
        else:
            model.cells[context][index].fast = 0
            model.cells[context][index].slow = 0.0


def examples(generator, context, count):
    return [(context, *generator.example(context)) for _ in range(count)]


def data(seed):
    generator = PublicDevGenerator(seed * 1009 + 17)
    train_a = examples(generator, "A", 240)
    before_a = examples(generator, "A", EVAL_COUNT)
    train_b = examples(generator, "B", 240)
    after_a = examples(generator, "A", EVAL_COUNT)
    after_b = examples(generator, "B", EVAL_COUNT)
    recovery = [(generator.example("A"), generator.example("B")) for _ in range(96)]
    held = {n: (examples(generator, "A", EVAL_COUNT),
                examples(generator, "B", EVAL_COUNT)) for n in CHECKPOINTS}
    return train_a, before_a, train_b, after_a, after_b, recovery, held


def accuracy(model, rows):
    return sum(model.predict(context, sensors) == outcome
               for context, sensors, outcome in rows) / len(rows)


def assess(model, dataset, flip_feedback=False, learn=True):
    train_a, before_a, train_b, after_a, after_b, recovery, held = dataset
    for context, sensor, outcome in train_a:
        if learn:
            model.learn_completed_public_feedback(context, sensor,
                                                  not outcome if flip_feedback else outcome, 2)
    early_a = accuracy(model, before_a)
    for context, sensor, outcome in train_b:
        if learn:
            model.learn_completed_public_feedback(context, sensor,
                                                  not outcome if flip_feedback else outcome, 2)
    after = [accuracy(model, after_a), accuracy(model, after_b)]
    lesion(model)
    scores = {}
    for n in range(97):
        if n in CHECKPOINTS:
            a, b = held[n]
            scores[n] = [accuracy(model, a), accuracy(model, b)]
        if n == 96:
            break
        for context, (sensor, outcome) in zip(("A", "B"), recovery[n]):
            if learn:
                model.learn_completed_public_feedback(context, sensor,
                                                      not outcome if flip_feedback else outcome, 2)
    return {"a_before_b": early_a, "a_after_b": after[0],
            "b_after_b": after[1], "damage_accuracy": scores,
            "postlesion_macro": sum(sum(scores[n]) / 2 for n in CHECKPOINTS[1:]) / 4,
            "recovery_by_96": next((n for n in CHECKPOINTS if n > 0
                                    and min(scores[n]) >= .75), None),
            "feedback_updates": model.feedback_updates}


def evaluate_genome(genome, datasets):
    return [assess(MetaColony(genome), data_row) for data_row in datasets]


def chosen_fitness(rows):
    return sum(row["postlesion_macro"] for row in rows) / len(rows)


def run():
    start = time.process_time()
    fit = [data(s) for s in FIT]
    baseline_start = time.process_time()
    fixed_fit = [assess(Colony(), d) for d in fit]
    fixed_reference_cpu = max(time.process_time() - baseline_start, 1e-9)
    search = []
    for genome in genomes():
        rows = evaluate_genome(genome, fit)
        search.append({"genome": asdict(genome), "fitness": chosen_fitness(rows)})
    # lexicographic ordering in genomes() wins exact ties
    winner_index = max(range(len(search)), key=lambda i: search[i]["fitness"])
    winner = genomes()[winner_index]
    outer_cpu = time.process_time() - start - fixed_reference_cpu
    cost_ratio = outer_cpu / fixed_reference_cpu
    cost_penalty = cost_ratio > 20.0
    validation = evaluate_genome(winner, [data(s) for s in VALID])
    held_data = [data(s) for s in HELD]
    models = {
        "evolved": lambda: MetaColony(winner),
        "r7_original": Colony,
        "fixed_genome": lambda: MetaColony(Genome(1.0, 0.0, 0.02, 0.03)),
        "online_logistic": LogisticControl,
        "no_learning_sham": Colony,
        "flipped_outcome_negative": lambda: MetaColony(winner),
    }
    evidence = {}
    for name, factory in models.items():
        evidence[name] = [assess(factory(), d,
                           flip_feedback=name == "flipped_outcome_negative",
                           learn=name != "no_learning_sham") for d in held_data]
    baseline = max(chosen_fitness(evidence[name]) for name in
                   ("r7_original", "fixed_genome", "online_logistic"))
    evolved = chosen_fitness(evidence["evolved"])
    restore_checks = []
    for d in held_data:
        m = MetaColony(winner)
        for context, sensor, outcome in d[0] + d[2]:
            m.learn_completed_public_feedback(context, sensor, outcome, 2)
        raw = m.checkpoint()
        cold = MetaColony.restore(raw)
        probes = d[3][:16] + d[4][:16]
        local_exact = all(m.predict(c, x) == cold.predict(c, x)
                          for c, x, _ in probes)
        request = {"snapshot": raw.decode("utf-8"),
                   "probes": [[c, list(x)] for c, x, _ in probes]}
        spawned = subprocess.run([sys.executable, "-B", __file__, "--cold-probe"],
                                 input=json.dumps(request), text=True,
                                 capture_output=True, timeout=20, check=True)
        independent = json.loads(spawned.stdout)
        cold_exact = independent == [m.predict(c, x) for c, x, _ in probes]
        restore_checks.append({"bytes": len(raw), "byte_exact": raw == cold.checkpoint(),
                               "predictions_exact": local_exact,
                               "independent_process_predictions_exact": cold_exact})
    retention = [z["a_before_b"] - z["a_after_b"] for z in evidence["evolved"]]
    success = (all(z["recovery_by_96"] is not None and
                   min(z["damage_accuracy"][96]) >= .75 for z in evidence["evolved"])
               and evolved >= baseline + .05
               and all(v <= .02 for v in retention)
               and all(z["byte_exact"] and z["predictions_exact"]
                       and z["independent_process_predictions_exact"]
                       and z["bytes"] <= 32768 for z in restore_checks)
               and not cost_penalty)
    report = {
        "schema": "ygg.mh01.source_free_dev.v1",
        "source_parent_sha": "f3cdabdb3420bb8604e41dda9903ae65eba008e7",
        "scientific_first_use": False, "accepted_model_mutation": False,
        "genome_count": len(search), "fit_seeds": FIT, "validation_seeds": VALID,
        "evaluation_seeds": HELD, "winner_index": winner_index,
        "winner": asdict(winner), "fit_search": search,
        "validation": validation, "held": evidence,
        "best_control_macro": baseline, "evolved_macro": evolved,
        "evolved_advantage": evolved - baseline, "a_retention_drops": retention,
        "restore_checks": restore_checks,
        "cpu_outer_search_seconds": round(outer_cpu, 6),
        "cpu_fixed_reference_fit_seconds": round(fixed_reference_cpu, 6),
        "cpu_all_stages_seconds": round(time.process_time() - start, 6),
        "peak_whole_process_rss": "UNVERIFIED",
        "cost_ratio_to_one_fixed_rule_run": round(cost_ratio, 3),
        "cost_penalty": cost_penalty,
        "development_mechanism": "DEV_MECHANISM_GO" if success
                                 else ("SCIENTIFIC_DEV_NO_GO_COST" if cost_penalty
                                       else "SCIENTIFIC_DEV_NO_GO"),
        "unfamiliar_family_transfer": "NOT_TESTED",
        "reward_free_lifetime_hebbian": False,
    }
    return report


if __name__ == "__main__":
    if sys.argv[1:] == ["--cold-probe"]:
        payload = json.loads(sys.stdin.read())
        colony = MetaColony.restore(payload["snapshot"].encode("utf-8"))
        probes = payload["probes"]
        print(json.dumps([colony.predict(ctx, tuple(bits)) for ctx, bits in probes]))
    elif len(sys.argv) == 1:
        print(json.dumps(run(), sort_keys=True, indent=2))
    else:
        raise SystemExit("MH01_UNKNOWN_ARGUMENTS")
