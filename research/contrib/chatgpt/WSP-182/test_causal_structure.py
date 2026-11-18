"""Frozen two-pass WSP182 source-free structural discovery, repair, and negatives."""
from __future__ import annotations

from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import random
import sys
import unittest

from causal_structure import (CausalEdges,PublicContrast,RetainedCausalRepair,N)

SEEDS=(217,223,227)


def sampled_edges(seed):
    r=random.Random(seed)
    a=[[F(0) for _ in range(N)] for _ in range(N)]
    for j in range(1,N):
        for i in range(j):
            a[j][i]=F(r.choice((-2,-1,0,1,2)),4)
    return CausalEdges(tuple(tuple(row) for row in a))


def witnesses(graph,seed):
    # Generation law and true graph exist in EVALUATOR only.
    # Independent two amplitudes per intervention, identity-matched
    # fabricated public baseline and consequence observations.
    r=random.Random(seed+500)
    rows=[]
    for index in range(N):
        for level in (F(1,2),F(3,2)):
            baseline=tuple(F(r.randrange(-4,5),4) for _ in range(N))
            change=graph.response(index,level)
            after=tuple(b+d for b,d in zip(baseline,change))
            rows.append(PublicContrast(index,baseline,after,level))
    return tuple(rows)


def conventional_inverse(witness_rows):
    """Independent, fully fitted conventional exact 4x4 matrix inversion.

    Uses ordinary Gauss-Jordan elimination, not the structural learner's
    descending direct-edge recursion. Both see precisely the same observations.
    """
    t=[[F(int(j==i)) for i in range(N)] for j in range(N)]
    for w in witness_rows:
        for j,v in enumerate(w.response()):
            t[j][w.action]=v
    aug=[t[j]+[F(int(j==k)) for k in range(N)] for j in range(N)]
    for i in range(N):
        p=aug[i][i]
        if p==0:raise ValueError("CONVENTIONAL_SINGULAR")
        aug[i]=[x/p for x in aug[i]]
        for j in range(N):
            if j != i:
                scale=aug[j][i]
                aug[j]=[x-scale*y for x,y in zip(aug[j],aug[i])]
    inverse=[row[N:] for row in aug]
    return CausalEdges(tuple(tuple(F(int(j==i))-inverse[j][i]
                                  for i in range(N)) for j in range(N)))


class WSP182TwoPassTests(unittest.TestCase):
    def test_pass1_exact_structure_reconstruction_and_strong_conventional_tie(self):
        for seed in SEEDS:
            with self.subTest(seed=seed):
                hidden=sampled_edges(seed)
                fit=witnesses(hidden,seed)
                native=CausalEdges.from_public_fit(fit)
                conventional=conventional_inverse(fit)
                self.assertEqual(native.weights,hidden.weights)
                self.assertEqual(native.weights,conventional.weights)
                for action in range(N):
                    # Fresh development test magnitude, same underlying law
                    # (NOT unfamiliar world), never supplied during FIT.
                    for magnitude in (F(3,4),F(5,4)):
                        self.assertEqual(native.response(action,magnitude),
                                         conventional.response(action,magnitude))
                self.assertEqual(
                    CausalEdges.restore(native.checkpoint()).checkpoint(),
                    native.checkpoint())
                self.assertEqual(max(abs(native.response(i,F(3,4))[j]-
                                         conventional.response(i,F(3,4))[j])
                                     for i in range(N) for j in range(N)),0)

    def test_pass2_one_edge_repair_and_cold_old_retention(self):
        for seed in SEEDS:
            with self.subTest(seed=seed):
                old=sampled_edges(seed)
                old_checkpoint=old.checkpoint()
                changed=[list(row) for row in old.weights]
                changed[3][1]+=F(1,2)
                new=CausalEdges(tuple(tuple(row) for row in changed))
                patched=RetainedCausalRepair.from_public_repair(
                    CausalEdges.from_public_fit(witnesses(old,seed)),
                    witnesses(new,seed+4000))
                self.assertEqual(patched.changed_direct_edge,(3,1))
                self.assertEqual(patched._old.checkpoint(),old_checkpoint)
                self.assertEqual(patched._current.weights,new.weights)
                restored=patched.cold_restore()
                self.assertEqual(restored.old_sha256,hashlib.sha256(old_checkpoint).hexdigest())
                self.assertEqual(restored._old.checkpoint(),old_checkpoint)
                observed_new=witnesses(new,seed+4100)[2] # action 1, first amplitude
                observed_old=witnesses(old,seed+4200)[2]
                self.assertEqual(patched.choose(()),"old")
                self.assertEqual(patched.choose((observed_new,)),"new")
                self.assertEqual(patched.choose((observed_old,)),"old")
                self.assertEqual(patched.predict(1,F(5,4),(observed_new,)),
                                 new.response(1,F(5,4)))
                self.assertEqual(patched.predict(1,F(5,4),(observed_old,)),
                                 old.response(1,F(5,4)))
                self.assertEqual(restored.predict(1,F(5,4),(observed_new,)),
                                 patched.predict(1,F(5,4),(observed_new,)))
                self.assertEqual(old.checkpoint(),old_checkpoint)

    def test_contradiction_gate_rejects_unrepresented_nonlinearity(self):
        base=sampled_edges(SEEDS[0])
        data=list(witnesses(base,SEEDS[0]))
        record=data[3] # second strength of action1
        altered=list(record.intervened)
        altered[3]+=F(1,8)*record.commanded_delta**2
        data[3]=PublicContrast(record.action,record.baseline,tuple(altered),
                               record.commanded_delta)
        with self.assertRaisesRegex(ValueError,"NONLINEAR_OR_DRIFT"):
            CausalEdges.from_public_fit(data)

    def test_repair_rejects_two_edge_mutation_and_preserves_old(self):
        old=sampled_edges(SEEDS[1])
        original=old.checkpoint()
        matrix=[list(row) for row in old.weights]
        matrix[3][1]+=F(1,2)
        matrix[2][0]-=F(1,4)
        other=CausalEdges(tuple(tuple(row) for row in matrix))
        with self.assertRaisesRegex(ValueError,"NOT_ONE_SPARSE_REPAIR"):
            RetainedCausalRepair.from_public_repair(old,witnesses(other,SEEDS[1]+100))
        self.assertEqual(old.checkpoint(),original)

    def test_refuse_ambiguous_unpaired_and_custody_corruption(self):
        graph=sampled_edges(SEEDS[2])
        rows=list(witnesses(graph,SEEDS[2]))
        with self.assertRaisesRegex(ValueError,"FIT_EIGHT_REQUIRED"):
            CausalEdges.from_public_fit(rows[:7])
        with self.assertRaisesRegex(ValueError,"TWO_LEVELS"):
            CausalEdges.from_public_fit(rows[:1]+rows[:1]+rows[2:])
        bad=rows[2]
        with self.assertRaisesRegex(ValueError,"PUBLIC_INTERVENTION"):
            PublicContrast(bad.action,bad.baseline,bad.intervened,F(1,5))
        with self.assertRaisesRegex(ValueError,"FUTURE_TO_PAST"):
            PublicContrast(2,(F(0),)*4,(F(1),F(0),F(1),F(0)),F(1))
        with self.assertRaisesRegex(ValueError,"PUBLIC_WITNESS_REQUIRED"):
            CausalEdges.from_public_fit([{"graph":graph.weights}]+rows[1:])
        with self.assertRaisesRegex(ValueError,"HISTORY_WINDOW"):
            RetainedCausalRepair(graph,CausalEdges(tuple(
                tuple(x+(F(1,2) if (j,i)==(3,1) else F(0))
                      for i,x in enumerate(row))
                for j,row in enumerate(graph.weights)))).choose((rows[0],rows[1]))

    def test_checkpoint_tamper_and_no_hidden_fields(self):
        old=sampled_edges(SEEDS[0])
        wire=old.checkpoint()
        self.assertEqual(old,CausalEdges.restore(wire))
        with self.assertRaisesRegex(ValueError,"CHECKPOINT_INTEGRITY"):
            CausalEdges.restore(wire[:-1]+bytes([wire[-1]^1]))
        with self.assertRaisesRegex(ValueError,"CHECKPOINT_SIZE"):
            CausalEdges.restore(b"")
        text=wire[8:-32].decode("ascii")
        tampered=text.replace('"schema":','"hidden_graph":1,"schema":')
        b=tampered.encode("ascii")
        payload=b"YCS1"+len(b).to_bytes(4,"big")+b
        payload+=hashlib.sha256(payload).digest()
        with self.assertRaisesRegex(ValueError,"CHECKPOINT_FIELDS"):
            CausalEdges.restore(payload)
        with self.assertRaisesRegex(ValueError,"CYCLIC_OR_DIAGONAL"):
            CausalEdges(((F(1),F(0),F(0),F(0)),(F(0),)*4,(F(0),)*4,(F(0),)*4))

    def test_independent_public_only_no_original_source(self):
        source=Path(__file__).with_name("causal_structure.py").read_text("utf-8")
        import ast
        tree=ast.parse(source)
        imports={a.name.split(".")[0] for node in ast.walk(tree)
                 if isinstance(node,ast.Import) for a in node.names}
        imports|={node.module.split(".")[0] for node in ast.walk(tree)
                 if isinstance(node,ast.ImportFrom) and node.module}
        self.assertFalse(imports&{"gym","torch","numpy","causal_gym","networkx"})
        self.assertNotIn("source_first_use_authority",source)
        self.assertNotIn("env.step(",source)
        self.assertNotIn("env.reset(",source)
        self.assertNotIn("source_graph",source)
        self.assertIn("no protected source imports or first-use calls",source)


if __name__=="__main__":
    unittest.main()
