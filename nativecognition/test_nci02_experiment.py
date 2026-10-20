"""NCI02 source-free developmental generator, budget and phenotype tests."""
import unittest
from nativecognition.developmental import Colony
from nativecognition.nci02_experiment import episode, observe, query, run, SLOTS


class NCI02Contract(unittest.TestCase):
    def test_source_isolation(self):
        a,b = episode(6000),episode(6200)
        self.assertNotEqual(a,b)
        self.assertEqual(len(a[1]),12)
        self.assertEqual(sorted({slot for slot,_ in a[1]}),[0,1,2,3])
        self.assertTrue(all(value in (-.8,.8) for _,value in a[1]))

    def test_query_blind_phenotype_custody(self):
        c=Colony(0)
        observe(c,episode(6201)[1],train=False)
        before=(tuple(c.state),tuple(c.genome),c.steps)
        query(c,3)
        self.assertEqual(before,(tuple(c.state),tuple(c.genome),c.steps))
        self.assertEqual(SLOTS,(0,2,4,6))

    def test_reproducible_bounded_evidence_and_no_acceptance(self):
        x=run()
        y=run()
        self.assertEqual(x,y)
        self.assertIn(x["result"], ("PASS_PROXY_ONLY","NEGATIVE"))
        self.assertEqual(x["scientific_original_firstuse"],0)
        self.assertFalse(x["entity_binding_learned"])
        self.assertFalse(x["native_composition_learned"])
        self.assertEqual(len(x["genome_weights_train_only"]),3)
        self.assertEqual(x["candidate_cell_count"],8)


if __name__ == "__main__":
    unittest.main()
