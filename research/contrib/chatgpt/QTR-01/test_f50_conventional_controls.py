"""F50 law-conditioned neural and logistic source-only engineering controls.

Tests use only registered FIT source-law graphs and observed FIT rows. No
development target, protected seed, target AST or held-out evaluator first use.
"""
import unittest
from unittest.mock import patch

import numpy as np
import f50_conventional_controls as c
import f50_public_corpus as public
import f50_worlds as world


class F50ConventionalControlsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.size=1024
        fit,val=world.source_split(cls.size)
        cls.fit_ids=tuple(sorted(fit)[:4])
        cls.val_ids=tuple(sorted(val)[:2])
        cls.fit={i:c.source_records(cls.size,i) for i in cls.fit_ids}
        cls.valid={i:c.source_records(cls.size,i,validation=True) for i in cls.val_ids}

    def test_frozen_controls_and_no_target_first_use(self):
        self.assertEqual(c.KINDS,("graph_conditioned_gru","law_conditioned_set_mlp",
                                 "graph_conditioned_logistic"))
        self.assertEqual(c.GRAPH_DIM,1035)
        self.assertEqual(c.HIDDEN,128)
        self.assertEqual(c.BATCH,128)
        self.assertEqual(c.PATIENCE,20)
        self.assertEqual(c.MAX_EPOCHS,200)
        self.assertEqual(c.LR,0.001)
        self.assertEqual(c.SEED,11)
        self.assertEqual(c.L2,0.001)
        self.assertEqual(c.ITERATIONS,500)
        self.assertEqual(c.TOLERANCE,1e-8)
        self.assertEqual(c.SUPPORT_EPISODES,8)
        for name in ("target_ast","target_law","sealed_heldout_inputs_for_evaluator_only"):
            self.assertNotIn(name,c.__dict__)

    def test_identical_fit_graph_for_all_three_controls(self):
        for i in self.fit_ids:
            graph,actions,labels=self.fit[i]
            original=public.PublicFIT(self.size).source_graph(i)
            expected=c.source_graph_vector(original)
            self.assertTrue(np.array_equal(graph,expected))
            self.assertEqual(actions.shape,(64,3,33))
            self.assertEqual(labels.shape,(64,3))
            self.assertTrue(np.isin(labels,[0,1]).all())
            encoded=original.serialize()
            self.assertEqual(len(encoded["nodes"]),len(original.nodes))
            self.assertEqual(graph.dtype,np.float32)
            self.assertEqual(c.source_records(self.size,i)[0].tobytes(),
                             graph.tobytes())
        for v in self.val_ids:
            with self.assertRaises(c.ConventionalRejected):
                c.source_records(self.size,v)
        for f in self.fit_ids:
            with self.assertRaises(c.ConventionalRejected):
                c.source_records(self.size,f,validation=True)

    def test_source_fit_validation_disjoint_and_source_receipt(self):
        fit,val=world.source_split(self.size)
        self.assertFalse(fit&val)
        self.assertFalse(set(self.fit_ids)&set(self.val_ids))
        meta=c.source_meta_episode(*self.fit[self.fit_ids[0]])
        graph,sx,sy,qx,qy=meta
        self.assertEqual(graph.shape,(1035,))
        self.assertEqual(sx.shape,(24,33))
        self.assertEqual(sy.shape,(24,1))
        self.assertEqual(qx.shape,(168,33))
        self.assertEqual(qy.shape,(168,))
        reversed_batch=c.source_meta_episode(*self.fit[self.fit_ids[0]],reverse=True)
        self.assertNotEqual(qy.tobytes(),reversed_batch[-1].tobytes())
        # Every support/query action occurs in the source table once.
        reconstructed=np.concatenate((sx,qx),axis=0)
        original=self.fit[self.fit_ids[0]][1].reshape(64*3,33)
        self.assertTrue(np.array_equal(reconstructed,original[np.r_[0:8*3,8*3:64*3]]))
        with self.assertRaises(c.ConventionalRejected):
            c.dataset_receipt(self.size,self.fit,self.valid)
        self.assertEqual(c.graph_mask_for_batch((2,3),0).tolist(),[[0.0],[1.0]])
        self.assertEqual(c.graph_mask_for_batch((2,3),1).tolist(),[[1.0],[0.0]])
        self.assertEqual(c.graph_mask_for_batch((2,3),0,validation=True).tolist(),
                         [[0.0],[0.0]])

    def test_torch_graph_gru_128_and_source_only_adam_step(self):
        torch,nn,_=c._torch()
        torch.set_num_threads(1)
        model=c.create_neural("graph_conditioned_gru")
        self.assertEqual(model.support.hidden_size,128)
        self.assertEqual(model.support.input_size,33+1+128)
        self.assertEqual(model.graph[0].in_features,1035)
        batch=c.meta_batch(self.fit,self.fit_ids[:2],epoch=0)
        self.assertEqual(batch[0].shape,(2,1035))
        self.assertEqual(batch[3].shape,(2,168,33))
        optimizer=torch.optim.Adam(model.parameters(),lr=.001)
        previous=[x.detach().clone() for x in model.parameters()]
        loss=c.one_neural_step(model,optimizer,batch)
        self.assertTrue(np.isfinite(loss))
        self.assertTrue(any(not torch.equal(a,b) for a,b in zip(previous,model.parameters())))
        q=c._to_torch(batch)
        with torch.no_grad():
            out=model(q[0],q[1],q[2],q[3],q[5])
        self.assertEqual(tuple(out.shape),(2,168))
        self.assertTrue(bool(torch.isfinite(out).all()))

    def test_torch_law_conditioned_set_mlp_width128(self):
        torch,nn,_=c._torch()
        torch.set_num_threads(1)
        model=c.create_neural("law_conditioned_set_mlp")
        self.assertEqual(model.graph[0].out_features,128)
        self.assertEqual(model.support[0].out_features,128)
        self.assertEqual(model.head[0].out_features,128)
        self.assertEqual(model.head[2].out_features,128)
        batch=c.meta_batch(self.fit,self.fit_ids[:2],epoch=1)
        optimizer=torch.optim.Adam(model.parameters(),lr=.001)
        loss=c.one_neural_step(model,optimizer,batch)
        self.assertTrue(np.isfinite(loss))
        val=c.evaluate_neural_source(model,self.valid,self.val_ids)
        self.assertTrue(np.isfinite(val))
        self.assertGreater(val,0)

    def test_explicit_graph_logistic_full_batch_lbfgs_fit_no_target(self):
        data=[c.logistic_source_rows(self.fit[i]) for i in self.fit_ids]
        for x,y in data:
            self.assertEqual(x.shape,(168,1102))
            self.assertEqual(y.shape,(168,))
            self.assertTrue(np.isfinite(x).all())
            self.assertTrue(np.isin(y,[0,1]).all())
        coef,receipt=c.logistic_fit_source(
            self.fit,self.fit_ids,self.valid,self.val_ids,max_iter=500,
            tolerance=1e-8,budget_seconds=240)
        self.assertIsNotNone(coef)
        self.assertEqual(coef.shape,(1103,))
        self.assertEqual(receipt["status"],"TRAINED_SOURCE_ONLY")
        self.assertTrue(receipt["validation_law_disjoint"])
        self.assertTrue(receipt["source_training_complete"])
        self.assertFalse(receipt["scientific_pass"])
        self.assertEqual(receipt["source_fit_laws"],4)
        self.assertEqual(receipt["source_validation_laws"],2)
        self.assertTrue(np.isfinite(receipt["source_validation_bce"]))

    def test_negative_wrong_solver_or_unsupported_neural_fails(self):
        with self.assertRaises(c.ConventionalRejected):
            c.create_neural("baseline_transformer")
        with self.assertRaises((c.ConventionalRejected,world.F50Rejected)):
            c.source_records(True,0)
        with self.assertRaises(c.ConventionalRejected):
            c.source_records(1024,True)
        with self.assertRaises(c.ConventionalRejected):
            c.logistic_fit_source(self.fit,self.fit_ids,self.valid,self.val_ids,
                                  max_iter=501)
        with self.assertRaises(c.ConventionalRejected):
            c.train_neural_source("graph_conditioned_gru",self.fit,
                                  self.fit_ids,self.valid,self.val_ids,
                                  max_epochs=10)

    def test_no_dev_seed_or_evaluator_exposure(self):
        with patch.object(world,"sealed_heldout_inputs_for_evaluator_only",
                          side_effect=AssertionError("F50_EVAL_LEAK")):
            for i in self.fit_ids:
                assert len(c.source_records(1024,i)[2])==64
        with self.assertRaises(world.F50Rejected):
            world._check_dev_seed(4127)
        self.assertEqual(c.SCHEMA,"yggdrasil.qtr01.f50.law-conditioned-controls.v1")


if __name__=="__main__":
    unittest.main()
