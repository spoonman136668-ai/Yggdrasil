"""F50 synthetic-public, no-target native causal-slot engineering controls."""
import unittest
from unittest.mock import patch

import f50_native_assoc as n
import f50_public_corpus as p
import f50_worlds as w


class F50NativeTests(unittest.TestCase):
    def test_frozen_budget_and_public_only_source_parity(self):
        self.assertEqual(n.PROPOSALS,2048)
        self.assertEqual(n.MAX_QUERIES,64)
        self.assertEqual(n.QUERY_POLICIES,("native","random","uniform"))
        self.assertEqual(set(n.ABLATIONS),
                         {"none","no_causal_slot_retention","public_outcome_shuffle",
                          "random_proposals_equal_2048","permuted_action_outcome_alignment"})
        self.assertNotIn("target_ast",n.__dict__)
        self.assertNotIn("target_law",n.__dict__)
        with patch.object(w,"sealed_heldout_inputs_for_evaluator_only",
                          side_effect=AssertionError("NO EVALUATOR ACCESS")):
            arm=n.NativeAssociation(1024,4013)
            independent=p.PublicFIT(1024)
            self.assertEqual(p.assert_equal_source_access(arm.corpus,independent),
                             arm.corpus.digest_for_fit_graphs())
            self.assertEqual(arm.observed_bits,0)
            self.assertEqual(len(arm.pool),512)

    def test_single_synthetic_public_update_contradiction_and_cold(self):
        arm=n.NativeAssociation(1024,4013)
        index,episode=arm.select()
        with self.assertRaisesRegex(n.NativeRejected,"QUERY_STATE_INVALID"):
            arm.select()
        with self.assertRaisesRegex(n.NativeRejected,"UNAUTHORIZED_OR_REPLAYED"):
            arm.observe((index+1)%512,(1,0,1))
        with self.assertRaises(p.PublicSourceRejected):
            arm.observe(index,(True,0,1))
        self.assertEqual(arm.observed_bits,0)
        arm.observe(index,(1,0,0))  # Fixture PUBLIC feedback, never target law.
        self.assertEqual(arm.observed_bits,3)
        self.assertEqual(arm.proposals,2048)
        self.assertEqual(len(arm.used),1)
        self.assertTrue(1<=len(arm.hypotheses)<=n.MEMORY)
        self.assertTrue(all(w.ast_depth(rule)<=6 for rule in arm.hypotheses))
        values=arm.probability(episode)
        self.assertEqual(len(values),3)
        self.assertTrue(all(0<=x<=1 for x in values))
        saved=arm.cold_checkpoint()
        clone=n.NativeAssociation.restore(saved)
        self.assertEqual(clone.cold_checkpoint(),saved)
        self.assertEqual(clone.probability(episode),values)
        self.assertEqual(clone.select(),arm.select())
        tampered=saved[:-1]+bytes((saved[-1]^1,))
        with self.assertRaises(n.NativeRejected):
            n.NativeAssociation.restore(tampered)

    def test_query_policies_are_bounded_and_deterministic(self):
        for policy in n.QUERY_POLICIES:
            with self.subTest(policy=policy):
                a=n.NativeAssociation(1024,4013,query_policy=policy)
                b=n.NativeAssociation(1024,4013,query_policy=policy)
                self.assertEqual(a.select(),b.select())
                self.assertEqual(a.pool,b.pool)

    def test_all_ablations_preserve_public_bit_and_proposal_counts(self):
        for mode in n.ABLATIONS[1:]:
            with self.subTest(mode=mode):
                a=n.NativeAssociation(1024,4013,mode=mode,query_policy="uniform")
                index,episode=a.select()
                a.observe(index,(1,0,0))
                self.assertEqual(a.observed_bits,3)
                self.assertEqual(a.proposals,2048)
                if mode=="no_causal_slot_retention":
                    self.assertEqual(a.observations,[])
                elif mode=="public_outcome_shuffle":
                    self.assertEqual(a.observations[0][1],(0,0,1))
                else:
                    self.assertEqual(a.observations[0][1],(1,0,0))
                self.assertEqual(a.used,[index])
                clone=n.NativeAssociation.restore(a.cold_checkpoint())
                self.assertEqual(clone.used,a.used)
                self.assertEqual(clone.proposals,2048)

    def test_protected_seed_and_malformed_policy_fail_closed(self):
        for seed in (4127,4159,163,True):
            with self.assertRaises(w.F50Rejected):
                n.NativeAssociation(1024,seed)
        for size in (True,128,8192):
            with self.assertRaises(w.F50Rejected):
                n.NativeAssociation(size,4013)
        with self.assertRaises(n.NativeRejected):
            n.NativeAssociation(1024,4013,mode="unregistered")
        with self.assertRaises(n.NativeRejected):
            n.NativeAssociation(1024,4013,query_policy="target_oracle")

    def test_no_source_changes_after_clone_or_public_event(self):
        a=n.NativeAssociation(1024,4013,query_policy="uniform")
        identity=a.corpus.digest_for_fit_graphs()
        first=a.corpus.snapshot(a.corpus.ids[0])
        index,_=a.select()
        a.observe(index,(0,1,0))
        self.assertEqual(identity,a.corpus.digest_for_fit_graphs())
        self.assertEqual(first,a.corpus.snapshot(a.corpus.ids[0]))


if __name__=="__main__":
    unittest.main()
