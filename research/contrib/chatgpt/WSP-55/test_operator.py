"""WSP55 prospective engineering SELFTEST; no DEV/PRIMARY first-use.

Evaluator may build WSP53 SELFTEST worlds and score heldout rows. The learner
module may import only public WSP54 parsing routines and python stdlib.
Engineering test success never implies scientific superiority.
"""
import inspect
import json
from dataclasses import replace
from pathlib import Path
import sys
import time
import unittest

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "WSP-53"))
sys.path.insert(0, str(root / "WSP-54"))
from source import build_world
from wsp55_operator import NoncommutingCompiler


def score(model, rows):
    counts = {"correct": 0, "wrong_confident": 0, "abstain": 0, "total": 0}
    predicted = []
    for r in rows:
        p = model.predict(r.before, r.acoustic_bits)
        predicted.append(p)
        counts["total"] += 1
        if p is None:
            counts["abstain"] += 1
        elif p == r.after:
            counts["correct"] += 1
        else:
            counts["wrong_confident"] += 1
    return counts, predicted


def swap_contrasts(world, rows, predicted, excluded):
    # Evaluator-only calculation. No generator labels or source functions
    # may be made visible to the learner.
    triples = [t for t in world._all_triples if t not in set(excluded)]
    paired = {t: (r, p) for t, r, p in zip(triples, rows, predicted)}
    ok = 0
    for e, first, second in triples:
        if first >= second:
            continue
        lhs = paired.get((e, first, second))
        rhs = paired.get((e, second, first))
        if lhs is None or rhs is None or lhs[0].after == rhs[0].after:
            continue
        if (lhs[1] == lhs[0].after and rhs[1] == rhs[0].after
                and lhs[1] != rhs[1]):
            ok += 1
    return ok


class OperatorEngineering(unittest.TestCase):
    def test_contracts_no_phase_or_gradient(self):
        self.assertEqual(NoncommutingCompiler.gradient_steps, 0)
        self.assertEqual(list(inspect.signature(NoncommutingCompiler.predict).parameters),
                         ["self", "before", "raw"])
        w = build_world("noncommuting_order", "SELFTEST", 9901, "identity")
        m = NoncommutingCompiler()
        for bad in (replace(w.phase_a[0], action_cost=0),
                    replace(w.phase_a[0], reset_cost=1),
                    replace(w.phase_a[0], acoustic_bits="no"),
                    replace(w.phase_a[0], before=(0,))):
            with self.assertRaises(ValueError):
                m.observe(bad)
        self.assertEqual(len(m.rows), 0)
        self.assertIsNone(m.predict(w.phase_a[0].before, w.phase_a[0].acoustic_bits))

    def test_six_source_isolated_worlds(self):
        results = []
        total_correct = total_wrong = total_swaps = 0
        for seed in (9901, 9902):
            for encoding in ("identity", "permuted", "rotated"):
                with self.subTest(seed=seed, encoding=encoding):
                    w = build_world("noncommuting_order", "SELFTEST", seed, encoding)
                    m = NoncommutingCompiler()
                    wall_start, cpu_start = time.perf_counter(), time.process_time()
                    for row in w.phase_a:
                        m.observe(row)
                    a, ap = score(m, w.heldout_a)
                    contrasts_a = swap_contrasts(w, w.heldout_a, ap, w._a_triples)
                    for row in w.phase_b:
                        m.observe(row)
                    b, bp = score(m, w.heldout_b)
                    wall_seconds = time.perf_counter() - wall_start
                    cpu_seconds = time.process_time() - cpu_start
                    contrasts_b = swap_contrasts(w, w.heldout_b, bp, w._b_triples)
                    total_correct += a["correct"] + b["correct"]
                    total_wrong += a["wrong_confident"] + b["wrong_confident"]
                    total_swaps += contrasts_a + contrasts_b
                    self.assertEqual(len(m.rows), 60)
                    self.assertEqual(m.gradient_steps, 0)
                    self.assertEqual(a["total"], 48)
                    self.assertEqual(b["total"], 84)
                    self.assertLessEqual(len(m.a_models), 512)
                    self.assertLessEqual(len(m.b_models), 512)
                    self.assertLessEqual(m.capacity_bits(), 3000000 * 8)
                    if seed == 9901 and encoding == "identity":
                        snap = m.snapshot()
                        cold = NoncommutingCompiler.restore(snap)
                        self.assertEqual(cold.snapshot(), snap)
                        self.assertEqual(score(cold, w.heldout_b)[0], b)
                        with self.assertRaises(ValueError):
                            NoncommutingCompiler.restore(snap.replace("wsp55.operator.v1", "wsp55.operator.v2"))
                    results.append({
                        "seed": seed, "encoding": encoding, "a": a, "b": b,
                        "swap_contrasts": contrasts_a + contrasts_b,
                        "hypotheses_a": len(m.a_models),
                        "hypotheses_b": len(m.b_models),
                        "search_nodes": m.nodes, "incomplete": m.incomplete,
                        "wall_seconds": round(wall_seconds, 6),
                        "cpu_seconds": round(cpu_seconds, 6),
                        "persistent_bits": m.capacity_bits(),
                        "source_a": w.source_receipt()["phase_a"][1]
                    })
        classification = ("SELFTEST_SIGNAL" if
                          total_correct >= 48 and total_wrong == 0 and total_swaps >= 1
                          else "SELFTEST_NEGATIVE_OR_INCONCLUSIVE")
        print("WSP55_SELFTEST_DIAGNOSTIC " +
              json.dumps({"classification": classification, "correct": total_correct,
                          "wrong_confident": total_wrong, "swaps": total_swaps,
                          "worlds": results}, sort_keys=True, separators=(",", ":")))
        self.assertEqual(len(results), 6)
        # A negative experiment is valid data, not an infrastructure failure.

if __name__ == "__main__":
    unittest.main()
