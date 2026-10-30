"""MG92 source-only selected-feedback and separate-process custody tests.

Source-shaped fixtures prove algorithm integrity only, not original task win.
"""
import os
import subprocess
import sys
import tempfile
import unittest
from research.native.itd02.mg91.test_teacher_values import shaped
from research.native.itd02.mg91.native_prototypes import PublicRewardPrototypes
from research.native.itd02.mg92.feedback_cells import PublicFeedbackGate
from research.native.itd02.mg19.original_mission_cells import OriginalMissionAdapter

class MG92Feedback(unittest.TestCase):
    def test_same_real_teacher_dataset_and_bounded_fitted_policy(self):
        traces=shaped()
        native=PublicFeedbackGate()
        original=PublicRewardPrototypes()
        native.fit(traces)
        original.fit(traces)
        self.assertEqual(native.data_sha,original.data_sha)
        self.assertEqual(native.training_count,original.training_count)
        self.assertEqual(native.examples,original.examples)
        self.assertEqual(native.choose(traces[0]["steps"][0]["before"])["action"],
                         original.choose(traces[0]["steps"][0]["before"])["action"])

    def test_actual_selected_unchanged_consequence_creates_penalty(self):
        model=PublicFeedbackGate()
        model.fit(shaped())
        before=shaped()[0]["steps"][0]["before"]
        adapter=OriginalMissionAdapter()
        adapter.reset_public(before)
        model.start_session(adapter,"mg92-selected-fixture",live=False)
        chosen=model.choose(before)["action"]
        initial=model._votes(before)
        for _ in range(8):
            adapter.submit(chosen)
            adapter.complete(before,0.,False,False)
            model.observe_selected(adapter,before,before)
        self.assertEqual(model.feedback_samples,8)
        self.assertEqual(model.failed[
            adapter.ledger[-1]["before_sha"]+":"+str(chosen)],8)
        self.assertEqual(model.streak,8)
        self.assertEqual(model._votes(before),initial)
        self.assertNotEqual(model.choose(before)["action"],chosen)
        self.assertEqual(model.training_count,2)

    def test_unselected_source_does_not_modify_memory(self):
        model=PublicFeedbackGate()
        model.fit(shaped())
        before=shaped()[0]["steps"][0]["before"]
        adapter=OriginalMissionAdapter()
        adapter.reset_public(before)
        model.start_session(adapter,"unselected",live=False)
        prior=model.checkpoint()
        with self.assertRaises(ValueError):
            model.observe_selected(adapter,before,before)
        self.assertEqual(prior,model.checkpoint())

    def test_independent_cold_and_corruption(self):
        model=PublicFeedbackGate()
        model.fit(shaped())
        wire=model.checkpoint()
        self.assertEqual(PublicFeedbackGate.restore(wire).checkpoint(),wire)
        with self.assertRaises(ValueError):
            PublicFeedbackGate.restore(wire+b"bad")
        with tempfile.TemporaryDirectory() as folder:
            path=os.path.join(folder,"model.bin")
            with open(path,"wb") as stream:
                stream.write(wire)
            script=("import pathlib,sys; "
                    "from research.native.itd02.mg92.feedback_cells import PublicFeedbackGate; "
                    "b=pathlib.Path(sys.argv[1]).read_bytes(); "
                    "assert PublicFeedbackGate.restore(b).checkpoint()==b")
            subprocess.run([sys.executable,"-B","-c",script,path],timeout=30,check=True)

if __name__=="__main__":
    unittest.main()
