"""NCI-04E native falsifier: erased functional identity is not observable.

Uses the qualified NCI-04D2 LocalTaskRuntime unchanged. Two different
pre-lesion task functions collapse to the identical surviving state after
damage, so ANY deterministic label-free algorithm reading only this surviving
state, stimuli and surviving neighbor predictions must give the same repair
for both. This is an information-theoretic ambiguity witness, NOT a trained
mechanism or a positive scientific claim.
"""
import unittest

from yggdrasil.task_runtime import LocalTaskRuntime

class TestNCI04EIdentifiability(unittest.TestCase):
    def test_distinct_lost_functions_become_observationally_identical(self):
        # Same shared genome; two pre-damage specialists have different roles.
        # Feature order: bias, center, left, right, left*right, center*left,
        # center*right. Separate experts approximate AND and XOR.
        expert_and=[-6.,0.,6.,6.,0.,0.,0.]
        expert_xor=[0.,0.,0.,0.,-9.,0.,0.]
        expert_idle=[0.,0.,0.,0.,0.,0.,0.]
        left=LocalTaskRuntime()
        right=LocalTaskRuntime()
        for runtime in (left,right):
            runtime.core.genome=[expert_and[:],expert_xor[:],expert_idle[:]]
        lost=3
        left.core.roles[lost]=[12.,-12.,-12.]
        right.core.roles[lost]=[-12.,12.,-12.]
        # For cell 3, neighbor indices are 2 and 4: choose (1,0)
        # => AND approximately 0, XOR approximately 1.
        stimuli=[0]*8
        stimuli[2]=1
        pre_a=left.predict(stimuli)[lost]
        pre_b=right.predict(stimuli)[lost]
        self.assertLess(pre_a,.01)
        self.assertGreater(pre_b,.99)
        self.assertGreater(pre_b-pre_a,.98)
        # Damage removes the sole information differentiating the two worlds.
        left.lesion([lost])
        right.lesion([lost])
        self.assertEqual(left.snapshot(),right.snapshot())
        self.assertEqual(left.predict(stimuli),right.predict(stimuli))
        # No post-damage labels. Both reconstructions must remain identical.
        repaired_a=left.repair_unlabeled(stimuli,steps=64)
        repaired_b=right.repair_unlabeled(stimuli,steps=64)
        self.assertEqual(left.snapshot(),right.snapshot())
        self.assertEqual(repaired_a,repaired_b)
        v=repaired_a[lost]
        # Their actual lost functions demand incompatible responses.
        # At least one of the two worlds has nonzero error; for squared error,
        # the minimax lower bound for outcomes (0,1) is 0.25.
        self.assertGreaterEqual(max(v*v,(1-v)*(1-v)),.25-1e-12)
        print("NCI04E_YGG_LOST_FUNCTION_IDENTIFIABILITY_NO_GO="
              f"pred_before=({pre_a:.6f},{pre_b:.6f}) "
              f"survivors_identical=1 repair_identical=1 "
              f"worst_world_brier={max(v*v,(1-v)*(1-v)):.6f}")

    def test_no_surviving_role_label_after_lesion(self):
        a=LocalTaskRuntime()
        b=LocalTaskRuntime()
        a.core.roles[0]=[3.,-1.,-2.]
        b.core.roles[0]=[-3.,2.,1.]
        a.lesion([0]);b.lesion([0])
        self.assertEqual(a.snapshot(),b.snapshot())
        # Post-lesion target supervision remains deliberately rejected.
        with self.assertRaises(ValueError):
            a.observe([0]*8,[0]*8)

if __name__=="__main__":
    unittest.main()
