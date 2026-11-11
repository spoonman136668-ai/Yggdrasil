import unittest
from cost_assay import (CONTEXTS,PUBLIC,observations,fresh_reference,train_mlp,
                        mlp_forward,predict,checkpoint)


class WSP19Tests(unittest.TestCase):
    def test_mlp_converges_xor_signature(self):
        obs=observations(19);w,n,bce=train_mlp(obs,17)
        self.assertEqual(len(w),41);self.assertLessEqual(n,4096);self.assertLessEqual(bce,.02)
        for x,y in obs:self.assertEqual(int(mlp_forward(w,x)[1]>0),y)

    def test_mlp_seed_determinism(self):
        self.assertEqual(train_mlp(observations(5),29),train_mlp(observations(5),29))

    def test_conventional_checkpoint_preserves_predictions(self):
        ref=fresh_reference();w,n,bce=train_mlp(observations(17),43)
        restored,size=checkpoint('mlp',[w],ref)
        self.assertGreater(size,0)
        for x in CONTEXTS:self.assertEqual(predict('mlp',w,x,ref),predict('mlp',restored[0],x,ref))

    def test_compiled_and_symbolic_cold_agreement(self):
        ref=fresh_reference();tree=ref.synthesize(observations(14))[2]
        c=ref.NumericNand.from_program(tree);cold,size=checkpoint('compiled',[c],ref)
        sym,other=checkpoint('symbolic',[tree],ref)
        for x in CONTEXTS:
            self.assertEqual(c.predict(x),cold[0].predict(x))
            self.assertEqual(c.predict(x),ref.symbolic_eval(sym[0],x))

    def test_all_signatures_and_no_extra_observations(self):
        for s in range(32):
            obs=observations(s);self.assertEqual(len(obs),5)
            self.assertEqual(tuple(x for x,y in obs),tuple(CONTEXTS[i] for i in PUBLIC))

    def test_8hot_preprocessing_and_cold(self):
        ref=fresh_reference();w,n,bce=ref.fully_train_8hot(observations(29))
        cold,size=checkpoint('adam8hot',[w],ref)
        for i,x in enumerate(CONTEXTS):self.assertEqual(predict('adam8hot',cold[0],x,ref),ref.trained_predict(w,i))


if __name__=='__main__':unittest.main()
