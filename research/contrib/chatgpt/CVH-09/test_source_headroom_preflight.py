"""CVH09 source and owner-custody first-use barriers, analytical no-action test."""
from __future__ import annotations
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import unittest

import source_headroom_preflight as a

HERE=Path(__file__).resolve().parent


def structural_fixture():
    """FICTIONAL IDS FOR UNIT NEGATIVES, NOT RESERVATIONS OR SOURCE LEASES."""
    it=iter(range(3_000_000_000,3_000_000_416))
    groups={"train":[next(it) for _ in range(64)],
            "held":{arm:[next(it) for _ in range(64)] for arm in a.ARMS},
            "transfer":{arm:[next(it) for _ in range(24)] for arm in a.ARMS},
            "held_family":"MDPPCH-v1",
            "transfer_family":"OTHER_ONLY_IF_UPSTREAM_OWNER_VERIFIES"}
    return groups


class OriginalSourceMathAndOwnerSafetyTests(unittest.TestCase):
    def test_genuine_pinned_original_source_equation_truth_table(self):
        self.assertEqual(a.ORIGINAL_SHA,"c94e9a4cd3641588b6b8507e71ccee5c27032bdf")
        self.assertEqual(a.MDP_BLOB_SHA,"6264ec5450754c009e98c3e85f6d5927ece0a9ab")
        expected={(0,0):Fraction(41,50),(0,1):Fraction(9,50),
                  (1,0):Fraction(9,50),(1,1):Fraction(41,50)}
        self.assertEqual({(s,b):a.exact_public_source_expected_reward(s,b)
             for s in (0,1) for b in (0,1)},expected)
        for state in (0,1):
            self.assertEqual(max(a.exact_public_source_expected_reward(state,act)
                                 for act in (0,1)),Fraction(41,50))
        for bad in (None,-1,2,True,.0,"0"):
            with self.assertRaises(ValueError):
                a.exact_public_source_expected_reward(bad,0)

    def test_theoretical_nonblind_source_design_ceiling_is_not_model_learning(self):
        h=a.theoretical_headroom()
        self.assertEqual(h["optimal_reward_per_source_do"],"41/50")
        self.assertEqual(h["best_control_ceiling_for_native_to_win_at_frozen_threshold"],"77/100")
        self.assertEqual(h["reward_when_action_differs_from_state"],"9/50")
        self.assertFalse(h["distinct_original_mdp_random_seed_alters_causal_equations"])
        self.assertFalse(h["same_mdppch_seed_transfer_is_unfamiliar_family"])
        self.assertEqual(h["source_first_use_actions_here"],0)
        self.assertFalse(h["scientific_pass"])
        self.assertEqual(h["digest_sha256"],
            sha256(a._canonical({k:v for k,v in h.items() if k!="digest_sha256"})).hexdigest())

    def test_exact_416_episode_slots_and_13312_budget_are_structure_only(self):
        q=a.audit_future_seed_shapes(structural_fixture())
        self.assertEqual(q["structurally_distinct_seed_count"],416)
        self.assertEqual(q["physical_actions_reserved_MAX_ONLY"],13312)
        self.assertFalse(q["real_source_first_use_PERMITTED"])
        self.assertFalse(q["source_original_seed_virginity_VERIFIED"])
        self.assertFalse(q["source_owner_approval_VERIFIED"])
        self.assertFalse(q["family_transference_VERIFIED"])

    def test_owner_is_absent_and_approval_scope_does_not_become_lease(self):
        p=a.blank_owner_cohort()
        self.assertEqual(p["user_authorized_cap"],13312)
        self.assertTrue(p["user_scope_approved"])
        self.assertFalse(p["owner_signature_qualified"])
        self.assertIsNone(p["independent_owner_lease"])
        self.assertIsNone(p["transfer_family_original_blob_sha"])
        self.assertEqual(p["train_seeds"],[])
        self.assertEqual(p["held_seeds_by_arm"],{arm:[] for arm in a.ARMS})
        self.assertEqual(p["transfer_seeds_by_arm"],{arm:[] for arm in a.ARMS})
        self.assertEqual(p["real_original_interventions_executed"],0)
        self.assertFalse(p["first_use_execution_permitted"])

    def test_duplicate_world_seed_never_accepted(self):
        f=structural_fixture()
        f["transfer"]["native"][0]=f["train"][0]
        with self.assertRaisesRegex(ValueError,"DUPLICATE"):
            a.audit_future_seed_shapes(f)

    def test_consumed_and_owner_protected_seed_never_accepted(self):
        for seed in (996100,996101,996102,996103,996500,996531,996600,996663):
            f=structural_fixture()
            f["held"]["fourcell"][0]=seed
            with self.assertRaises(PermissionError):
                a.audit_future_seed_shapes(f)

    def test_same_causal_family_under_different_seed_is_not_transfer(self):
        f=structural_fixture()
        f["transfer_family"]=f["held_family"]
        with self.assertRaisesRegex(ValueError,"SAME_FAMILY"):
            a.audit_future_seed_shapes(f)

    def test_wrong_roster_sizes_unbounded_or_untrusted_types_denied(self):
        r=structural_fixture()
        r["train"].pop()
        with self.assertRaisesRegex(ValueError,"COHORT_SIZE"):
            a.audit_future_seed_shapes(r)
        for bad in (True,-1,2**63,None,3.14,"0"):
            r=structural_fixture()
            r["held"]["native"][0]=bad
            with self.assertRaisesRegex(ValueError,"SEED_NOT_BOUNDED"):
                a.audit_future_seed_shapes(r)
        r=structural_fixture()
        del r["held"]["recurrent"]
        with self.assertRaisesRegex(ValueError,"ARM_FAMILY_SHAPE"):
            a.audit_future_seed_shapes(r)

    def test_no_original_source_entrypoint_or_unapproved_seed_allocator(self):
        file=(HERE/"source_headroom_preflight.py").read_text(encoding="utf-8")
        self.assertNotIn("import causal_gym",file)
        self.assertNotIn("env.reset(",file)
        self.assertNotIn("env.do(",file)
        self.assertNotIn("requests.",file)
        self.assertNotIn("subprocess.",file)
        self.assertIn("original_source_one_shot_runner_id",file)
        self.assertIn("first_use_execution_permitted",file)
        self.assertFalse((HERE/"source_runner.py").exists())
        self.assertFalse((HERE/"first_use_source_execution.json").exists())
        self.assertFalse((HERE/"original_world_episodes.json").exists())

    def test_prior_original_source_fkp24_whitelist_unchanged_and_no_seed_replay(self):
        fkp24=(HERE.parent/"FKP-24"/"native_public_mdp.py").read_text()
        self.assertIn("MECHANICAL_PUBLIC_SEEDS=(996100,996101,996102,996103)",fkp24)
        self.assertIn('raise PermissionError("FKP24_UNAUTHORIZED_OR_PROTECTED_WORLD")',fkp24)
        self.assertEqual(len(a.KNOWN_CONSUMED),4)
        self.assertTrue(a.KNOWN_CONSUMED.isdisjoint(set(a.PROTECTED)))

    def test_frozen_approved_budget_and_original_owner_lease_missing(self):
        pre=json.loads((HERE/"prereg.json").read_text())
        self.assertEqual(pre["user_authorization"]["maximum_original_physical_do"],13312)
        self.assertTrue(pre["user_authorization"]["scope_approved"])
        self.assertFalse(pre["current_gate"]["first_use_permitted_now"])
        self.assertIsNone(pre["required_source_custody"]["original_owner_lease_ref"])
        self.assertIsNone(pre["required_source_custody"]["independent_seed_ledger_sha"])
        self.assertFalse(pre["required_source_custody"]["owner_actor_qualified"])
        self.assertFalse(pre["current_gate"]["science_action_run"])
        self.assertEqual(pre["cohorts"]["total_episode_slots"],416)

    def test_full_preflight_does_not_claim_science_or_source_actions(self):
        result=a.preflight()
        self.assertEqual(result["source_original_firstuse"],
                         "BLOCKED_NO_OWNER_QUALIFIED_VIRGIN_COHORT")
        self.assertEqual(result["physical_original_source_actions_executed"],0)
        self.assertTrue(result["source_family_transfer_not_achievable_by_mdppch_seed_changes"])
        self.assertFalse(result["scientific_pass"])
        self.assertFalse(result["native_promoted"])
        self.assertFalse(result["deployment"])
        self.assertEqual(result["digest_sha256"],
            sha256(a._canonical({k:v for k,v in result.items() if k!="digest_sha256"})).hexdigest())

    def test_persisted_result_must_match_entire_exact_preflight(self):
        file=HERE/"result.json"
        if file.exists():
            self.assertEqual(json.loads(file.read_text()),a.preflight())
        else:
            self.skipTest("result not committed yet; no firstuse admitted")


if __name__=="__main__":
    unittest.main()
