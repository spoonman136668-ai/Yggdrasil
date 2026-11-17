"""Native persistent 1920-program search and input-only actions: negatives."""
import importlib.util
import json
from pathlib import Path
import unittest
from yggdrasil.native_hypothesis_portfolio import (
    NativeHypothesisPortfolio,ALL_CANDIDATES,CANDIDATES,GATES,grammar,
    evaluate_program,votes,canonical,digest,SOURCE_MODE)
from yggdrasil.native_context_basis import NativeContextBasis

ROOT=Path(__file__).resolve().parents[1]
CAMPAIGN=ROOT/"research/contrib/chatgpt/CKAD-PORTFOLIO-V1/campaign.py"
spec=importlib.util.spec_from_file_location("ckad_portfolio_v1_dev_fixture",CAMPAIGN)
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)

def add(model,slot,m,y):
    return model.observe(slot,m,y,digest(canonical([slot,m,y,SOURCE_MODE])))

class NativePortfolioTests(unittest.TestCase):
    def test_supplied_bank_and_action_causal_terms(self):
        self.assertEqual(CANDIDATES,1920)
        self.assertEqual(len(grammar()),1920)
        self.assertEqual(len(GATES),15)
        self.assertEqual(len(votes()),64)
        for m in (0,3,17,32,63):
            for i in (0,1,2,100,600,1919):
                linear,gate,bias=grammar()[i]
                got=bool(votes()[m]&(1<<i))
                self.assertEqual(got,bool(evaluate_program(m,linear,gate,bias)))

    def test_cumulative_learning_preserves_prior_slots(self):
        m=NativeHypothesisPortfolio()
        self.assertEqual(m.count(0),CANDIDATES)
        world=c.FabricatedWorld(500,"IN_FAMILY",(32,33),tuple(range(32)))
        for mask in range(8):
            m=add(m,0,mask,world.observe(mask))
        original=m.vector(0)
        for mask in range(8):
            m=add(m,1,mask,world._truth(mask))
        self.assertEqual(m.vector(0),original)
        self.assertEqual(m.count(0),m.count(1))
        self.assertEqual(m.details(0)["observations"],8)
        raw=m.checkpoint()
        recovered=NativeHypothesisPortfolio.restore(raw,digest(raw))
        self.assertEqual(recovered.checkpoint(),raw)
        self.assertEqual(recovered.vector(0),original)
        self.assertEqual(recovered.vector(1),m.vector(1))

    def test_disallowed_original_authority_and_duplicates(self):
        m=NativeHypothesisPortfolio()
        with self.assertRaises(ValueError):
            m.observe(0,3,1,"0"*64)
        with self.assertRaises(ValueError):
            add(m,0,64,1)
        with self.assertRaises(ValueError):
            add(m,0,0,2)
        a=add(m,0,0,0)
        with self.assertRaises(ValueError):
            add(a,0,0,0)
        self.assertEqual(m.count(0),CANDIDATES)

    def test_invalid_cold_checksum_and_false_weight_state(self):
        m=add(NativeHypothesisPortfolio(),0,5,1)
        raw=m.checkpoint()
        with self.assertRaises(ValueError):
            NativeHypothesisPortfolio.restore(raw,"0"*64)
        document=json.loads(raw)
        document["entries"][0]["live_hex"]="0"
        tampered=canonical(document)
        with self.assertRaises(ValueError):
            NativeHypothesisPortfolio.restore(tampered,digest(tampered))
        self.assertFalse(json.loads(raw)["accepted_native"])

    def test_frozen_disjoint_inputs(self):
        held,pool,init,pending=c.split_inputs()
        self.assertEqual((len(held),len(pool),len(init),len(pending)),
                         (32,32,8,24))
        self.assertFalse(set(held)&set(pool))
        self.assertEqual((held,pool,init,pending),c.split_inputs())

    def test_selector_uses_only_public_candidate_state(self):
        held,pool,init,pending=c.split_inputs()
        actor=c.FabricatedWorld(500,"IN_FAMILY",held,pool)
        model=NativeHypothesisPortfolio()
        used=[]
        for m in init:
            y=actor.observe(m)
            model=add(model,0,m,y)
            used.append(m)
        for policy in c.POLICIES:
            p=c.pick(policy,0,model,used,pending)
            self.assertIn(p,pending)
            self.assertEqual(p,c.pick(policy,0,model,used,pending))
        with self.assertRaises(ValueError):
            actor.held_truth(held[0])
        with self.assertRaises(ValueError):
            actor.observe(held[0])

    def test_independent_expression_enumerator_exact_parity(self):
        held,pool,init,pending=c.split_inputs()
        for seed,kind in ((500,"IN_FAMILY"),(501,"SHIFT")):
            actor=c.FabricatedWorld(seed,kind,held,pool)
            model=NativeHypothesisPortfolio()
            observations=[]
            for mask in init+pending[:8]:
                y=actor.observe(mask)
                model=add(model,0,mask,y)
                observations.append((mask,y))
            independent,count=c.independent_symbolic_predict(observations)
            self.assertEqual(model.vector(0),independent)
            self.assertEqual(model.count(0),count)

    def test_corrupt_first_eight_only(self):
        input_mask=tuple(range(8))
        original=(0,1,1,0,0,0,1,1)
        broken=c.corrupt_initial(500,input_mask,original)
        self.assertEqual(sum(a!=b for a,b in zip(broken,original)),2)
        self.assertEqual(broken,c.corrupt_initial(500,input_mask,original))

    def test_a3_sourcefree_audit_fixture_does_not_read_held(self):
        held,pool,initial,pending=c.split_inputs()
        audit=c.audit_control(501,"SHIFT",held,pool,initial,pending)
        self.assertEqual(audit["world"].effect_calls,16)
        self.assertEqual(len(audit["outputs"]),64)
        with self.assertRaises(ValueError):
            audit["world"].held_truth(held[0])

    def test_bootstrap_and_lookahead_frozen(self):
        delta=[0.125 if i%2 else -0.125 for i in range(32)]
        self.assertEqual(c.bootstrap_lower(delta),c.bootstrap_lower(delta))
        held,pool,initial,pending=c.split_inputs()
        model=NativeHypothesisPortfolio()
        a=c.pick_two_step(0,model._state(0)[0],pending)
        b=c.pick_two_step(0,model._state(0)[0],pending)
        self.assertEqual(a,b)
        self.assertIn(a,pending)

    def test_sourcefree_project_boundaries(self):
        text=CAMPAIGN.read_text()
        for forbidden in ("CausalGym", "Wingless", "YggdrasilOriginalSource",
                          "original_world.reset(", "original_world.do(",
                          "ckad09_generator", "original_source_first_use"):
            self.assertNotIn(forbidden,text)
        self.assertEqual(c.IN_SEEDS,tuple(range(701,733)))
        self.assertEqual(c.SHIFT_SEEDS,tuple(range(801,817)))
        self.assertEqual(c.CORRUPT_SEEDS,tuple(range(901,917)))

if __name__=="__main__":
    unittest.main()
