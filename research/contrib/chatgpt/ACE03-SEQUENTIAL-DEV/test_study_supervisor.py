"""Fabricated records only; never generate registered world observations."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from study_gate import TASKS
from study_worker import expected_stream_identity
from study_supervisor import Journal, EXPERIMENT, match_identity, _collect, _classify_readback, read_record

def identity():
    return dict(experiment=EXPERIMENT,source_sha='1'*40,source_tree='2'*40,
        supervisor_blob='3'*40,prereg_blob='4'*40,runner='YGG-C-LINKDEADKB',
        runtime_sha256='5'*64,admission_sha256='6'*64,qualifier_run=1)

def fabricated(task):
    # Fabricated miniature input only, no registered generator or observations.
    s,f,a,alter=task
    held=(511,)
    return held,[dict(phase=i,events=[(k,0,(0,1,0,1) if alter and i<3 else (1,0,1,0))],
        a_law=[[5]*4],c_law=[[5]*4],negative_key=2) for i,k in enumerate((0,1,0,2))]

def fabricated_row(task,held,phases,traced,stop):
    s,f,a,alter=task; h,c=expected_stream_identity(phases)
    return dict(seed=s,family=f,arm=a,alter_prior=alter,cursor=2816,cold_identity=False,
        wall_seconds=.1,compute_seconds=.01,peak_rss_bytes=10000,
        traced_peak_bytes=1000 if traced else None,c_final=.19 if a=='candidate' else .20,
        c_cold=.25,c_early=.25,balanced_null_brier=.25,a_boundaries=[.20]*4,
        checkpoint_boundaries=[dict(bytes=100,sha256='0'*64)]*4,
        unknown_abstentions=1,unknown_prediction=[.5]*4,stream_sha256=h,c_trace_sha256=c,
        c_forecast_sha256='2'*64,readout_boundaries=['3'*64]*4)

class Clock:
    def __init__(self):self.t=0.
    def __call__(self):
        self.t+=.1; return self.t

class SupervisorFixtures(unittest.TestCase):
    def test_identity_drift(self):
        for key,value in [('runner','unrelated'),('source_sha','7'*40),('admission_sha256','8'*64)]:
            altered=dict(identity());altered[key]=value
            with self.assertRaises(ValueError):match_identity(identity(),altered)
        match_identity(identity(),identity())
    def test_missing_and_partial_start_are_denied(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve()
            with self.assertRaises(ValueError):Journal(root/'missing',identity())
            (root/EXPERIMENT).mkdir()
            with self.assertRaises(FileExistsError):Journal(root,identity())
    def test_exclusive_start_and_tamper(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve(); j=Journal(root,identity())
            with self.assertRaises(FileExistsError):Journal(root,identity())
            (j.path/'STARTED.json').write_bytes(b'{}')
            with self.assertRaises(ValueError):j.verify_started()
    def test_complete_and_archive_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            j=Journal(Path(tmp).resolve(),identity())
            r=_collect(j,fabricated,fabricated_row,clock=Clock())
            self.assertEqual(r['rows'],480)
            terminal,h=read_record(j.path/'TERMINAL.json')
            self.assertEqual(terminal['state'],'RAW_COMPLETE')
            with self.assertRaises(ValueError):_classify_readback(j,'0'*64,r['row_hashes'])
            bad=list(r['row_hashes']);bad[0]='0'*64
            with self.assertRaises(ValueError):_classify_readback(j,h,bad)
            self.assertEqual(_classify_readback(j,h,r['row_hashes'])['arithmetic_disposition'],'DEV_PASS_CONDITIONAL')
            # Original raw rows must not acquire post-comparison cold identity.
            self.assertFalse(j.read_row(0)[0]['row']['cold_identity'])
            with self.assertRaises(FileExistsError):Journal(Path(tmp).resolve(),identity())
    def test_repeated_collection_rejected_before_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            j=Journal(Path(tmp).resolve(),identity())
            with self.assertRaises(TimeoutError):
                _collect(j,fabricated,lambda *args: (_ for _ in ()).throw(TimeoutError('fixture')),clock=Clock())
            def forbidden(*args): self.fail('input built after consumed trial')
            with self.assertRaisesRegex(ValueError,'prior collection'):_collect(j,forbidden,forbidden,clock=Clock())
    def test_failure_consumes_and_preserves_raw(self):
        with tempfile.TemporaryDirectory() as tmp:
            j=Journal(Path(tmp).resolve(),identity())
            def fail(task,*args):
                if task==TASKS[1]:raise TimeoutError('fabricated failure')
                return fabricated_row(task,*args)
            with self.assertRaises(TimeoutError):_collect(j,fabricated,fail,clock=Clock())
            self.assertEqual(read_record(j.path/'TERMINAL.json')[0]['state'],'FAILED_CONSUMED')
            self.assertEqual(j.read_row(0)[0]['slot'],0)
            with self.assertRaises(FileExistsError):Journal(Path(tmp).resolve(),identity())
    def test_counterfactual_or_arm_mismatch_is_denied(self):
        with tempfile.TemporaryDirectory() as tmp:
            j=Journal(Path(tmp).resolve(),identity())
            def drift(task):
                if task==TASKS[1]:
                    held,phases=fabricated(task);phases[0]['events'][0]=(0,1,(1,0,1,0))
                    return held,phases
                return fabricated(task)
            with self.assertRaisesRegex(ValueError,'input parity'):_collect(j,drift,fabricated_row,clock=Clock())
    def test_slot_duplicate_and_deadline(self):
        with tempfile.TemporaryDirectory() as tmp:
            j=Journal(Path(tmp).resolve(),identity());j.row(0,{},['a','b'])
            with self.assertRaises(FileExistsError):j.row(0,{},['a','b'])
        with tempfile.TemporaryDirectory() as tmp:
            j=Journal(Path(tmp).resolve(),identity())
            times=iter([0.,14401.])
            with self.assertRaisesRegex(ValueError,'aggregate deadline'):_collect(j,fabricated,fabricated_row,clock=lambda:next(times))
            self.assertEqual(read_record(j.path/'TERMINAL.json')[0]['state'],'FAILED_CONSUMED')

if __name__=='__main__':unittest.main()
