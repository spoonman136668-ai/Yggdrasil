"""KNOW26 source-only unknown affordance tests: no hidden map leaks or false promotions."""
import json
import unittest

from unknown_action_affordance_dev import (
    PREREG,SCHEMA,PROTO,MODE,ALL_MAPS,TRUE_MAPS,FIT_LAWS,
    HELD_LAWS,HELD_SEEDS,POLICIES,HELD_FAMILY,
    frozen_protocol,context,causal_bit,truth_table,private_coin,
    witnessed,expected_brier,JointHypothesis,ContextActionBeta,
    Passive,fit_source,model_for,evaluate_world,canonical,digest,
)


class Know26Tests(unittest.TestCase):
    def test_frozen_source_split_and_mapping_permutations(self):
        p=frozen_protocol()
        self.assertEqual(p["schema"],PROTO)
        self.assertEqual(PREREG,
                         "ba8d9a071a251f3061ac907c4cf5c611726d2221")
        self.assertEqual(len(ALL_MAPS),6)
        self.assertEqual(len(set(ALL_MAPS)),6)
        self.assertEqual(len(TRUE_MAPS),3)
        self.assertEqual(set(HELD_FAMILY),
                         {truth_table(law) for law in HELD_LAWS})
        self.assertEqual(p["fit"]["total_per_mapping"],108)
        self.assertEqual(p["held"]["worlds"],24)
        self.assertEqual(p["held"]["held_witnesses_per_policy"],768)
        self.assertEqual(p["held"]["high_evaluator_queries_per_policy"],96)
        self.assertEqual(p["held"]["low_evaluator_queries_per_policy"],96)
        self.assertTrue(set(HELD_SEEDS).isdisjoint(
            {seed for seed,law,steps in FIT_LAWS}))
        self.assertTrue(set(HELD_SEEDS).isdisjoint({
            13311,13317,11311,11317,12111,12117,13011,13027,
            13049,11903,11909,11911}))

    def test_anonymous_action_meaning_kept_private_from_learner(self):
        for map_id,physical in enumerate(TRUE_MAPS):
            self.assertEqual(physical[0],0)
            self.assertEqual(set(physical[1:]),{1,2,4})
            for action in (0,1,2,3):
                self.assertTrue(0<=physical[action]<8)
            for t in range(32):
                c=context(t)
                self.assertLess(c,4)
                for action in range(4):
                    a=witnessed(HELD_SEEDS[0],HELD_LAWS[0],t,action,map_id)
                    b=witnessed(HELD_SEEDS[0],HELD_LAWS[0],t,action,map_id)
                    self.assertEqual(a,b)
                    self.assertIn(a,(0,1))
        m=JointHypothesis([1/6.]*6)
        self.assertNotIn("private_map_id",m.__dict__)
        self.assertNotIn("hidden_law",m.__dict__)
        self.assertEqual(len(m.allowed),6)
        self.assertEqual(len(m.laws),256)
        self.assertEqual(len(m.logw),6)
        self.assertEqual(len(m.logw[0]),256)
        with self.assertRaisesRegex(ValueError,"PRIVATE_NOISE"):
            private_coin(HELD_SEEDS[0],0,True)
        with self.assertRaisesRegex(ValueError,"FROZEN_SOURCE"):
            witnessed(HELD_SEEDS[0],HELD_LAWS[0],32,0,0)
        with self.assertRaisesRegex(ValueError,"FROZEN_SOURCE"):
            witnessed(HELD_SEEDS[0],"xor02",0,0,0)

    def test_single_witness_updates_and_strict_replay(self):
        yes=JointHypothesis([1/6.]*6)
        no=JointHypothesis([1/6.]*6)
        yes.observe(0,0,1,1)
        no.observe(0,0,1,0)
        self.assertGreater(yes.prob(0,1),no.prob(0,1))
        self.assertEqual(len(yes.events),1)
        self.assertEqual(len(no.events),1)
        with self.assertRaisesRegex(ValueError,"ONE_WITNESS"):
            yes.observe(0,0,1,1)
        with self.assertRaisesRegex(ValueError,"ONE_WITNESS"):
            yes.observe(1,1,1,1,source_mode="original_world")
        with self.assertRaisesRegex(ValueError,"ONE_WITNESS"):
            yes.observe(1,1,True,1)
        with self.assertRaisesRegex(ValueError,"ONE_WITNESS"):
            yes.observe(1,1,1,2)
        with self.assertRaisesRegex(ValueError,"FORECAST_INPUT"):
            yes.prob(0,True)
        self.assertEqual(MODE,"engineering_fixture_only")

    def test_cold_checkpoint_tamper_duplicate_wrong_sha(self):
        m=JointHypothesis([1/6.]*6,length=36)
        for t in range(17):
            m.observe(t,context(t),t%4,int(t%3==0))
        raw=m.checkpoint()
        cold=JointHypothesis.restore(raw,digest(raw))
        self.assertEqual(raw,cold.checkpoint())
        self.assertEqual(m.mapping_posterior(),cold.mapping_posterior())
        for c in range(8):
            self.assertEqual(m.prob(c,0),cold.prob(c,0))
        with self.assertRaises(ValueError):
            JointHypothesis.restore(raw,"0"*64)
        altered=raw.replace(b'"accepted_native":false',
                            b'"accepted_native":true')
        with self.assertRaises(ValueError):
            JointHypothesis.restore(altered,digest(altered))
        repeated=raw.replace(b'"source_mode":',
                             b'"source_mode":"original","source_mode":')
        with self.assertRaises(ValueError):
            JointHypothesis.restore(repeated,digest(repeated))
        wrong=json.loads(raw)
        wrong["events"][0][2]=4
        corrupted=canonical(wrong)
        with self.assertRaises(ValueError):
            JointHypothesis.restore(corrupted,digest(corrupted))

    def test_fit_worlds_only_and_cold_protected_ledger(self):
        for map_id in range(3):
            posterior,archive=fit_source(map_id)
            self.assertEqual(len(archive),3)
            self.assertEqual(len(posterior),6)
            self.assertAlmostEqual(sum(posterior),1,places=12)
            self.assertTrue(all(p>=0 for p in posterior))
            for a in archive:
                z=JointHypothesis.restore(a["raw"],a["source_sha"])
                self.assertEqual(z.checkpoint(),a["raw"])
                self.assertEqual(
                    [z.prob(c,0) for c in range(4,8)],a["readout_high"])
                self.assertEqual(len(z.events),36)
            self.assertNotIn("private_map",z.__dict__)

    def test_controls_have_same_held_witnesses_and_privilege_fenced(self):
        prior,_=fit_source(0)
        for name in POLICIES:
            row=evaluate_world(name,0,HELD_SEEDS[0],
                               HELD_LAWS[0],prior)
            self.assertEqual(row["witnessed_actions"],32)
            self.assertEqual(len(row["readout_high"]),4)
            self.assertGreater(row["checkpoint_bytes"],0)
            self.assertGreaterEqual(row["high_sum"],.51-1e-8)
        with self.assertRaisesRegex(ValueError,"PRIVILEGED_MAPPING"):
            model_for("known_mapping_256",prior)
        with self.assertRaisesRegex(ValueError,"PRIVILEGED_MAPPING"):
            model_for("known_held_law_family",prior)
        self.assertEqual(model_for("no_fit_joint_bayes",prior).allowed,
                         tuple(range(6)))
        self.assertEqual(len(model_for("fit_MAP_256",prior).allowed),1)
        self.assertEqual(len(model_for("no_fit_MAP_256",prior).allowed),1)
        with self.assertRaisesRegex(ValueError,"WORLD"):
            evaluate_world("fit_joint_bayes",0,HELD_SEEDS[0],
                           FIT_LAWS[0][1],prior)
        with self.assertRaisesRegex(ValueError,"WORLD"):
            evaluate_world("fit_joint_bayes",3,HELD_SEEDS[0],
                           HELD_LAWS[0],prior)

    def test_expected_brier_truth_and_no_witnessed_high_context(self):
        self.assertAlmostEqual(expected_brier(.85,.85),.1275)
        self.assertAlmostEqual(expected_brier(.5,.15),.25)
        for seed in HELD_SEEDS:
            for law in HELD_LAWS:
                for t in range(32):
                    self.assertLess(context(t),4)
        self.assertEqual(len(POLICIES),8)


if __name__=="__main__":
    unittest.main()
