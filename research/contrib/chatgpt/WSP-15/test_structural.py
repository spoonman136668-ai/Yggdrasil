"""WSP15 interfaces, feedback causality and cold-state negative controls."""
import hashlib
import inspect
import json
import unittest
from structural import (PlasticNand, context, checked_examples, mismatch,
                        forward, threshold, LENGTHS, PUBLIC)


class WSP15Tests(unittest.TestCase):
    def obs(self, value):
        return tuple((context(i), value) for i in PUBLIC)

    def test_threshold_mismatch_truth_table_independent(self):
        for pred in (0, 1):
            for y in (0, 1):
                self.assertEqual(threshold(pred+y-1)-threshold(pred+y-2), int(pred != y))

    def test_reward_commits_numeric_benefit_and_reverts_harm(self):
        m = PlasticNand()
        # Blank NAND0 outputs1; observed all1 improves over input0.
        old, new, reward = m.trial(self.obs(1), 12, 3)
        self.assertLess(new, old)
        self.assertEqual(reward, 1)
        raw = m.snapshot()
        old, new, reward = m.trial(self.obs(1), 12, 0)
        self.assertGreater(new, old)
        self.assertEqual(reward, 0)
        self.assertEqual(m.snapshot(), raw)

    def test_reward_lesion_same_noise_prevents_learning(self):
        m, random = PlasticNand(), PlasticNand()
        raw = m.snapshot()
        for j, k in ((12, 3), (0, 2), (1, 1), (12, 7)):
            m.trial(self.obs(1), j, k, "disabled")
            random.trial(self.obs(1), j, k, "random")
        self.assertEqual(m.snapshot(), raw)
        self.assertNotEqual(random.snapshot(), raw)

    def test_direct_dot_product_matches_address_reference(self):
        m = PlasticNand()
        for j, n in enumerate(LENGTHS):
            m.rows[j] = [int(k == n-1) for k in range(n)]
        for i in range(8):
            values = list(context(i))
            for g in range(6):
                a, b = m.rows[2*g].index(1), m.rows[2*g+1].index(1)
                values.append(1-int(values[a] == values[b] == 1))
            self.assertEqual(m.predict(context(i)), values[m.rows[-1].index(1)])

    def test_canonical_checkpoint_and_cold_output(self):
        m = PlasticNand()
        m.trial(self.obs(1), 12, 3)
        restored = PlasticNand.restore(m.snapshot())
        self.assertEqual(restored.snapshot(), m.snapshot())
        for i in range(8):
            self.assertEqual(m.predict(context(i)), restored.predict(context(i)))
        self.assertEqual(sum(LENGTHS), 75)

    def test_corruption_oversize_trailing_truncated_rejected(self):
        raw = PlasticNand().snapshot()
        for bad in (raw[:-1], raw+b"x", raw[:-1]+bytes([raw[-1]^1]), b"x"*3000, "x"):
            with self.assertRaisesRegex(ValueError, "CHECKPOINT_REJECTED"):
                PlasticNand.restore(bad)

    def test_forged_digest_cannot_authorize_bad_synapses(self):
        raw = PlasticNand().snapshot()
        for field, value in (("architecture", "x"), ("schema", "x"), ("rows", [[True]])):
            d = json.loads(raw[9:-32])
            d[field] = value
            b = json.dumps(d, sort_keys=True, separators=(",", ":")).encode()
            p = b"WSP15"+len(b).to_bytes(4, "big")+b
            with self.assertRaises(ValueError):
                PlasticNand.restore(p+hashlib.sha256(p).digest())

    def test_strict_inputs_and_proposal_boundary(self):
        for bad in ([], (), tuple((list(x), y) for x, y in self.obs(1)), tuple((x, True) for x, y in self.obs(1))):
            with self.assertRaises(ValueError):
                checked_examples(bad)
        for bad in (True, -1, 8):
            with self.assertRaises(ValueError):
                context(bad)
        for j, k in ((13, 0), (0, -1), (True, 0), (0, 3)):
            with self.assertRaises(ValueError):
                PlasticNand().trial(self.obs(1), j, k)
        with self.assertRaises(ValueError):
            PlasticNand().learn(self.obs(1), True)

    def test_proposal_identical_across_evidence_and_counters(self):
        a, b = PlasticNand(), PlasticNand()
        for j, k in ((12, 3), (0, 0), (1, 1), (12, 0)):
            a.trial(self.obs(1), j, k, "random")
            b.trial(self.obs(0), j, k, "random")
        self.assertEqual(a.snapshot(), b.snapshot())
        self.assertEqual(a.proposals, 4)
        self.assertEqual(a.gate_evaluations, 240)
        self.assertEqual(a.accepted, 4)

    def test_trial_rejects_malformed_evidence_and_damaged_state(self):
        with self.assertRaises(ValueError):
            PlasticNand().trial((), 0, 0)
        m = PlasticNand()
        m.rows[0][0] = True
        with self.assertRaises(ValueError):
            m.trial(self.obs(1), 0, 0)

    def test_circuit_isolation_and_no_symbolic_compiler_dependency(self):
        a, b = PlasticNand(), PlasticNand()
        raw = b.snapshot()
        a.trial(self.obs(1), 12, 3)
        self.assertEqual(b.snapshot(), raw)
        import structural
        src = inspect.getsource(structural)
        self.assertNotIn("import nand_program", src)
        self.assertNotIn("synthesize(", src)
        self.assertNotIn("catalog(", src)


if __name__ == "__main__":
    unittest.main()
