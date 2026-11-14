"""MD34 physics-only source contract and anti-shortcut negative controls.

No native learner or official science. Tests use ONLY frozen synthetic
fixture worlds 15000..15095 and no newly reserved future holdout.
"""
import inspect
import json
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from partial_routes import (
    LOCK, FIRST, LAST, MOTIFS, TRAIN, TRANSFER, ZERO, LAWS,
    fixture_spec, fixture_world, manifest, paid_bit, public_blind,
    public_parity_only, privileged_physics_oracle, task_preflight, digest,
)


class MD34InformationLimitedPhysics(unittest.TestCase):
    def test_prereg_frozen_before_source_and_disjoint_mechanisms(self):
        self.assertEqual(
            LOCK["source_parent"],
            "ba1ba1fc56a42e41913e6ecfaf2ab1f68de2642c")
        self.assertEqual(
            LOCK["status"], "TASK_ONLY_FROZEN_BEFORE_GENERATOR_OR_OUTCOMES")
        self.assertEqual(len(MOTIFS), 6)
        self.assertEqual((len(TRAIN), len(TRANSFER)), (3, 3))
        self.assertFalse(set(TRAIN) & set(TRANSFER))
        self.assertEqual(len(set(manifest()["six_mechanism_sha256"].values())), 6)
        self.assertEqual((FIRST, LAST), (15000, 15095))
        self.assertEqual(LOCK["observation_and_physics"]["global_probe_cap"], 1)

    def test_reserved_official_previous_and_out_of_scope_seed_fence(self):
        forbidden = [True, "15000", -1, 14999, 15096, 9100, 9195,
                     8301, 8420, 11000, 11767, 12000, 13191, 14000,
                     1900001, 2900001, 3900001, 4900001,
                     1080001, 2080001, 3080001, 4080001]
        for seed in forbidden:
            with self.subTest(seed=seed):
                with self.assertRaisesRegex(
                        AssertionError,
                        "OFFICIAL_FIRST_USE_OR_UNALLOCATED_SEED_FORBIDDEN"):
                    fixture_spec(seed)
        with self.assertRaisesRegex(
                AssertionError, "INVALID_HIDDEN_REWIRE_CONDITION"):
            fixture_world(FIRST, rewire=1)

    def test_four_episode_blocks_same_law_four_contexts_four_offsets(self):
        seen = {}
        for block in range(24):
            specs = [fixture_spec(FIRST + 4 * block + i)
                     for i in range(4)]
            self.assertEqual([s["context"] for s in specs], [0, 1, 2, 3])
            for key in ("E", "G0", "G1", "D", "offset"):
                self.assertEqual(len({str(s[key]) for s in specs}), 1)
            motif = MOTIFS[block % 6]
            seen.setdefault(motif, []).append(specs[0]["offset"])
        self.assertEqual({m: offsets for m, offsets in seen.items()},
                         {m: [0, 1, 2, 3] for m in MOTIFS})

    def test_observations_never_expose_private_law_or_hidden_future(self):
        for seed in range(FIRST, LAST + 1):
            stable = fixture_world(seed, rewire=False)
            changed = fixture_world(seed, rewire=True)
            initial = stable.observe()
            self.assertEqual(initial, changed.observe())
            for illegal in ("seed", "motif", "offset", "rewire",
                            "latent_h", "latent_x", "E", "G0", "D", "goal"):
                self.assertNotIn(illegal, initial.keys())
            context = initial["required_context"]
            for action in ({"kind": "actuator", "channel": context},
                           {"kind": "route", "choice": 0}):
                obs_a, _, done_a = stable.step(action)
                obs_b, _, done_b = changed.step(action)
                self.assertFalse(done_a or done_b)
                self.assertEqual(obs_a, obs_b)
                self.assertEqual(obs_a["sensor_vector"], ZERO)
            self.assertEqual(stable.observe()["phase"], 2)

    def test_every_paid_probe_returns_exactly_one_bit_not_full_answer(self):
        seed = FIRST + 3
        spec = fixture_spec(seed)
        for phase in range(3):
            world = fixture_world(seed, rewire=True)
            if phase >= 1:
                world.step({"kind": "actuator", "channel": spec["context"]})
            if phase >= 2:
                world.step({"kind": "route", "choice": 0})
            action = (
                {"kind": "diagnostic", "mechanism": "encoder_parity",
                 "channel": spec["context"]}
                if phase == 0 else
                {"kind": "diagnostic", "mechanism": "route_parity",
                 "channel": 1} if phase == 1 else
                {"kind": "diagnostic", "mechanism": "terminal_parity"}
            )
            before = world.observe()
            after, reward, done = world.step(action)
            self.assertFalse(done)
            self.assertEqual(reward, -0.09)
            self.assertEqual(after["remaining_diagnostics"], 0)
            self.assertEqual(len(after["charged_history"]),
                             len(before["charged_history"]) + 1)
            self.assertIn(paid_bit(after), (0, 1))
            with self.assertRaisesRegex(
                    AssertionError, "GLOBAL_PAID_DIAGNOSTIC_CAP"):
                world.step(action)

    def test_unavailable_foreign_or_second_stage_probes_rejected(self):
        world = fixture_world(FIRST, rewire=False)
        initial = world.observe()
        with self.assertRaisesRegex(
                AssertionError, "UNAUTHORIZED_ENCODER_QUERY"):
            world.step({"kind": "diagnostic",
                        "mechanism": "terminal_parity"})
        self.assertEqual(world.observe(), initial)
        world.step({"kind": "actuator", "channel": 0})
        with self.assertRaisesRegex(
                AssertionError, "UNAUTHORIZED_PAID_ROUTE_QUERY"):
            world.step({"kind": "diagnostic", "mechanism": "route_parity",
                        "channel": 3})
        with self.assertRaisesRegex(
                AssertionError, "WRONG_ACTION_FOR_CAUSAL_PHASE"):
            world.step({"kind": "terminal", "guess": 0})
        world.step({"kind": "route", "choice": 0})
        with self.assertRaisesRegex(
                AssertionError, "UNAUTHORIZED_TERMINAL_QUERY"):
            world.step({"kind": "diagnostic", "mechanism": "encoder_parity",
                        "channel": 0})
        self.assertEqual(world.observe()["remaining_diagnostics"], 1)

    def test_irreversible_routes_are_not_equivalent_and_are_charged(self):
        for seed in range(FIRST, LAST + 1):
            one = fixture_world(seed, rewire=False)
            two = fixture_world(seed, rewire=False)
            precursor = one.observe()["required_context"]
            for world in (one, two):
                _, cost, _ = world.step(
                    {"kind": "actuator", "channel": precursor})
                self.assertEqual(cost, -0.02)
            _, cost1, _ = one.step({"kind": "route", "choice": 0})
            _, cost2, _ = two.step({"kind": "route", "choice": 1})
            self.assertEqual((cost1, cost2), (-0.02, -0.05))
            spec = fixture_spec(seed)
            h = spec["E"][spec["context"]]
            target1 = (spec["D"][spec["G0"][h]] + spec["offset"]) % 4
            target2 = (spec["D"][spec["G1"][h]] + spec["offset"]) % 4
            self.assertNotEqual(target1, target2)
            _, reward1, _ = one.step(
                {"kind": "terminal", "guess": target1})
            _, reward2, _ = two.step(
                {"kind": "terminal", "guess": target1})
            self.assertEqual(reward1, 0.98)
            self.assertEqual(reward2, -0.52)
            self.assertEqual(one.receipt()["net_utility"], 0.94)
            self.assertEqual(two.receipt()["net_utility"], -0.59)

    def test_rewiring_changes_only_post_action_paid_terminal_evidence(self):
        for seed in range(FIRST, LAST + 1):
            a = fixture_world(seed, rewire=False)
            b = fixture_world(seed, rewire=True)
            context = a.observe()["required_context"]
            for act in ({"kind": "actuator", "channel": context},
                        {"kind": "route", "choice": 0}):
                p, _, _ = a.step(act)
                q, _, _ = b.step(act)
                self.assertEqual(p, q)
            probe = {"kind": "diagnostic",
                     "mechanism": "terminal_parity"}
            p, cost1, _ = a.step(probe)
            q, cost2, _ = b.step(probe)
            self.assertEqual((cost1, cost2), (-0.09, -0.09))
            self.assertNotEqual(p["sensor_vector"], q["sensor_vector"])
            self.assertEqual(paid_bit(p) ^ paid_bit(q), 1)

    def test_frozen_blind_parity_oracle_scores_are_analytically_separated(self):
        result = task_preflight()
        self.assertEqual(result["fixture_physical_worlds"], 192)
        self.assertEqual(result["four_episode_law_blocks"], 24)
        self.assertEqual(result["oracle_mean_reward"], 0.94)
        self.assertEqual(result["blind_mean_reward"], -0.185)
        self.assertEqual(result["one_paid_bit_mean_reward"], 0.1)
        self.assertEqual(result["oracle_minus_blind"], 1.125)
        self.assertEqual(result["oracle_minus_one_bit"], 0.84)
        self.assertEqual(result["blind_success_fraction"], 0.25)
        self.assertEqual(result["one_paid_bit_success_fraction"], 0.5)
        self.assertEqual(
            result["stable_rewire_observationally_equal_until_paid_probe"],
            "96/96")
        self.assertEqual(result["route_causal_consequence_distinct"], "96/96")
        self.assertEqual(
            set(result["per_motif"]), set(MOTIFS))
        for rec in result["per_motif"].values():
            self.assertEqual(rec, {
                "physical_worlds": 32, "blind_correct": 8,
                "one_bit_correct": 16})
        self.assertFalse(result["official_first_use"])
        self.assertFalse(result["trained_agent_evaluated"])
        self.assertEqual(result["conventional_training_headroom"], "UNVERIFIED")

    def test_actual_public_policies_replay_and_cannot_read_hidden_spec(self):
        for policy in (public_blind, public_parity_only):
            source = inspect.getsource(policy)
            for forbidden in (
                    "._spec", "._rewire", "._hidden_h", "._hidden_x",
                    "._terminal(", "fixture_spec(", "privileged_physics_oracle"):
                self.assertNotIn(forbidden, source)
        for seed in (FIRST, FIRST + 33, LAST):
            for changed in (False, True):
                receipts = [
                    public_parity_only(
                        fixture_world(seed, rewire=changed))
                    for _ in range(2)
                ]
                self.assertEqual(receipts[0], receipts[1])
                rec = receipts[0]
                self.assertEqual(
                    rec["public_trace_sha256"], digest(rec["trace"]))
                self.assertEqual(rec["paid_steps"], 4)
                self.assertEqual(rec["charged_diagnostics"], 1)
                self.assertEqual(
                    [v["action"]["kind"] for v in rec["trace"]],
                    ["actuator", "route", "diagnostic", "terminal"])
                self.assertEqual(
                    len(rec["public_trace_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
