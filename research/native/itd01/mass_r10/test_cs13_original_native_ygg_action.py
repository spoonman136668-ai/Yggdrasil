"""CS13 focused source-free authentic native model and conventional arm tests."""
import pathlib,sys,unittest
p=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(p))
sys.path.insert(0,str(p.parent/"r7"))
from run_cs13_original_native_ygg_action import (
    actual_native_Colony,TrainedTable,Logistic,decide,ARMS,FIT_N,DEV_N,
    MAP_KEYS,original_seed,
)
class Boundaries(unittest.TestCase):
 def test_actual_unchanged_native_feedback_checkpoint(self):
    Colony=actual_native_Colony()
    m=Colony()
    before=m.checkpoint()
    for _ in range(8):
        m.learn_completed_public_feedback("A",(True,True,False,True),True,2)
    self.assertEqual(m.feedback_updates,8)
    self.assertNotEqual(m.checkpoint(),before)
    cold=Colony.restore(m.checkpoint())
    self.assertEqual(cold.checkpoint(),m.checkpoint())
    self.assertTrue(cold.predict("A",(True,True,False,True)))
 def test_conventional_fit_only_real_boolean_labels(self):
    examples=[{"context":("A" if i%2==0 else "B"),
               "public_sensors_4":(bool(i%2),bool(i%3),bool(i%5),True),
               "public_real_source_label_good":bool(i%2)} for i in range(128)]
    tab=TrainedTable();tab.fit(examples)
    log=Logistic();log.fit(examples)
    self.assertEqual(log.updates,128*20)
    for ctx in ("A","B"):
        for c in range(8):
            s=(*(bool(c&(1<<j)) for j in range(3)),True)
            self.assertIn(tab.predict(ctx,s),(True,False))
            self.assertIn(log.predict(ctx,s),(True,False))
 def test_constant_and_cold_decisions(self):
    c=actual_native_Colony()()
    t=TrainedTable();l=Logistic()
    senses=(True,False,True,True)
    self.assertTrue(decide(ARMS[5],"A",senses,c,t,l,c))
    self.assertFalse(decide(ARMS[6],"A",senses,c,t,l,c))
    self.assertFalse(decide(ARMS[4],"A",senses,c,t,l,c))
 def test_frozen_source_roles(self):
    fit={original_seed("FIT",m,i) for m in range(2) for i in range(FIT_N)}
    dev={original_seed("DEV",m,i) for m in range(2) for i in range(DEV_N)}
    self.assertFalse(fit&dev)
    self.assertEqual(len(fit),128)
    self.assertEqual(len(dev),256)
    self.assertEqual(len(ARMS),7)
    self.assertEqual(len(MAP_KEYS),2)
if __name__=="__main__":
 unittest.main()
