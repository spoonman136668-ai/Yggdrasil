"""WSP161 frozen source-free public weight-retention comparison.

Only fabricated public states and observed outcomes. No upstream source
simulator import, original interventions, hidden laws or private family labels.
"""
import hashlib
import json
import math
from pathlib import Path
import random
import struct
import sys
import time
import unittest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / "WSP-159"))
sys.path.insert(0, str(HERE / "WSP-160"))

from public_boundary import PublicTransition
from direct_weights import ProgrammedPublicDynamics, MAX_ROWS
from projected_repair import ProjectedWeightRepair, MAGIC


def authored_outcome(s, a):
    """Investigator-only fixture construction; never supplied to model."""
    sign = 2*a - 1
    return tuple(
        s[k] + (0.05, -0.03, 0.02, -0.01)[k]
        + (0.07, 0.05, -0.06, 0.035)[k] * s[k % 3]
        + (0.025, 0.04, 0.015, -0.02)[k] * s[(k+1) % 3]
        + sign * (0.09, -0.055, 0.06, -0.04)[k]
        + sign * 0.02 * s[(k+2) % 3]
        + s[3] * (0.6, -0.45, 0.35, -0.25)[k]
        + sign * s[3] * (0.2, -0.1, 0.12, -0.09)[k]
        for k in range(4)
    )


def sourcefree_rows(seed):
    r = random.Random(seed)
    def make(n, novel):
        rows = []
        for i in range(n):
            s = [r.uniform(-1.0,1.0) for _ in range(3)]
            s.append((1 if r.randrange(2) else -1) * r.uniform(0.35, 1.0)
                     if novel else 0.0)
            a = i % 2
            rows.append(PublicTransition.from_public(
                observation=s, action=a, next_observation=authored_outcome(s,a),
                reward=1.0, terminated=False, truncated=False))
        return rows
    return make(192,False),make(64,False),make(128,True),make(64,True)


def fit_old(rows):
    m=ProgrammedPublicDynamics()
    for r in rows:
        m=m.observe(r.observation,r.action,r.next_observation)
    return m


def measure(rows, pred):
    sq = sum((pred(r.observation,r.action)[k]-r.next_observation[k])**2
             for r in rows for k in range(4))
    return math.sqrt(sq/(len(rows)*4))


def max_drift(rows, m, base):
    return max(abs(m.predict(r.observation,r.action)[k]-
                   base.predict(r.observation,r.action)[k])
               for r in rows for k in range(4))


def independent_solve(gram, rhs):
    a=[list(gram[i])+[rhs[i]] for i in range(len(rhs))]
    n=len(rhs)
    for j in range(n):
        pivot=max(range(j,n),key=lambda i:abs(a[i][j]))
        if abs(a[pivot][j])<1e-14:
            raise AssertionError("constrained independent batch singular")
        a[pivot],a[j]=a[j],a[pivot]
        factor=a[j][j]
        a[j]=[x/factor for x in a[j]]
        for i in range(n):
            if i!=j:
                f=a[i][j]
                a[i]=[a[i][k]-f*a[j][k] for k in range(n+1)]
    return tuple(a[i][-1] for i in range(n))


def constrained_batch_control(base, anchors, rows):
    # Independently fit batch ridge to the exact SAME protected public feature
    # subspace as the projected editor; no RLS internals or learned coefficients.
    frozen=ProjectedWeightRepair(base,anchors)
    width=10
    gram=[[float(i==j) for j in range(width)] for i in range(width)]
    rhs=[[0.0]*4 for _ in range(width)]
    for r in rows:
        z=frozen.projected_features(r.observation,r.action)
        b=base.predict(r.observation,r.action)
        y=[r.next_observation[k]-b[k] for k in range(4)]
        for i in range(width):
            for j in range(width):
                gram[i][j]+=z[i]*z[j]
            for k in range(4):
                rhs[i][k]+=z[i]*y[k]
    weights=tuple(independent_solve(gram,[rhs[i][k] for i in range(width)])
                  for k in range(4))
    def predict(observation,action):
        b=base.predict(observation,action)
        z=frozen.projected_features(observation,action)
        return tuple(b[k]+math.fsum(w*v for w,v in zip(weights[k],z))
                     for k in range(4))
    return predict


class ProjectedRepairTests(unittest.TestCase):
    def test_frozen_three_seed_retention_new_learning_and_controls(self):
        metrics=[]
        for seed in (607,809,911):
            old_fit,old_valid,new_fit,new_valid=sourcefree_rows(seed)
            start=time.process_time()
            base=fit_old(old_fit)
            anchors=[(r.observation,r.action) for r in old_fit[:16]]
            model=ProjectedWeightRepair(base,anchors)
            self.assertEqual(model.protected_rank,8)
            frozen_baseline=measure(new_valid,base.predict)
            naive=base
            for row in new_fit:
                naive=naive.observe(row.observation,row.action,row.next_observation)
            naive_old_drift=max_drift(old_valid,naive,base)
            for row in new_fit:
                model,status=model.observe(row.observation,row.action,
                                           row.next_observation)
                self.assertEqual(status,"UPDATED")
            self.assertEqual(model.seen,128)
            independent=constrained_batch_control(base,anchors,new_fit)
            edit_rmse=measure(new_valid,model.predict)
            old_rmse=measure(old_valid,model.predict)
            drift=max_drift(old_valid,model,base)
            batch_rmse=measure(new_valid,independent)
            max_gap=max(abs(model.predict(r.observation,r.action)[k]-
                            independent(r.observation,r.action)[k])
                        for r in new_valid for k in range(4))
            self.assertLessEqual(drift,1e-9)
            self.assertLessEqual(edit_rmse,.03)
            self.assertGreaterEqual(frozen_baseline-edit_rmse,.05)
            self.assertLessEqual(max_gap,1e-8)
            checkpoint=model.checkpoint()
            restored=ProjectedWeightRepair.restore(checkpoint)
            self.assertEqual(restored.checkpoint(),checkpoint)
            self.assertEqual(restored._base.checkpoint(),base.checkpoint())
            self.assertEqual(
                [restored.predict(r.observation,r.action) for r in new_valid],
                [model.predict(r.observation,r.action) for r in new_valid])
            metrics.append(dict(seed=seed,old_fit=192,old_valid=64,
                new_fit=128,new_valid=64,protected_rank=model.protected_rank,
                old_anchor_prediction_max_drift=drift,
                old_valid_rmse=old_rmse,
                new_valid_rmse=edit_rmse,
                frozen_base_new_rmse=frozen_baseline,
                naive_continue_old_drift=naive_old_drift,
                naive_continue_new_rmse=measure(new_valid,naive.predict),
                constrained_batch_new_rmse=batch_rmse,
                batch_prediction_max_gap=max_gap,
                checkpoint_bytes=len(checkpoint),
                checkpoint_sha256=hashlib.sha256(checkpoint).hexdigest(),
                cpu_seconds=time.process_time()-start,
                original_source_actions=0))
        self.assertNotIn("causal_gym",sys.modules)
        print("WSP161_FROZEN_SOURCEFREE_RESULTS="+json.dumps(
            metrics,sort_keys=True,separators=(",",":")))

    def test_old_context_alias_contradiction_refused_without_reset(self):
        old_fit,old_valid,new_fit,new_valid=sourcefree_rows(607)
        base=fit_old(old_fit)
        anchors=[(r.observation,r.action) for r in old_fit[:16]]
        m=ProjectedWeightRepair(base,anchors)
        old=old_fit[0]
        forged=tuple(v+.5 for v in old.next_observation)
        before=m.checkpoint()
        after,status=m.observe(old.observation,old.action,forged)
        self.assertEqual(status,"UNIDENTIFIABLE")
        self.assertIs(after,m)
        self.assertEqual(m.checkpoint(),before)
        self.assertEqual(m.seen,0)

    def test_cold_update_continuation_is_identical(self):
        old_fit,_,new_fit,_=sourcefree_rows(607)
        base=fit_old(old_fit)
        anchors=[(r.observation,r.action) for r in old_fit[:16]]
        m=ProjectedWeightRepair(base,anchors)
        m,status=m.observe(new_fit[0].observation,new_fit[0].action,
                           new_fit[0].next_observation)
        self.assertEqual(status,"UPDATED")
        restored=ProjectedWeightRepair.restore(m.checkpoint())
        follow=new_fit[1]
        a,_=m.observe(follow.observation,follow.action,follow.next_observation)
        b,_=restored.observe(follow.observation,follow.action,
                             follow.next_observation)
        self.assertEqual(a.checkpoint(),b.checkpoint())

    def test_tamper_and_rehashed_bad_basis_rejected(self):
        old_fit,_,new_fit,_=sourcefree_rows(607)
        m=ProjectedWeightRepair(fit_old(old_fit),
           [(r.observation,r.action) for r in old_fit[:16]])
        raw=m.checkpoint()
        for damaged in (raw[:-1],raw+b" ",b"FAKE"+raw[4:],raw[:15]+
                        bytes((raw[15]^1,))+raw[16:],"not bytes"):
            with self.subTest(damaged=str(type(damaged))):
                with self.assertRaises(ValueError):
                    ProjectedWeightRepair.restore(damaged)
        data=json.loads(raw[8:-32])
        data["q"][0][0]+=0.2
        payload=json.dumps(data,sort_keys=True,separators=(",",":"),
                           allow_nan=False).encode("ascii")
        signed=MAGIC+len(payload).to_bytes(4,"big")+payload
        signed+=hashlib.sha256(signed).digest()
        with self.assertRaisesRegex(ValueError,"FIELDS"):
            ProjectedWeightRepair.restore(signed)

    def test_bad_public_fields_and_anchor_capacity(self):
        old_fit,_,new_fit,_=sourcefree_rows(809)
        base=fit_old(old_fit)
        anchors=[(r.observation,r.action) for r in old_fit[:16]]
        m=ProjectedWeightRepair(base,anchors)
        for action in (2,-1,False,"1"):
            with self.subTest(action=action),self.assertRaises(ValueError):
                m.observe(new_fit[0].observation,action,new_fit[0].next_observation)
        with self.assertRaises(ValueError):
            m.observe([math.nan,0,0,0],1,new_fit[0].next_observation)
        with self.assertRaises(ValueError):
            m.observe([0,0,0,0],1,[math.inf,0,0,0])
        with self.assertRaises(TypeError):
            m.observe(new_fit[0].observation,1,new_fit[0].next_observation,
                      hidden_wind=1)
        with self.assertRaisesRegex(ValueError,"ANCHOR_COUNT"):
            ProjectedWeightRepair(base,anchors+anchors[:1])

    def test_repair_cap_and_sourcefree_classification(self):
        old_fit,_,new_fit,_=sourcefree_rows(911)
        base=fit_old(old_fit)
        m=ProjectedWeightRepair(base,
           [(r.observation,r.action) for r in old_fit[:16]])
        full=ProjectedWeightRepair._from_state(
            m._base,m._basis,m._weights,m._inverse,MAX_ROWS)
        with self.assertRaisesRegex(ValueError,"BUDGET"):
            full.observe(new_fit[0].observation,new_fit[0].action,
                         new_fit[0].next_observation)
        self.assertEqual(ProjectedWeightRepair.restore(
            full.checkpoint()).seen,MAX_ROWS)


if __name__=="__main__":
    unittest.main()
