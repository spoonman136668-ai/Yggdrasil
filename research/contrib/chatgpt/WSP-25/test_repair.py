import hashlib
import json
import unittest
from repair import LocalRepair,match
from run_dev import acquire,actual,retained,y_score
from world import World

class RepairTests(unittest.TestCase):
    def ready(self):return acquire(World(0),None)[0]
    def test_numeric_matcher_all_addresses(self):
        for a in (0,1):
            for b in (0,1):
                for x in (0,1):
                    for y in (0,1):self.assertEqual(match([1-a,a,1-b,b],x,y),int((a,b)==(x,y)))
    def test_query_never_before_complete_and_uses_own_coverage(self):
        self.assertIsNone(LocalRepair().validation_query());m=self.ready();q=m.validation_query()
        self.assertEqual(m.seen[2*q[2]+q[3]],0)
        m.observe(actual(World(0),q,None));self.assertIsNone(m.validation_query())
    def test_one_exception_preserves_old_facts_and_other_bucket(self):
        m=self.ready();q=m.validation_query();old=retained(m);pair=q[2:];e=actual(World(0),q,pair);m.observe(e)
        self.assertEqual(m.occupied,1);self.assertEqual(m.base.snapshot(),old[0]);self.assertEqual(y_score(m,World(0)),4)
        for i,s in enumerate(old[-2]):
            if s:self.assertEqual(m.joint(0,i//2,i%2),old[-1][i])
    def test_old_fact_conflict_is_local_and_nondestructive(self):
        m=self.ready();q=m.validation_query();m.observe(actual(World(0),q,q[2:]));before=retained(m)
        i=next(i for i,s in enumerate(m.seen) if s);m.observe((0,i//2,i%2,1-m.labels[i],3))
        self.assertEqual(m.fault_z,1);self.assertIsNone(m.joint(0,0,0));self.assertEqual(retained(m),before);self.assertEqual(y_score(m,World(0)),4)
    def test_disabled_growth_fails_closed(self):
        m=self.ready();m.growth_enabled=0;q=m.validation_query();m.observe(actual(World(0),q,q[2:]))
        self.assertEqual((m.occupied,m.fault_z),(0,1));self.assertEqual(y_score(m,World(0)),4)
    def test_cold_and_repeat_idempotence(self):
        m=self.ready();q=m.validation_query();e=actual(World(0),q,q[2:]);m.observe(e);raw=m.snapshot()
        restored=LocalRepair.restore(raw);restored.observe(e);self.assertEqual(restored.snapshot(),raw)
    def test_checkpoint_tamper_truncation_and_wrong_type(self):
        raw=self.ready().snapshot()
        for bad in (raw[:-1],raw+b'x',raw[:12]+bytes([raw[12]^1])+raw[13:],bytearray(raw),'x'):
            with self.assertRaises(ValueError):LocalRepair.restore(bad)
    def test_resigned_noncanonical_states_rejected(self):
        raw=self.ready().snapshot();d=json.loads(raw[9:-32]);variants=[]
        for key,value in (('weights',[1,0,0,0]),('occupied',True),('seen',[1,2,0,0]),('schema','wrong'),('extra',0)):
            v=dict(d);v[key]=value;variants.append(v)
        for v in variants:
            body=json.dumps(v,sort_keys=True,separators=(',',':')).encode();r=b'WSP25'+len(body).to_bytes(4,'big')+body;r+=hashlib.sha256(r).digest()
            with self.assertRaises(ValueError):LocalRepair.restore(r)
    def test_invalid_events_and_queries_rejected(self):
        m=self.ready()
        for e in ([0,0,0,0,0],(0,1,0,0,0),(0,0,0,2,3),(0,0,0,0,True)):
            with self.assertRaises(ValueError):m.observe(e)
        for q in ((True,0,0),(0,2,0),(0,0,-1)):
            with self.assertRaises(ValueError):m.joint(*q)
    def test_noise_indistinguishability_then_clean_repeat_fault(self):
        m=self.ready();q=m.validation_query();e=actual(World(0),q,None);bad=list(e);bad[3]^=1;m.observe(tuple(bad))
        self.assertNotEqual(m.joint(0,*q[2:]),e[3]);m.observe(e);self.assertEqual(m.fault_z,1);self.assertEqual(y_score(m,World(0)),4)

if __name__=='__main__':unittest.main()
