"""CVH07 frozen conventional recurrent/exploration source-free qualification."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import unittest

import recurrent_control as rc
import qualify_sourcefree as q

HERE=Path(__file__).resolve().parent


class FrozenTrainAndSourceAuthorityTests(unittest.TestCase):
    def test_frozen_sourcefree_prereg_and_parent_exact(self):
        p=json.loads((HERE/"prereg.json").read_text())
        self.assertEqual(p["schema"],
                         "yggdrasil.cvh07.recurrent-and-exploration-fully-train-sourcefree-prereg.v1")
        self.assertEqual(q.FIRST,"94b04dfada301786387fd9fcf887d17a89d23f77")
        self.assertEqual(q.PARENT,"b4ad72bad038223a722ef7e052407c26484ee0ce")
        self.assertFalse(p["authority"]["first_use_original"])
        self.assertFalse(p["authority"]["owner_signed_lease"])
        self.assertFalse(p["authority"]["protected_external_cohorts"])
        self.assertEqual(p["toy_only_data"]["steps_per_episode"],8)
        self.assertEqual(p["recurrent"]["train_epochs"],48)
        self.assertEqual(p["recurrent"]["hidden"],8)
        self.assertEqual(p["recurrent"]["weight_seed"],1707)
        self.assertEqual(p["toy_evaluation"]["total_mock_actions"],512)
        self.assertFalse(p["thresholds"]["scientific_pass"])

    def test_no_original_cohort_firstuse_and_source_only_generator_restricted(self):
        old,prereg=q.deny_original_firstuse()
        self.assertEqual(old["actual_source_interventions_this_gate"],0)
        self.assertEqual(old["train_seed_ids"],[])
        self.assertEqual(old["held_seed_ids_by_arm"],
                         {"native":[],"fourcell":[],"recurrent":[],"exploration":[]})
        self.assertEqual(old["transfer_seed_ids_by_arm"],
                         {"native":[],"fourcell":[],"recurrent":[],"exploration":[]})
        for i in (996100,996103,996500,996531,996600,996663,197,300,517,0):
            with self.assertRaises(PermissionError):
                rc.training_tape(i)
        for i in (996100,996103,996500,996600,1,100,196):
            with self.assertRaises(PermissionError):
                q.toy_action_from_selected_policy(i,0,0,0)
        self.assertEqual([len(rc.training_tape(seed)) for seed in q.TRAIN_SEEDS],
                         [8]*96)
        self.assertTrue(all(not r.terminated and r.truncated for seed in q.TRAIN_SEEDS
                            for r in rc.training_tape(seed)[-1:]))

    def test_exact_frozen_actual_training_convergence_on_toy_only(self):
        result=q.qualify_sourcefree()
        self.assertEqual(result["recurrent"]["train_epochs_completed"],48)
        self.assertEqual(result["recurrent"]["weight_parameters"],129)
        self.assertLess(result["recurrent"]["final_train_brier"],
                        result["recurrent"]["initial_train_brier"]-0.02)
        self.assertGreaterEqual(result["recurrent"]["toy_validation_brier"],0)
        self.assertLessEqual(result["recurrent"]["toy_validation_brier"],1)
        self.assertTrue(result["recurrent"]["fully_trained_on_FROZEN_TOY_TRAIN_ONLY"])
        self.assertFalse(result["recurrent"]["fully_trained_on_original_external_source"])
        self.assertEqual(result["learned_arm_public_training_actions"],
                         {"native":768,"fourcell":768,"recurrent":768})
        self.assertEqual(result["actual_original_source_do_actions"],0)
        self.assertFalse(result["new_original_source_firstuse_authorized"])
        self.assertFalse(result["scientific_pass"])
        self.assertFalse(result["native_accepted"])
        self.assertFalse(result["deployment"])
        self.assertEqual(result["receipt_sha256"],
                         rc.digest({k:v for k,v in result.items() if k!="receipt_sha256"}))
        self.assertEqual(q.qualify_sourcefree(),result)

    def test_four_policy_mock_selected_action_budget_and_cold(self):
        r=q.qualify_sourcefree()
        self.assertEqual(set(r["arms"]),set(q.ARMS))
        self.assertEqual(len(r["arms"]),4)
        self.assertEqual(r["toy_test_actions_per_arm"],128)
        self.assertEqual(sum(v["public_actions"] for v in r["arms"].values()),512)
        for value in r["arms"].values():
            self.assertEqual(value["public_actions"],128)
            self.assertEqual(value["mock_episode_count"],16)
            self.assertEqual(value["original_source_actions"],0)
            self.assertEqual(len(value["cold_checkpoint_sha256"]),64)
        self.assertTrue(r["source_firstuse_still_DISARMED"])
        self.assertTrue(r["original_model_code_unchanged"])
        self.assertTrue(r["baseline_fourcell_code_unchanged"])

    def test_recurrent_action_order_and_private_field_fail_closed(self):
        p=rc.ConventionalPublicRNN()
        with self.assertRaisesRegex(ValueError,"NOT_FULLY_TRAINED"):
            p.choose(0,())
        # A pretrained controller can be obtained only after actual frozen toy
        # TRAIN optimization; don't train from validation or true source.
        f=q.fit_equal_public_training_tapes()
        p=f["models"]["recurrent"]
        a=p.choose(0,())
        with self.assertRaisesRegex(ValueError,"NO_REPLAY"):
            p.choose(0,())
        with self.assertRaisesRegex(ValueError,"NO_COLD_REPLAY"):
            p.snapshot()
        badtype=rc.namedtuple("PrivateEvent",(*rc.FIELDS,"private_source_label"))
        with self.assertRaisesRegex(ValueError,"PUBLIC_FIELDS_ONLY"):
            p.observe(badtype(0,a,1,0,False,False,99))
        with self.assertRaisesRegex(ValueError,"UNEXPECTED"):
            p.observe(rc.PublicConsequence(0,1-a,1,0,False,False))
        self.assertEqual(p.seen,0)
        p.observe(rc.PublicConsequence(0,a,0,1,False,False))
        self.assertEqual(p.seen,1)
        old=p.snapshot()
        self.assertEqual(rc.ConventionalPublicRNN.restore(old).snapshot(),old)
        with self.assertRaisesRegex(ValueError,"REJECTED"):
            rc.ConventionalPublicRNN.restore(old.replace(b'"trained":true',b'"trained":false'))

    def test_explorer_deterministic_cold_and_uncertain_action_denial(self):
        p=rc.SeededPublicExplorer(1777)
        qx=rc.SeededPublicExplorer(1777)
        state=0;hist=[]
        for step in range(5):
            a=p.choose(state,tuple(hist))
            self.assertEqual(a,qx.choose(state,tuple(hist)))
            with self.assertRaisesRegex(ValueError,"NO_UNOBSERVED"):
                p.choose(state,tuple(hist))
            row=rc.PublicConsequence(state,a,step%2,state^a,False,False)
            p.observe(row);qx.observe(row)
            hist.append(row);state=row.after
            if step==2:
                p=rc.SeededPublicExplorer.restore(p.snapshot())
        self.assertEqual(p.snapshot(),qx.snapshot())
        private=rc.namedtuple("PrivateEvent",(*rc.FIELDS,"hidden"))
        a=p.choose(state,tuple(hist))
        with self.assertRaisesRegex(ValueError,"PUBLIC_FIELDS_ONLY"):
            p.observe(private(state,a,0,state,False,False,888))
        self.assertEqual(p.seen,5)
        with self.assertRaisesRegex(ValueError,"UNCONFIRMED"):
            p.snapshot()

    def test_training_log_no_future_label_to_policy_or_hidden_seed(self):
        source=(HERE/"recurrent_control.py").read_text()
        self.assertNotIn("import causal_gym",source)
        self.assertNotIn("env.reset(",source)
        self.assertNotIn("env.do(",source)
        self.assertNotIn("ctf_do(",source)
        self.assertNotIn("requests.get(",source)
        self.assertNotIn("subprocess.",source)
        self.assertIn("PublicConsequence(state,action,reward,new_state",source)
        self.assertIn("p=sigmoid(",source)
        self.assertIn("future_delta",source)
        self.assertIn("_sgd_full_episode",source)
        self.assertIn("self.outstanding",source)
        self.assertIn("hidden=seed&1",source)
        self.assertIn("training_tape(seed)",(HERE/"qualify_sourcefree.py").read_text())

    def test_recurrent_cold_dimensions_and_semantic_forgery_denied(self):
        f=q.fit_equal_public_training_tapes()
        p=f["models"]["recurrent"]
        raw=p.snapshot()
        value=json.loads(raw)
        value["payload"]["wo"][0]=1000000000
        with self.assertRaisesRegex(ValueError,"REJECTED"):
            rc.ConventionalPublicRNN.restore(rc.canonical(value))
        value["sha256"]=rc.digest(value["payload"])
        with self.assertRaisesRegex(ValueError,"REJECTED"):
            rc.ConventionalPublicRNN.restore(rc.canonical(value))
        with self.assertRaisesRegex(ValueError,"REJECTED"):
            rc.ConventionalPublicRNN.restore(b"{}")

    def test_independently_validated_fitted_fourcell_and_native_unchanged(self):
        f=q.fit_equal_public_training_tapes()
        controls=f["models"]
        source=tuple(row for ep in f["train"] for row in ep)
        from fourcell_control import independent_fourcell_public_batch
        count,total=independent_fourcell_public_batch(source)
        self.assertEqual(count,controls["fourcell"].count)
        self.assertEqual(total,controls["fourcell"].total)
        self.assertEqual(sum(count),768)
        self.assertEqual(controls["native"].memory.seen,768)
        self.assertEqual(controls["fourcell"].seen,768)

    def test_training_does_not_read_original_external_source(self):
        qx=q.qualify_sourcefree()
        self.assertEqual(qx["training_source"],"EXPERIMENTER_SYNTHETIC_FIXTURE_ONLY")
        self.assertEqual(qx["actual_original_source_construction"],0)
        self.assertEqual(qx["actual_original_source_reset"],0)
        self.assertEqual(qx["actual_original_source_do_actions"],0)
        self.assertEqual(qx["protected_original_source_cohorts_opened"],[])
        self.assertFalse(qx["scientific_pass"])


if __name__=="__main__":
    unittest.main()
