import hashlib
import json
import unittest
from knowledge import NumericKnowledge,ACTIONS,PRIOR,parity,event_checked
from controls import SymbolicKnowledge,train_bucket
from world import World


class WSP24Tests(unittest.TestCase):
    def test_numeric_parity_matches_independent_rule(self):
        for weights in PRIOR:
            for bits in PRIOR:self.assertEqual(parity(weights,bits),sum(a*b for a,b in zip(weights,bits))%2)

    def test_observational_confounding_requires_intervention(self):
        a,b=World(0),World(6)
        self.assertEqual([a.event(u) for u in (0,1)],[b.event(u) for u in (0,1)])
        self.assertNotEqual(a.act((0,1,1)),b.act((0,1,1)))
        m=NumericKnowledge()
        for u in (0,1):m.observe(a.event(u))
        self.assertFalse(m.complete());self.assertIn(m.choose(),ACTIONS)

    def test_numeric_and_symbolic_query_agree_before_hidden_feedback(self):
        world=World(11);n=NumericKnowledge();s=SymbolicKnowledge()
        for u in (0,1):n.observe(world.event(u));s.observe(world.event(u))
        self.assertEqual(n.choose(),s.choose())

    def test_clamped_Y_does_not_update_Y_mechanism(self):
        world=World(13);m=NumericKnowledge();before=m.viable[0][:]
        m.observe(world.event(0,2,0,1));self.assertEqual(m.viable[0],before)

    def test_cold_checkpoint_retains_numeric_knowledge(self):
        world=World(12);m=NumericKnowledge()
        for u in (0,1):m.observe(world.event(u))
        raw=m.snapshot();cold=NumericKnowledge.restore(raw)
        self.assertEqual(cold.snapshot(),raw);self.assertEqual(cold.choose(),m.choose())

    def test_corruption_and_forged_inconsistent_coefficients_rejected(self):
        raw=NumericKnowledge().snapshot()
        for bad in (raw[:-1],raw+b'x',raw[:-1]+bytes([raw[-1]^1])):
            with self.assertRaises(ValueError):NumericKnowledge.restore(bad)
        d=json.loads(raw[9:-32]);d['known'][0][0]=1
        body=json.dumps(d,sort_keys=True,separators=(',',':')).encode();p=b'WSP24'+len(body).to_bytes(4,'big')+body
        with self.assertRaises(ValueError):NumericKnowledge.restore(p+hashlib.sha256(p).digest())

    def test_real_contradiction_faults_and_abstains(self):
        m=NumericKnowledge();m.observe((0,0,0,0,0));m.observe((0,0,0,1,0))
        self.assertEqual(m.fault,1);self.assertIsNone(m.choose());self.assertIsNone(m.joint(0,0,0))
        self.assertEqual(NumericKnowledge.restore(m.snapshot()).fault,1)

    def test_strict_event_validation(self):
        for e in ([0,0,0,0,0],(True,0,0,0,0),(0,1,0,0,0),(0,0,0,0,True)):
            with self.assertRaises(ValueError):event_checked(e)
        with self.assertRaises(ValueError):World(True)

    def test_conventional_bucket_really_converges_from_outcomes(self):
        p,steps,loss=train_bucket([((1,0,0),0),((1,1,0),1),((1,0,1),1)])
        self.assertLessEqual(loss,.01);self.assertLessEqual(steps,4096);self.assertAlmostEqual(sum(p),1.)
        self.assertEqual(p.index(max(p)),6)

    def test_no_cross_world_state_or_event_table(self):
        a,b=NumericKnowledge(),NumericKnowledge();before=b.snapshot()
        a.observe(World(63).event(0));self.assertEqual(b.snapshot(),before)
        self.assertNotIn('world',a.__dict__);self.assertNotIn('events',a.__dict__)


if __name__=='__main__':unittest.main()
