"""WSP153 fabricated development and exact algebra tests, no source first-use."""
import unittest
from itertools import combinations
from json import dumps
from pathlib import Path
import sparse_operators as M

class SparseOperatorTests(unittest.TestCase):
    def rows(self,form,vs=(0,1,2,3),xs=(1,2,4,8,16,32,21,42)):
        return tuple((x,M._effect(form,vs,x),
                      "observed_do" if i<4 else "do") for i,x in enumerate(xs))

    def test_01_class_is_exact_sparse_22_monomial_1794_candidates(self):
        self.assertEqual(len(M.MONOMIALS),22)
        self.assertEqual(len(M.CANDIDATES),1794)
        self.assertEqual(len(set(M.CANDIDATES)),1794)
        self.assertEqual(M.CANDIDATES[0],0)
        for form in ("AND2","OR2","XOR2","COMPOSE3"):
            truth=sum(1<<x for x in range(64)
                      if M._effect(form,(0,1,2,3),x))
            self.assertIn(truth,M.CANDIDATES)
        # Every stated out-of-class negative is truly not representable.
        for form in ("CUBIC3","CUBIC_XOR","ODD4","EXACT2OF4"):
            truth=sum(1<<x for x in range(64)
                      if M._effect(form,(0,1,2,3),x))
            self.assertNotIn(truth,M.CANDIDATES)

    def test_02_exact_independent_symbolic_parity(self):
        for form in ("AND2","OR2","XOR2","COMPOSE3","CUBIC3"):
            for n in (0,4,8):
                r=self.rows(form)[:n]
                model=M.fit(r)
                symbolic,count=M.exact_symbolic_independent(r)
                self.assertEqual(model["candidate_count"],count)
                self.assertEqual(model["prediction"],symbolic)
                self.assertEqual(len(symbolic),64)
                for x,y,prov in r:self.assertEqual(symbolic[x],y)
        self.assertEqual(M.readout_from_survivors(()),(None,)*64)

    def test_03_actions_custody_and_no_passive_shortcuts(self):
        r=self.rows("XOR2")[:4]
        self.assertEqual(M.choose_next(r),M.choose_next(r))
        self.assertNotIn(M.choose_next(r),[x for x,y,p in r])
        with self.assertRaises(ValueError):
            M.choose_next(self.rows("XOR2"))
        with self.assertRaises(ValueError):
            M.fit(((1,0,"passive"),))
        with self.assertRaises(ValueError):
            M.fit(((1,0,"do"),(1,1,"do")))
        with self.assertRaises(ValueError):
            M.fit(((64,0,"do"),))
        self.assertEqual(M.readout_from_survivors(()),(None,)*64)

    def test_04_conventional_control_fits_charged_training_data(self):
        for form in ("AND2","OR2","XOR2","COMPOSE3"):
            r=self.rows(form)
            p=M.train_cart(r)
            self.assertEqual(len(p),64)
            self.assertTrue(all(p[x]==y for x,y,_ in r),
                            "fully fitted CART must reproduce charged data")
            self.assertEqual(p,M.train_cart(r))

    def test_05_cold_isolation_and_no_protected_source_reference(self):
        text=Path(M.__file__).read_text(encoding="utf8")
        for banned in ("import source","from source import",
                       "WSP151|SOURCE|","WSP149|HELD|","WSP153|SOURCE|",
                       "first_use_authorization.json","SCIENTIFIC_PASS.json"):
            self.assertNotIn(banned,text)
        self.assertEqual(M.WARM,(1,2,4,8))
        for form in ("AND2","XOR2","OR2","COMPOSE3"):
            r=M.collect(form,(0,1,2,3),"active")
            self.assertEqual(len(r),8)
            self.assertEqual(len({x for x,y,p in r}),8)
            self.assertTrue(all(p=="observed_do" for x,y,p in r[:4]))
            self.assertTrue(all(p=="do" for x,y,p in r[4:]))

    def test_06_full_fixed_fabricated_cohort(self):
        a=M.fabricated_study()
        self.assertEqual((a["worlds"],a["on_worlds"],a["off_worlds"]),(20,16,4))
        self.assertFalse(a["scientific_pass"])
        self.assertFalse(a["first_use"])
        self.assertTrue(a["symbolic_parity"])
        self.assertIn(a["classification"],(
            "SOURCEFREE_SPARSE_OPERATOR_DEVELOPMENT_NO_GO",
            "SOURCEFREE_SPARSE_OPERATOR_DEVELOPMENT_SUPPORTED"))
        self.assertGreaterEqual(a["on_held"],16*48)
        self.assertEqual(a["active_on_wrong"],0,
                         "conditional certainty must hold on in-class truth")
        for p in ("fixed","active","symbolic","cart","wsp151"):
            score=a["scores"][p]
            self.assertEqual(score["held"],
                score["correct"]+score["wrong"]+score["abstain"])
            self.assertEqual(a["on_scores"][p]["held"]+a["off_scores"][p]["held"],
                             score["held"])
        self.assertEqual(a["on_scores"]["symbolic"],a["on_scores"]["active"])
        self.assertEqual(len(a["receipt_sha256"]),64)
        print("WSP153_NONRESOURCE_OUTCOME_DIGEST",M.digest({
            k:v for k,v in a.items() if k not in ("cpu_s","wall_s")}))
        print("WSP153_FABRICATED_DEVELOPMENT_SCORES",dumps(a,sort_keys=True))

if __name__=="__main__":unittest.main()
