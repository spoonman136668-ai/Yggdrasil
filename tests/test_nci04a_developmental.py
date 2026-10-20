"""NCI-04A native local-genome contract checks."""
import io
import json
import unittest
from yggdrasil.developmental import LocalGenome
from scripts.nci04a_developmental import run

class NativeDevelopment(unittest.TestCase):
    def test_local_learning_snapshot_and_lesion(self):
        m=LocalGenome();bits=[0,1,1,0,0,1,0,1]
        for i in range(150): m.observe(bits,[1,0,1,0,1,0,1,0])
        before=m.snapshot();p=m.predict(bits)
        self.assertNotEqual(p[0],.5)
        n=LocalGenome();n.restore(before)
        self.assertEqual(n.snapshot(),before)
        n.lesion(0)
        self.assertEqual(n.role_weights(0),[1/3]*3)
        self.assertNotEqual(n.role_weights(1),[1/3]*3)
        self.assertEqual(len(n.predict(bits)),8)
    def test_fail_closed(self):
        m=LocalGenome();before=m.snapshot()
        for bits,outcomes in [([0]*7,[0]*8),([0]*8,[3]+[0]*7)]:
            with self.assertRaises(ValueError): m.observe(bits,outcomes)
        self.assertEqual(m.snapshot(),before)
        for bad in ['{','{}','{"schema":"bad"}']:
            with self.assertRaises((ValueError,TypeError)): m.restore(bad)
        with self.assertRaises(ValueError): m.lesion(9)
    def test_local_only_information(self):
        m=LocalGenome();a=[0]*8;b=[0]*8
        b[4]=1
        self.assertEqual(m.predict_cell(a,0),m.predict_cell(b,0))
        b[1]=1
        self.assertEqual(m.predict_cell(a,0),m.predict_cell(b,0))
        for _ in range(15): m.train_cell(b,0,1)
        self.assertNotEqual(m.predict_cell(a,0),m.predict_cell(b,0))
    def test_offline_entrypoint(self):
        events=[{"op":"observe","bits":[0]*8,"consequences":[1]*8},{"op":"predict","bits":[0]*8},{"op":"cell_roles","cell":0},{"op":"snapshot"}]
        stream=io.StringIO("\n".join(json.dumps(x) for x in events)+"\n")
        out=io.StringIO()
        run(stream,out)
        self.assertEqual(len(out.getvalue().strip().splitlines()),3)
        with self.assertRaises(ValueError):
            run(io.StringIO('{"op":"execute"}\n'),io.StringIO())

if __name__=="__main__": unittest.main()
