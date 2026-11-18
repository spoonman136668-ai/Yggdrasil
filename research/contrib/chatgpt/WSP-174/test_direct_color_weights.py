"""WSP178 exact direct-weight program against matched conventional counts.

All records here are fabricated public-format inputs, not source-first-use.
"""
from __future__ import annotations

import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import unittest

from public_boundary import PublicEvidence
from stochastic_controls import ConditionalDirichlet, descendant_brier, descendants
from direct_color_weights import DirectColorWeights

POS = ((0, 0), (0, 4), (4, 0), (4, 4), (2, 2))


def scene(colors):
    return tuple((x, y, c) for (x, y), c in zip(POS, colors))


def record(action=10, target3=4, current3=3):
    old = scene((0, 1, 2, current3, 4))
    goal = scene((0, 1, 0, 3, 4))
    new = scene((0, 1, 0, target3, 4))
    reward = sum(x[2] == g[2] for x, g in zip(new, goal)) / 5
    return PublicEvidence(current=old, goal=goal, action=action,
                          next=new, reward=reward, done=False)


def conventional_pooled(records, event):
    """Independent exact conventional posterior with IDENTICAL FEATURES."""
    counts = Counter(r.next[t][2] for r in records
                     if r.action == event.action for t in descendants(r.action)
                     if t == 3)
    n = sum(counts.values())
    return tuple((1 + counts[k]) / (5 + n) for k in range(5))


class DirectColorWeightTests(unittest.TestCase):
    def test_programming_and_freeze(self):
        m = DirectColorWeights()
        e = record()
        with self.assertRaisesRegex(ValueError, "NOT_FROZEN"):
            m.forecast(e.policy_input(), e.action)
        m.fit_observed(e)
        self.assertEqual(m.summary()["fit_records"], 1)
        self.assertEqual(m.summary()["fit_descendants"], 2)
        m.freeze()
        self.assertEqual(m.forecast(e.policy_input(), e.action)[3],
                         (1/6, 1/6, 1/6, 1/6, 2/6))
        self.assertEqual(m.forecast(e.policy_input(), e.action)[4],
                         (1/6, 1/6, 1/6, 1/6, 2/6))
        with self.assertRaisesRegex(ValueError, "FIT_FROZEN"):
            m.fit_observed(e)

    def test_matched_feature_bayes_equivalence_is_a_negative_control(self):
        # Changing only arithmetic to "direct programming" cannot beat
        # an independently fitted conventional Bayes posterior with same
        # feature family, counts, and prior. Avoid a false research GO.
        for sequence in ((4,), (4, 3, 4), (0, 1, 2, 3, 4, 4, 0)):
            training = [record(target3=c) for c in sequence]
            native = DirectColorWeights()
            for e in training:
                native.fit_observed(e)
            native.freeze()
            forecast = native.forecast(training[0].policy_input(), 10)[3]
            expected = conventional_pooled(training, training[0])
            self.assertEqual(forecast, expected)

    def test_conventional_contextual_control_can_outperform_pooled_weights(self):
        training = [record(target3=4, current3=3),
                    record(target3=3, current3=4)]
        held = record(target3=4, current3=3)
        direct = DirectColorWeights()
        traditional = ConditionalDirichlet()
        for event in training:
            direct.fit_observed(event)
            traditional.fit_observed(event)
        direct.freeze()
        traditional.freeze()
        p_direct = direct.forecast(held.policy_input(), held.action)
        p_trad = traditional.forecast(held.policy_input(), held.action)
        self.assertLess(descendant_brier(held, p_trad),
                        descendant_brier(held, p_direct))

    def test_no_oracle_and_policy_input_strict(self):
        m = DirectColorWeights()
        e = record()
        with self.assertRaisesRegex(ValueError, "PUBLIC_ONLY"):
            m.fit_observed({"graph": "secret", "action": 10})
        m.fit_observed(e)
        m.freeze()
        for bad in ({**e.policy_input(), "next": e.next},
                    {**e.policy_input(), "hidden_graph": 7}):
            with self.assertRaisesRegex(ValueError, "PUBLIC_POLICY_FIELDS"):
                m.forecast(bad, e.action)
        with self.assertRaisesRegex(ValueError, "ACTION"):
            m.forecast(e.policy_input(), 25)

    def test_no_descendant_action_is_not_falsely_perfect(self):
        e = PublicEvidence(current=scene((0, 1, 2, 3, 0)),
                           goal=scene((0, 1, 2, 3, 0)),
                           action=24, next=scene((0, 1, 2, 3, 4)),
                           reward=0.8, done=False)
        m = DirectColorWeights()
        m.fit_observed(e)
        self.assertEqual(m.summary()["fit_records"], 1)
        self.assertEqual(m.summary()["fit_descendants"], 0)
        m.freeze()
        self.assertEqual(m.forecast(e.policy_input(), e.action), {})
        self.assertIsNone(descendant_brier(e, m.forecast(e.policy_input(), e.action)))

    def test_exact_cold_checkpoint_and_independent_models(self):
        m = DirectColorWeights()
        e = record()
        for c in (4, 3, 3, 1, 4):
            m.fit_observed(record(target3=c))
        m.freeze()
        raw = m.canonical()
        restored = DirectColorWeights.restore(raw, m.sha256())
        self.assertEqual(restored.canonical(), raw)
        self.assertEqual(restored.forecast(e.policy_input(), e.action),
                         m.forecast(e.policy_input(), e.action))
        with self.assertRaisesRegex(ValueError, "FIT_FROZEN"):
            restored.fit_observed(e)

    def test_tamper_and_invalid_checkpoint_refused(self):
        m = DirectColorWeights()
        m.fit_observed(record())
        m.freeze()
        raw = m.canonical()
        with self.assertRaisesRegex(ValueError, "WIRE_HASH"):
            DirectColorWeights.restore(raw, "0" * 64)
        d = json.loads(raw)
        d["hidden_graph"] = 9
        fake = json.dumps(d, sort_keys=True, separators=(",", ":")).encode()
        with self.assertRaisesRegex(ValueError, "WIRE_SCHEMA"):
            DirectColorWeights.restore(fake, hashlib.sha256(fake).hexdigest())
        d.pop("hidden_graph")
        d["cells"][0][2] = -1
        bad = json.dumps(d, sort_keys=True, separators=(",", ":")).encode()
        with self.assertRaisesRegex(ValueError, "CELL_COUNTS"):
            DirectColorWeights.restore(bad, hashlib.sha256(bad).hexdigest())
        for invalid in (b"", b"x" * 17000, "string"):
            with self.assertRaisesRegex(ValueError, "WIRE_SIZE"):
                DirectColorWeights.restore(invalid, "0" * 64)

    def test_immutability_of_unseen_cells(self):
        a = record()
        m = DirectColorWeights()
        m.fit_observed(a)
        m.fit_observed(record(target3=3))
        m.freeze()
        future = m.forecast(a.policy_input(), 5)
        self.assertEqual(future, {i: (0.2,) * 5 for i in (2, 3, 4)})
        self.assertEqual(m.summary()["weight_cells"], 2)

    def test_standard_library_and_no_original_runtime(self):
        content = Path(__file__).with_name("direct_color_weights.py").read_text("utf-8")
        tree = ast.parse(content)
        imports = {item.name.split(".")[0] for node in ast.walk(tree)
                   if isinstance(node, ast.Import) for item in node.names}
        imports |= {node.module.split(".")[0] for node in ast.walk(tree)
                    if isinstance(node, ast.ImportFrom) and node.module}
        self.assertFalse(imports & {"numpy", "torch", "gym", "causal_gym"})
        for protected in ("source_first_use_authority", "source_env.step",
                          "protected_seed", "lease.execute", "source_env.reset"):
            self.assertNotIn(protected, content)


if __name__ == "__main__":
    unittest.main()
