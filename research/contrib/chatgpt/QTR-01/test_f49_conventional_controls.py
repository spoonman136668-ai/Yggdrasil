"""F49 fully-trained conventional-control implementation tests, source-only."""
import unittest
import numpy as np
import f49_worlds as w
import f49_conventional_controls as f


class TestF49ConventionalControls(unittest.TestCase):
    def test_locked_protocol_and_exact_input_representation(self):
        p=w.freeze()
        self.assertIn("conventional_mlp",p["arms"])
        self.assertIn("conventional_logistic",p["arms"])
        self.assertEqual(len(f.features(1,0,2)),18)
        x=f.pair_features((1,2,3))
        self.assertEqual(x.shape,(2,18))
        self.assertEqual(int(x[0,0]),1)
        self.assertEqual(int(x[0,8]),0)
        self.assertEqual(int(x[1,8]),1)
        self.assertEqual(int(x[1,1]),1)
        self.assertEqual(int(x[1,16]),1)
        self.assertEqual(int(x[1,17]),1)
        self.assertNotIn("target_ast",f.__dict__)

    def test_train_validation_split_is_train_only_and_deterministic(self):
        x=np.arange(1800,dtype=float).reshape(100,18)
        y=np.arange(100,dtype=float)%2
        a=f.split_train_validation(x,y)
        b=f.split_train_validation(x,y)
        self.assertEqual([len(z) for z in a],[90,90,10,10])
        for x1,x2 in zip(a,b):
            self.assertTrue(np.array_equal(x1,x2))
        self.assertFalse(set(a[0][:,0]).intersection(set(a[2][:,0])))

    def test_logistic_full_batch_solver_and_fit_restrictions(self):
        x=np.stack([f.features(a,0,a%4) for a in range(1,65)])
        y=(x[:,0]*x[:,1])
        model=f.Logistic()
        result=model.fit(x,y,max_iter=20,tolerance=1e-8)
        self.assertLessEqual(result["iterations"],20)
        self.assertTrue(np.isfinite(model.w).all())
        self.assertTrue(np.isfinite(model.probabilities(x)).all())
        before=model.w.copy()
        clone=model.clone()
        clone.w+=1
        self.assertTrue(np.array_equal(model.w,before))
        for drift in (0,501):
            with self.assertRaises(f.ControlRejected):
                model.fit(x,y,max_iter=drift)
        with self.assertRaises(f.ControlRejected):
            model.fit(x,y,tolerance=1e-4)

    def test_mlp_two_hidden_layers_training_exact_16_public_updates(self):
        x=np.stack([f.features(a,0,a%4) for a in range(1,49)])
        y=(x[:,0] ^ x[:,1]) if False else ((x[:,0]+x[:,1])%2)
        model=f.MLP(seed=11)
        self.assertEqual([z.shape for z in model.params],
                         [(18,64),(64,),(64,64),(64,),(64,1),(1,)])
        fit=model.pretrain(x[:36],y[:36],x[36:],y[36:],
                           max_epochs=2,patience=1)
        self.assertLessEqual(fit["epochs"],2)
        self.assertTrue(0<=fit["best_validation_loss"])
        old=model.steps
        model.adapt_public(x[:2],y[:2])
        self.assertEqual(model.steps-old,16)
        self.assertTrue(np.isfinite(model.probabilities(x)).all())
        clone=model.clone()
        clone.params[0][0,0]+=10
        self.assertNotEqual(clone.params[0][0,0],model.params[0][0,0])

    def test_pretrained_admission_requires_full_source_and_correct_type(self):
        with self.assertRaisesRegex(f.ControlRejected,"SOURCE_TRAINING_INCOMPLETE"):
            f.Pretrained("conventional_mlp",256,f.MLP(),0,0,{})
        with self.assertRaisesRegex(f.ControlRejected,"WRONG_SOURCE_MODEL"):
            f.Pretrained("conventional_mlp",256,f.Logistic(),256*128,0,{})
        with self.assertRaises(f.ControlRejected):
            f.permitted_source_training(128)

    def test_source_rows_are_sourced_not_target_laws(self):
        x,y=f.permitted_source_training(256)
        self.assertEqual(x.shape,(256*128,18))
        self.assertEqual(y.shape,(256*128,))
        self.assertTrue(np.all((y==0)|(y==1)))
        tr,out=w.source_training_row(256,0)[0]
        self.assertTrue(np.array_equal(x[:2],f.pair_features(tr)))
        self.assertEqual(tuple(y[:2].astype(int)),out)

    def test_bad_feature_rejected_before_any_training(self):
        for args in ((True,0,0),(0,-1,0),(0,0,4),(256,0,0)):
            with self.assertRaises(f.ControlRejected): f.features(*args)
        with self.assertRaises(f.ControlRejected):
            f.pair_features((0,2,1))


if __name__=="__main__":
    unittest.main()
