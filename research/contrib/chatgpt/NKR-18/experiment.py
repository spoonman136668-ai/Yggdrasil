"""NKR-18 frozen, reused-fixture knowledge acquisition and retention screen.

No original data access, scientific first-use or accepted-native activation.
The learner exports the existing affine weights, not a new architecture.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from yggdrasil.native_relation_memory import NativeRelationMemory, NativeRelationReadout
from yggdrasil.public_causal_cells import PublicCausalCells

SCALES = (2, 4, 8, 16)
COLD = (6, 7, 9, 11, 12, 13, 14, 15)
ARMS = ("native", "retrieval", "nearest_memory", "cart", "exact_symbolic")


def canonical(doc):
    return json.dumps(doc, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("ascii")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def reference():
    path = ROOT / "research/contrib/chatgpt/NKR-11/experiment.py"
    spec = importlib.util.spec_from_file_location("nkr18_unchanged_reference", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def address(slot):
    return (slot - 7, True) if slot >= 7 else (slot, False)


def predict_slot(model, slot, x, action):
    local, retained = address(slot)
    return model.predict(local, x, action, retained=retained)


def observe_slot(model, slot, row):
    ref, x, action, outcome = row
    local, retained = address(slot)
    return model.observe_public(local, x, action, outcome, ref,
                                retained=retained)


def raw_input(x, action):
    return x | (action << 4)


def fit_cart(rows, bits=tuple(range(5))):
    """Fully grown binary CART, exact Gini; zero-gain XOR splits are allowed."""
    ones = sum(y for _, _, _, y in rows)
    majority = int(ones * 2 > len(rows))
    if ones in (0, len(rows)) or not bits:
        return majority
    choices = []
    for bit in bits:
        groups = tuple([r for r in rows if (raw_input(r[1], r[2]) >> bit) & 1 == v]
                       for v in (0, 1))
        if any(not g for g in groups):
            continue
        loss = sum(Fraction(sum(r[3] for r in g) *
                            (len(g) - sum(r[3] for r in g)), len(g))
                   for g in groups)
        choices.append((loss, bit, groups))
    if not choices:
        return majority
    _, chosen, groups = min(choices, key=lambda item: (item[0], item[1]))
    remaining = tuple(b for b in bits if b != chosen)
    return chosen, fit_cart(groups[0], remaining), fit_cart(groups[1], remaining)


def predict_cart(tree, x, action):
    value = raw_input(x, action)
    while type(tree) is tuple:
        bit, left, right = tree
        tree = right if value & (1 << bit) else left
    return tree


def nearest(rows, x, action):
    target = raw_input(x, action)
    return min(enumerate(rows), key=lambda item: (
        (raw_input(item[1][1], item[1][2]) ^ target).bit_count(), item[0]))[1][3]


def isolated_inference(readout, queries):
    """A fresh process gets compact bytes+inputs, never training/source labels."""
    code = '''import json, sys
from yggdrasil.native_relation_memory import NativeRelationReadout
p=json.load(sys.stdin)
r=NativeRelationReadout(bytes.fromhex(p['checkpoint_hex']),p['sha256'])
out=[]
for slot,x,a in p['queries']:
    out.append(r.predict(slot-7 if slot>=7 else slot,x,a,retained=slot>=7))
assert not any(k in sys.modules for k in ('nkr18_unchanged_reference',))
print(json.dumps(out,separators=(',',':')))
'''
    payload = {"checkpoint_hex": readout.checkpoint().hex(),
               "sha256": readout.checkpoint_sha256, "queries": queries}
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONPATH=str(ROOT),
               PYTHONHASHSEED="0")
    result = subprocess.run([sys.executable, "-B", "-c", code],
                            input=canonical(payload), capture_output=True,
                            cwd=ROOT.parent, env=env, timeout=30, check=True)
    return json.loads(result.stdout)


def metric(predictions, truth):
    return {"correct": sum(p is not None and p == y for p, y in zip(predictions, truth)),
            "covered": sum(p is not None for p in predictions),
            "wrong": sum(p is not None and p != y for p, y in zip(predictions, truth)),
            "abstained": sum(p is None for p in predictions), "queries": len(truth)}


def run_frozen():
    started = time.monotonic()
    ref = reference()
    legacy_before = PublicCausalCells().snapshot()
    # Immutable, already consumed computational source, collected once, not
    # rescanned per control/scale. Cold targets remain evaluator-only.
    train = [ref.collect_paired_interventions(ref.ComputationalEnvironment(w))
             for w in range(12)]
    later = [ref.collect_warmup(ref.ComputationalEnvironment(w)) for w in range(4)]
    source_sha = digest(canonical({"train": train, "later": later}))
    cold_queries = [(w, x, a) for w in range(12) for x in COLD for a in (0, 1)]
    all_queries = [(w, x, a) for w in range(12) for x in range(16) for a in (0, 1)]
    scales, trace = [], []
    for scale in SCALES:
        bank = NativeRelationMemory()
        controls, training_seconds = {}, {a: 0.0 for a in ARMS}
        unseen_milestones = []
        for world in range(12):
            rows = train[world][:scale]
            presentations = [rows[i % scale] for i in range(16)]
            t = time.monotonic()
            for row in presentations:
                observe_slot(bank, world, row)
            training_seconds["native"] += time.monotonic() - t
            t = time.monotonic()
            retrieval = {(x, a): y for _, x, a, y in presentations}
            training_seconds["retrieval"] += time.monotonic() - t
            t = time.monotonic()
            memory = tuple(presentations)
            training_seconds["nearest_memory"] += time.monotonic() - t
            t = time.monotonic()
            tree = fit_cart(presentations)
            training_seconds["cart"] += time.monotonic() - t
            if any(predict_cart(tree, x, a) != y for _, x, a, y in presentations):
                raise AssertionError("NKR18_CART_NOT_FULLY_TRAINED")
            t = time.monotonic()
            symbolic = ref.independent_symbolic_fit(presentations)
            training_seconds["exact_symbolic"] += time.monotonic() - t
            controls[world] = (retrieval, memory, tree, symbolic)
            if scale == 16 and world + 1 in (1, 4, 8, 12):
                query = [(s, x, a) for s in range(12, 16)
                         for x in range(16) for a in (0, 1)]
                unseen_milestones.append({"learned_worlds": world + 1,
                                          "unknown_queries": len(query),
                                          "covered": sum(predict_slot(bank, *q) is not None
                                                         for q in query)})
        before_bytes = bank.checkpoint()
        if bank.unique_observations != scale * 12:
            raise AssertionError("NKR18_DUPLICATES_COUNTED_AS_KNOWLEDGE")
        full_cold = NativeRelationMemory.restore(before_bytes)
        compact = bank.compact_inference()
        compact_cold = NativeRelationReadout(compact.checkpoint(), compact.checkpoint_sha256)
        before = [predict_slot(bank, *q) for q in all_queries]
        subprocess_values = isolated_inference(compact_cold, all_queries)
        if (subprocess_values != before
                or [predict_slot(full_cold, *q) for q in all_queries] != before):
            raise AssertionError("NKR18_NO_OBSERVATION_FREE_COLD_PARITY")
        predictions = {a: [] for a in ARMS}
        inference_seconds = {a: 0.0 for a in ARMS}
        for world, x, action in cold_queries:
            retrieval, memory, tree, symbolic = controls[world]
            functions = {
                "native": lambda: predict_slot(compact_cold, world, x, action),
                "retrieval": lambda: retrieval.get((x, action)),
                "nearest_memory": lambda: nearest(memory, x, action),
                "cart": lambda: predict_cart(tree, x, action),
                "exact_symbolic": lambda: ref.independent_symbolic_predict(symbolic, x, action),
            }
            for arm in ARMS:
                t = time.monotonic()
                predictions[arm].append(functions[arm]())
                inference_seconds[arm] += time.monotonic() - t
        if predictions["native"] != predictions["exact_symbolic"]:
            raise AssertionError("NKR18_STRONG_SYMBOLIC_CONTROL_DISAGREES")
        # All fit/export/inference completed before evaluator-only truth read.
        truth = [ref.ComputationalEnvironment(w).intervene(x, a)
                 for w, x, a in cold_queries]
        scores = {a: metric(predictions[a], truth) for a in ARMS}
        if scores["native"]["wrong"]:
            raise AssertionError("NKR18_AFFINE_IDENTIFIABILITY_INCORRECT")
        all_truth = [ref.ComputationalEnvironment(w).intervene(x, a)
                     for w, x, a in all_queries]
        pre_metric = metric(before, all_truth)
        # Sequential accumulation in the SAME bank, not a frozen old-bank copy.
        for offset in range(4):
            for row in later[offset]:
                observe_slot(bank, offset + 12, row)
        after_training = bank.checkpoint()
        after_bank = NativeRelationMemory.restore(after_training)
        after_compact = after_bank.compact_inference()
        after = isolated_inference(after_compact, all_queries)
        if before != after or bank.unique_observations != scale * 12 + 128:
            raise AssertionError("NKR18_LATER_SLOT_INTERFERENCE_OR_COUNT")
        conflicts = 0
        for world in range(12):
            source, x, a, y = train[world][0]
            try:
                observe_slot(bank, world, (source + "-conflict", x, a, 1 - y))
            except ValueError as exc:
                if str(exc) != "NATIVE_RELATION_CONFLICTING_DUPLICATE":
                    raise
                conflicts += 1
        if conflicts != 12 or bank.checkpoint() != after_training:
            raise AssertionError("NKR18_CONFLICT_OVERWROTE_OLD_KNOWLEDGE")
        ablation = None
        if scale == 16:
            doc = json.loads(compact.checkpoint())
            doc["weights_float32_le"] = ["0" * 80] * 16
            raw = canonical(doc)
            lesioned = NativeRelationReadout(raw, digest(raw))
            ablated = [predict_slot(lesioned, *q) for q in cold_queries]
            ablation = dict(metric(ablated, truth),
                            predictions_changed=sum(p != q for p, q in
                                                    zip(ablated, predictions["native"])))
        row = {
            "distinct_per_world": scale, "native_unique_before": scale * 12,
            "native_unique_after": bank.unique_observations,
            "presentations_per_arm": 192,
            "coefficient_capacity": 160,
            "ranks": [bank.rank(*address(w)[:1], retained=address(w)[1])
                      for w in range(12)],
            "cold": scores,
            "training_checkpoint_bytes": len(before_bytes),
            "compact_checkpoint_bytes": len(compact.checkpoint()),
            "compact_sha256": compact.checkpoint_sha256,
            "compact_parent_sha256": compact.training_checkpoint_sha256,
            "cold_full_and_record_free_parity": True,
            "retention": {"identical_predictions": sum(p == q for p, q in zip(before, after)),
                          "all_predictions": 384,
                          "correct_before": pre_metric["correct"],
                          "correct_after": metric(after, all_truth)["correct"],
                          "later_unique_observations": 128,
                          "conflicts_rejected": conflicts,
                          "same_slot_drift_learning": False},
            "unknown_address_milestones": unseen_milestones,
            "zero_coefficient_ablation": ablation,
            "training_seconds": training_seconds,
            "inference_seconds": inference_seconds,
        }
        scales.append(row)
        trace.append({"scale": scale, "predictions": predictions,
                      "retained_before": before, "retained_after": after})
    if PublicCausalCells().snapshot() != legacy_before:
        raise AssertionError("NKR18_LEGACY_OWNER_MUTATION")
    first, last = scales[0]["cold"]["native"], scales[-1]["cold"]["native"]
    gain = last["correct"] - first["correct"]
    supported = last["correct"] >= 173 and gain >= 38 and last["wrong"] == 0
    result = {
        "schema": "yggdrasil.nkr18.knowledge-acquisition-retention.result.v1",
        "classification": ("SUPPORTED_BOUNDED_KNOWLEDGE_DEVELOPMENT" if supported
                           else "NEGATIVE_BOUNDED_KNOWLEDGE_DEVELOPMENT"),
        "engineering_contract_pass": True, "scientific_pass": False,
        "accepted_native": False, "original_science_first_uses": 0,
        "source_sha256": source_sha,
        "distinct_training_source_outcomes": 192,
        "distinct_later_learning_source_outcomes": 128,
        "total_training_presentations_per_arm_across_scales": 768,
        "gain_scale16_vs_scale2_correct": gain,
        "strong_symbolic_gain_correct": last["correct"] - scales[-1]["cold"]["exact_symbolic"]["correct"],
        "prediction_trace_sha256": digest(canonical(trace)),
        "scales": scales,
        "wall_seconds": time.monotonic() - started,
    }
    if result["wall_seconds"] > 120:
        raise RuntimeError("NKR18_FROZEN_WALL_BUDGET_EXCEEDED")
    return result


def stable_result(result):
    # Times are observations, never semantic identities across platforms.
    doc = json.loads(json.dumps(result))
    doc.pop("wall_seconds")
    for scale in doc["scales"]:
        scale.pop("training_seconds")
        scale.pop("inference_seconds")
    return doc


if __name__ == "__main__":
    actual = run_frozen()
    if len(sys.argv) == 3 and sys.argv[1] == "--verify":
        expected = json.loads(Path(sys.argv[2]).read_text())
        if stable_result(actual) != stable_result(expected):
            raise AssertionError("NKR18_CROSS_PLATFORM_FROZEN_RESULT_DRIFT")
    print("NKR18_FROZEN_KNOWLEDGE=" + json.dumps(actual, sort_keys=True), flush=True)
