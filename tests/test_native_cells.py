"""T45-O native local-development candidate checks."""
import io
import json
import unittest
from yggdrasil.cells import DevelopmentalCells
from scripts.native_cells import run

class TestNativeCells(unittest.TestCase):
    def test_learning_retention_differentiation_and_lesion(self):
        m=DevelopmentalCells()
        bits=[1,0,1,0,1,0,1,0]
        targets=[1,1,1,1,0,0,0,0]
        before=m.predict(bits)
        for _ in range(120):
            m.observe(bits,targets)
        after=m.predict(bits)
        self.assertGreater(after[0],before[0])
        self.assertLess(after[4],before[4])
        self.assertNotEqual(m.weights[0],m.weights[4])
        snap=m.snapshot()
        n=DevelopmentalCells();n.restore(snap)
        self.assertEqual(n.snapshot(),snap)
        n.lesion(4)
        self.assertGreater(n.predict(bits)[4],after[4])
        expected=[(a+b)/2 for a,b in zip(n.weights[3],n.weights[5])]
        n.neighbor_copy_baseline(4)
        self.assertEqual(n.weights[4],expected)
        # If neighbors carry opposite functions, restoration can cancel to zero;
        # this is explicitly NOT accepted regeneration evidence.
    def test_fail_closed(self):
        m=DevelopmentalCells();initial=m.snapshot()
        for args in [([0]*7,[0]*8,.02),([0]*8,[2]+[0]*7,.02),([0]*8,[0]*8,float("nan"))]:
            with self.assertRaises(ValueError):
                m.observe(*args)
            self.assertEqual(m.snapshot(),initial)
        with self.assertRaises(ValueError):
            m.restore('{"schema":"wrong"}')
        with self.assertRaises(ValueError):
            m.lesion(20)
    def test_offline_cli(self):
        events=[
            {"op":"observe","bits":[0]*8,"consequences":[1]*8},
            {"op":"predict","bits":[0]*8},
            {"op":"snapshot"}
        ]
        out=io.StringIO()
        run(io.StringIO("\n".join(json.dumps(e) for e in events)+"\n"),out)
        self.assertEqual(len(out.getvalue().strip().splitlines()),2)
        with self.assertRaises(ValueError):
            run(io.StringIO('{"op":"execute"}\n'),io.StringIO())

if __name__=="__main__":
    unittest.main()
