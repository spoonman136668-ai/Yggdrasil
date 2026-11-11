import hashlib
import json
import unittest
from neutral import NeutralNand, PlasticNand, PUBLIC, context, checked_six, mismatch
from run_dev import trained_six


class WSP16Tests(unittest.TestCase):
    def obs(self):
        return tuple((context(i), context(i)[0]) for i in PUBLIC)+((context(3), 0),)

    def test_six_observation_custody(self):
        self.assertEqual(checked_six(self.obs()), self.obs())
        for bad in (self.obs()[:-1], (), list(self.obs()), self.obs()[:-1]+((context(3), True),)):
            with self.assertRaises(ValueError):
                checked_six(bad)

    def test_neutral_mode_crosses_plateaus_without_increasing_total_error(self):
        m = NeutralNand().adapt(self.obs(), 17)
        before = mismatch(PlasticNand().rows, self.obs())
        self.assertLessEqual(mismatch(m.rows, self.obs()), before)
        self.assertGreater(m.neutral_accepts, 0)
        self.assertEqual(m.proposals, 1024)
        self.assertEqual(m.gate_evaluations, 73728)
        self.assertEqual(m.noise_draws, 2048)

    def test_disabled_preserves_all_initial_synapses(self):
        initial = PlasticNand().snapshot()
        m = NeutralNand(initial).adapt(self.obs(), 29, "disabled")
        self.assertEqual(m.rows, PlasticNand.restore(initial).rows)
        self.assertEqual(m.accepted, 0)

    def test_random_does_not_consult_evidence_for_commits(self):
        a = self.obs()
        b = tuple((x, 1-y) for x, y in a)
        ma = NeutralNand().adapt(a, 43, "random")
        mb = NeutralNand().adapt(b, 43, "random")
        self.assertEqual(ma.snapshot(), mb.snapshot())

    def test_strict_accepts_only_improvements(self):
        m = NeutralNand().adapt(self.obs(), 71, "strict")
        self.assertEqual(m.neutral_accepts, 0)
        self.assertEqual(m.accepted, m.improving_accepts)

    def test_cold_policy_and_synapse_identity(self):
        m = NeutralNand().adapt(self.obs(), 17)
        raw = m.snapshot()
        cold = NeutralNand.restore(raw)
        self.assertEqual(cold.snapshot(), raw)
        for i in range(8):
            self.assertEqual(m.predict(context(i)), cold.predict(context(i)))
        with self.assertRaises(ValueError):
            NeutralNand.restore(PlasticNand().snapshot())

    def test_corrupt_and_noncanonical_checkpoints_rejected(self):
        raw = NeutralNand().snapshot()
        for bad in (raw[:-1], raw+b"x", raw[:-1]+bytes([raw[-1]^1]), b"x"*5000):
            with self.assertRaises(ValueError):
                NeutralNand.restore(bad)
        d = json.loads(raw[9:-32]); d["schema"] = "wrong"
        body = json.dumps(d, sort_keys=True, separators=(",", ":")).encode()
        p = b"WSP16"+len(body).to_bytes(4,"big")+body
        with self.assertRaises(ValueError):
            NeutralNand.restore(p+hashlib.sha256(p).digest())

    def test_conventional_control_converges_six_correctly(self):
        pred, steps, bce = trained_six(self.obs())
        self.assertLessEqual(bce, .02)
        self.assertLessEqual(steps, 2048)
        for i, (_x, y) in zip(PUBLIC+(3,), self.obs()):
            self.assertEqual(pred[i], y)

    def test_invalid_mode_seed_state_rejected(self):
        for seed in (True, -1, 4):
            with self.assertRaises(ValueError):
                NeutralNand().adapt(self.obs(), seed)
        with self.assertRaises(ValueError):
            NeutralNand().adapt(self.obs(), 17, "unknown")
        damaged = NeutralNand(); damaged.rows[0] = [True]*3
        with self.assertRaises(ValueError):
            damaged.adapt(self.obs(), 17)

    def test_no_cross_task_state_mutation(self):
        initial = PlasticNand().snapshot()
        a, b = NeutralNand(initial), NeutralNand(initial)
        old = b.snapshot()
        a.adapt(self.obs(), 17)
        self.assertEqual(b.snapshot(), old)
        self.assertEqual(initial, PlasticNand().snapshot())


if __name__ == "__main__":
    unittest.main()
