"""KNOW14 frozen generator and source-negative controls, no original world."""
import unittest
from itertools import product
from fractions import Fraction
from same_slot_blind_regime_dev import (
    SEEDS,CUES,N,FIT,world,subject,object_id,expected,training_events,
    fact_bit,rows_for,detect,controls,score,canonical,digest)


class FactsDouble:
    def __init__(self,i=0,*,no_cue=False,duplicate=False,
                 source_mode="engineering_fixture_only"):
        self.rows=set()
        self.source_mode=source_mode
        for task in (0,1):
            true,mode,cols=world(i,task)
            for e in range(N):
                q=subject(i,task,e)
                self.rows.add((q,960,object_id(task,4,mode[e])))
                for f in range(4):
                    if no_cue:
                        b=0
                    elif duplicate and f==(true+1)%4:
                        b=task
                    else:
                        b=cols[f][e]
                    self.rows.add((q,CUES[f],object_id(task,f,b)))
    def fact(self,q,p,o):
        visible=(q,p,o) in self.rows
        return {"classification":"DEVELOPMENT_OBSERVED_FACT_NOT_ADMITTED"
                if visible else "UNKNOWN_ABSTAIN",
                "witnessed":visible,
                "source_mode":self.source_mode,
                "source_provenance":"SOURCE_SHA_PINNED_BYTES_NOT_AUTHENTICATED",
                "native_accepted":False,
                "verified_new_real_knowledge":False,
                "can_write_causal_consequence":False}


class LinearAccumulatorDouble:
    """Independent small GF2 consistency oracle for source-only unit controls."""
    def __init__(self,context_bits=2,rows=()):
        self.rows=tuple(rows)
    def stage_update(self,address,rows,expected_source_sha256,*,max_degree=1):
        if (address!=0 or max_degree!=1 or
                digest(canonical(rows))!=expected_source_sha256):
            raise ValueError("INVALID_SOURCE")
        merged=self.rows+tuple(tuple(x) for x in rows)
        consistent=[]
        for coeff in product((0,1),repeat=4):
            if all((coeff[0]^((ctx&1)*coeff[1])^
                    (((ctx>>1)&1)*coeff[2])^(action*coeff[3]))==label
                   for ctx,action,label in merged):
                consistent.append(coeff)
        if not consistent:
            raise ValueError("CKAD_NATIVE_CUMULATIVE_MODEL_INADEQUATE")
        return LinearAccumulatorDouble(rows=merged)


class Know14Tests(unittest.TestCase):
    def test_frozen_seeds_private_roles_and_held_balance(self):
        self.assertEqual(SEEDS,(1111,2222,3333))
        self.assertEqual(CUES,(961,962,963,964))
        for i in range(3):
            for task in (0,1):
                private,modes,cols=world(i,task)
                self.assertEqual(private,(i+1)%4)
                self.assertEqual(cols[private],(task,)*64)
                for split in (0,1):
                    self.assertEqual(sum(modes[split*32:(split+1)*32]),16)
                    for f,col in enumerate(cols):
                        if f==private:continue
                        for m in (0,1):
                            vals=[col[e] for e in range(split*32,(split+1)*32)
                                  if modes[e]==m]
                            self.assertEqual(sum(vals),8)

    def test_each_source_cue_selected_only_from_witnessed_actions(self):
        for i in range(3):
            f=FactsDouble(i)
            a,b=training_events(i,0),training_events(i,1)
            winners,rejected=detect(f,a,b,LinearAccumulatorDouble)
            self.assertEqual(len(winners),1)
            self.assertEqual(len(rejected),3)
            self.assertEqual(winners[0][0],(i+1)%4)
            self.assertEqual(len(winners[0][3]),64)
            self.assertEqual(len(winners[0][4]),64)

    def test_no_discriminating_cue_fails_closed(self):
        f=FactsDouble(no_cue=True)
        winners,rejected=detect(f,training_events(0,0),
                                training_events(0,1),LinearAccumulatorDouble)
        self.assertEqual(len(winners),0)
        self.assertEqual(len(rejected),4)

    def test_equal_two_discriminating_cues_require_abstention(self):
        f=FactsDouble(duplicate=True)
        winners,rejected=detect(f,training_events(0,0),
                                training_events(0,1),LinearAccumulatorDouble)
        self.assertEqual(len(winners),2)
        # The caller must require *exactly* one, never prefer first.
        self.assertNotEqual(len(winners),1)

    def test_unknown_or_conflicting_cue_and_wrong_source_abstain(self):
        f=FactsDouble()
        priv,mode,_cols=world(0,0)
        q=subject(0,0,0)
        self.assertEqual(fact_bit(f,q,CUES[priv],0,priv),0)
        one=(q,CUES[priv],object_id(0,priv,0))
        f.rows.remove(one)
        self.assertIsNone(fact_bit(f,q,CUES[priv],0,priv))
        f.rows.add(one)
        f.rows.add((q,CUES[priv],object_id(0,priv,1)))
        self.assertIsNone(fact_bit(f,q,CUES[priv],0,priv))
        fake=FactsDouble(source_mode="asserted_owner")
        self.assertIsNone(fact_bit(fake,q,CUES[priv],0,priv))

    def test_static_qpq_is_not_action_consequence(self):
        f=FactsDouble()
        i=0
        rows=rows_for(f,training_events(i,0),0,(i+1)%4)
        self.assertEqual(len(rows),64)
        self.assertEqual(set((c,a) for c,a,y in rows),
                         {(0,0),(0,1),(1,0),(1,1)})
        self.assertEqual(set(y for c,a,y in rows),{0,1})

    def test_fitted_strong_symbolic_retains_both_regimes(self):
        observations=[[m|(task<<1),a,expected(task,m,a)]
                      for task in (0,1) for m in (0,1) for a in (0,1)]
        table=controls(observations)
        self.assertEqual(len(table),8)
        for c,a,y in observations:self.assertEqual(table[(c,a)],Fraction(y))

    def test_held_forecasts_and_action_rewards_only_from_scoring(self):
        f=FactsDouble()
        cue=(0+1)%4
        total=[]
        for task in (0,1):
            metrics=score(f,0,task,cue,{
                "native":lambda c,a,t=task:expected(t,c&1,a),
                "facts_only":lambda c,a:Fraction(1,2)})
            self.assertEqual(metrics["brier"]["native"],[0,1])
            self.assertEqual(metrics["brier"]["facts_only"],[1,4])
            self.assertEqual(metrics["correct_action_rewards"]["native"],32)
            total.append(metrics["native_fingerprint"])
        self.assertNotEqual(total[0],total[1])

    def test_invalid_public_identifiers_and_action_bits_refused(self):
        for v in (True,-1,2):
            with self.assertRaises(ValueError):expected(0,0,v)
            with self.assertRaises(ValueError):object_id(0,4,v)
        for v in (True,-1,64):
            with self.assertRaises(ValueError):subject(0,0,v)

    def test_no_owner_checkpoint_or_live_action_methods(self):
        import same_slot_blind_regime_dev as m
        for unsafe in ("activate","merge","deploy","observe_experience",
                       "promote_canonical","modify_owner","scheduler"):
            self.assertFalse(hasattr(m,unsafe))
if __name__=="__main__":unittest.main()
