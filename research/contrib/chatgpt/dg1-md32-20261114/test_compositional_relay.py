"""Independent MD32 causal-physics checks; fixture only, no science first-use."""
import inspect
import json
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from compositional_relay import (
    BASES, LOCK, MOTIFS, TRAIN, TRANSFER, ZERO, RelayWorld, canonical,
    digest, fixture_spec, fixture_world, law_manifest, one_hot,
    preflight_task, run_public_blind, run_public_two_probe,
    run_privileged_oracle,
)


class MD32TwoLinkPhysics(unittest.TestCase):
    def test_original_frozen_prereg_and_distinct_structure_classes(self):
        self.assertEqual(LOCK["parent"]["exact_qualified_sha"],
                         "aedbe74d2b31ead5a0517ce3aa827df9e64abda9")
        self.assertEqual(
            LOCK["status"],
            "FROZEN_TASK_DESIGN_ONLY_BEFORE_GENERATOR_SOURCE_OR_FIXTURE_RESULTS")
        self.assertEqual(len(BASES), 6)
        self.assertEqual(set(TRAIN) & set(TRANSFER), set())
        self.assertEqual(len(TRAIN), 3)
        self.assertEqual(len(TRANSFER), 3)
        manifest = law_manifest()
        self.assertEqual(len(set(manifest["mechanism_sha256"].values())), 6)
        self.assertEqual(manifest["train_motifs"], ["relay", "fork", "collider"])
        self.assertEqual(manifest["transfer_motifs"],
                         ["braid", "inhibitor", "crossbridge"])

    def test_official_and_other_research_seeds_are_rejected(self):
        invalid = [True, 9099, 9196, 1900001, 2900001, 3900001, 4900001,
                   1080001, 2080001, 3080001, 4080001, 8301, "9100"]
        for seed in invalid:
            with self.subTest(seed=seed):
                with self.assertRaisesRegex(
                        AssertionError, "OFFICIAL_FIRST_USE_OR_UNALLOCATED"):
                    fixture_world(seed, rewire=False)
        with self.assertRaisesRegex(AssertionError,
                                    "UNFROZEN_CHANGE_CONDITION"):
            fixture_world(9100, rewire=1)

    def test_four_episode_shared_laws_and_all_offsets_per_motif(self):
        all_motifs = {}
        for block in range(24):
            specs = [fixture_spec(9100 + block * 4 + i) for i in range(4)]
            self.assertEqual([s["required_precursor"] for s in specs],
                             [0, 1, 2, 3])
            self.assertEqual({s["motif"] for s in specs},
                             {MOTIFS[block % 6]})
            self.assertEqual(len({s["encoder"] for s in specs}), 1)
            self.assertEqual(len({s["decoder"] for s in specs}), 1)
            self.assertEqual(len({s["offset"] for s in specs}), 1)
            all_motifs.setdefault(specs[0]["motif"], []).append(
                specs[0]["offset"])
        for motif in MOTIFS:
            self.assertEqual(all_motifs[motif], [0, 1, 2, 3])

    def test_public_observations_identical_until_paid_decoder_intervention(self):
        for seed in range(9100, 9196):
            stable = fixture_world(seed, rewire=False)
            changed = fixture_world(seed, rewire=True)
            initial = stable.observe()
            self.assertEqual(initial, changed.observe())
            for forbidden in ("offset", "rewire", "motif", "decoder",
                              "encoder", "latent", "graph", "seed"):
                # A diagnostic menu necessarily describes an "encoder" or
                # "decoder" mechanism, so inspect field names, not text.
                self.assertNotIn(forbidden, initial.keys())
            precursor = initial["required_precursor"]
            action = {"kind": "actuator", "channel": precursor}
            s1, _, done = stable.step(action)
            s2, _, done2 = changed.step(action)
            self.assertFalse(done)
            self.assertFalse(done2)
            self.assertEqual(s1, s2)
            self.assertEqual(s1["sensor_vector"], list(ZERO))
            # An intervention into the decoder, not the ambient state,
            # makes a real causal difference.
            h = fixture_spec(seed)["encoder"][precursor]
            probe = {"kind": "diagnostic", "mechanism": "decoder",
                     "channel": h}
            before, cost1, _ = stable.step(probe)
            after, cost2, _ = changed.step(probe)
            self.assertEqual((cost1, cost2), (-0.08, -0.08))
            self.assertNotEqual(before["sensor_vector"],
                                after["sensor_vector"])

    def test_no_free_preview_no_infinite_diagnostics(self):
        w = fixture_world(9100, rewire=False)
        start = w.observe()
        with self.assertRaisesRegex(AssertionError,
                                    "NO_ROOT_OR_FOREIGN_ENCODER_PREVIEW"):
            w.step({"kind": "diagnostic", "mechanism": "encoder",
                    "channel": 3})
        self.assertEqual(w.observe(), start)
        enc = {"kind": "diagnostic", "mechanism": "encoder", "channel": 0}
        _, cost, _ = w.step(enc)
        self.assertEqual(cost, -0.08)
        with self.assertRaisesRegex(AssertionError, "PAID_PROBE_CAP_OR_SHAPE"):
            w.step(enc)
        stage1, cost, _ = w.step({"kind": "actuator", "channel": 0})
        self.assertEqual(cost, -0.02)
        self.assertEqual(stage1["sensor_vector"], list(ZERO))
        with self.assertRaisesRegex(AssertionError,
                                    "ONLY_INTERNAL_DECODER_PROBE"):
            w.step({"kind": "diagnostic", "mechanism": "encoder",
                    "channel": 0})
        _, cost, _ = w.step({"kind": "diagnostic", "mechanism": "decoder",
                             "channel": 0})
        self.assertEqual(cost, -0.08)
        with self.assertRaisesRegex(AssertionError, "PAID_PROBE_CAP_OR_SHAPE"):
            w.step({"kind": "diagnostic", "mechanism": "decoder",
                    "channel": 1})
        _, final, done = w.step({"kind": "actuator", "channel": 0})
        self.assertTrue(done)
        self.assertIn(final, (-0.52, 0.98))
        self.assertEqual(w.receipt()["paid_steps"], 4)
        with self.assertRaisesRegex(AssertionError, "NO_ACTION_AFTER_DONE"):
            w.step({"kind": "actuator", "channel": 0})

    def test_independent_reference_oracle_and_actual_two_paid_probes(self):
        for seed in range(9100, 9196):
            spec = fixture_spec(seed)
            for rewire in (False, True):
                paid = run_public_two_probe(fixture_world(seed, rewire=rewire))
                oracle = run_privileged_oracle(
                    fixture_world(seed, rewire=rewire), spec, rewire)
                self.assertEqual(paid["net_utility"], 0.8)
                self.assertEqual(paid["paid_steps"], 4)
                self.assertEqual(oracle["net_utility"], 0.96)
                self.assertEqual(oracle["paid_steps"], 2)
                self.assertEqual([x["action"]["kind"] for x in paid["trace"]],
                                 ["diagnostic", "actuator",
                                  "diagnostic", "actuator"])

    def test_balanced_blind_and_task_headroom_gate(self):
        proof = preflight_task()
        self.assertEqual(proof["fixture_worlds"], 192)
        self.assertEqual(proof["paired_stable_rewire_identifiability"], "96/96")
        self.assertEqual(proof["oracle_mean_net_utility"], 0.96)
        self.assertEqual(proof["blind_mean_net_utility"], -0.165)
        self.assertEqual(proof["public_two_probe_mean_net_utility"], 0.8)
        self.assertEqual(proof["fixed_action_success_fraction"], 0.25)
        self.assertEqual(proof["oracle_blind_headroom"], 1.125)
        self.assertEqual(proof["oracle_two_probe_gap"], 0.16)
        self.assertEqual(len(proof["per_motif"]), 6)
        self.assertTrue(all(x["fixed_terminal_success"] == 8
                            for x in proof["per_motif"].values()))
        self.assertFalse(proof["official_first_use"])
        self.assertFalse(proof["learner_training_executed"])

    def test_public_policy_never_reads_hidden_law(self):
        for policy in (run_public_blind, run_public_two_probe):
            source = inspect.getsource(policy)
            for forbidden in ("._spec", "._rewire", "._latched",
                              "_decode(", "fixture_spec(", "run_privileged"):
                self.assertNotIn(forbidden, source)
        for seed in (9100, 9148, 9195):
            traces = [run_public_two_probe(fixture_world(seed, rewire=True))
                      for _ in range(2)]
            self.assertEqual(traces[0], traces[1])
            self.assertEqual(traces[0]["public_trace_sha256"],
                             digest(traces[0]["trace"]))
            self.assertEqual(len(traces[0]["public_trace_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
