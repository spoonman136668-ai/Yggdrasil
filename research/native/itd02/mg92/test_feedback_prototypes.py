"""MG92 source-only feedback and independent-process canonical model regression.

Fixtures are *not* evidence of authentic original-world task completion.
"""
import os
import subprocess
import sys
import tempfile
import unittest
from research.native.itd02.mg92.feedback_prototypes import SourceFeedbackPrototypes
from research.native.itd02.mg91.native_prototypes import PublicRewardPrototypes
from research.native.itd02.mg91.independent_linear import IndependentLinearControl
from research.native.itd02.mg91.test_teacher_values import shaped
from research.native.itd02.mg19.original_mission_cells import OriginalMissionAdapter
from research.native.itd02.r10.public_adapter import digest

class MG92FeedbackTests(unittest.TestCase):
    def trained(self):
        samples=shaped()
        candidate=SourceFeedbackPrototypes()
        original=PublicRewardPrototypes()
        linear=IndependentLinearControl()
        for model in (candidate,original,linear):
            model.fit(samples)
        self.assertEqual(candidate.data_sha,original.data_sha)
        self.assertEqual(candidate.data_sha,linear.data_sha)
        return candidate,original,linear

    def test_feedback_does_not_affect_original_trained_parent(self):
        policy,baseline,linear=self.trained()
        a=shaped()[0]["steps"][0]["before"]
        adapter=OriginalMissionAdapter()
        adapter.reset_public(a)
        policy.start_session(adapter,"mg92-public-test",live=False)
        baseline.start_session(adapter,"mg91-original-test",live=False)
        self.assertEqual(policy.choose(a)["action"],baseline.choose(a)["action"])
        parent=policy.parent.examples
        manifest=policy.data_sha
        selected=policy.choose(a)["action"]
        for _ in range(8):
            adapter.submit(selected)
            adapter.complete(a,0.,False,False)
            policy.observe_selected(adapter,a,a)
        self.assertEqual(policy.parent.examples,parent)
        self.assertEqual(policy.data_sha,manifest)
        self.assertEqual(policy.observed,8)
        self.assertEqual(policy.changes,0)
        self.assertEqual(policy.streak,8)
        self.assertEqual(policy.unchanged[digest(a)+":"+str(selected)],8)
        self.assertNotEqual(policy.choose(a)["action"],selected)
        self.assertEqual(baseline.choose(a)["action"],selected)

    def test_same_source_change_not_penalized_and_session_reset(self):
        policy,_,_=self.trained()
        a=shaped()[0]["steps"][0]["before"]
        b=shaped()[0]["steps"][1]["before"]
        original=OriginalMissionAdapter()
        original.reset_public(a)
        policy.start_session(original,"fixture-only",live=False)
        original.submit(0)
        original.complete(b,0.,False,False)
        policy.observe_selected(original,a,b)
        self.assertEqual(policy.changes,1)
        self.assertEqual(policy.unchanged,{})
        self.assertEqual(policy.streak,1)
        reset=OriginalMissionAdapter()
        reset.reset_public(a)
        policy.start_session(reset,"second episode",live=False)
        self.assertEqual(policy.observed,0)
        self.assertEqual(policy.streak,0)
        self.assertEqual(policy.parent.training_count,2)

    def test_unselected_source_fails_closed_without_state_mutation(self):
        p,_,_=self.trained()
        a=shaped()[0]["steps"][0]["before"]
        adapter=OriginalMissionAdapter()
        adapter.reset_public(a)
        p.start_session(adapter,"mg92-unselected",live=False)
        prior=p.checkpoint()
        with self.assertRaises(ValueError):
            p.observe_selected(adapter,a,a)
        self.assertEqual(p.checkpoint(),prior)

    def test_cold_checkpoint_is_independent_process_verifiable(self):
        p,_,_=self.trained()
        a=shaped()[0]["steps"][0]["before"]
        adapter=OriginalMissionAdapter()
        adapter.reset_public(a)
        p.start_session(adapter,"source-cold",live=False)
        adapter.submit(0)
        adapter.complete(a,0.,False,False)
        p.observe_selected(adapter,a,a)
        wire=p.checkpoint()
        self.assertEqual(SourceFeedbackPrototypes.restore(wire).checkpoint(),wire)
        with self.assertRaises(ValueError):
            SourceFeedbackPrototypes.restore(wire+b"!tamper")
        with tempfile.TemporaryDirectory() as temp:
            target=os.path.join(temp,"source.bin")
            with open(target,"wb") as f:f.write(wire)
            script=("import pathlib,sys; "
                    "from research.native.itd02.mg92.feedback_prototypes import SourceFeedbackPrototypes; "
                    "x=pathlib.Path(sys.argv[1]).read_bytes(); "
                    "assert SourceFeedbackPrototypes.restore(x).checkpoint()==x")
            subprocess.run([sys.executable,"-B","-c",script,target],check=True,timeout=30)

if __name__=="__main__":
    unittest.main()
