"""Fabricated accounting records only, never a scientific trial."""
import unittest
import hashlib
from study_gate import TASKS, PRIMARY, COUNTERFACTUAL, classify, allocation_probe


def expected():
    # Fabricated distinct identities; no registered generator.
    return {(s,f,a,x):(hashlib.sha256(f'{s}:{f}:{x}'.encode()).hexdigest(),
                       hashlib.sha256(f'{s}:{f}:C'.encode()).hexdigest()) for s,f,a,x in TASKS}


def evaluate(a,b,t):
    return classify(a,b,t,expected())


def records(traced):
    identities=expected()
    return [dict(seed=s,family=f,arm=a,alter_prior=x,cursor=2816,cold_identity=True,
        wall_seconds=1.,compute_seconds=.5,peak_rss_bytes=10000000,
        traced_peak_bytes=10000 if traced else None,c_final=.19 if a=='candidate' else .20,
        c_cold=.25,c_early=.25,balanced_null_brier=.25,a_boundaries=[.20]*4,
        checkpoint_boundaries=[dict(bytes=100,sha256='0'*64)]*4,
        unknown_abstentions=1,unknown_prediction=[.5]*4,stream_sha256=identities[(s,f,a,x)][0],c_trace_sha256=identities[(s,f,a,x)][1],c_forecast_sha256='2'*64)
        for s,f,a,x in TASKS]


class GateFixtures(unittest.TestCase):
    def test_schedule(self):
        self.assertEqual((len(PRIMARY),len(COUNTERFACTUAL),len(TASKS)),(224,16,240))
        self.assertEqual(len(set(TASKS)),240)

    def test_conditional_pass(self):
        r=evaluate(records(False),records(True),500.)
        self.assertEqual(r['arithmetic_disposition'],'DEV_PASS_CONDITIONAL')
        self.assertFalse(r['scientific_gain_verified'])

    def test_invalid_custody_and_budget(self):
        for field,value in [('cursor',2815),('cold_identity',False),('peak_rss_bytes',2**30),
                            ('unknown_abstentions',0),('wall_seconds',61)]:
            a,b=records(False),records(True)
            a[0][field]=value
            self.assertEqual(evaluate(a,b,500.)['arithmetic_disposition'],'INVALID')
        a,b=records(False),records(True)
        self.assertEqual(evaluate(a[:-1],b,500.)['arithmetic_disposition'],'INVALID')
        self.assertEqual(evaluate(a+[a[0]],b,500.)['arithmetic_disposition'],'INVALID')
        self.assertEqual(evaluate(a,b,479.)['arithmetic_disposition'],'INVALID')
        b[0]['c_final']=.18
        self.assertEqual(evaluate(a,b,500.)['arithmetic_disposition'],'INVALID')

    def test_negative_preserved(self):
        for field,value in [('c_final',.21),('a_boundaries',[.2,.23,.2,.2])]:
            a,b=records(False),records(True)
            a[0][field]=b[0][field]=value
            self.assertEqual(evaluate(a,b,500.)['arithmetic_disposition'],'DEV_NO_GO')
        a,b=records(False),records(True)
        a[0]['compute_seconds']=.9
        for row in a:
            if row['seed']==a[0]['seed'] and row['family']=='related' and row['arm']=='count':
                row['compute_seconds']=.1
        self.assertEqual(evaluate(a,b,500.)['arithmetic_disposition'],'INVALID')

    def test_counterfactual_identity(self):
        a,b=records(False),records(True)
        for rows in (a,b):
            for row in rows:
                if row['alter_prior'] and row['arm']=='local-only':
                    row['c_forecast_sha256']='3'*64
        self.assertEqual(evaluate(a,b,500.)['arithmetic_disposition'],'INVALID')

    def test_input_parity(self):
        a,b=records(False),records(True)
        a[0]['stream_sha256']=b[0]['stream_sha256']='5'*64
        self.assertEqual(evaluate(a,b,500.)['arithmetic_disposition'],'INVALID')

    def test_counterfactual_unchanged_rejected_even_if_expected(self):
        a,b=records(False),records(True)
        ids=expected()
        for rows in (a,b):
            for row in rows:
                if row['alter_prior']:
                    k=(row['seed'],row['family'],row['arm'],True)
                    ids[k]=ids[(k[0],k[1],k[2],False)]
                    row['stream_sha256']=ids[k][0]
        self.assertEqual(classify(a,b,500.,ids)['arithmetic_disposition'],'INVALID')

    def test_zero_compute_and_missing_expected_rejected(self):
        a,b=records(False),records(True)
        a[0]['compute_seconds']=0.
        self.assertEqual(evaluate(a,b,500.)['arithmetic_disposition'],'INVALID')
        self.assertEqual(classify(records(False),records(True),500.,{})['arithmetic_disposition'],'INVALID')

    def test_allocation_probe(self):
        with allocation_probe(True) as result:
            data=bytearray(8192)
        self.assertGreaterEqual(result['traced_peak_bytes'],len(data))
        self.assertGreater(result['peak_rss_bytes'],0)
        with allocation_probe(False) as result:
            pass
        self.assertIsNone(result['traced_peak_bytes'])

if __name__=='__main__':
    unittest.main()
