"""KNOW13 source-free fixed-generator + negative control tests."""
import unittest
from fractions import Fraction
from same_address_cumulative_facts_dev import (
    SEEDS,PREDS,FIT,N,world,subject,obj,bit,reward,fit_events,
    select_role,shared_rows,symbolic,conventional,evaluate,canonical,sha)

class FactDouble:
    def __init__(self,i=0,p=0,mode="engineering_fixture_only"):
        self.kind=mode
        self.data=set()
        role,truth,cols=world(i,p)
        for e in range(N):
            for f in range(4):
                self.data.add((subject(i,p,e),PREDS[f],obj(p,f,cols[f][e])))
    def fact(self,q,p,o):
        yes=(q,p,o) in self.data
        return {"classification":"DEVELOPMENT_OBSERVED_FACT_NOT_ADMITTED"
                if yes else "UNKNOWN_ABSTAIN","source_mode":self.kind,
                "source_provenance":"SOURCE_SHA_PINNED_BYTES_NOT_AUTHENTICATED",
                "witnessed":yes,"native_accepted":False,
                "verified_new_real_knowledge":False,
                "can_write_causal_consequence":False}
class BasisDouble:
    def __init__(self,context_bits=1,answers=None):
        self.answers=answers or {}
    def stage_fit(self,slot,rows,pin,*,max_degree=None):
        if sha(canonical(rows))!=pin or max_degree!=1:raise ValueError("SOURCE")
        a={}
        for ctx,act,y in rows:
            if (ctx,act) in a and a[(ctx,act)]!=y:
                raise ValueError("STOCHASTIC_OR_CONFLICTING_INPUT_MODEL_INADEQUATE")
            a[(ctx,act)]=y
        return BasisDouble(answers=a)
    def predict(self,slot,ctx,act):return self.answers.get((ctx,act))
class Tests(unittest.TestCase):
    def test_frozen_seeds_and_source_types(self):
        self.assertEqual(SEEDS,(707,808,909))
        self.assertEqual(PREDS,(940,941,942,943))
    def test_balanced_true_role_and_distractors(self):
        for i in range(3):
            for phase in (0,1):
                r,t,cols=world(i,phase)
                self.assertEqual(r,(i+phase+2)%4)
                self.assertEqual(cols[r],t)
                for split in (0,1):
                    self.assertEqual(sum(t[split*FIT:(split+1)*FIT]),16)
                    for f,c in enumerate(cols):
                        if f==r:continue
                        for m in (0,1):
                            v=[c[e] for e in range(split*FIT,(split+1)*FIT)
                               if t[e]==m]
                            self.assertEqual(sum(v),8)
    def test_role_selected_from_public_fact_and_witnesses(self):
        for i in range(3):
            for p in (0,1):
                f=FactDouble(i,p)
                actual=select_role(f,fit_events(i,p),p,BasisDouble)
                self.assertEqual(actual,world(i,p)[0])
                rows=shared_rows(f,fit_events(i,p),p,actual)
                self.assertEqual(len(rows),64)
                self.assertEqual(set(ctx>>1 for ctx,a,y in rows),{p})
                self.assertEqual(set((ctx&1,a) for ctx,a,y in rows),
                                 {(0,0),(0,1),(1,0),(1,1)})
    def test_unknown_collision_and_source_spoof_refuse(self):
        f=FactDouble()
        role,t,cols=world(0,0)
        q=subject(0,0,0)
        triple=(q,PREDS[role],obj(0,role,t[0]))
        self.assertEqual(bit(f,q,0,role),t[0])
        f.data.remove(triple)
        self.assertIsNone(bit(f,q,0,role))
        f.data.add(triple)
        f.data.add((q,PREDS[role],obj(0,role,1-t[0])))
        self.assertIsNone(bit(f,q,0,role))
        self.assertIsNone(bit(FactDouble(mode="asserted_owner"),q,0,role))
    def test_ambiguous_roles_abstain(self):
        f=FactDouble()
        role,t,cols=world(0,0)
        other=(role+1)%4
        for e in range(FIT):
            q=subject(0,0,e)
            f.data.remove((q,PREDS[other],obj(0,other,cols[other][e])))
            f.data.add((q,PREDS[other],obj(0,other,t[e])))
        self.assertIsNone(select_role(f,fit_events(0,0),0,BasisDouble))
    def test_no_source_abstains(self):
        f=FactDouble()
        f.data.clear()
        self.assertIsNone(select_role(f,fit_events(0,0),0,BasisDouble))
    def test_independent_fully_fitted_controls(self):
        rows=[[m|(p<<1),a,reward(p,m,a)] for p in (0,1)
              for m in (0,1) for a in (0,1)]
        s=symbolic(rows);c=conventional(rows)
        self.assertEqual(len(s),8)
        for ctx,a,y in rows:
            self.assertEqual(s[(ctx,a)],Fraction(y))
            self.assertEqual(c(ctx,a),Fraction(y))
    def test_held_readout_reproducible(self):
        f=FactDouble()
        role,_,_=world(0,0)
        a=evaluate(f,0,0,role,{"native":lambda ctx,a:reward(0,ctx&1,a)})
        self.assertEqual(a,evaluate(f,0,0,role,{
            "native":lambda ctx,a:reward(0,ctx&1,a)}))
        self.assertEqual(a["brier"]["native"],[0,1])
    def test_bad_identifiers_and_outcomes(self):
        for x in (True,-1,2):
            with self.assertRaises(ValueError):reward(0,0,x)
            with self.assertRaises(ValueError):obj(0,0,x)
            with self.assertRaises(ValueError):subject(0,0,x)
    def test_canonical_and_absent_activation(self):
        self.assertEqual(canonical({"b":2,"a":1}),b'{"a":1,"b":2}')
        import same_address_cumulative_facts_dev as m
        for forbidden in ("activate","deploy","merge","promote_canonical",
                          "observe_experience","controller"):
            self.assertFalse(hasattr(m,forbidden))
if __name__=="__main__":unittest.main()
