"""Synthetic-only tests for proposed evidence envelope; NO original engines."""
import copy
import random
import unittest
from hashlib import sha256

from public_counts import PublicCounts, synthetic_contract_selftest
from provenance_receipt import SOURCE_COMMITS, make_evidence_envelope


class EvidenceEnvelopeTests(unittest.TestCase):
    def setUp(self):
        self.a = bytes([11]) * 70
        self.b = bytes([12]) * 70
        self.c = bytes([13]) * 70
        self.seeds = [699901, 699907]
        acts = [random.Random(1000003 * s + 337).randrange(2)
                for s in self.seeds]
        self.episodes = [[(self.a, acts[0], self.b)],
                         [(self.a, acts[1], self.c)]]
        self.model = PublicCounts(70, 2).fit(self.episodes)
        self.kwargs = dict(
            source_name="DeepMindPycolabApprehend",
            source_commit=SOURCE_COMMITS["DeepMindPycolabApprehend"][0],
            cohort="engineering_only",
            harness_sha256=sha256(b"synthetic-only test harness").hexdigest(),
            runtime_contract_sha256=sha256(b"no source executed").hexdigest(),
        )

    def envelope(self, episodes=None, model=None, seeds=None, **overrides):
        kwargs = dict(self.kwargs)
        kwargs.update(overrides)
        return make_evidence_envelope(
            self.model if model is None else model,
            self.episodes if episodes is None else episodes,
            self.seeds if seeds is None else seeds,
            **kwargs)

    def test_frozen_learner_selftest(self):
        self.assertEqual(synthetic_contract_selftest(),
                         "P0FC2_SYNTHETIC_PUBLIC_COUNTS_CONTRACT=PASS")

    def test_exact_determinism(self):
        a = self.envelope()
        b = self.envelope()
        self.assertEqual(a, b)
        self.assertEqual(a["payload"]["status"],
                         "DECLARED_NOT_INDEPENDENTLY_ATTESTED")

    def test_source_commit_drift_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "SOURCE_WIRE_IDENTITY_DRIFT"):
            self.envelope(source_commit="f" * 40)

    def test_protocol_drift_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "FROZEN_INPUT_IDENTITY_DRIFT"):
            self.envelope(design_blob="f" * 40)

    def test_harness_qualification_identity_required(self):
        with self.assertRaisesRegex(ValueError, "DEPENDENCIES_MISSING"):
            self.envelope(harness_sha256="")

    def test_held_seed_rejected(self):
        with self.assertRaisesRegex(ValueError, "UNAUTHORIZED_SEED"):
            self.envelope(seeds=[699901, 701101])

    def test_duplicate_seed_rejected(self):
        with self.assertRaisesRegex(ValueError, "UNAUTHORIZED_SEED"):
            self.envelope(seeds=[699901, 699901])

    def test_training_input_change_detected_by_replay(self):
        changed = copy.deepcopy(self.episodes)
        changed[1][0] = (self.a, self.episodes[1][0][1], self.b)
        with self.assertRaisesRegex(ValueError, "INPUT_CONTENT_MISMATCH"):
            self.envelope(episodes=changed)

    def test_source_change_affects_receipt(self):
        alt = [[(self.a, self.episodes[0][0][1], self.b)],
               [(self.a, self.episodes[1][0][1], self.a)]]
        alt_model = PublicCounts(70, 2).fit(alt)
        self.assertNotEqual(self.envelope()["envelope_sha256"],
                            self.envelope(model=alt_model, episodes=alt)["envelope_sha256"])

    def test_training_episode_order_is_semantically_inert(self):
        reversed_seeds = self.seeds[::-1]
        reversed_episodes = self.episodes[::-1]
        self.assertEqual(self.envelope(),
                         self.envelope(episodes=reversed_episodes,
                                       seeds=reversed_seeds))

    def test_actor_trace_tampering_fails(self):
        tampered = copy.deepcopy(self.episodes)
        before, action, after = tampered[0][0]
        tampered[0][0] = (before, 1 - action, after)
        with self.assertRaisesRegex(ValueError, "ACTOR_TRACE_MISMATCH"):
            self.envelope(episodes=tampered)

    def test_discontinuous_episode_rejected(self):
        # A source episode may not silently splice two unrelated trajectories.
        seed = self.seeds[0]
        rng = random.Random(1000003 * seed + 337)
        first_action = rng.randrange(2)
        second_action = rng.randrange(2)
        broken = [[(self.a, first_action, self.b),
                   (self.c, second_action, self.a)]]
        broken_model = PublicCounts(70, 2).fit(broken)
        with self.assertRaisesRegex(ValueError, "EPISODE_CONTINUITY_DRIFT"):
            self.envelope(model=broken_model, episodes=broken, seeds=[seed])

    def test_continuous_episode_accepted(self):
        seed = self.seeds[0]
        rng = random.Random(1000003 * seed + 337)
        first_action = rng.randrange(2)
        second_action = rng.randrange(2)
        continuous = [[(self.a, first_action, self.b),
                       (self.b, second_action, self.c)]]
        continuous_model = PublicCounts(70, 2).fit(continuous)
        receipt = self.envelope(model=continuous_model,
                                episodes=continuous, seeds=[seed])
        self.assertEqual(receipt["payload"]["learner_count_tables"]["training_steps"], 2)

    def test_no_retroactive_scientific_admission(self):
        record = self.envelope()["payload"]
        self.assertNotIn("qualified", record["status"].lower())
        self.assertNotIn("accepted", record["status"].lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
