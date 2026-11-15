"""WSP113 fixtures use only manually fabricated edge masks; no hidden oracle."""
import unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from native import DirectCausalWriter,transition_with_edges,EDGES,SUPPORT
from controls import ExactBayesianGraph,IndependentSymbolicGraph,FittedKernelGraph,independent_effect

def fake_public_train():
    return tuple(tuple((s,a,independent_effect(s,a,(w*7)%64))
                       for s in range(16) for a in range(8))
                 for w in range(128))

class TestInterventionCausalMemory(unittest.TestCase):
    def test_native_equations_numeric_edge_writes_and_real_downstream_effect(self):
        for mask in (0,3,11,27,63):
            weights=[float((mask>>i)&1) for i in range(6)]
            for s in (0,1,3,7,8,15):
                for a in range(8):
                    self.assertEqual(transition_with_edges(s,a,weights),
                                     independent_effect(s,a,mask))
        # Intervention into node zero can propagate changes to descendants.
        self.assertNotEqual(independent_effect(0,0,63),independent_effect(0,1,63))
    def test_eight_interventions_and_cold_replay(self):
        mask=0b101101
        for Model in (DirectCausalWriter,IndependentSymbolicGraph,ExactBayesianGraph):
            model=Model()
            seen=[]
            for _ in range(8):
                s,a=model.choose()
                self.assertIn((s,a),SUPPORT)
                self.assertNotIn((s,a),seen)
                seen.append((s,a))
                y=independent_effect(s,a,mask)
                model.observe(s,a,y)
                self.assertEqual(model.predict(s,a),y)
            self.assertEqual(len(seen),8)
            with self.assertRaises(ValueError):model.choose()
        direct=DirectCausalWriter()
        for s,a in seen:
            direct.observe(s,a,independent_effect(s,a,mask))
        state=direct.checkpoint()
        restored=DirectCausalWriter.restore(state)
        self.assertEqual(len(direct.programmed_bytes),24)
        self.assertEqual(direct.programmed_bytes,restored.programmed_bytes)
        self.assertEqual([direct.predict(s,a) for s in range(16) for a in range(8)],
                         [restored.predict(s,a) for s in range(16) for a in range(8)])
        self.assertEqual(direct.triple(11,(0,3,7)),restored.triple(11,(0,3,7)))
        bad={"schema":state["schema"],"sha256":state["sha256"],
             "fields":dict(state["fields"])}
        w=bad["fields"]["weights_le_f32"]
        bad["fields"]["weights_le_f32"]=("ff" if w[:2]!="ff" else "00")+w[2:]
        with self.assertRaises(ValueError):DirectCausalWriter.restore(bad)
    def test_matched_control_training_and_known_effect_memory(self):
        train=fake_public_train()
        model=FittedKernelGraph(train)
        mask=0b111111
        for _ in range(8):
            s,a=model.choose()
            y=independent_effect(s,a,mask)
            model.observe(s,a,y)
            self.assertEqual(model.predict(s,a),y)
        with self.assertRaises(ValueError):model.choose()
        self.assertEqual(len(train),128)
        self.assertEqual(len(train[0]),128)
    def test_wrong_binding_and_no_feedback_controls(self):
        direct=DirectCausalWriter()
        no_feedback=[direct.predict(s,a) for s in (0,3,8) for a in range(8)]
        true=[independent_effect(s,a,63) for s in (0,3,8) for a in range(8)]
        self.assertNotEqual(no_feedback,true)
        with self.assertRaises(ValueError):direct.observe(8,1,3)
        with self.assertRaises(ValueError):direct.observe(0,0,1)
    def test_public_fixtures_do_not_import_hidden_generator(self):
        for filename in ("native.py","controls.py"):
            content=(ROOT/filename).read_text(encoding="utf-8")
            self.assertNotIn("from oracle import",content)
            self.assertNotIn("import oracle",content)
        self.assertFalse((ROOT/"SCIENTIFIC_PASS.json").exists())
        self.assertFalse((ROOT/"PROTECTED_FIRST_USE.json").exists())

if __name__=="__main__":
    unittest.main()
