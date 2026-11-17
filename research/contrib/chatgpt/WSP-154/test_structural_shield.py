"""WSP154 source-free algebra and fabricated-cohort regression; no owner calls."""
import unittest
from hashlib import sha256
from pathlib import Path
import structural_shield as M

class StructuralShieldTests(unittest.TestCase):
    def rows(self,kind,vs=(0,1,2,3,4),xs=(1,2,4,8,16,32,21,42)):
        return tuple((x,M.effect(kind,vs,x),
                      "observed_do" if k<4 else "do")
                     for k,x in enumerate(xs))

    def test_01_exact_basis_and_no_named_template_learner(self):
        self.assertEqual(len(M.MONOMIALS),42)
        self.assertEqual(len(set(M.MONOMIALS)),42)
        self.assertEqual(len(M.CANDIDATES),12384)
        self.assertEqual(len(set(M.CANDIDATES)),12384)
        self.assertEqual(M.CANDIDATES[0],0)
        for form in M.ON+("CUBIC3","CUBIC_XOR","PAIR_TRIPLE"):
            truth=sum(1<<x for x in range(64)
                      if M.effect(form,(0,1,2,3,4),x))
            self.assertIn(truth,M.CANDIDATES,form)
        for form in ("ODD4","EXACT2OF4","QUAD4"):
            truth=sum(1<<x for x in range(64)
                      if M.effect(form,(0,1,2,3,4),x))
            self.assertNotIn(truth,M.CANDIDATES,form)

    def test_02_exact_symbolic_independent_agreement(self):
        for form in ("OR2","XOR2","COMPOSE3","CUBIC3","ODD4"):
            for n in (0,4,8):
                rows=self.rows(form)[:n]
                model=M.fit(rows)
                out,k=M.symbolic_independent(rows)
                self.assertEqual((model["predictions"],model["candidate_count"]),
                                 (out,k),form)
                self.assertEqual(len(out),64)
                for x,y,_ in rows:self.assertEqual(out[x],y)

    def test_03_out_of_class_counterworld_matches_all_eight_paid(self):
        rows=self.rows("AND2")
        fake_zero=tuple((x,0,prov) for x,y,prov in rows)
        for x in range(64):
            if x in {r[0] for r in fake_zero}:continue
            witness=M.alias_witness(fake_zero,x)
            self.assertEqual(witness.bit_count(),1)
            self.assertTrue(all(((witness>>v)&1)==0 for v,_,_ in fake_zero))
            self.assertEqual((witness>>x)&1,1)
            self.assertNotIn(witness,M.CANDIDATES)
        with self.assertRaises(ValueError):
            M.alias_witness(fake_zero,rows[0][0])

    def test_04_guarded_unknown_and_provenance(self):
        for k in M.OFF:
            rows=self.rows(k)
            p=M.fit(rows)
            if not p["candidate_count"]:
                self.assertEqual(p["predictions"],(None,)*64)
        with self.assertRaises(ValueError):
            M.fit(((1,1,"passive"),))
        with self.assertRaises(ValueError):
            M.fit(((1,0,"do"),(1,1,"do")))
        with self.assertRaises(ValueError):
            M.fit(((64,0,"do"),))

    def test_05_source_isolation_no_original_source(self):
        text=Path(M.__file__).read_text(encoding="utf8")
        for banned in ("import source","from source import",
                       "WSP151|SOURCE|","WSP149|HELD|",
                       "WSP153|SOURCE|","WSP154|SOURCE|",
                       "SCIENTIFIC_PASS.json","first_use_authorization.json"):
            self.assertNotIn(banned,text)
        self.assertEqual(M.P.WARM,(1,2,4,8))
        for kind in ("COMPOSE3","CUBIC_XOR","ODD4"):
            rows=M.collect(kind,(0,1,2,3,4))
            self.assertEqual((len(rows),len(set(x for x,y,p in rows))),(8,8))
            self.assertTrue(all(prov=="observed_do" for x,y,prov in rows[:4]))
            self.assertTrue(all(prov=="do" for x,y,prov in rows[4:]))

    def test_06_full_new_fabricated_cohort_frozen_scores(self):
        r=M.study()
        self.assertEqual((r["worlds"],r["on_worlds"],r["off_worlds"]),
                         (24,12,12))
        self.assertFalse(r["science_pass"])
        self.assertFalse(r["original_first_use"])
        self.assertEqual(len(r["worlds_digest"]),64)
        self.assertIn(r["classification"],(
           "SOURCEFREE_STRUCTURAL_SHIELD_DEVELOPMENT_SUPPORTED",
           "SOURCEFREE_STRUCTURAL_SHIELD_DEVELOPMENT_NO_GO"))
        for name,groups in r["scores"].items():
            for k in ("on","off"):
                x=groups[k]
                self.assertEqual(x["held"],672)
                self.assertEqual(x["right"]+x["wrong"]+x["abstain"],672)
        self.assertEqual(r["scores"]["symbolic"],r["scores"]["guarded"])
        self.assertEqual(r["scores"]["guarded"]["on"]["wrong"],0)
        import json
        resource_free={k:v for k,v in r.items() if k not in ("cpu_s","wall_s")}
        print("WSP154_NONRESOURCE_OUTCOME_DIGEST",M.digest(resource_free))
        print("WSP154_FABRICATED_DEVELOPMENT_SCORES",json.dumps(r,sort_keys=True))
if __name__=="__main__":
    unittest.main()
