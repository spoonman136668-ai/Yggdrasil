"""Explicit tiny fixtures, nonstudy seed. No registered generator or scores."""
import time
import unittest
from study_worker import execute_explicit,verify_pair,child,worker,encode
from transfer_study_eval import ARMS


def fixture():
    held=(510,511)
    phases=[]
    for phase,key in enumerate((0,1,0,2)):
        phases.append(dict(phase=phase,events=[(key,i,(i%2,1,0,1)) for i in range(12)],
                           a_law=[[5]*4 for _ in held],c_law=[[5]*4 for _ in held],negative_key=2))
    return held,phases

class WorkerFixtures(unittest.TestCase):
    def test_all_arms_two_passes(self):
        held,phases=fixture()
        for arm in ARMS:
            with self.subTest(arm=arm):
                task=(1,'fixture',arm,False)
                a=execute_explicit(task,held,phases,False,time.monotonic()+60)
                b=execute_explicit(task,held,phases,True,time.monotonic()+60)
                self.assertFalse(a['cold_identity'])
                verify_pair(a,b)
                self.assertTrue(a['cold_identity'] and b['cold_identity'])
                self.assertEqual(a['cursor'],48)
                self.assertGreater(b['traced_peak_bytes'],0)
                self.assertGreater(a['peak_rss_bytes'],0)
                self.assertEqual(len(a['readout_boundaries']),4)
                self.assertIsNone(a['traced_peak_bytes'])
    def test_deadline(self):
        held,phases=fixture()
        with self.assertRaises(TimeoutError):
            execute_explicit((1,'fixture','count',False),held,phases,False,time.monotonic()-1)
    def test_held_leakage(self):
        held,phases=fixture(); phases[0]['events'][0]=(0,510,(0,)*4)
        with self.assertRaises(ValueError):
            worker(dict(arm='count',seed=1,traced=False,held=held,phases=phases,
                        checkpoint=None,expected_before=None,expected_cursor=0))
    def test_bad_predecessor(self):
        held,phases=fixture()
        with self.assertRaises(ValueError):
            worker(dict(arm='count',seed=1,traced=False,held=held,phases=phases[1:2],
                        checkpoint=None,expected_before=None,expected_cursor=0))
    def test_mismatch(self):
        held,phases=fixture(); task=(1,'fixture','count',False)
        a=execute_explicit(task,held,phases,False,time.monotonic()+60)
        b=execute_explicit(task,held,phases,True,time.monotonic()+60)
        b['readout_boundaries'][0]='bad'
        with self.assertRaises(ValueError): verify_pair(a,b)
        self.assertFalse(a['cold_identity'])

if __name__=='__main__': unittest.main()
