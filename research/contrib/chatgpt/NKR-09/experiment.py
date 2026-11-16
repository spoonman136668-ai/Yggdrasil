"""NKR-09: deterministic source-safe rule-induction and microfeedback study.

All target labels are synthetic engineering fixtures. The cold test truth is
kept OUT of the NKR-08 observation ledger and NKR-09 feedback. The exact
symbolic rule learner sees identical training and first eight feedback labels.
No independent scientific first-use or real action/causal observations.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from yggdrasil.native_cumulative_facts import (
    BUNDLE_SCHEMA, CumulativeNativeFacts, canonical, digest,
    PINNED_MANIFEST_SHA, PINNED_TRAIN_SHA)
from yggdrasil.native_knowledge_activation import NativeKnowledgeSession
from yggdrasil.native_relation_discovery import (
    FEEDBACK_SCHEMA, NativeRelationDiscovery, FEEDBACK_WEIGHT)
from yggdrasil.public_causal_cells import PublicCausalCells


class EmptySymbolicBase:
    """Harness-only fake: explicitly NO original historical source opened."""
    def has_fact(self, s, p, o):
        return False

    def objects(self, s, p, *, limit=64, after=0):
        return []

    def close(self):
        pass


def world():
    """Freeze Q/P/Q source, transfers, shift labels and unrelated controls."""
    edges = []
    truth = {}
    for s in range(1, 65):
        a, b = 20000 + s, 40000 + s
        edges.extend((
            (s, 11, 10000 + s), (10000 + s, 12, a),
            (s, 13, 30000 + s), (30000 + s, 14, b)))
        if s <= 32:
            edges.append((s, 15, a if s <= 24 else b))
            edges.append((s, 16, b if s <= 24 else a))
            edges.append((s, 29, 50000 + s))  # unreachable decoy
        elif s <= 40:
            truth[(s, 15)] = b           # explicit feedback after predictions
        elif s <= 52:
            truth[(s, 15)] = b if s <= 49 else a
        else:
            truth[(s, 16)] = b if s <= 61 else a
    return tuple(sorted(set(edges))), truth


def staged_fixture():
    edges, truth = world()
    base = NativeKnowledgeSession(EmptySymbolicBase(), {
        "schema": "yggdrasil.nkr06.offline-factual-activation.v1",
        "image_manifest_sha256": PINNED_MANIFEST_SHA,
        "source_train_sha256": PINNED_TRAIN_SHA,
        "native_accepted": False,
    })
    records = [[*row, f"synthetic-row-{i:04d}"]
               for i, row in enumerate(edges)]
    raw = canonical({
        "schema": BUNDLE_SCHEMA,
        "source_id": "nkr09-synthetic-only-induction-world",
        "source_kind": "direct_public_observation",
        "source_mode": "engineering_fixture_only",
        "records": records})
    initial = CumulativeNativeFacts(base)
    candidate, receipt = initial.stage(raw, digest(raw))
    if receipt["new_unique_facts"] != len(edges):
        raise AssertionError("NKR09_FIXTURE_INGESTION_INCOMPLETE")
    return candidate, edges, truth


def microfeedback(truth):
    # Feedback subjects are 33..40 only, target p15. The future 41..64
    # outcomes are NEVER ingested as evidence.
    rows = [[s, 15, truth[(s, 15)], f"public-target-{s:04d}"]
            for s in range(33, 41)]
    return canonical({
        "schema": FEEDBACK_SCHEMA,
        "source_id": "nkr09-8-synthetic-outcomes-only",
        "source_kind": "public_target_outcome",
        "source_mode": "engineering_fixture_only",
        "records": rows})


def symbolic_rule_scores(edges):
    """Independent literal Counter/set control: no NKR-09 mining calls."""
    adjacency = defaultdict(set)
    direct = defaultdict(set)
    for x, p, y in edges:
        adjacency[x].add((p, y))
        direct[(x, y)].add(p)
    matched = defaultdict(set)
    for x, p1, y in edges:
        for p2, z in adjacency.get(y, ()):
            for p3 in direct.get((x, z), ()):
                if p3 not in (p1, p2):
                    matched[(p3, p1, p2)].add(x)
    return {key: len(xs) for key, xs in matched.items() if len(xs) >= 6}


def symbolic_prediction(edges, p3, subject, support, feedback=()):
    """Same information, fully fitted explicit symbolic template baseline."""
    outgoing = defaultdict(set)
    for x, p, o in edges:
        outgoing[(x, p)].add(o)
    scores = {}
    for (target, p1, p2), initial in support.items():
        if target != p3:
            continue
        for mid in outgoing[(subject, p1)]:
            for obj in outgoing[(mid, p2)]:
                good = bad = 0
                for q, rel, truth in feedback:
                    if rel != p3:
                        continue
                    answers = set()
                    for other in outgoing[(q, p1)]:
                        answers.update(outgoing[(other, p2)])
                    if truth in answers:
                        good += 1
                    else:
                        bad += 1
                value = initial + FEEDBACK_WEIGHT * (good - bad)
                scores[obj] = max(scores.get(obj, -10**9), value)
    return min(scores, key=lambda obj: (-scores[obj], obj)) if scores else None


def run_frozen():
    started = time.monotonic()
    native_before = PublicCausalCells().snapshot()
    facts, edges, truths = staged_fixture()
    initial = NativeRelationDiscovery(facts)
    sources = sorted((entry["target_relation"], entry["first_relation"],
                      entry["second_relation"], entry["training_support"])
                     for entry in initial.rules())
    expected = sorted([(15, 11, 12, 24), (15, 13, 14, 8),
                       (16, 11, 12, 8), (16, 13, 14, 24)])
    if sources != expected:
        raise AssertionError("NKR09_RULE_MINING_FAIL")
    frozen = {s: initial.predict(s, 15)["proposals"][0]["object_q"]
              for s in range(41, 53)}
    pre_feedback = [initial.predict(s, 15) for s in range(33, 41)]
    if any(not x["proposals"] for x in pre_feedback):
        raise AssertionError("NKR09_FEEDBACK_PROPOSAL_MISSING")
    baseline = facts.checkpoint()
    raw = microfeedback(truths)
    adapted, receipt = initial.stage_feedback(raw, digest(raw))
    if receipt["new_feedback"] != 8 or receipt["native_accepted"]:
        raise AssertionError("NKR09_FEEDBACK_CUSTODY_FAILURE")
    if facts.checkpoint() != baseline or initial.checkpoint() == adapted.checkpoint():
        raise AssertionError("NKR09_BASE_OR_INITIAL_MUTATED")
    cold = NativeRelationDiscovery(facts, adapted.checkpoint(),
                                   checkpoint_sha256=adapted.checkpoint_sha256)
    independent = symbolic_rule_scores(edges)
    if independent != {
        (15,11,12):24,(15,13,14):8,(16,11,12):8,(16,13,14):24}:
        raise AssertionError("NKR09_SYMBOLIC_CONTROL_TRAIN_DRIFT")
    feedback_labels = [(s, 15, truths[(s,15)]) for s in range(33,41)]
    cold_hits = static_hits = symbolic_hits = 0
    for s in range(41, 53):
        direct = facts.objects(s, 15)["objects"]
        if direct:
            raise AssertionError("NKR09_PROTECTED_COLD_TRUTH_LEAK")
        result = cold.predict(s, 15)
        if (result["classification"] != "UNVERIFIED_ADAPTIVE_RELATION_HYPOTHESES"
                or result["verified_new_knowledge"]
                or result["native_accepted"]
                or result["can_write_causal_consequence"]):
            raise AssertionError("NKR09_HYPOTHESIS_WRONGLY_CERTIFIED")
        prediction = result["proposals"][0]["object_q"]
        independent_pred = symbolic_prediction(edges, 15, s, independent,
                                               feedback_labels)
        if prediction != independent_pred:
            raise AssertionError("NKR09_STRONG_SYMBOLIC_COMPARATOR_NOT_TIED")
        cold_hits += int(prediction == truths[(s,15)])
        static_hits += int(frozen[s] == truths[(s,15)])
        symbolic_hits += int(independent_pred == truths[(s,15)])
    retained_before = retained_after = 0
    for s in range(53,65):
        before = initial.predict(s,16)
        after = cold.predict(s,16)
        if before["proposals"] != after["proposals"]:
            raise AssertionError("NKR09_UNRELATED_RULE_INTERFERENCE")
        retained_before += int(before["proposals"][0]["object_q"] == truths[(s,16)])
        retained_after += int(after["proposals"][0]["object_q"] == truths[(s,16)])
    if (cold_hits != 9 or static_hits != 3 or symbolic_hits != 9
            or retained_before != 9 or retained_after != 9):
        raise AssertionError("NKR09_FROZEN_TEST_TARGETS_FAILED")
    if cold.predict(41,29)["classification"] != "UNKNOWN_ABSTAIN":
        raise AssertionError("NKR09_UNRELATED_DECOY_FALSE_RULE")
    if PublicCausalCells().snapshot() != native_before:
        raise AssertionError("NKR09_LEGACY_CAUSAL_BYTES_DRIFT")
    if cold.checkpoint() != adapted.checkpoint():
        raise AssertionError("NKR09_COLD_REPLAY_FAIL")
    return {
        "schema":"yggdrasil.nkr09.synthetic-feedback-frozen-result.v1",
        "classification":"SOURCE_SAFE_RELATION_FEEDBACK_DEVELOPMENT_DIAGNOSTIC",
        "source_mode":"engineering_fixture_only",
        "fixture_training_records":len(edges),
        "induced_rule_templates":len(sources),
        "frozen_rule_counts":sources,
        "feedback_labels_revealed":8,
        "protected_cold_queries":12,
        "cold_static_hits1":static_hits,
        "cold_after_feedback_hits1":cold_hits,
        "cold_equal_evidence_symbolic_hits1":symbolic_hits,
        "cold_gain_over_static_hits1":cold_hits-static_hits,
        "unrelated_relation_retention_hits1_before":retained_before,
        "unrelated_relation_retention_hits1_after":retained_after,
        "unknown_relation_abstains":True,
        "original_fact_checkpoint_unchanged":True,
        "legacy_ypp_checkpoint_unchanged":True,
        "new_real_world_facts":0,
        "scientific_pass":False,
        "original_scientific_first_use":False,
        "accepted_native":False,
        "rule_checkpoint_sha256":cold.checkpoint_sha256,
        "source_checkpoint_sha256":facts.checkpoint_sha256,
        "total_runtime_seconds":time.monotonic()-started,
    }


if __name__=="__main__":
    print("NKR09_FROZEN_DEV_DIAGNOSTIC="+
          json.dumps(run_frozen(),sort_keys=True,separators=(",",":")),
          flush=True)
