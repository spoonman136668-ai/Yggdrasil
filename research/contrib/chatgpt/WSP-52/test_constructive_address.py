"""WSP52 constructive-address successor diagnostic; SELFTEST only."""
import json
import math
import unittest
from dataclasses import asdict

from constructive_address import ConstructiveAddressWriter, CountOnlyAddressWriter, _features, _observable
from source import Observation, build_world
from fixture_harness import learn_observations, score_observations
from direct_writer import DirectWeightWriter


class ConstructiveAddressTests(unittest.TestCase):
    def test_input_is_raw_acoustics_and_changed_physical_state_only(self):
        row = Observation((0,)*8, "101011000111001", (1,)+(0,)*7)
        features = _features(row.acoustic_bits)
        self.assertAlmostEqual(sum(features.values()), 1.0)
        self.assertTrue(all(4 <= len(x) <= 6 for x in features))
        self.assertEqual(_observable(row)[1], (0, 1))
        for invalid in (Observation((0,)*8, "10bad", (1,)+(0,)*7),
                        Observation((0,)*8, "1"*15, (1,1)+(0,)*6),
                        Observation((0,)*8, "1"*15, (1,)+(0,)*7, 0)):
            with self.assertRaises(ValueError):
                _observable(invalid)

    def test_gradient_constructively_routes_numerical_writes(self):
        w = build_world("SELFTEST", 9001, "identity")
        candidate = ConstructiveAddressWriter()
        no_gradient = ConstructiveAddressWriter(steps=0)
        for row in w.phase_a:
            candidate.observe(row)
            no_gradient.observe(row)
        self.assertEqual(candidate.actions, 36)
        self.assertIsNone(candidate.predict(w.heldout_a[0].before,
                                            w.heldout_a[0].acoustic_bits))
        candidate.seal_a()
        no_gradient.seal_a()
        self.assertEqual(candidate.gradient_steps, 64)
        self.assertEqual(no_gradient.gradient_steps, 0)
        self.assertGreater(candidate.gradient_operations, 0)
        self.assertTrue(all(all(math.isfinite(x) for x in arr)
                            for arr in candidate.coefficients.values()))
        self.assertEqual(no_gradient.numeric_weight_count, 0)
        self.assertGreater(candidate.numeric_weight_count, 0,
                           "learned routing must actually create numerical associations")
        self.assertGreater(candidate.write_candidates, 0)

    def test_exact_budget_cold_restore_retention_and_negative_conflict(self):
        w = build_world("SELFTEST", 9001, "permuted")
        candidate = ConstructiveAddressWriter()
        learn_observations(candidate, w.phase_a)
        candidate.seal_a()
        before_b = score_observations(candidate, w.heldout_a)
        learn_observations(candidate, w.phase_b)
        candidate.finalize_b()
        after_b = score_observations(candidate, w.heldout_b)
        candidate.use_phase("A")
        retention = score_observations(candidate, w.heldout_a)
        self.assertEqual((candidate.actions, candidate.gradient_steps), (42, 64))
        data = candidate.snapshot()
        clone = ConstructiveAddressWriter.restore(data)
        self.assertEqual(clone.snapshot(), data)
        self.assertEqual(clone.capacity_bits(), candidate.capacity_bits())
        for row in w.heldout_a[:15]+w.heldout_b[:15]:
            self.assertEqual(clone.predict(row.before, row.acoustic_bits),
                             candidate.predict(row.before, row.acoustic_bits))
        for tampered in (data + " ", data[:-1] + "x"):
            with self.assertRaises(ValueError):
                ConstructiveAddressWriter.restore(tampered)
        with self.assertRaises(ValueError):
            candidate.observe(w.phase_b[0])
        for score in (before_b, after_b, retention):
            self.assertEqual(score.total,
                             score.correct+score.abstentions+score.wrong_confident)

        repeated = Observation((0,)*8, "101001011011101", (1,)+(0,)*7)
        conflicting = Observation(repeated.before, repeated.acoustic_bits,
                                  (2,)+(0,)*7)
        conflict = ConstructiveAddressWriter()
        for _ in range(36):
            conflict.observe(repeated)
        conflict.seal_a()
        for _ in range(6):
            conflict.observe(conflicting)
        conflict.finalize_b()
        self.assertIsNone(conflict.predict(repeated.before, repeated.acoustic_bits))

    def test_full_preexisting_six_fixture_receipts_no_protected_data(self):
        # This is an exploratory non-preregistered successor diagnostic.
        rows = []
        for seed in (9001, 9002):
            for encoding in ("identity", "permuted", "rotated"):
                w = build_world("SELFTEST", seed, encoding)
                model = ConstructiveAddressWriter()
                ablation = ConstructiveAddressWriter(steps=0)
                count_only = CountOnlyAddressWriter()
                direct = DirectWeightWriter()
                for learner in (model, ablation, count_only, direct):
                    learn_observations(learner, w.phase_a)
                model.seal_a()
                ablation.seal_a()
                count_only.seal_a()
                a = score_observations(model, w.heldout_a)
                count_a = score_observations(count_only, w.heldout_a)
                direct_a = score_observations(direct, w.heldout_a)
                for learner in (model, ablation, count_only, direct):
                    learn_observations(learner, w.phase_b)
                model.finalize_b()
                ablation.finalize_b()
                count_only.finalize_b()
                b = score_observations(model, w.heldout_b)
                count_b = score_observations(count_only, w.heldout_b)
                direct_b = score_observations(direct, w.heldout_b)
                model.use_phase("A")
                retention = score_observations(model, w.heldout_a)
                replay = ConstructiveAddressWriter.restore(model.snapshot())
                count_replay = CountOnlyAddressWriter.restore(count_only.snapshot())
                self.assertEqual(count_replay.snapshot(), count_only.snapshot())
                self.assertEqual(count_only.gradient_steps, 0)
                self.assertEqual(replay.actions, 42)
                self.assertEqual(replay.gradient_steps, 64)
                for row in w.heldout_a[:3]+w.heldout_b[:3]:
                    self.assertEqual(model.predict(row.before,row.acoustic_bits),
                                     replay.predict(row.before,row.acoustic_bits))
                rows.append({"seed":seed, "encoding":encoding,
                             "A":asdict(a),"B":asdict(b),"retention":asdict(retention),
                             "direct_A":asdict(direct_a),"direct_B":asdict(direct_b),
                             "count_only_A":asdict(count_a),"count_only_B":asdict(count_b),
                             "count_only_capacity_bits":count_only.capacity_bits(),
                             "count_only_numeric_weights":count_only.numeric_weight_count,
                             "actions":model.actions,
                             "gradient_updates":model.gradient_steps,
                             "gradient_operations":model.gradient_operations,
                             "numeric_weights":model.numeric_weight_count,
                             "persistent_bits":model.capacity_bits(),
                             "ablation_numeric_weights":ablation.numeric_weight_count})
        self.assertEqual(len(rows), 6)
        print("WSP52_CONSTRUCTIVE_EXPLORATORY_SELFTEST "+
              json.dumps(rows, sort_keys=True, separators=(",",":")),flush=True)

if __name__ == "__main__":
    unittest.main()
