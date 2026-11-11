import hashlib
import json
import unittest
from joint_credit import JointNand,PlasticNand,context,proposal,errors,threshold


class WSP20Tests(unittest.TestCase):
    def test_coherent_proposal_wires_legal_gate_and_output(self):
        old=PlasticNand().rows;new=proposal(old,(0,0,2,3,4),True)
        self.assertEqual(new[4],[0,0,0,1,0]);self.assertEqual(new[5],[0,0,0,0,1]);self.assertEqual(new[-1][5],1)
        self.assertEqual(old,PlasticNand().rows)

    def test_single_proposal_does_not_touch_other_rows(self):
        old=PlasticNand().rows;new=proposal(old,(3,2,0,0,0),False)
        for j in range(13):
            if j!=3:self.assertEqual(old[j],new[j])

    def test_numeric_protection_blocks_tradeoff(self):
        before=[0,1];after=[1,0];mask=[1,0]
        reward=threshold(sum(before)-sum(after))*threshold(-sum(p*e for p,e in zip(mask,after)))
        self.assertEqual(reward,0)

    def test_error_neurons_match_independent_binary_comparison(self):
        m=PlasticNand();obs=tuple((context(i),i%2) for i in (0,1,2,4,7,3))
        self.assertEqual(errors(m.rows,obs),[int(m.predict(x)!=y) for x,y in obs])

    def test_cold_custody_and_protection_state(self):
        m=JointNand();m.protection=[1,0,1,1,0];r=JointNand.restore(m.snapshot())
        self.assertEqual(m.snapshot(),r.snapshot());self.assertEqual(m.protection,r.protection)

    def test_corruption_and_nonbinary_protection_rejected(self):
        m=JointNand();raw=m.snapshot()
        for bad in (raw[:-1],raw+b'x',raw[:-1]+bytes([raw[-1]^1])):
            with self.assertRaises(ValueError):JointNand.restore(bad)
        d=json.loads(raw[9:-32]);d['protection']=[True]*5
        body=json.dumps(d,sort_keys=True,separators=(',',':')).encode();p=b'WSP20'+len(body).to_bytes(4,'big')+body
        with self.assertRaises(ValueError):JointNand.restore(p+hashlib.sha256(p).digest())

    def test_invalid_adaptation_rejected_before_proposals(self):
        m=JointNand()
        with self.assertRaises(ValueError):m.adapt((),17,'joint_protected')
        self.assertEqual(m.proposals,0)

    def test_cold_and_separate_models_do_not_alias(self):
        a=JointNand();b=JointNand.restore(a.snapshot());a.rows[0][0]=1
        self.assertNotEqual(a.snapshot(),b.snapshot())


if __name__=='__main__':unittest.main()
