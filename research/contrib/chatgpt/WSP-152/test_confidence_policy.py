"""WSP152 fabricated-only tests; never open first-use synthetic or protected source."""
import unittest
from fractions import Fraction
from pathlib import Path
import confidence_policy as C

class ConfidenceCoverageTests(unittest.TestCase):
    def rows(self,form,s,xs=(1,2,4,8,16,32,21,42)):
        return tuple((x,C.M.law(form,s,x),"observed_do" if k<4 else "do")
                     for k,x in enumerate(xs))

    def test_01_unknown_probability_exact_ceiling(self):
        for form,subset in (("OR",1),("OR",5),("AND",3),("AND",7)):
            rows=self.rows(form,subset)
            m=C.M.fit(rows)
            c=C.ceiling(m)
            self.assertEqual(c["maximum_confidence"],1-m["unknown"]/(2*m["denominator"]))
            self.assertEqual(c["globally_blocked"],c["unknown"]>Fraction(1,50))
            for x in range(64):
                p=C.M.predict_probability(m,x)
                self.assertGreaterEqual(p,1-c["maximum_confidence"])
                self.assertLessEqual(p,c["maximum_confidence"])
            if c["globally_blocked"]:
                self.assertEqual(C.M.readout(m),(None,)*64)
        for subset in (1,5):
            self.assertTrue(C.ceiling(C.M.fit(self.rows("OR",subset)))["globally_blocked"])

    def test_02_counterfactual_reweight_exact_parent_probability(self):
        mem=C.M.empty_memory()
        for form,subset in (("OR",5),("AND",3)):
            rows=self.rows(form,subset)[:4]
            model=C.M.fit(rows,mem)
            ws,u=C._integers(model)
            x=next(x for x in range(64) if x not in {a for a,b,c in rows})
            for y in (0,1):
                fut,fu=C._future(ws,u,x,y)
                other=C.M.fit(rows+((x,y,"do"),),mem)
                total=sum(fut)+fu
                for q in range(64):
                    p=Fraction(2*sum(fut[j] for j in range(126) if C.PRED[j][q])+fu,2*total)
                    self.assertEqual(p,C.M.predict_probability(other,q))
                held={q for q,_,_ in rows}|{x}
                predicted=sum(1 for q in range(64) if q not in held and
                    (C.M.predict_probability(other,q)>=C.CONF or
                     C.M.predict_probability(other,q)<=1-C.CONF))
                self.assertEqual(C._coverage(fut,fu,held),predicted)

    def test_03_deterministic_actions_and_guardrails(self):
        m=C.M.empty_memory()
        r=self.rows("OR",5)[:4]
        x=C.choose_next(r,m)
        self.assertEqual(x,C.choose_next(r,m))
        self.assertNotIn(x,[a for a,b,c in r])
        with self.assertRaises(ValueError):
            C.choose_next(self.rows("OR",5),m)
        with self.assertRaises(ValueError):
            C.choose_next(((1,0,"do"),(1,1,"do")),m)
        with self.assertRaises(ValueError):
            C.choose_next(((1,0,"passive"),),m)

    def test_04_no_source_and_frozen_original_unchanged(self):
        s=Path(C.__file__).read_text(encoding="utf8")
        for forbidden in ("import source","from source import","WSP151|SOURCE|",
                          "WSP149|SOURCE|","first_use_authorization.json",
                          "SCIENTIFIC_PASS.json","Custodian("):
            self.assertNotIn(forbidden,s)
        self.assertEqual(len(C.HYP),126)
        self.assertEqual(len(C.ONES),126)
        self.assertEqual(C.Q_MAX,Fraction(1,50))
        self.assertEqual(C.CONF,Fraction(99,100))

    def test_05_full_fabricated_cohort_and_sealed_negative_controls(self):
        result,worlds=C.fabricated_study()
        self.assertEqual(result["worlds"],16)
        self.assertEqual((result["on"],result["off"]),(12,4))
        self.assertEqual(len(worlds),16)
        self.assertEqual(result["held_total"],sum(x["held"] for x in worlds))
        self.assertTrue(all(x["held"]>=40 for x in worlds))
        self.assertFalse(result["scientific_pass"])
        self.assertFalse(result["protected_first_use"])
        self.assertEqual(result["classification"] in (
            "SOURCEFREE_CONFIDENCE_POLICY_NO_GO",
            "SOURCEFREE_CONFIDENCE_POLICY_DEVELOPMENT_GAIN"),True)
        for p,c in result["per_policy"].items():
            self.assertEqual(c["correct"]+c["wrong"]+c["abstain"],c["held"])
            self.assertEqual(c["globally_blocked_worlds"]+
                             c["confidence_eligible_worlds"],16)
            self.assertEqual(c["held"],result["held_total"])
        self.assertEqual(len(result["world_receipt_sha256"]),64)
        print("WSP152_FABRICATED_DEVELOPMENT_RESULT",C._digest({
             k:v for k,v in result.items() if k not in ("cpu_s","wall_s")}))
        import json
        print("WSP152_FABRICATED_SCORES",json.dumps(result,sort_keys=True))

if __name__=="__main__":
    unittest.main()
