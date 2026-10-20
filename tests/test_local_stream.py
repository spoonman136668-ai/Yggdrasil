"""Native experience substrate checks; development only, no scientific first-use."""
import io
import json
import math
import unittest
from yggdrasil.local_stream import LocalStream
from yggdrasil.cells import DevelopmentalCells
from scripts.native_cells import run

class TestLocalExperience(unittest.TestCase):
    def test_exact_one_hop_and_query_blind(self):
        m=LocalStream()
        m.weights[1][2]=2.0  # diagnostic probe of permitted local left input
        m.state[0]=.9
        x=[0.0]*8
        high=m.predict_local(x)[1]
        m.state[0]=0.0
        low=m.predict_local(x)[1]
        self.assertGreater(high,low)
        m.state[5]=.9  # not a physical neighbor of cell 1
        self.assertEqual(m.predict_local(x)[1],low)
        prior=m.snapshot_local()
        for _ in range(20):m.predict_local(x)
        self.assertEqual(m.snapshot_local(),prior)

    def test_learning_damage_and_new_experience_recovery(self):
        m=LocalStream()
        x=[1.0]*8
        observed=[1.0]*8
        for _ in range(110):m.observe_local(x,observed,.1)
        before=m.predict_local(x)[3]
        self.assertGreater(before,.8)
        preserved=m.snapshot_local()
        m.lesion_local(3)
        damaged=m.predict_local(x)[3]
        self.assertEqual(damaged,.5)
        m.rehabilitate_local(3)
        reopened=m.predict_local(x)[3]
        self.assertEqual(reopened,.5)
        for _ in range(110):m.observe_local(x,observed,.1)
        recovered=m.predict_local(x)[3]
        self.assertGreater(recovered,.8)
        # This is retraining, not proven faster regeneration.
        self.assertGreater(recovered,damaged)
        n=LocalStream();n.restore_local(preserved)
        self.assertEqual(n.snapshot_local(),preserved)
        self.assertNotEqual(m.snapshot_local(),preserved)
        print(f"NCI04_Y_FUNCTIONAL_DEV_BEFORE={before:.6f} DAMAGED={damaged:.6f} RETRAINED={recovered:.6f}")

    def test_invalid_observations_are_atomic(self):
        m=LocalStream()
        before=m.snapshot_local()
        for bad in ([0.0]*7,[math.nan]*8,[2.0]*8):
            with self.assertRaises(ValueError):m.observe_local(bad,[0.0]*8)
            self.assertEqual(m.snapshot_local(),before)
        with self.assertRaises(ValueError):m.restore_local("{}")
        self.assertEqual(m.snapshot_local(),before)
        with self.assertRaises(ValueError):m.rehabilitate_local(0)
        with self.assertRaises(ValueError):m.lesion_local(20)

    def test_native_cli_additive_contract_and_existing_baseline(self):
        inputs=[{"op":"local_observe","stimulus":[1]*8,"observed_next":[1]*8},
                {"op":"local_predict","stimulus":[1]*8},
                {"op":"local_snapshot"},
                {"op":"predict","bits":[0]*8}]
        output=io.StringIO()
        run(io.StringIO("".join(json.dumps(item)+"\n" for item in inputs)),output)
        rows=[json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual(len(rows),3)
        self.assertIn("probabilities",rows[0])
        self.assertEqual(rows[1]["schema"],"yggdrasil.nci04.localstream.v1")
        self.assertEqual(len(rows[2]["probabilities"]),8)
        with self.assertRaises(ValueError):
            run(io.StringIO('{"op":"local_lesion","cell":19}\n'),io.StringIO())

    def test_trained_equal_information_local_baseline_retained(self):
        x=[1,0,1,0,1,0,1,0]
        y=[0,1,0,1,0,1,0,1]
        m=LocalStream()
        baseline=DevelopmentalCells()
        for _ in range(96):
            m.observe_local(x,y,.1)
            baseline.observe(x,y,.1)
        native=m.predict_local(x)
        strong=baseline.predict(x)
        mse=lambda values:sum((p-target)**2 for p,target in zip(values,y))/8
        candidate_loss=mse(native);strong_loss=mse(strong)
        print(f"NCI04_Y_NATIVE_DEV_MSE={candidate_loss:.7f} TRAINED_NATIVE_LOCAL_CONTROL_MSE={strong_loss:.7f} NATIVE_WEIGHTS=32 BASELINE_WEIGHTS=56")
        self.assertTrue(math.isfinite(candidate_loss) and math.isfinite(strong_loss))

if __name__=="__main__":
    unittest.main()
