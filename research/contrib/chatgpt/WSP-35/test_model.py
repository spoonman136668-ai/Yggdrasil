import unittest
from model import NumericCircuit,GateTrainCache,table,source_spec,GATES,ROW
from run_dev import generate,oracle,TARGETS,run

def example():
    # Deliberate eight-step signal chain, no hidden target answers in compilation.
    return tuple((0,1,table(6)) if i==0 else (i+2,2,table(6)) for i in range(8))

class BlankCircuitTests(unittest.TestCase):
    def test_source_and_weight_only_cold_replay(self):
        spec=example()
        m=NumericCircuit.synthesize(spec)
        raw=m.snapshot()
        n=NumericCircuit.restore(raw)
        self.assertEqual(n.snapshot(),raw)
        self.assertEqual(m.rows,n.rows)
        self.assertEqual(len(n.rows)*ROW,216)
        for x in TARGETS:
            self.assertEqual(n.predict(x),oracle(spec,x))
    def test_zero_prior(self):
        m=NumericCircuit()
        self.assertEqual(len(m.snapshot())>100,True)
        self.assertEqual(tuple(m.predict(x) for x in TARGETS),(0,)*8)
    def test_invalid_future_source_and_nonbit_atomic(self):
        spec=list(example())
        for bad in ((3,1,table(6)),(0,1,(0,1,False,1)),(0,1,(0,0,0))):
            trial=spec[:];trial[0]=bad
            with self.assertRaises(ValueError):
                NumericCircuit.synthesize(tuple(trial))
        self.assertEqual(NumericCircuit().rows,NumericCircuit().rows)
    def test_corrupted_checkpoint_and_canonical_reject(self):
        raw=NumericCircuit.synthesize(example()).snapshot()
        for bad in (raw[:-1],raw+b"x",raw[:12]+b"x"+raw[13:],b""):
            with self.assertRaises(ValueError):
                NumericCircuit.restore(bad)
    def test_bad_route_and_disabled_payload_rejected(self):
        zero=[[0]*ROW for _ in range(GATES)]
        zero[0][-1]=1
        with self.assertRaises(ValueError):NumericCircuit(zero)
        zero[0][-1]=0
        zero[0][0]=1
        with self.assertRaises(ValueError):NumericCircuit(zero)
    def test_train_converged_all_frozen_truth_tables(self):
        c=GateTrainCache()
        for mask in (8,14,6,9,7,1,11,4):
            self.assertEqual(c.fit(table(mask)),table(mask))
        self.assertEqual(c.fresh_fits,8)
        self.assertLessEqual(c.worst_bce,0.01)
        for mask in (8,14):
            c.fit(table(mask))
        self.assertEqual(c.hits,2)
    def test_dev_primary_graph_families_separate(self):
        a=generate("DEV",0);b=generate("PRIMARY",0)
        self.assertNotEqual(a,b)
        for i,(p,q,truth) in enumerate(b):
            self.assertTrue(0<=p<3+i and 0<=q<3+i)
            self.assertEqual(len(truth),4)
    def test_gate_and_route_ablation_diagnostic(self):
        spec=example()
        model=NumericCircuit.synthesize(spec)
        broken=list(spec)
        broken[0]=(0,1,table(0))
        different=NumericCircuit.synthesize(tuple(broken))
        self.assertTrue(any(model.predict(x)!=different.predict(x) for x in TARGETS))
    def test_dev_smoke_all_worlds(self):
        report=run("DEV")
        self.assertEqual(report["engineering"],"PASS")
        self.assertEqual(report["checks"]["worlds"],64)
        self.assertEqual(report["scores"]["direct"],512)
        self.assertEqual(report["scores"]["conventional"],512)

if __name__=="__main__":unittest.main()
