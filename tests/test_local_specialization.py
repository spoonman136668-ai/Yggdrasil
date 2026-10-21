"""NCI-04C local specialization feasibility; no scientific first-use."""
import json
import math
import unittest
from yggdrasil.local_specialization import LocalSpecialization

def scenes(step, context=0):
    x = [float(((step*13 + i*19 + context*7) % 29) < 12) for i in range(8)]
    y = []
    for i in range(8):
        left, right = (i-1)%8, (i+1)%8
        y.append(.8 * x[left] + .2 * x[right] if i%2==0 else .7*x[i]+.3*x[right])
    return x, y

def loss(model, contexts, samples=24, location=3):
    err=0
    for context in contexts:
        for t in range(samples):
            x,y=scenes(t+211,context)
            err += (model.predict(x)[location]-y[location])**2
    return err/(len(contexts)*samples)

def train(model, periods):
    for context, count in periods:
        for t in range(count):
            x,y=scenes(t,context)
            model.learn(x,y)

class NCI04C(unittest.TestCase):
    def test_ring_locality_and_prediction_read_only(self):
        model=LocalSpecialization()
        model.weights[1][2]=4.0
        model.trace[0]=.9
        high=model.predict([0]*8)[1]
        model.trace[0]=.1
        low=model.predict([0]*8)[1]
        self.assertGreater(high,low)
        model.trace[5]=.9
        self.assertEqual(low,model.predict([0]*8)[1])
        state=model.snapshot()
        for _ in range(15):model.predict([0]*8)
        self.assertEqual(model.snapshot(),state)

    def test_damage_recovery_versus_cold_and_neighbor_copy(self):
        original=LocalSpecialization(rate=.18,teach=.3)
        train(original,[(0,96),(1,48),(0,48)])
        pre=loss(original,[0])
        original.lesion(3)
        damaged=loss(original,[0])
        self.assertGreater(damaged,pre)
        original.regrow(3)
        cold=LocalSpecialization(rate=.18,teach=0)
        cold.weights=[r.copy() for r in original.weights]
        cold.trace=original.trace.copy()
        cold.alive=original.alive.copy()
        cold.recovering=[False]*8
        copied=LocalSpecialization(rate=.18,teach=0)
        copied.weights=[r.copy() for r in original.weights]
        copied.trace=original.trace.copy()
        copied.alive=original.alive.copy()
        copied.weights[3]=[(a+b)/2 for a,b in zip(copied.weights[2],copied.weights[4])]
        before=loss(original,[0])
        self.assertGreater(before,pre)
        for t in range(24):
            x,y=scenes(t+311,0)
            original.learn(x,y)
            cold.learn(x,y)
            copied.learn(x,y)
        after=loss(original,[0])
        cold_loss=loss(cold,[0]);copy_loss=loss(copied,[0])
        print("NCI04C_Y_RECOVERY before=%0.6f damage=%0.6f recovered=%0.6f cold=%0.6f neighbor_copy=%0.6f" % (pre,damaged,after,cold_loss,copy_loss))
        self.assertTrue(all(math.isfinite(x) for x in (pre,damaged,after,cold_loss,copy_loss)))
        self.assertLess(after,damaged)
        self.assertNotEqual(original.weights[3],copied.weights[3])
        self.assertNotEqual(original.weights[0],original.weights[1])

    def test_reject_corrupted_checkpoint_and_atomic_learning(self):
        model=LocalSpecialization()
        state=model.snapshot()
        for scene in [([0]*7,[0]*8),([0]*8,[float('nan')]*8)]:
            with self.assertRaises(ValueError):model.learn(*scene)
            self.assertEqual(state,model.snapshot())
        with self.assertRaises(ValueError):model.restore('{"schema":"other"}')
        self.assertEqual(state,model.snapshot())
        model.lesion(4)
        model.regrow(4)
        recovered=LocalSpecialization();recovered.restore(model.snapshot())
        self.assertEqual(recovered.snapshot(),model.snapshot())

if __name__=='__main__': unittest.main()
