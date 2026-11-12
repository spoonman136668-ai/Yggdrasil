"""WSP51 frozen source-experience program-discovery battery.

Only the evaluator knows the latent world and encoding. The learner receives
current-state actions and observed encoded replies, never source family labels.
"""
import argparse
import hashlib
import itertools
import json
import platform
import subprocess
import sys
import time
from pathlib import Path
from synthesis import LearnedProgram, catalog
from world import World
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "WSP-50"))
from domains import Encoding, EncodedSource
from frozen_world import rng_for
from raw_equations import EquationBank, BankModel, AdaptiveModel


def affine_consensus(width, rows):
    """Strong conventional affine hypothesis control on identical evidence."""
    n = 1 << width
    if not rows:
        return [None] * n, n * (n // 2)
    x0, y0 = rows[0]
    matches = []
    for m in range(1, n, 2):
        b = (y0 - m * x0) % n
        if all((m * x + b) % n == y for x, y in rows[1:]):
            matches.append((m, b))
    predictions = []
    for x in range(n):
        values = {(m * x + b) % n for m, b in matches}
        predictions.append(next(iter(values)) if len(values) == 1 else None)
    return predictions, len(matches)


def frozen_raw(width):
    models = [BankModel([EquationBank(width, degree) for _ in range(2)])
              for degree in (1, 2, 3, "full")]
    return models, AdaptiveModel(models)


def one_episode(width, family, seed, encoding_kind, cohort):
    tag = f"WSP51|{cohort}|{seed}|{width}|{family}"
    world = World(width, family, tag)
    encoding = Encoding(width, encoding_kind, tag)
    source = EncodedSource(world, encoding)
    learned = LearnedProgram(width)
    raw_models, raw = frozen_raw(width)
    n = 1 << width
    rows = []
    state = 0
    source_s = 0.0
    update_s = 0.0
    acq_time = time.perf_counter()

    def take(action):
        nonlocal state, source_s, update_s
        if len(rows) >= 8192:
            raise AssertionError("SOURCE_BUDGET")
        t = time.perf_counter()
        x = state
        y = source.apply(action, x)
        source_s += time.perf_counter() - t
        t = time.perf_counter()
        learned.observe(action, x, y)
        for model in raw_models:
            model.banks[action].observe(x, y)
        rows.append((action, x, y))
        state = y
        update_s += time.perf_counter() - t
        return x, y

    for index in range(n):
        learned.record_cycle(state, index)
        take(0)
    learned.certify(state)
    expected_cycle = (len({x for a, x, y in rows}) == n and state == 0)
    assert bool(learned.cycle.valid) == expected_cycle, "CYCLE_CERTIFICATION"
    if learned.cycle.valid:
        assert all(learned.cycle.coord(encoding.encode(i)) == i for i in range(n)), "CYCLE_ORACLE_PARITY"
    acquisition_s = time.perf_counter() - acq_time

    def evaluate(phase):
        t = time.perf_counter()
        facts = {(a, x): y for a, x, y in rows}
        assert len(facts) == sum(b.seen.bit_count() for b in learned.cycle.seen), "EXACT_FACT_CUSTODY"
        assert all(learned.apply(a, x) == y and raw.apply(a, x) == y for (a, x), y in facts.items()), "FACT_RETENTION"
        assert len(rows) <= 8192
        snapshot = learned.snapshot()
        restored = LearnedProgram.restore(snapshot)
        assert restored.snapshot() == snapshot, "COLD_CANONICAL"
        try:
            LearnedProgram.restore(snapshot + b"1")
        except ValueError:
            pass
        else:
            raise AssertionError("CHECKPOINT_TAMPER")
        allpairs = [(a, x) for a in range(2) for x in range(n)]
        assert all(restored.apply(a, x) == learned.apply(a, x) for a, x in allpairs), "COLD_PARITY"
        latent_action1 = [(encoding.decode(x), encoding.decode(y))
                          for (a, x), y in facts.items() if a == 1]
        if learned.cycle.valid:
            predicted_mask = learned.bank.matching(latent_action1)
            assert learned.live == predicted_mask, "BATCH_GRAMMAR_PARITY"
            for x in range(n):
                rawx = encoding.encode(x)
                reference = learned.bank.unanimous(predicted_mask, x)
                expected = None if reference is None else encoding.encode(reference)
                fact, known = learned.fact(1, rawx)
                if not known:
                    assert learned.apply(1, rawx) == expected, "INDEPENDENT_PREDICTOR_PARITY"
            affine, affine_candidates = affine_consensus(width, latent_action1)
        else:
            assert learned.live == learned.bank.full_mask, "UNCERTIFIED_RULE_LEAK"
            affine, affine_candidates = [None] * n, 0
        unseen = [x for x in range(n) if (1, encoding.encode(x)) not in facts]
        correct = wrong = unknown = raw_correct = raw_wrong = raw_unknown = aff_correct = aff_wrong = aff_unknown = 0
        for x in unseen:
            observed = encoding.encode(world.apply(1, x))
            answer = learned.apply(1, encoding.encode(x))
            raw_answer = raw.apply(1, encoding.encode(x))
            affine_answer = (encoding.encode(affine[x])
                             if affine[x] is not None and learned.cycle.valid else None)
            for prediction, category in ((answer, "learned"), (raw_answer, "raw"), (affine_answer, "affine")):
                if prediction is None:
                    if category == "learned": unknown += 1
                    elif category == "raw": raw_unknown += 1
                    else: aff_unknown += 1
                elif prediction == observed:
                    if category == "learned": correct += 1
                    elif category == "raw": raw_correct += 1
                    else: aff_correct += 1
                else:
                    if category == "learned": wrong += 1
                    elif category == "raw": raw_wrong += 1
                    else: aff_wrong += 1
        rng = rng_for(tag + "|evaluations")
        compositions = []
        for j in range(24):
            x = rng.randrange(n)
            actions = tuple(rng.randrange(2) for _ in range((2, 3, 4)[j % 3]))
            compositions.append((x, actions))
        goal_tests = []
        for _ in range(8):
            x = rng.randrange(n)
            actions = tuple(rng.randrange(2) for _ in range(3))
            goal_tests.append((x, world.rollout(x, actions)))
        composed = sum(learned.rollout(encoding.encode(x), actions) == encoding.encode(world.rollout(x, actions))
                       for x, actions in compositions)
        plans = sum((p is not None and world.rollout(x, p) == goal)
                    for x, goal in goal_tests
                    for p in [learned.plan(encoding.encode(x), encoding.encode(goal))])
        observed_recall = sum(learned.apply(a, x) == y for (a, x), y in facts.items())
        score = dict(phase=phase, cohort=cohort, width=width, family=family, seed=seed,
                     encoding=encoding_kind, cycle_valid=bool(learned.cycle.valid),
                     action_replies=len(rows), unique_facts=len(facts),
                     action1_unique=sum(a == 1 for a, x in facts),
                     unseen=len(unseen), correct=correct, wrong_known=wrong, abstain=unknown,
                     raw_correct=raw_correct, raw_wrong_known=raw_wrong, raw_abstain=raw_unknown,
                     affine_correct=aff_correct, affine_wrong_known=aff_wrong, affine_abstain=aff_unknown,
                     affine_hypotheses=affine_candidates,
                     composed=composed, plan_success=plans,
                     observed_recall=observed_recall,
                     program_hypotheses=learned.live.bit_count(),
                     catalog_unique=len(learned.bank.maps),
                     catalog_bit_register_payload=len(learned.bank.maps) * n * width,
                     version_space_bits=len(learned.bank.maps),
                     cold=True,
                     counterworld_possible=bool(unseen))
        return score, time.perf_counter() - t

    after_cycle, eval_s = evaluate("post_cycle")
    probes = []
    active_s = 0.0
    for _ in range(12):
        started = time.perf_counter()
        if learned.cycle.valid:
            coordinate = learned.suggest_probe()
            if coordinate is None:
                break
            navigation = 0
            while learned.cycle.coord(state) != coordinate:
                take(0)
                navigation += 1
                if navigation > n:
                    raise AssertionError("NAVIGATION")
            take(1)
            probes.append(coordinate)
        else:
            take(1)
            probes.append(None)
        active_s += time.perf_counter() - started
    after_probe, spent = evaluate("post_probe")
    eval_s += spent
    decoded_rows = [(a, encoding.decode(x), encoding.decode(y)) for a, x, y in rows]
    return [after_cycle, after_probe], decoded_rows, dict(
        acquisition_s=acquisition_s, source_seconds=source_s,
        memory_and_reference_update_s=update_s, active_policy_and_navigation_s=active_s,
        evaluation_s=eval_s, probes=len(probes))


def run(cohort):
    p = json.loads(Path(__file__).with_name("prereg.json").read_text())
    assert cohort in ("DEV", "PRIMARY")
    started = time.perf_counter()
    trace = hashlib.sha256()
    result = dict(schema="wsp51.result.v1", cohort=cohort, episodes=[], timings={},
                  latent_trajectory_checks=0, classification=None,
                  source={"sha": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
                          "platform": platform.platform(), "python": platform.python_version()})
    for width, family, seed in itertools.product(p["widths"], p["families"], p["splits"][cohort]):
        latent_rows = None
        for kind in p["encodings"]:
            episodes, rows, timings = one_episode(width, family, seed, kind, cohort)
            if latent_rows is not None:
                assert rows == latent_rows, "ENCODING_ACTION_TRAJECTORY_MISMATCH"
            latent_rows = rows
            result["latent_trajectory_checks"] += 1
            result["episodes"] += episodes
            for k, v in timings.items():
                result["timings"][k] = result["timings"].get(k, 0) + v
            trace.update(json.dumps([episodes, rows], sort_keys=True, separators=(",", ":")).encode())
    pos = [e for e in result["episodes"] if e["phase"] == "post_probe" and e["family"] in p["families"][:3]]
    neg = [e for e in result["episodes"] if e["phase"] == "post_probe" and e["family"] in p["families"][3:5]]
    invalid = [e for e in result["episodes"] if e["phase"] == "post_probe" and e["family"] == "broken_spine"]
    totals = {k: sum(e[k] for e in pos) for k in ("correct", "wrong_known", "unseen", "raw_correct", "affine_correct")}
    by_encoding = {}
    for kind in p["encodings"]:
        subset = [e for e in pos if e["encoding"] == kind]
        n = sum(e["unseen"] for e in subset)
        by_encoding[kind] = dict(correct=sum(e["correct"] for e in subset), total=n,
                                 accuracy=sum(e["correct"] for e in subset) / n if n else None)
    negatives = {family: dict(unseen=sum(e["unseen"] for e in neg if e["family"] == family),
                              abstain=sum(e["abstain"] for e in neg if e["family"] == family),
                              wrong=sum(e["wrong_known"] for e in neg if e["family"] == family))
                 for family in p["families"][3:5]}
    fact_retention = all(e["observed_recall"] == e["unique_facts"] for e in result["episodes"])
    positive = bool(pos) and all(e["unseen"] and e["correct"] / e["unseen"] >= 0.95
                                 and not e["wrong_known"] and
                                 e["correct"] / e["unseen"] - max(e["raw_correct"], e["affine_correct"]) / e["unseen"] >= .20
                                 for e in pos)
    negative = bool(neg) and all(v["unseen"] and v["abstain"] / v["unseen"] >= .90
                                 and v["wrong"] == 0 for v in negatives.values())
    invalid_valid = all(not e["cycle_valid"] for e in invalid)
    result["bounded_metrics"] = dict(positives=totals, positive_encoding=by_encoding,
                                     negatives=negatives, invalid_cycle_rejected=invalid_valid,
                                     fact_retention=fact_retention,
                                     positive_gate=positive, negative_gate=negative,
                                     threshold_pass=positive and negative and invalid_valid and fact_retention)
    result["classification"] = ("DEV_SUPPORTED_BOUNDED_PROGRAM_INDUCTION"
                                if result["bounded_metrics"]["threshold_pass"]
                                else "MIXED_BOUNDED_PROGRAM_DISCOVERY_LIMIT")
    result["trace_sha256"] = trace.hexdigest()
    result["timings"]["whole_assay_seconds"] = time.perf_counter() - started
    result["independent_scientific_pass"] = False
    print("WSP51_RESULT", json.dumps(result, sort_keys=True))
    return result


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cohort", choices=("DEV", "PRIMARY"), default="DEV")
    args = ap.parse_args()
    run(args.cohort)
