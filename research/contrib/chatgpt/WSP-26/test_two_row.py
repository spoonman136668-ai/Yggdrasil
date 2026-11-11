import hashlib
import json
import random
import unittest
from two_row import TwoRow,PlasticNand,pack_rows,unpack_rows,lanes,forward_lanes,error_lanes,changed_proposal,context,LENGTHS
from joint_credit import JointNand,errors,proposal,threshold
from structural import forward

OBS=tuple((context(i),i%2) for i in (0,1,2,4,7,3))
class TwoRowTests(unittest.TestCase):
    def test_independent_256_circuit_full_numeric_differential(self):
        rng=random.Random(26001)
        for _ in range(256):
            rows=[]
            for i,n in enumerate(LENGTHS):
                address=rng.randrange(n if i==12 else n+1);rows.append([int(j==address) for j in range(n)])
            masks=pack_rows(rows);self.assertEqual(unpack_rows(masks),rows)
            for x in map(context,range(8)):self.assertEqual(forward_lanes(masks,x,1),forward(rows,x))
            label=sum(y<<i for i,(x,y) in enumerate(OBS));e=error_lanes(masks,lanes(OBS),label)
            self.assertEqual([(e>>j)&1 for j in range(6)],errors(rows,OBS))
    def test_single_trajectory_matches_unchanged_numeric_reference(self):
        # Fixed prefix audits only, no primary outcomes or tuning.
        for seed in (17,29,43,71):
            base=PlasticNand();initial=base.snapshot();model=TwoRow(initial,'single_protected').adapt(OBS,seed,128)
            ref=JointNand(initial);ref.protection=[1-e for e in errors(ref.rows,OBS)[:5]];rng=random.Random(seed)
            for _ in range(128):
                j=rng.randrange(13);k=rng.randrange(LENGTHS[j]);g=rng.randrange(6);a=rng.randrange(3+g);b=rng.randrange(3+g)
                trial=proposal(ref.rows,(j,k,g,a,b),False);before=errors(ref.rows,OBS);after=errors(trial,OBS)
                reward=threshold(sum(before)-sum(after))*threshold(-sum(p*e for p,e in zip(ref.protection,after[:5])))
                ref.rows=[[a+reward*(b-a) for a,b in zip(old,new)] for old,new in zip(ref.rows,trial)]
            self.assertEqual(model.rows,ref.rows)
    def test_pair_last_write_wins_and_other_rows_untouched(self):
        old=pack_rows(PlasticNand().rows);new=changed_proposal(old,(0,2,0,1,0),True)
        self.assertEqual(new[0],2);self.assertEqual(new[1:],old[1:])
    def test_protection_disabled_and_exact_budget_prefix(self):
        initial=PlasticNand().snapshot()
        for arm in ('mixed_protected','single_protected','pair_protected','disabled'):
            m=TwoRow(initial,arm).adapt(OBS,17,32)
            self.assertEqual((m.proposals,m.gate_evaluations,m.noise_draws),(32,2304,160))
            e=error_lanes(m.masks,lanes(OBS),sum(y<<i for i,(x,y) in enumerate(OBS)))
            self.assertEqual(e&m.protection,0)
            if arm=='disabled':self.assertEqual(m.rows,PlasticNand.restore(initial).rows)
    def test_cold_full_state_and_corrupt_checkpoint(self):
        m=TwoRow().adapt(OBS,17,32);raw=m.snapshot();r=TwoRow.restore(raw)
        self.assertEqual(r.snapshot(),raw);self.assertEqual([r.predict(context(i)) for i in range(8)],[m.predict(context(i)) for i in range(8)])
        for bad in (raw[:-1],raw+b'x',bytearray(raw),raw[:12]+bytes([raw[12]^1])+raw[13:]):
            with self.assertRaises(ValueError):TwoRow.restore(bad)
    def test_resigned_invalid_schema_and_protection(self):
        raw=TwoRow().snapshot();d=json.loads(raw[9:-32])
        for key,value in (('schema','bad'),('protection',True),('protection',32),('arm','bad'),('extra',0)):
            v=dict(d);v[key]=value;body=json.dumps(v,sort_keys=True,separators=(',',':')).encode();r=b'WSP26'+len(body).to_bytes(4,'big')+body;r+=hashlib.sha256(r).digest()
            with self.assertRaises(ValueError):TwoRow.restore(r)
    def test_invalid_examples_seed_mode_state(self):
        for obs,seed,n in ((list(OBS),17,1),(OBS,True,1),(OBS,1,1),(OBS,17,0),(OBS,17,8193)):
            with self.assertRaises(ValueError):TwoRow().adapt(obs,seed,n)
        with self.assertRaises(ValueError):TwoRow(arm='bad')
        m=TwoRow();m.masks[0]=3
        with self.assertRaises(ValueError):m.snapshot()
        with self.assertRaises(ValueError):TwoRow().predict((True,0,1))

if __name__=='__main__':unittest.main()
