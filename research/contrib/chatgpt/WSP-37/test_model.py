"""WSP-37 focused guards: unknown-rule scope, cold durability, mutation and parity."""
import unittest
from model import NumericProgram,acquire,gradient_fit
from battery import generator,schedule,transfer_topology,inputs,run

class WSP37Tests(unittest.TestCase):
    def test_full_unknown_function_all_arities(self):
        for a in (2,3,4):
            for kind in ("arbitrary","structured"):
                graph,truth=generator("DEV",a,kind,2)
                rows=schedule("DEV",a,kind,2,"full")
                p,history=acquire(a,graph,rows,lambda g,k:truth[g][k])
                self.assertEqual(p.tables,truth)
                self.assertEqual(len(history),8*(1<<a))
                self.assertEqual(NumericProgram.restore(p.snapshot()).snapshot(),p.snapshot())
                self.assertNotEqual(graph,transfer_topology("DEV",a,kind,2))
                for x in inputs(a): self.assertIn(p.predict(x),(0,1))
    def test_budget_and_same_data(self):
        a=4; graph,truth=generator("DEV",a,"arbitrary",3)
        for b in ("zero","half","full"):
            rows=schedule("DEV",a,"arbitrary",3,b)
            p,_=acquire(a,graph,rows,lambda g,k:truth[g][k])
            t,updates,loss=gradient_fit(p.tables,rows)
            self.assertEqual(t,p.tables)
            self.assertLessEqual(loss,.01)
            if b=="zero": self.assertEqual(updates,0)
            elif b=="full": self.assertEqual(p.tables,truth)
    def test_forbidden_query_and_nonbit(self):
        graph,_=generator("DEV",3,"arbitrary",0)
        r=schedule("DEV",3,"arbitrary",0,"half")
        with self.assertRaises(ValueError): acquire(3,graph,r,lambda g,k:2)
        with self.assertRaises(ValueError): acquire(3,graph,tuple(((0,0),)*8),lambda g,k:0)
    def test_cold_corruption(self):
        graph,truth=generator("DEV",4,"structured",0)
        p=NumericProgram(4,graph,truth); raw=p.snapshot()
        for bad in (raw[:-1],raw+b"Z",raw[:-1]+bytes((raw[-1]^1,)),b"",raw.replace(b'"arity":4',b'"arity":3')):
            with self.assertRaises(ValueError): NumericProgram.restore(bad)
    def test_patch_one_row_only(self):
        graph,truth=generator("DEV",3,"structured",2)
        p=NumericProgram(3,graph,truth)
        patched=p.patch(7,5,1-truth[7][5])
        self.assertEqual(sum(a!=b for t,u in zip(p.tables,patched.tables) for a,b in zip(t,u)),1)
        self.assertEqual(NumericProgram.restore(patched.snapshot()).tables,patched.tables)
    def test_world_and_schedule_determinism(self):
        self.assertEqual(generator("DEV",4,"arbitrary",11),generator("DEV",4,"arbitrary",11))
        self.assertNotEqual(generator("DEV",4,"arbitrary",11),generator("PRIMARY",4,"arbitrary",11))
        self.assertEqual(schedule("DEV",4,"arbitrary",11,"half"),schedule("DEV",4,"arbitrary",11,"half"))
    def test_complete_development_battery(self):
        r=run("DEV")
        self.assertEqual(r["engineering"],"PASS")
        self.assertEqual(r["science"],"SCIENTIFIC_NEGATIVE")
        self.assertEqual(len(r["six_regimes_three_budgets"]),18)

if __name__=="__main__": unittest.main()
