import unittest
from grounding import World,DirectLearner,TableLearner,Erased,TrainedLearner,NumericPlane

class Tests(unittest.TestCase):
    def test_numeric_plane_contradiction(self):
        p=NumericPlane(2)
        p.observe(32,3);self.assertEqual(p.read(32),3)
        p.observe(32,2);self.assertIsNone(p.read(32))
        self.assertIsNone(p.read(17))
    def test_world_has_unique_groundings(self):
        for enc in ('identity','permuted','shifted'):
            w=World('DEV',103,enc)
            self.assertEqual(len(set(w.forms.values())),8)
            self.assertEqual(len(w.evidence()),10)
            self.assertEqual(len(set(w.unknown)),4)
    def test_unseen_composition(self):
        w=World('DEV',103,'permuted');l=DirectLearner()
        for e in w.evidence():l.observe(e)
        self.assertEqual(l.source_events,10)
        self.assertEqual(l.sensor_resets,4)
        for v in range(2):
            for o in range(4):
                for t in range(2):
                    u=(w.forms['verb',v],w.forms['noun',o],w.forms['destination',t])
                    state=(0,1,0,1)
                    self.assertEqual(l.result(u,state),w.true_result(v,o,t,state))
    def test_true_negative_and_slot_order(self):
        w=World('DEV',103,'shifted');l=DirectLearner()
        for e in w.evidence():l.observe(e)
        u=(w.forms['verb',0],w.unknown[0],w.forms['destination',0])
        self.assertIsNone(l.decode(u))
        u=(w.forms['noun',0],w.forms['verb',0],w.forms['destination',0])
        self.assertIsNone(l.decode(u))
    def test_restore_tamper_and_retention(self):
        w=World('DEV',103,'identity');l=DirectLearner()
        for e in w.evidence():l.observe(e)
        before=l.snapshot()
        self.assertEqual(DirectLearner.restore(before).snapshot(),before)
        with self.assertRaises(ValueError):DirectLearner.restore(before+b'!')
        l.observe(('noun',w.synonym,0))
        self.assertEqual(l.planes['noun'].read(w.forms['noun',0]),0)
        l.observe(('noun',w.forms['noun',3],1))
        self.assertIsNone(l.planes['noun'].read(w.forms['noun',3]))
        self.assertEqual(DirectLearner.restore(l.snapshot()).snapshot(),l.snapshot())
    def test_converged_trained_and_exact_table(self):
        w=World('DEV',103,'identity')
        arms=(DirectLearner(),TrainedLearner(),TableLearner(),Erased())
        for e in w.evidence():
            for a in arms:a.observe(e)
        arms[1].train()
        self.assertEqual(arms[1].training_updates,2800)
        u=(w.forms['verb',1],w.forms['noun',2],w.forms['destination',1]);s=(0,1,0,1)
        for a in arms[:3]:self.assertEqual(a.result(u,s),w.true_result(1,2,1,s))
        self.assertIsNone(arms[3].result(u,s))
    def test_event_rejects_bad_consequence(self):
        l=DirectLearner()
        with self.assertRaises(ValueError):l.observe(('verb_effect',2,0,0,0,0,1))

if __name__=='__main__':unittest.main()
