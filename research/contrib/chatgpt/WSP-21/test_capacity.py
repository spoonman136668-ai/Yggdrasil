import unittest
from capacity import evidence,select,embed,reference,context,PlasticNand
class WSP21Tests(unittest.TestCase):
    def test_known_nand_embeds_and_cold_restores(self):
        model=embed((1,(0,0),(0,1)))
        for i in range(8):self.assertEqual(model.predict(context(i)),1-(context(i)[0]&context(i)[1]))
        self.assertEqual(PlasticNand.restore(model.snapshot()).snapshot(),model.snapshot())
    def test_no_capacity_expansion_or_truncation(self):
        tree=(0,0)
        for _ in range(7):tree=(1,tree,(0,1))
        with self.assertRaisesRegex(ValueError,"MORE_THAN_SIX"):embed(tree)
    def test_evidence_and_external_reference(self):
        obs=evidence(0);cost,mask,tree=select(obs)
        self.assertTrue(all(reference().symbolic_eval(tree,x)==y for x,y in obs))
        for bad in (True,-1,64):
            with self.assertRaises(ValueError):evidence(bad)
        with self.assertRaises(ValueError):select(())
        with self.assertRaises(ValueError):select(tuple((x,True) for x,y in obs))
    def test_padded_sites_do_not_change_raw_output(self):
        model=embed((0,2))
        for i in range(8):self.assertEqual(model.predict(context(i)),context(i)[2])
        self.assertTrue(model.canonical());self.assertEqual(sum(map(len,model.rows)),75)
if __name__=="__main__":unittest.main()
