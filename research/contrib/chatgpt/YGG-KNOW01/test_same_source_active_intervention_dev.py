"""KNOW16 source-only negative controls and fixed intervention validity."""
import unittest
from same_source_active_intervention_dev import (
    SEEDS,ROLES,PROBE,FIXED,HELD,N,source_rows,patterns,subject,object_id,
    factual_bit,observations,best_intervention,update_hypotheses,
    solve_role,score,outcome,digest,canonical)

class FactsDouble:
    def __init__(self,seed,*,source_mode="engineering_fixture_only"):
        self.rows={(q,p,o) for q,p,o,ref in source_rows(seed)}
        self.mode=source_mode
    def fact(self,q,p,o):
        exists=(q,p,o) in self.rows
        return {"classification":"DEVELOPMENT_OBSERVED_FACT_NOT_ADMITTED"
                if exists else "UNKNOWN_ABSTAIN",
                "source_mode":self.mode,
                "source_provenance":"SOURCE_SHA_PINNED_BYTES_NOT_AUTHENTICATED",
                "witnessed":exists,"native_accepted":False,
                "verified_new_real_knowledge":False,
                "can_write_causal_consequence":False}

class Tests(unittest.TestCase):
    def test_source_role_independence_and_balanced_features(self):
        for seed in SEEDS:
            rows=source_rows(seed)
            self.assertEqual(len(rows),136)
            self.assertEqual(len(set(row[0] for row in rows)),N)
            self.assertEqual(len(set(row[2] for row in rows)),8)
            self.assertEqual(len(PROBE),16)
            self.assertEqual(len(FIXED),2)
            self.assertEqual(len(HELD),16)
            self.assertEqual(len(set(subject(seed,e) for e in range(N))),N)
            self.assertEqual(tuple(sorted(patterns(seed)[e] for e in PROBE)),
                             tuple(range(16)))
            self.assertEqual(tuple(sorted(patterns(seed)[e] for e in HELD)),
                             tuple(range(16)))
            for f in ROLES:
                self.assertEqual(sum((p>>f)&1 for p in patterns(seed)),17)
            for hidden_role in ROLES:
                # Generator does not take hidden role. No static-role signal.
                self.assertEqual(source_rows(seed),rows)

    def test_zero_action_roles_not_identifiable(self):
        for seed in SEEDS:
            f=FactsDouble(seed)
            for role in ROLES:
                self.assertEqual(len(ROLES),4)
                self.assertEqual(observations(f,seed,PROBE[0]),
                                 observations(f,seed,PROBE[0]))

    def test_active_two_interventions_identify_four_worlds(self):
        for seed in SEEDS:
            f=FactsDouble(seed)
            for role in ROLES:
                actual=solve_role(f,seed,role,"active")
                self.assertEqual(actual["selected"],role)
                self.assertEqual(actual["remaining_candidates"],1)
                self.assertEqual(actual["witnessed_actions"],2)
                self.assertTrue(all(a==1 for e,a,y in actual["observations"]))
                self.assertEqual(solve_role(f,seed,role,"active"),actual)

    def test_random_and_passive_honest_action_budgets(self):
        for seed in SEEDS:
            f=FactsDouble(seed)
            samples=[solve_role(f,seed,role,"random") for role in ROLES]
            self.assertTrue(all(x["witnessed_actions"]==2 for x in samples))
            # Query schedule independent of private hidden role, outcomes differ.
            self.assertEqual(
                [[e,a] for e,a,y in samples[0]["observations"]],
                [[e,a] for e,a,y in samples[1]["observations"]])
            for role in ROLES:
                passive=solve_role(f,seed,role,"passive")
                self.assertIsNone(passive["selected"])
                self.assertTrue(all(a==0 for e,a,y in passive["observations"]))

    def test_missing_source_fails_closed(self):
        seed=SEEDS[0]; f=FactsDouble(seed)
        q=subject(seed,0)
        f.rows.remove((q,971,object_id(0,(patterns(seed)[0]>>0)&1)))
        with self.assertRaisesRegex(ValueError,"SOURCE_UNQUALIFIED"):
            observations(f,seed,0)

    def test_conflicting_or_spoofed_source_fails_closed(self):
        seed=SEEDS[0];f=FactsDouble(seed)
        q=subject(seed,0)
        old=(patterns(seed)[0]>>0)&1
        f.rows.add((q,971,object_id(0,1-old)))
        with self.assertRaisesRegex(ValueError,"SOURCE_UNQUALIFIED"):
            observations(f,seed,0)
        with self.assertRaisesRegex(ValueError,"SOURCE_UNQUALIFIED"):
            observations(FactsDouble(seed,source_mode="claimed_owner"),seed,0)

    def test_policy_abstains_if_all_candidates_are_source_identical(self):
        seed=SEEDS[0];f=FactsDouble(seed)
        for e in PROBE:
            q=subject(seed,e)
            for role in ROLES:
                f.rows.discard((q,971+role,object_id(role,0)))
                f.rows.discard((q,971+role,object_id(role,1)))
                f.rows.add((q,971+role,object_id(role,0)))
        self.assertIsNone(best_intervention(f,seed,ROLES,set()))

    def test_contradictory_witness_does_not_forge_identity(self):
        seed=SEEDS[0];f=FactsDouble(seed)
        e,a=best_intervention(f,seed,ROLES,set())
        self.assertIn(a,(0,1))
        first=update_hypotheses(f,seed,ROLES,e,a,0)
        second=update_hypotheses(f,seed,ROLES,e,a,1)
        self.assertFalse(set(first)&set(second))
        self.assertEqual(set(first)|set(second),set(ROLES))

    def test_role_free_opaque_identifiers(self):
        for seed in SEEDS:
            self.assertTrue(all(4_221_000_000 <= subject(seed,e) <
                                4_222_000_000 for e in range(N)))
        for f in ROLES:
            for b in (0,1):
                self.assertTrue(4_222_000_000 <= object_id(f,b) <
                                4_223_000_000)
        # The source IDs are opaque and *not* phase or hidden-role coded.
        self.assertEqual(len(set(object_id(f,b) for f in ROLES
                                 for b in (0,1))),8)

    def test_held_source_only_and_strong_baseline(self):
        seed=SEEDS[0];f=FactsDouble(seed)
        for role in ROLES:
            result=score(f,seed,role,{
                "native":lambda bit,a:outcome(a,bit),
                "symbolic":lambda bit,a:outcome(a,bit)})
            self.assertEqual(result["predictions"],32)
            self.assertEqual(result["brier"]["native"],[0,1])
            self.assertEqual(result["optimal_decisions"]["symbolic"],16)

    def test_inputs_refuse_bool_or_invalid(self):
        seed=SEEDS[0]
        with self.assertRaises(ValueError):subject(seed,True)
        with self.assertRaises(ValueError):object_id(0,True)
        with self.assertRaises(ValueError):outcome(True,0)
        with self.assertRaises(ValueError):observations(FactsDouble(seed),seed,34)
        for invalid in (-1,4,True):
            with self.assertRaises(ValueError):object_id(invalid,0)

    def test_no_canonical_owner_or_live_source_methods(self):
        import same_source_active_intervention_dev as m
        for forbidden in ("activate","deploy","merge","trainer_owner",
                          "schedule","observe_experience","write_canonical"):
            self.assertFalse(hasattr(m,forbidden))

if __name__=="__main__":unittest.main()
