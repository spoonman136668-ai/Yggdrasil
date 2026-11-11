import hashlib
import json
import random
import unittest
from routed import Routed,PlasticNand,traced_forward,influence_proxy,first_eligible,context,LENGTHS
from two_row import TwoRow,pack_rows
from diagnostics import audit,intervened
from joint_credit import JointNand,errors,proposal,threshold
OBS=tuple((context(i),i%2) for i in (0,1,2,4,7,3))
class RoutedTests(unittest.TestCase):
    def test_all_four_local_NAND_derivatives_exact(self):
        for a in (0,1):
            for b in (0,1):
                y=1-a*b
                self.assertEqual(y^(1-(1-a)*b),b)
                self.assertEqual(y^(1-a*(1-b)),a)
    def test_independent_full_forward_and_influence_proxy_audit(self):
        c=audit();self.assertEqual(c['forward_checks'],2048);self.assertEqual(c['influence_checks'],26624)
        self.assertEqual(c['agreement']+c['false_positive']+c['false_negative'],26624)
    def test_reconvergence_negative_is_preserved(self):
        # g0=NAND(x0,x1)=0 at(1,1,0); g1=NAND(g0,g0).
        b=PlasticNand();b.rows[0]=[1,0,0];b.rows[1]=[0,1,0]
        b.rows[2]=[0,0,0,1];b.rows[3]=[0,0,0,1];b.rows[-1]=[0,0,0,0,1,0,0,0,0]
        x=(1,1,0);p,values=traced_forward(pack_rows(b.rows),x,1)
        self.assertEqual(influence_proxy(pack_rows(b.rows),values,1)[0],0)
        self.assertNotEqual(intervened(b.rows,x,0),p)
    def test_original_prefix_matches_unchanged_control(self):
        for seed in (17,29,43,71):
            raw=PlasticNand().snapshot();m=Routed(raw,'original_single').adapt(OBS,seed,128)
            ref=TwoRow(raw,'single_protected').adapt(OBS,seed,128)
            self.assertEqual(m.rows,ref.rows)
            original=JointNand(raw);original.protection=[1-e for e in errors(original.rows,OBS)[:5]];rng=random.Random(seed)
            for _ in range(128):
                j=rng.randrange(13);k=rng.randrange(LENGTHS[j]);g=rng.randrange(6);a=rng.randrange(3+g);b=rng.randrange(3+g)
                trial=proposal(original.rows,(j,k,g,a,b),False);before=errors(original.rows,OBS);after=errors(trial,OBS)
                reward=threshold(sum(before)-sum(after))*threshold(-sum(p*e for p,e in zip(original.protection,after[:5])))
                original.rows=[[a+reward*(b-a) for a,b in zip(old,new)] for old,new in zip(original.rows,trial)]
            self.assertEqual(m.rows,original.rows)
            for k in ('accepted','changed_coordinates','accepted_coordinates','noise_draws','gate_evaluations','proposed_row_writes','proposals'):self.assertEqual(getattr(m,k),getattr(ref,k))
    def test_first_eligible_rotation_and_empty_feedback(self):
        influences=[0]*13;influences[2]=influences[9]=1
        self.assertEqual(first_eligible(influences,1,3),9);self.assertEqual(first_eligible(influences,1,10),2)
        self.assertEqual(first_eligible(influences,0,7),7)
    def test_disabled_protection_and_budget(self):
        raw=PlasticNand().snapshot()
        for arm in ('error_routed','correct_routed','uniform_matched','original_single','disabled'):
            m=Routed(raw,arm).adapt(OBS,17,32)
            self.assertEqual((m.proposals,m.reverse_steps,m.eligibility_tests,m.auxiliary_draws),(32,192,416,32))
            if arm=='disabled':self.assertEqual(m.rows,PlasticNand.restore(raw).rows)
    def test_cold_and_tamper(self):
        m=Routed().adapt(OBS,17,32);raw=m.snapshot();r=Routed.restore(raw)
        self.assertEqual(r.snapshot(),raw);self.assertEqual([m.predict(context(i)) for i in range(8)],[r.predict(context(i)) for i in range(8)])
        for bad in (raw[:-1],raw+b'x',bytearray(raw),raw[:12]+bytes([raw[12]^1])+raw[13:]):
            with self.assertRaises(ValueError):Routed.restore(bad)
    def test_resigned_noncanonical_rejected(self):
        raw=Routed().snapshot();d=json.loads(raw[9:-32])
        for key,value in (('schema','bad'),('protection',True),('protection',32),('arm','bad'),('extra',0)):
            v=dict(d);v[key]=value;body=json.dumps(v,sort_keys=True,separators=(',',':')).encode();r=b'WSP27'+len(body).to_bytes(4,'big')+body;r+=hashlib.sha256(r).digest()
            with self.assertRaises(ValueError):Routed.restore(r)
    def test_invalid_inputs(self):
        for obs,seed,n in ((list(OBS),17,1),(OBS,True,1),(OBS,1,1),(OBS,17,0),(OBS,17,8193)):
            with self.assertRaises(ValueError):Routed().adapt(obs,seed,n)
        with self.assertRaises(ValueError):Routed(arm='bad')
        m=Routed();m.masks[0]=3
        with self.assertRaises(ValueError):m.snapshot()
        with self.assertRaises(ValueError):Routed().predict((True,0,1))
if __name__=='__main__':unittest.main()
