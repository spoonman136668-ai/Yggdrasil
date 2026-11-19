"""CKAD48 fixture tests. Only seed 0 is permitted for engineering fixtures."""
from __future__ import annotations

import importlib.util
import math
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("ckad48_fixture",HERE/"campaign.py")
M=importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)


class CKAD48FixtureTests(unittest.TestCase):
    def test_frozen_prereg_and_held_source_access(self):
        self.assertEqual(M.PREREG,"dba16e4e3a1c7f51ea18b45b15da84761de9e5ba")
        self.assertEqual(M.DEV,(48111,48112))
        self.assertEqual((M.OLD,M.NOVEL_END,M.TOTAL),(80,192,256))
        self.assertEqual(len(M.PARTITIONS),4)
        self.assertTrue(set(M.DEV).isdisjoint(M.PILOT+M.PRIMARY))
        for seed in (*M.PILOT,*M.PRIMARY,47111,47112,0):
            with self.assertRaisesRegex(ValueError,"CKAD48_ONLY_REGISTERED_DEV"):
                M.score_seed(seed)
        with self.assertRaisesRegex(ValueError,"CKAD48_ONLY_REGISTERED_DEV"):
            M.world_source(M.PRIMARY[0],0)

    def test_private_world_real_four_action_effects_and_boundaries(self):
        first,secret=M.world_source(0,0)
        second,other=M.world_source(0,1)
        self.assertEqual(len(first),256)
        self.assertEqual(len(set(key for key,_ in first)),256)
        self.assertNotEqual(first,second)
        self.assertEqual(M.world_source(0,0),(first,secret))
        self.assertTrue(all(row["a1"] in (0,1) and row["a2"] in (0,1)
                            for _,row in first[:80]))
        self.assertTrue(all(row["a1"] in (2,3) and row["a2"] in (2,3)
                            for _,row in first[80:192]))
        self.assertTrue(all(row["a1"] in (0,1) and row["a2"] in (0,1)
                            for _,row in first[192:]))
        self.assertEqual(secret["private_state_partition"],"highbit")
        self.assertEqual(other["private_state_partition"],"parity")
        self.assertTrue(all(secret["private_action_effect_mappings"][0][a]!=
            secret["private_action_effect_mappings"][1][a] for a in range(4)))
        self.assertEqual(sorted(secret["private_action_effect_mappings"][0]),[0,1,2,3])
        self.assertEqual(sorted(secret["private_action_effect_mappings"][1]),[0,1,2,3])
        # Same public action can have genuinely different physical effects.
        self.assertNotEqual(M.private_true_action_effect(0,secret["private_action_effect_mappings"],0,0),
                            M.private_true_action_effect(0,secret["private_action_effect_mappings"],2,0))
        with self.assertRaisesRegex(ValueError,"CKAD48_QUAD"):
            M.private_true_action_effect(0,secret["private_action_effect_mappings"],4,0)

    def test_true_counterfactual_expected_brier_not_training(self):
        events,secret=M.world_source(0,1)
        true_map=secret["private_action_effect_mappings"]
        for s in range(4):
            for a in range(4):
                for b in range(4):
                    p=M.private_expected_reward(1,true_map,s,a,b)
                    self.assertGreater(p,0)
                    self.assertLess(p,1)
                    self.assertLess(M.expected_brier(p,p),.25)
        with self.assertRaisesRegex(ValueError,"CKAD48_BRIER_DOMAIN"):
            M.expected_brier(-.1,.5)
        self.assertEqual(set(events[2][1]),
                        {"s0","a1","s1","a2","s2","y"})

    def test_every_arm_trains_exact_real_source_and_cold_retains_old(self):
        events,_=M.world_source(0,0)
        for mode in M.ARMS[:4]:
            learner=M.NativeStateEffects(mode)
            for t,event in enumerate(events):
                if t in M.PROBE_TIMES:
                    before=learner.checkpoint()
                    x=learner.predict_reward(0,2,3)
                    y=learner.transition(3,1)
                    self.assertTrue(0<x<1)
                    self.assertAlmostEqual(sum(y),1.0,delta=1e-12)
                    self.assertEqual(learner.checkpoint(),before)
                learner.observe(*event)
                if t==79:
                    prefix=learner.source[:80].copy()
            self.assertEqual(learner.source[:80],prefix)
            self.assertEqual(learner.n,256)
            self.assertEqual(sum(sum(v) for v in learner.reward),256)
            self.assertEqual(sum(sum(sum(v) for v in state) for state in learner.tabular),512)
            self.assertTrue(all(sum(learner.invariant[a])>0 for a in range(4)))
            self.assertAlmostEqual(sum(learner.posterior),1,delta=1e-12)
            full=learner.checkpoint()
            cold=M.NativeStateEffects.restore(full,M.sha256(full))
            self.assertEqual(cold.checkpoint(),full)
            self.assertEqual(cold.predict_reward(0,2,3),learner.predict_reward(0,2,3))
            self.assertTrue(learner.check_custody(events[-1])["cold_exact"])
            self.assertEqual(learner.checkpoint(),full)

    def test_state_dependent_nonxor_falsifies_global_invariant(self):
        context=M.NativeStateEffects("state_partition_native")
        false_model=M.NativeStateEffects("false_XOR_invariant")
        # Every 4-state × 4-action cell is genuinely exercised. The action's
        # effect flips between two XOR deltas conditional on high state bit.
        for t in range(256):
            s=(t//4)%4
            a=t%4
            delta=a if (s>>1)==0 else (a^2)
            s1=s^delta
            b=(a+1)%4
            delta2=b if (s1>>1)==0 else (b^2)
            s2=s1^delta2
            row={"s0":s,"a1":a,"s1":s1,"a2":b,"s2":s2,
                 "y":(s2&1)^((s2>>1)&1)}
            ident=M.sha256(f"ckad48-nonxor-fixture-only|{t}")
            context.observe(ident,row)
            false_model.observe(ident,row)
        actual=0
        false=0
        for s in range(4):
            for a in range(4):
                true_dest=s^(a if (s>>1)==0 else (a^2))
                actual+=context.transition(s,a)[true_dest]
                false+=false_model.transition(s,a)[true_dest]
        self.assertGreater(actual/16,false/16+.2)
        self.assertGreater(context.posterior[2],.85)
        self.assertEqual(context.n,false_model.n)
        self.assertGreater(sum(context.invariant[2]),0)

    def test_exact_model_uses_one_shared_structure_across_actions(self):
        src,_=M.world_source(0,1)
        bma=M.NativeStateEffects("exact_structure_BMA")
        for event in src[:125]:
            bma.observe(*event)
        a,b,s=2,3,1
        candidate=bma.predict_reward(s,a,b)
        rewards=[(pos+1)/(neg+pos+2) for neg,pos in bma.reward]
        same_structure=sum(w*sum(
            p1*p2*rewards[s2]
            for s1,p1 in enumerate(bma._transition_under(i,s,a))
            for s2,p2 in enumerate(bma._transition_under(i,s1,b)))
            for i,w in enumerate(bma.posterior))
        self.assertAlmostEqual(candidate,same_structure,delta=1e-14)
        before=bma.checkpoint()
        self.assertEqual(before,bma.checkpoint())
        self.assertGreater(max(bma.posterior),.25)

    def test_duplicate_id_conflict_and_checkpoint_tamper(self):
        events,_=M.world_source(0,1)
        m=M.NativeStateEffects("state_partition_native")
        for event in events[:100]:m.observe(*event)
        identifier,row=events[99]
        raw=m.checkpoint()
        self.assertIs(m.observe(identifier,row),m)
        self.assertEqual(raw,m.checkpoint())
        fake=dict(row,y=1-row["y"])
        with self.assertRaisesRegex(ValueError,"CKAD48_CONFLICTING_SOURCE_ID"):
            m.observe(identifier,fake)
        self.assertEqual(raw,m.checkpoint())
        with self.assertRaisesRegex(ValueError,"CKAD48_CHECKPOINT_SHA"):
            M.NativeStateEffects.restore(raw,"0"*64)

    def test_frozen_science_acceptance_is_not_a_toy_always_pass(self):
        def pretend(seed,c=.14,ex=.138,tab=.156,inv=.17,
                    early=.15,cold=.14,coverage=10):
            def arm_group(candidate):
                return {"expected_brier":{
                    "state_partition_native":candidate,
                    "exact_structure_BMA":ex,
                    "unrestricted_tabular":tab,
                    "false_XOR_invariant":inv,
                    "uniform_sham":.25}}
            groups={phase:arm_group(c) for phase in M.PHASES}
            groups["early_novel"]=arm_group(early)
            groups["cold_return"]=arm_group(cold)
            meta={"cold_exact":True,"duplicate_idempotent":True,
                  "conflict_atomic":True,"old_source_retained":True,
                  "per_action_transition_counts":[coverage]*4}
            return {"seed":seed,"world_model_receipts":[meta]*8,
                    "groups":groups}
        a,b=[pretend(seed) for seed in M.DEV]
        self.assertEqual(M.classify([a,b]),"DEV_FEASIBLE_NOT_SCIENTIFIC")
        self.assertEqual(M.classify([a,pretend(M.DEV[1],c=.15)]),"DEV_NO_GO")
        self.assertEqual(M.classify([a,pretend(M.DEV[1],tab=.148)]),"DEV_NO_GO")
        self.assertEqual(M.classify([a,pretend(M.DEV[1],inv=.16)]),"DEV_NO_GO")
        self.assertEqual(M.classify([a,pretend(M.DEV[1],early=.17)]),"DEV_NO_GO")
        self.assertEqual(M.classify([a,pretend(M.DEV[1],cold=.16)]),"DEV_NO_GO")
        self.assertEqual(M.classify([a,pretend(M.DEV[1],coverage=0)]),"SOURCE_INVALID")
        with self.assertRaisesRegex(AssertionError,"CKAD48_DEV_ORDER"):
            M.classify([b,a])


if __name__=="__main__":
    unittest.main()
