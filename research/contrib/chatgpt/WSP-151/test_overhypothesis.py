"""Fabricated-row only. NEVER import source owner or scored studies."""
import unittest
from fractions import Fraction
import overhypothesis as M

class SyntheticFabricatedOnly(unittest.TestCase):
    def rows(self,kind,subset,actions=(1,2,4,8,16,32,21,42)):
        return tuple((x,M.law(kind,subset,x),
                      "do" if i>=4 else "observed_do")
                     for i,x in enumerate(actions))
    def test_01_prior_and_exact_bayesian_enumeration(self):
        mem=M.empty_memory()
        self.assertEqual(M.prior_or(mem),Fraction(1,2))
        for i in range(16):
            mem=M.remember(mem,self.rows("AND",3),world_id=i)
        p=M.prior_or(mem)
        self.assertLess(p,Fraction(1,2))
        mem=M.freeze(mem)
        self.assertEqual(mem,M.restore(mem))
        self.assertEqual(M.prior_or(mem),p)
        self.assertTrue(0<p<1)
    def test_02_source_free_probability_and_action_discrimination(self):
        mem=M.empty_memory()
        for kind,s in (("OR",1),("AND",3),("OR",5)):
            rows=self.rows(kind,s)
            model=M.fit(rows,mem)
            for x in range(64):
                p=M.predict_probability(model,x)
                self.assertTrue(0<p<1)
            self.assertEqual(len(M.readout(model)),64)
            proposed=M.propose_next(rows[:4],mem)
            self.assertIsInstance(proposed,int)
            self.assertNotIn(proposed,[x for x,_,_ in rows[:4]])
    def test_03_cold_memory_guards_and_provenance(self):
        m=M.empty_memory();rows=self.rows("OR",5)
        m=M.remember(m,rows,0)
        with self.assertRaises(ValueError):M.remember(m,rows,0)
        with self.assertRaises(ValueError):M.remember(m,rows,-1)
        with self.assertRaises(ValueError):M.remember(m,rows[:7],1)
        with self.assertRaises(ValueError):
            M.remember(m,rows[:4]+((0,1,"passive"),)+rows[5:],1)
        with self.assertRaises(ValueError):
            M.validate_rows(((1,0,"do"),(1,1,"do")))
        with self.assertRaises(ValueError):M.restore({**m,"digest":"0"*64})
        with self.assertRaises(ValueError):M.freeze(m)
        for i in range(1,16):m=M.remember(m,rows,i)
        m=M.freeze(m)
        with self.assertRaises(ValueError):M.remember(m,rows,16)
        with self.assertRaises(ValueError):M.propose_next(rows,m)
    def test_04_unknown_never_forced_and_no_owner_import(self):
        m=M.fit((),M.empty_memory())
        self.assertEqual(M.readout(m),(None,)*64)
        from pathlib import Path
        src=Path(M.__file__).read_text(encoding="utf8")
        for forbidden in ("import source","from source",
                          "WSP151|SOURCE|","Custodian","WSP149|HELD|"):
            self.assertNotIn(forbidden,src)
if __name__=="__main__":unittest.main()
