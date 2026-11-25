"""R0 source-free cluster and receipt negatives."""
import time
import unittest
from uj03a_pilot import group
from uj04r_source_audit import audit,split,bucket,prior_keys,unused

def rows():
    out=[]
    for i in range(24):
        a=10+i//2
        out.append((str(i),group('fixture '+chr(97+i)),
                    f'<<{a}+2={a+2}>> then <<{a+2}*2={2*(a+2)}>>'))
    out.append(('reject',group('unsupported question'),'no annotation'))
    return tuple(out)

class R0Tests(unittest.TestCase):
    def test_duplicate_chain_clusters(self):
        rr=rows()
        parts,assignment=split(rr,time.monotonic()+30)
        for i in range(0,24,2):
            self.assertEqual(assignment[rr[i][1]],assignment[rr[i+1][1]])
        self.assertEqual(sum(map(len,parts)),25)
        self.assertEqual(assignment,split(tuple(reversed(rr)),time.monotonic()+30)[1])
        self.assertIsNone(assignment[rr[-1][1]][1])
    def test_audit_custody(self):
        report,receipts=audit(rows(),time.monotonic()+30)
        self.assertEqual(report['group_overlap'],0)
        self.assertEqual(report['exact_full_chain_overlap'],0)
        self.assertEqual(report['fit']['accepted_chains']+report['diagnostic']['accepted_chains'],24)
        self.assertEqual(sum(x['count'] for x in report['group_partitions']),25)
        self.assertFalse(report['source_feasible'])
        self.assertFalse(report['prior_q0_chain_overlap_verified'])
        self.assertEqual(report['model_training_steps'],0)
        self.assertTrue(audit(rows(),time.monotonic()+30,set())[0]['prior_q0_chain_overlap_verified'])
    def test_fail_closed(self):
        with self.assertRaises(RuntimeError):
            split(rows()+rows()[:1],time.monotonic()+30)
        with self.assertRaises(RuntimeError):
            audit(rows(),time.monotonic()-1)
        with self.assertRaises(ValueError):
            prior_keys(b'fake')
        with self.assertRaises(ValueError):
            unused(b'fake',set())
