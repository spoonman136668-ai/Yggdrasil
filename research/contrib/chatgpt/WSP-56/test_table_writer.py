"""WSP56 prospective six-world SELFTEST; no protected source first-use.

Only the evaluator imports the independent source.py; table_writer.py must
operate exclusively on public physical transitions and raw bit strings.
"""
from dataclasses import replace
import inspect
import json
from pathlib import Path
import time
import unittest
import table_writer
from table_writer import TableWriter
from source import ENCODINGS, SEEDS, build_world, _nonaffine


def score(model, rows, predictor=None):
    predictor = predictor or model.predict
    counts = {"correct": 0, "wrong_confident": 0, "abstain": 0, "total": len(rows)}
    predictions = []
    for row in rows:
        predicted = predictor(row.before, row.acoustic_bits)
        predictions.append(predicted)
        if predicted is None:
            counts["abstain"] += 1
        elif predicted == row.after:
            counts["correct"] += 1
        else:
            counts["wrong_confident"] += 1
    return counts, predictions


def swap_contrasts(rows, tuples, predictions):
    lookup = {spec: (r, predicted)
              for spec, r, predicted in zip(tuples, rows, predictions)}
    correct = valid = 0
    for e, a, b, x in tuples:
        if a >= b:
            continue
        l = lookup.get((e, a, b, x))
        r = lookup.get((e, b, a, x))
        if l is None or r is None or l[0].after[e] == r[0].after[e]:
            continue
        valid += 1
        if (l[1] == l[0].after and r[1] == r[0].after
                and l[1][e] != r[1][e]):
            correct += 1
    return correct, valid


def affine_projection(model, rows):
    """Privileged structural ablation: only project learned op tables."""
    # No true source operation tables, grammar, or labels are accessed here.
    scored = []
    for candidate in model.lexical_models:
        affine_ops = {}
        for code, truth in candidate["operations"].items():
            _, a, b = min((sum(truth[x] != ((a*x+b) % 7) for x in range(7)),
                           a, b) for a in range(7) for b in range(7))
            affine_ops[code] = [(a*x+b) % 7 for x in range(7)]
        projected = {**candidate, "operations": affine_ops}
        grammars = model._regime_candidates(candidate)
        scored.append((projected, grammars))
    def predict(before, raw):
        answers = set()
        for m, grammars in scored:
            if not grammars:
                return None
            for order in grammars:
                answers.add(TableWriter._infer(before, raw, m, order))
        return next(iter(answers)) if len(answers) == 1 else None
    return score(model, rows, predict)[0]


class DirectNonaffineLearning(unittest.TestCase):
    def test_source_separation_and_guardrails(self):
        source_code = Path(table_writer.__file__).read_text("utf-8")
        self.assertNotIn("from source import", source_code)
        self.assertNotIn("import source", source_code)
        self.assertEqual(TableWriter.gradient_steps, 0)
        self.assertEqual(list(inspect.signature(TableWriter.predict).parameters),
                         ["self", "before", "bits"])
        with self.assertRaises(PermissionError):
            build_world(2201, "identity", cohort="PRIMARY")
        with self.assertRaises(PermissionError):
            build_world(2201, "identity", cohort="DEV")
        world = build_world(2201, "identity")
        model = TableWriter()
        for malformed in (replace(world.unary[0], action_cost=0),
                          replace(world.unary[0], reset_cost=1),
                          replace(world.unary[0], acoustic_bits="bad"),
                          replace(world.unary[0], before=(0,))):
            with self.assertRaises(ValueError):
                model.observe(malformed)
        self.assertEqual(len(model.rows), 0)

    def test_frozen_six_out_of_family_worlds(self):
        records = []
        total_correct = total_wrong = total_swaps = total_valid = 0
        total_lookup = total_affine = 0
        for seed in SEEDS:
            for encoding in ENCODINGS:
                with self.subTest(seed=seed, encoding=encoding):
                    world = build_world(seed, encoding)
                    self.assertEqual(world.receipt(),
                                     build_world(seed, encoding).receipt())
                    self.assertTrue(all(_nonaffine(op) for op in world._operators))
                    learner = TableWriter()
                    tick = time.perf_counter()
                    cpu = time.process_time()
                    for row in world.unary + world.paired_a:
                        learner.observe(row)
                    a, a_predictions = score(learner, world.heldout_a)
                    gram_a = learner.current_grammars()
                    before_snapshot = learner.snapshot()
                    cold_a = TableWriter.restore(before_snapshot)
                    self.assertEqual(score(cold_a, world.heldout_a)[0], a)
                    affine_a = affine_projection(learner, world.heldout_a)
                    for row in world.paired_b:
                        learner.observe(row)
                    b, b_predictions = score(learner, world.heldout_b)
                    gram_b = learner.current_grammars()
                    affine_b = affine_projection(learner, world.heldout_b)
                    after_snapshot = learner.snapshot()
                    cold_b = TableWriter.restore(after_snapshot)
                    self.assertEqual(cold_b.snapshot(), after_snapshot)
                    self.assertEqual(score(cold_b, world.heldout_b)[0], b)
                    with self.assertRaises(ValueError):
                        TableWriter.restore(after_snapshot.replace(
                            "wsp56.table-writer.v1", "wsp56.table-writer.v2"))
                    elapsed = time.perf_counter() - tick
                    cpu_elapsed = time.process_time() - cpu
                    self.assertEqual(len(learner.rows), 60)
                    self.assertEqual(learner.gradient_steps, 0)
                    self.assertEqual(learner.numeric_weight_count(), 28)
                    self.assertLessEqual(learner.capacity_bits(), 1000000 * 8)
                    self.assertEqual(a["total"], 96)
                    self.assertEqual(b["total"], 96)
                    contrasts_a, valid_a = swap_contrasts(
                        world.heldout_a, world._heldout_a_tuples, a_predictions)
                    contrasts_b, valid_b = swap_contrasts(
                        world.heldout_b, world._heldout_b_tuples, b_predictions)
                    actions = world.unary + world.paired_a + world.paired_b
                    observed = {(r.before, r.acoustic_bits): r.after for r in actions}
                    def lookup(before, raw):
                        return observed.get((before, raw))
                    lookup_correct = sum(score(learner, rows, lookup)[0]["correct"]
                                         for rows in (world.heldout_a, world.heldout_b))
                    total_lookup += lookup_correct
                    total_affine += affine_a["correct"] + affine_b["correct"]
                    total_correct += a["correct"] + b["correct"]
                    total_wrong += a["wrong_confident"] + b["wrong_confident"]
                    total_swaps += contrasts_a + contrasts_b
                    total_valid += valid_a + valid_b
                    records.append({
                        "seed": seed, "encoding": encoding, "source": world.receipt(),
                        "a": a, "b": b, "swap_correct": contrasts_a + contrasts_b,
                        "swap_evaluable": valid_a + valid_b,
                        "grammar_hypotheses_before": gram_a,
                        "grammar_hypotheses_after": gram_b,
                        "model_count": len(learner.lexical_models),
                        "numeric_weights": learner.numeric_weight_count(),
                        "persistent_bits": learner.capacity_bits(),
                        "lookup_correct": lookup_correct,
                        "affine_projection_correct": affine_a["correct"] + affine_b["correct"],
                        "wall_seconds": round(elapsed, 6),
                        "cpu_seconds": round(cpu_elapsed, 6)
                    })
        classification = ("SELFTEST_SIGNAL" if
                          total_correct >= 768 and total_wrong == 0 and
                          total_swaps >= 24 else "SELFTEST_NEGATIVE_OR_INCONCLUSIVE")
        print("WSP56_SELFTEST_DIAGNOSTIC " + json.dumps({
            "classification": classification, "correct": total_correct,
            "wrong_confident": total_wrong, "swap_correct": total_swaps,
            "swap_evaluable": total_valid, "lookup_correct": total_lookup,
            "affine_projection_correct": total_affine,
            "fixtures": records}, sort_keys=True, separators=(",", ":")))
        self.assertEqual(len(records), 6)
        self.assertEqual(sum(z["a"]["total"]+z["b"]["total"] for z in records), 1152)
        # An exploratory negative is a valid science diagnostic, not test failure.


if __name__ == "__main__":
    unittest.main()
