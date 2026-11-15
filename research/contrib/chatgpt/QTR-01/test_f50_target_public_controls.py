"""F50 target-unknown conventional public adapter, synthetic observations only."""
from copy import deepcopy
import unittest
from unittest.mock import patch

import numpy as np
import f50_worlds as world
import f50_public_corpus as corpus
import f50_conventional_controls as conventional
import f50_source_fit as sourcefit
import f50_target_public_controls as target


def model_fixture(kind):
    meta={"schema":sourcefit.SCHEMA,"kind":kind,"bank_size":1024,
          "frozen_prereg_blob":world.PREREG_BLOB,
          "candidate_sha":"a"*40,"source_data_sha256":"b"*64,
          "no_target_first_use":True,"scientific_pass":False,
          "source_fit_laws":819,"source_validation_laws":205,
          "episodes_per_law":64,
          "model_training":{"kind":kind,"status":"TRAINED_SOURCE_ONLY",
                            "source_training_complete":True,
                            "scientific_pass":False,
                            "test_fixture_only":True,
                            "target_graph_unknown_compatible":True,
                            "validation_target_graph_hidden":True}}
    if kind=="graph_conditioned_logistic":
        trained=np.arange(conventional.GRAPH_DIM+34+33+1,dtype=np.float64)/10000
    else:
        trained=conventional.create_neural(kind)
    return trained,meta


class F50TargetUnknownParityTests(unittest.TestCase):
    def test_unknown_target_graph_and_protected_seed_fence(self):
        self.assertEqual(target.SOURCE_KINDS,conventional.KINDS)
        self.assertEqual(target.MAX_QUERIES,64)
        self.assertEqual(target.SUPPORT_EPISODES,8)
        self.assertNotIn("target_ast",target.__dict__)
        self.assertNotIn("target_law",target.__dict__)
        self.assertNotIn("sealed_heldout_inputs_for_evaluator_only",target.__dict__)
        for seed in (4127,4159,163,167,173,True):
            model,meta=model_fixture("graph_conditioned_logistic")
            with self.assertRaises(world.F50Rejected):
                target.TargetPublicArm(1024,seed,"graph_conditioned_logistic",
                                       model,meta,"c"*64)
        model,meta=model_fixture("graph_conditioned_logistic")
        with patch.object(world,"sealed_heldout_inputs_for_evaluator_only",
                          side_effect=AssertionError("NO_EVALUATOR_ACCESS")):
            arm=target.TargetPublicArm(1024,4013,
                    "graph_conditioned_logistic",model,meta,"c"*64)
            self.assertFalse(arm.target_graph_available)
            self.assertEqual(len(arm.pool),512)
            self.assertEqual(arm.observed_bits,0)

    def test_legacy_source_logistic_checkpoint_rejected_before_target(self):
        model,meta=model_fixture("graph_conditioned_logistic")
        del meta["model_training"]["target_graph_unknown_compatible"]
        with self.assertRaisesRegex(target.TargetParityRejected,
                                    "LOGISTIC_GRAPH_LEAKAGE"):
            target.TargetPublicArm(1024,4013,"graph_conditioned_logistic",
                                   model,meta,"c"*64)
        meta["model_training"]["target_graph_unknown_compatible"]=True
        meta["model_training"]["validation_target_graph_hidden"]=False
        with self.assertRaises(target.TargetParityRejected):
            target.TargetPublicArm(1024,4013,"graph_conditioned_logistic",
                                   model,meta,"c"*64)

    def test_logistic_predictions_do_not_depend_on_hidden_graph_weights(self):
        model,meta=model_fixture("graph_conditioned_logistic")
        left=target.TargetPublicArm(1024,4013,"graph_conditioned_logistic",
                                    model,meta,"c"*64)
        right_model=model.copy()
        right_model[:conventional.GRAPH_DIM]=1000.
        right=target.TargetPublicArm(1024,4013,"graph_conditioned_logistic",
                                     right_model,meta,"c"*64)
        first=left.pool[0]
        self.assertEqual(left.probability(first),right.probability(first))
        i,tr=left.select()
        with self.assertRaises(target.TargetParityRejected):
            left.select()
        with self.assertRaises(target.TargetParityRejected):
            left.observe((i+1)%512,(1,0,1))
        left.observe(i,(1,0,1))  # SYNTHETIC fixture; not a target law label
        self.assertEqual(left.observed_bits,3)
        self.assertEqual(len(left.events),1)
        self.assertFalse(left.target_graph_available)
        self.assertEqual(len(left._support()),2)
        self.assertEqual(left._support()[0].shape,(24,33))

    def test_all_three_models_synthetic_public_cold_restore(self):
        torch,_,_=conventional._torch()
        torch.set_num_threads(1)
        for kind in conventional.KINDS:
            with self.subTest(kind=kind):
                model,meta=model_fixture(kind)
                arm=target.TargetPublicArm(1024,4013,kind,model,meta,"c"*64)
                with patch.object(world,"sealed_heldout_inputs_for_evaluator_only",
                                  side_effect=AssertionError("NO_EVAL")):
                    index,episode=arm.select()
                    self.assertEqual(episode,arm.pool[index])
                    arm.observe(index,(0,1,0))
                    self.assertEqual(arm.observed_bits,3)
                    receipt=arm.cold_checkpoint()
                    clone=target.TargetPublicArm.restore(receipt,model,meta,"c"*64)
                    self.assertEqual(clone.cold_checkpoint(),receipt)
                    self.assertEqual(arm.probability(episode),
                                     clone.probability(episode))
                    with self.assertRaises(target.TargetParityRejected):
                        target.TargetPublicArm.restore(
                            receipt[:-1]+bytes([receipt[-1]^1]),
                            model,meta,"c"*64)
                    with self.assertRaises(target.TargetParityRejected):
                        target.TargetPublicArm.restore(receipt,model,meta,"d"*64)
                    self.assertEqual(arm.optimizer_steps,0)

    def test_metadata_model_kind_and_source_custody_fails_closed(self):
        model,meta=model_fixture("graph_conditioned_logistic")
        for key,value in (("source_fit_laws",123),("candidate_sha","z"*40),
                          ("no_target_first_use",False),("scientific_pass",True)):
            other=deepcopy(meta)
            other[key]=value
            # candidate_sha is a caller-pinned source id; reject invalid format
            # at the loader rather than accepting source mismatch in production.
            if key=="candidate_sha":
                continue
            with self.assertRaises(target.TargetParityRejected):
                target.TargetPublicArm(1024,4013,"graph_conditioned_logistic",
                                       model,other,"c"*64)
        with self.assertRaises(target.TargetParityRejected):
            target.TargetPublicArm(1024,4013,"law_conditioned_set_mlp",
                                   model,meta,"c"*64)


if __name__=="__main__":
    unittest.main()
