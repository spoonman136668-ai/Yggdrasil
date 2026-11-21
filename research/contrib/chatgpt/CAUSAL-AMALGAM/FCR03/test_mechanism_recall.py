import json
import unittest
from mechanism_recall import (Stage, StagewiseRecall, best_law, canonical, digest,
                              evaluate, laws)
SHA='86264b41a08d49f558418c0fba367f3a2636befa'

def event(i,c,x1,s2,x2,y):
    return (f'{i+1:064x}',c,x1,s2,x2,y)

class TestRecall(unittest.TestCase):
    def test_complete_law_class(self):
        self.assertEqual(len(laws(2)),8)
        self.assertEqual(len(laws(4)),32)
        for x in ((0,0),(0,1),(1,0),(1,1)):
            self.assertEqual(evaluate((3,0),x),x[0]^x[1])

    def test_initial_no_outcome_leak(self):
        model=StagewiseRecall()
        self.assertEqual(model.transition_forecast(1,0),0.5)
        self.assertEqual(model.reward_forecast(1,0,1,0),0.5)
        self.assertEqual(model.ledger,[])

    def test_pure_read(self):
        model=StagewiseRecall()
        for i in range(60):
            c=i%2; x1=(i//2)%2;x2=(i//4)%2;s2=c^x1
            model.admit_fixture(*event(i,c,x1,s2,x2,s2^x2))
        before=model.checkpoint(SHA)
        for i in range(50):
            model.transition_forecast(i%2,(i//2)%2)
            model.reward_forecast(i%2,(i//2)%2,(i//4)%2,(i//8)%2)
        self.assertEqual(before,model.checkpoint(SHA))

    def test_archive_recall_supported_by_public_evidence(self):
        model=Stage(2)
        for i in range(64):
            c=i&1;x1=(i>>1)&1
            model.observe((c,x1),c^x1)
        a=model.current
        for i in range(64,128):
            c=i&1;x1=(i>>1)&1
            model.observe((c,x1),x1)
        self.assertNotEqual(model.current,a)
        for i in range(128,192):
            c=i&1;x1=(i>>1)&1
            model.observe((c,x1),c^x1)
        self.assertEqual(model.current,a)
        self.assertGreaterEqual(model.recalls,1)
        self.assertLessEqual(len(model.archive),3)

    def test_cold_restore_retains_forecast_and_provenance(self):
        model=StagewiseRecall()
        for i in range(100):
            c=i&1;x1=(i>>1)&1;x2=(i>>2)&1;s2=c^x1
            model.admit_fixture(*event(i,c,x1,s2,x2,s2^x2))
        raw=model.checkpoint(SHA)
        cold=StagewiseRecall.restore(model.ledger,raw,digest(raw),SHA)
        self.assertEqual(raw,cold.checkpoint(SHA))
        self.assertEqual(model.reward_forecast(1,0,1,0),cold.reward_forecast(1,0,1,0))
        with self.assertRaises(ValueError):StagewiseRecall.restore(model.ledger,raw,'f'*64,SHA)
        with self.assertRaises(ValueError):StagewiseRecall.restore(model.ledger,raw,digest(raw),'e'*40)
        corrupted=json.loads(raw);corrupted['scientific_pass']=True
        altered=canonical(corrupted)
        with self.assertRaises(ValueError):StagewiseRecall.restore(model.ledger,altered,digest(altered),SHA)
        changed=list(model.ledger)
        changed[-1]=(changed[-1][0],*changed[-1][1:5],1-changed[-1][5])
        with self.assertRaises(ValueError):StagewiseRecall.restore(changed,raw,digest(raw),SHA)

    def test_duplicate_and_bad_input_do_not_mutate(self):
        model=StagewiseRecall()
        e=event(0,1,0,1,0,1)
        model.admit_fixture(*e);p=model.checkpoint(SHA)
        with self.assertRaisesRegex(ValueError,'DUPLICATE'):
            model.admit_fixture(*e)
        with self.assertRaisesRegex(ValueError,'DUPLICATE'):
            model.admit_fixture(*event(0,1,0,1,0,0))
        with self.assertRaisesRegex(ValueError,'BIT'):
            model.admit_fixture(*event(1,1,True,1,0,1))
        self.assertEqual(model.checkpoint(SHA),p)

    def test_invalid_extra_phase_feature(self):
        model=StagewiseRecall()
        with self.assertRaises(TypeError): model.transition_forecast(1,0,phase='A')
        with self.assertRaises(TypeError): model.reward_forecast(1,0,1,0,phase='B')

    def test_unidentifiable_non_affine_negative(self):
        # No affine XOR function equals x AND y on all four public bit pairs.
        truth={(a,b):a&b for a in (0,1) for b in (0,1)}
        self.assertTrue(all(any(evaluate(law,k)!=v for k,v in truth.items())
                            for law in laws(2)))

    def test_checkpoint_missing_state_rejected(self):
        model=StagewiseRecall()
        model.admit_fixture(*event(0,1,0,1,0,1))
        data=json.loads(model.checkpoint(SHA))
        del data['reward']
        raw=canonical(data)
        with self.assertRaises(ValueError):StagewiseRecall.restore(model.ledger,raw,digest(raw),SHA)

if __name__=='__main__': unittest.main()
