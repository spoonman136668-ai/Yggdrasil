"""ST8 source-only tests; no held, negative, interference source execution."""
import json
import unittest

from research.nci04_st8.private_world import (
    ACTIONS,PrivateCubicWorld,source_episode,private_params,
    pack,rol,monomials,effect,coefficient_rows,public_cue
)
from research.nci04_st8.source_audit import (
    put_constraint,source_gate
)


class ST8Source(unittest.TestCase):
    def test_authentic_training_source_public_cues_and_real_actions(self):
        for law in (3,5,7,11):
            for trial in (0,1,10):
                hist,cue=source_episode(law,100,trial)
                self.assertEqual(cue,private_params(law,100,trial))
                self.assertEqual(tuple(z[1] for z in hist),ACTIONS)
                self.assertEqual(public_cue(hist[:3]),cue)
                for before,act,after,change in hist:
                    self.assertEqual(tuple(a^b for a,b in zip(before,after)),change)

    def test_true_source_has_nonzero_private_cubic_terms(self):
        coeff=coefficient_rows()
        self.assertEqual(len(coeff),8)
        self.assertGreaterEqual(sum((x>>36).bit_count() for x in coeff),120)
        self.assertEqual(monomials(255).bit_count(),92)
        self.assertEqual(monomials(255,2).bit_count(),36)
        self.assertEqual(monomials(3).bit_count(),3)
        self.assertEqual(monomials(3,2).bit_count(),3)

    def test_public_delayed_consequence_uses_unknown_cubic_rule(self):
        hist,cue=source_episode(3,102,2)
        r,A,B=cue
        before,action,after,_=hist[4]
        self.assertEqual(action,3)
        self.assertEqual(
            pack(after)^rol(pack(before),r)^A,effect(B)
        )

    def test_original_source_cold_restoration(self):
        world=PrivateCubicWorld(3,101,2)
        for act in ACTIONS[:3]:world.step(act)
        raw=world.snapshot()
        new=PrivateCubicWorld.restore(raw)
        self.assertEqual(new.snapshot(),raw)
        for act in ACTIONS[3:]:
            self.assertEqual(new.step(act),world.step(act))

    def test_invalid_actions_have_no_effect(self):
        world=PrivateCubicWorld(3,100,0)
        raw=world.snapshot()
        for bad in (-1,0,1,2,4,True,1.0,"3"):
            with self.assertRaises(ValueError):world.step(bad)
            self.assertEqual(raw,world.snapshot())

    def test_source_snapshot_fails_closed(self):
        w=PrivateCubicWorld(3,100,0)
        obj=json.loads(w.snapshot())
        for patch in ({"schema":"fake"},{"r":4},{"B":-1},
                      {"law":True},{"step":6},{"pending":256}):
            d=dict(obj);d.update(patch)
            with self.assertRaises(ValueError):
                PrivateCubicWorld.restore(json.dumps(
                    d,sort_keys=True,separators=(",",":")
                ))

    def test_original_feature_elimination_and_conflict(self):
        basis=[0]*36
        self.assertEqual(put_constraint(basis,1,1,36),"INDEPENDENT")
        self.assertEqual(put_constraint(basis,1,1,36),"REDUNDANT")
        self.assertEqual(put_constraint(basis,1,0,36),"CONTRADICTS")
        with self.assertRaises(ValueError):
            put_constraint(basis,1<<36,0,36)

    def test_source_gate_refuses_precondition_drift(self):
        valid=(1536,7680,1536,92,200,80,0,8,0)
        self.assertEqual(source_gate(*valid)["disposition"],
                         "SOURCE_CUBIC_FALSIFIES_QUADRATIC_DEV_ONLY")
        for i,replacement in ((0,1535),(1,7679),(2,1535),
                              (3,91),(4,119),(5,15),(6,1),
                              (7,7),(8,1)):
            xs=list(valid);xs[i]=replacement
            self.assertEqual(source_gate(*xs)["disposition"],
                             "SOURCE_NONCUBIC_OR_UNIDENTIFIABLE_DEV_NO_GO")


if __name__=="__main__":
    unittest.main()
