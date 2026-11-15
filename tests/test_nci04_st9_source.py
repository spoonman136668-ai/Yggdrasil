"""ST9 source-only mechanic and frozen stop tests; no held/negative runs."""
import json
import unittest

from research.nci04_st9.private_world import (
    F,PrivateWorld,original_episode,source_coefficients,
    effect,rol,pack,rotation,initial
)
from research.nci04_st9.source_audit import (
    ACTIVE,PASSIVE_REPEAT,PASSIVE_DISPERSED,
    greedy_public_actor,rank,insert,source_gate
)


class ST9SourceOnly(unittest.TestCase):
    def test_genuine_neutral_then_public_chosen_intervention(self):
        for law in (3,5,7,11):
            for B in (1,3,9,12):
                history=original_episode(law,101,0,B)
                self.assertEqual(len(history),2)
                self.assertEqual(tuple(e[1] for e in history),(0,B+1))
                for before,action,after,target in history:
                    self.assertEqual(tuple(x^y for x,y in zip(before,after)),target)
                before,_,post,_=history[0]
                self.assertEqual(
                    [r for r in (1,2,3) if rol(pack(before),r)==pack(post)],
                    [rotation(law)]
                )
                before,_,after,_=history[1]
                self.assertEqual(
                    pack(after)^rol(pack(before),rotation(law)),effect(B)
                )

    def test_active_policy_is_public_rank_8_no_source_oracle(self):
        self.assertEqual(greedy_public_actor(),ACTIVE)
        self.assertEqual(rank(ACTIVE),8)
        self.assertEqual(rank(PASSIVE_REPEAT),4)
        self.assertEqual(rank(PASSIVE_DISPERSED),6)
        self.assertEqual(F(15,1).bit_count(),4)
        self.assertEqual(F(15,2).bit_count(),8)

    def test_source_coefficients_are_evaluator_private_and_nonlinear(self):
        rows=source_coefficients(False)
        self.assertEqual(len(rows),8)
        self.assertGreaterEqual(sum((x>>4).bit_count() for x in rows),8)
        for b in (0,1,3,6,9,12,15):
            self.assertEqual(
                effect(b),sum(((F(b,2)&row).bit_count()&1)<<j
                              for j,row in enumerate(rows))
            )
        self.assertEqual(effect(0),0)

    def test_original_cold_restore_and_action_consequence(self):
        world=PrivateWorld(3,102,0)
        world.step(0)
        snap=world.snapshot()
        restored=PrivateWorld.restore(snap)
        self.assertEqual(restored.snapshot(),snap)
        self.assertEqual(world.step(10),restored.step(10))
        self.assertEqual(world.snapshot(),restored.snapshot())

    def test_invalid_actions_never_modify_original_source(self):
        world=PrivateWorld(3,100,0)
        before=world.snapshot()
        for a in (-1,1,17,True,1.0,"0"):
            with self.assertRaises(ValueError):world.step(a)
            self.assertEqual(before,world.snapshot())
        world.step(0)
        prev=world.snapshot()
        for a in (-1,0,17,False,"1"):
            with self.assertRaises(ValueError):world.step(a)
            self.assertEqual(prev,world.snapshot())

    def test_bad_snapshot_fails_closed(self):
        world=PrivateWorld(3,100,0)
        valid=json.loads(world.snapshot())
        for changes in ({"schema":"other"},{"law":True},{"rotation":0},
                        {"x":256},{"step":3},{"step":True}):
            data={**valid,**changes}
            with self.assertRaises(ValueError):
                PrivateWorld.restore(json.dumps(
                    data,sort_keys=True,separators=(",",":")
                ))

    def test_real_linear_contradiction_detection(self):
        rows=[0]*4
        self.assertEqual(insert(rows,1,1,4),"NEW")
        self.assertEqual(insert(rows,1,1,4),"KNOWN")
        self.assertEqual(insert(rows,1,0,4),"CONTRADICTION")
        with self.assertRaises(ValueError):
            insert(rows,1<<4,1,4)

    def test_frozen_source_gate_rejects_missing_fairness(self):
        episodes={n:8 for n in ("active","passive_repeat","passive_dispersed")}
        steps={n:16 for n in episodes}
        x=[episodes,steps,24,8,[4,6],16,1,0,0]
        self.assertEqual(source_gate(*x)["disposition"],
            "SOURCE_BUDGETED_CAUSAL_REPAIR_IDENTIFIABLE_DEV_ONLY")
        for index,bad in ((2,23),(3,7),(4,[4,5]),(5,7),
                          (6,0),(7,1),(8,1)):
            y=list(x);y[index]=bad
            self.assertEqual(source_gate(*y)["disposition"],
                "SOURCE_NONIDENTIFIABLE_OR_NO_LINEAR_CONTRADICTION_DEV_NO_GO")
        y=list(x);y[0]={"active":8,"passive_repeat":8,"passive_dispersed":7}
        self.assertEqual(source_gate(*y)["disposition"],
            "SOURCE_NONIDENTIFIABLE_OR_NO_LINEAR_CONTRADICTION_DEV_NO_GO")


if __name__=="__main__":
    unittest.main()
