#!/usr/bin/env python3
"""F47: source-free causal hypothesis-tournament intervention selection (DEV only).

A fixed source-free causal law generator with new hashes provides public paired
interventions. This experiment changes ONLY the isolated action-selection
mechanism; F46 learning, MLE and stronger structured controls remain frozen.
"""
from functools import lru_cache
from hashlib import sha1, sha256
from pathlib import Path
from time import perf_counter
import json

from f46_active_intervention_dev import (
    Arm, LocalLearner, MLE, SIZES, LIMIT, STRATEGIES,
    F46Rejected, hash64, performance, UINT64
)

HERE = Path(__file__).resolve().parent
POLICY = HERE / "f47_prereg.json"
FROZEN_BLOB = "916c385e104809b8029940b43fc25cc4892033af"
SCHEMA = "yggdrasil.qtr01.f47.coverage-constrained-hypothesis-tournament-dev.v1"
SEEDS = (127, 131, 137)
BUDGETS = (24, 12, 6)
MODES = {127:"invariant",131:"context_gated",137:"context_flip"}
DEGREES = (0,1,2,4,8)
PATTERNS = ((1,1),(0,1),(1,-1))
POLICIES = ("native_tournament","uniform","random","conventional_active")
CUTOFF = 0.45


class RejectedF47(ValueError):
    pass


def freeze(path=POLICY):
    raw=Path(path).read_bytes()
    blob=sha1(b"blob "+str(len(raw)).encode()+b"\x00"+raw).hexdigest()
    if blob!=FROZEN_BLOB:
        raise RejectedF47("F47_PREREG_SOURCE_CUSTODY_DRIFT")
    p=json.loads(raw)
    worlds=p.get("worlds",{})
    gate=p.get("frozen_go",{})
    fences=p.get("fences",{})
    if (p.get("schema")!=SCHEMA
        or p.get("status")!="FROZEN_BEFORE_F47_CODE_OR_RESULTS"
        or p.get("source_parent")!="e3fc033c8b9e3bd06d456cf4584914c9ce0c6dc4"
        or worlds.get("sizes_high_first")!=list(SIZES)
        or worlds.get("seeds")!=list(SEEDS)
        or worlds.get("law_by_seed")!={str(k):v for k,v in MODES.items()}
        or worlds.get("degree_options")!=list(DEGREES)
        or worlds.get("budgets_mean_repetitions_high_first")!=list(BUDGETS)
        or gate!={"b12_native_tournament_direct_gain_over_uniform_min":0.02,
            "b6_native_tournament_direct_gain_over_uniform_min":0.02,
            "b12_native_tournament_direct_gain_over_strongest_conventional_min":0.01,
            "b12_native_tournament_twohop_F1_min":0.60,
            "b6_minimum_repetitions_in_every_row":4,
            "b6_max_repetitions_per_row":12,
            "b12_max_repetitions_per_row":24,
            "b24_max_repetitions_per_row":48,
            "require_nine_worlds_three_budgets":True,
            "require_cold_tamper_and_real_interference":True,
            "require_exact_actions_equal_across_policies":True}
        or len(fences)!=8 or not all(v is True for v in fences.values())):
        raise RejectedF47("F47_FROZEN_POLICY_DRIFT")
    return p


class World:
    """Graph private to test evaluator. Every query returns only public outcomes."""
    def __init__(self,n,seed):
        if type(n) is not int or n not in SIZES or type(seed) is not int or seed not in SEEDS:
            raise RejectedF47("F47_UNREGISTERED_WORLD")
        self.n,self.seed,self.mode=n,seed,MODES[seed]
        graph={}
        degree_counts={str(d):0 for d in DEGREES}
        for s in range(n):
            degree=DEGREES[hash64(f"F47/degree/v1|{n}|{seed}|{s}")%5]
            degree_counts[str(degree)]+=1
            choices=sorted((hash64(f"F47/edge/v1|{n}|{seed}|{s}|{t}"),t)
                           for t in range(n) if t!=s)
            for _,t in choices[:degree]:
                graph[(s,t)]=1 if hash64(f"F47/sign/v1|{n}|{seed}|{s}|{t}")%2==0 else -1
        self._private_graph=graph
        self._private_degrees=degree_counts

    @lru_cache(maxsize=16384)
    def intervene(self,s,c,a,rep):
        if (type(s) is not int or not 0<=s<self.n
            or type(c) is not int or c not in (0,1)
            or type(a) is not int or a not in (0,1)
            or type(rep) is not int or not 0<=rep<LIMIT):
            raise RejectedF47("F47_INVALID_PUBLIC_INTERVENTION")
        obs=[]
        for t in range(self.n):
            effect=self._private_graph.get((s,t),0)
            if self.mode=="context_gated" and c==0:
                effect=0
            elif self.mode=="context_flip" and c==1:
                effect=-effect
            numerator=7 if (effect==1 and a==1) or (effect==-1 and a==0) else 2
            u=hash64(f"F47/obs/v1|{self.n}|{self.seed}|{s}|{c}|{a}|{rep}|{t}")
            obs.append(int(u<numerator*(UINT64//8)))
        return tuple(obs)

    def evaluator_only_truth(self):
        ans={}
        for (s,t),v in self._private_graph.items():
            for c in (0,1):
                if c==0 and self.mode=="context_gated":
                    continue
                ans[(c,s,t)]=-v if c==1 and self.mode=="context_flip" else v
        return ans

    def evaluator_degree_histogram(self):
        return dict(self._private_degrees)


def signed_category(value):
    if value>=CUTOFF:return 1
    if value<=-CUTOFF:return -1
    return 0


def qualitative_votes(mle,s):
    """Return genuine discrete law-vs-effect category disagreement by context."""
    n=mle.n
    if not mle.seen[0][s] or not mle.seen[1][s]:
        return (0,0)
    votes=[0,0]
    for t in range(n):
        if t==s:continue
        measured=(mle.delta(0,s,t),mle.delta(1,s,t))
        seen=(signed_category(measured[0]),signed_category(measured[1]))
        best=None
        for pattern in PATTERNS:
            norm=sum(x*x for x in pattern)
            coeff=sum(a*b for a,b in zip(measured,pattern))/norm
            residual=sum((a-coeff*b)**2 for a,b in zip(measured,pattern))
            if best is None or residual<best[0]:
                best=(residual,pattern,coeff)
        pattern,coeff=best[1],best[2]
        projected=tuple(signed_category(coeff*p) for p in pattern)
        if seen==(0,0):
            continue
        for c in (0,1):
            if seen[c]!=projected[c]:
                votes[c]+=1
    return tuple(votes)


class RowBudgetArm(Arm):
    """Same native source, MLE and public observation interface, capped policy."""
    def __init__(self,policy,n,seed):
        parent_kind="native_active" if policy=="native_tournament" else policy
        if policy not in POLICIES:raise RejectedF47("F47_UNKNOWN_POLICY")
        super().__init__(parent_kind,n,seed)
        self.policy=policy
        self.priority_votes_count=0
        self._votes_cached={}

    def max_rows(self,step):
        # Cumulative prefixes: 12*N pair queries b6; 24*N b12; 48*N b24.
        if step < 12*self.n:return 12
        if step < 24*self.n:return 24
        return 48

    def select(self,step):
        cap=self.max_rows(step)
        n=self.n
        if self.policy=="uniform":
            c,s=divmod(step%(2*n),n)
            if self.native.seen[c][s]>=cap:
                raise RejectedF47("F47_UNIFORM_CAP_ERROR")
            return c,s
        available=[(c,s) for c in (0,1) for s in range(n)
                   if self.native.seen[c][s]<cap]
        if not available:raise RejectedF47("F47_POLICY_EXHAUSTED_ROW_CAP")
        if self.policy=="random":
            return self.rng.choice(available)
        if self.policy=="conventional_active":
            fresh=[(c,s) for c,s in available if self.native.seen[c][s]==0]
            if fresh:return fresh[0]
            return max(available,key=lambda row:(self.priority(*row),
                                                  -(row[0]*n+row[1])))
        # Qualitative tournament F47: mandatory 4 paired interventions on ALL
        # rows before any discretionary allocation (not F46 heuristic).
        fresh=[(c,s) for c,s in available if self.native.seen[c][s]<4]
        if fresh:return fresh[0]
        per_source=[]
        for s in range(n):
            version=(self.mle.seen[0][s],self.mle.seen[1][s])
            prior=self._votes_cached.get(s)
            if prior is None or prior[0]!=version:
                prior=(version,qualitative_votes(self.mle,s))
                self._votes_cached[s]=prior
            per_source.append(prior[1])
        self.priority_votes_count+=1
        def score(row):
            c,s=row
            count=self.native.seen[c][s]
            return (per_source[s][c]/(1+count),-(c*n+s))
        return max(available,key=score)


def validate_one_world(n,seed):
    world=World(n,seed)
    arms={kind:RowBudgetArm(kind,n,seed) for kind in POLICIES}
    total=48*n
    snapshots={}
    times={}
    start=perf_counter()
    for step in range(total):
        for arm in arms.values():
            arm.step(world,step)
        if step+1 in (12*n,24*n,48*n):
            b=(step+1)//(2*n)
            snapshot={}
            for kind,arm in arms.items():
                rec=arm.checkpoint_report(world,b)
                counts=[v for byctx in arm.native.seen for v in byctx]
                rec["minimum_pair_count_per_row"]=min(counts)
                rec["maximum_pair_count_per_row"]=max(counts)
                rec["visited_all_rows"]=min(counts)>0
                rec["policy_priority_calls"]=arm.priority_votes_count
                snapshot[kind]=rec
            if len({v["pairs"] for v in snapshot.values()})!=1:
                raise RejectedF47("F47_UNEQUAL_ACTION_COUNTS")
            snapshots[b]={
                "nodes":n,"seed":seed,"context_law":world.mode,
                "mean_paired_repetitions":b,
                "source_degree_histogram_evaluator_only":world.evaluator_degree_histogram(),
                "policies":snapshot,
                "native_and_conventional_active_histories_equal":
                    arms["native_tournament"].visited==arms["conventional_active"].visited
            }
    return [snapshots[b] for b in BUDGETS],round(perf_counter()-start,4)


def run():
    p=freeze()
    results=[]
    times=[]
    for n in SIZES:
        for seed in SEEDS:
            worlds,elapsed=validate_one_world(n,seed)
            results.extend(worlds)
            times.append({"nodes":n,"seed":seed,"dev_elapsed_seconds":elapsed})
    def aggregate(b,policy,model="native",key="direct"):
        group=[x for x in results if x["mean_paired_repetitions"]==b]
        if len(group)!=9:raise RejectedF47("F47_INCOMPLETE_WORLD_FAMILY")
        return sum(x["policies"][policy][model][key]["f1"] for x in group)/9
    at12=aggregate(12,"native_tournament")
    at6=aggregate(6,"native_tournament")
    uni12=aggregate(12,"uniform")
    uni6=aggregate(6,"uniform")
    strong=max(
        aggregate(12,"conventional_active","fully_fitted_family_aware"),
        aggregate(12,"uniform","fully_fitted_family_aware"),
        aggregate(12,"uniform","fully_fitted_independent_MLE"))
    g=p["frozen_go"]
    controls=all(
        a["cold_restore_exact"] and a["tamper_rejected"]
        and a["real_intervention_held_unrelated_row"]
        and a["same_stream_independent_MLE_equal"]
        for w in results for a in w["policies"].values())
    coverage=all(
        (w["policies"]["native_tournament"]["minimum_pair_count_per_row"]>=g["b6_minimum_repetitions_in_every_row"]
         and w["policies"]["native_tournament"]["maximum_pair_count_per_row"]<=
            g["b6_max_repetitions_per_row"] if w["mean_paired_repetitions"]==6
         else w["policies"]["native_tournament"]["maximum_pair_count_per_row"]<=
            (g["b12_max_repetitions_per_row"] if w["mean_paired_repetitions"]==12
             else g["b24_max_repetitions_per_row"]))
        for w in results)
    equal=all(len({v["pairs"] for v in w["policies"].values()})==1 for w in results)
    go=(len(results)==27 and controls and coverage and equal
        and at12-uni12>=g["b12_native_tournament_direct_gain_over_uniform_min"]
        and at6-uni6>=g["b6_native_tournament_direct_gain_over_uniform_min"]
        and at12-strong>=g["b12_native_tournament_direct_gain_over_strongest_conventional_min"]
        and aggregate(12,"native_tournament","native","twohop")>=
            g["b12_native_tournament_twohop_F1_min"])
    return {
        "schema":SCHEMA,
        "classification":"DEV_TOURNAMENT_ACTIVE_POLICY_GO" if go
                         else "DEV_TOURNAMENT_ACTIVE_POLICY_NO_GO",
        "frozen_parent":p["source_parent"],
        "scales_high_first":list(SIZES),"seeds":list(SEEDS),"budgets_high_first":list(BUDGETS),
        "all_action_budgets_equal":equal,
        "all_cold_and_interference_controls_pass":controls,
        "all_native_min_exploration_and_row_caps":coverage,
        "native_tournament_direct_F1_b12":at12,
        "native_tournament_direct_F1_b6":at6,
        "uniform_direct_F1_b12":uni12,
        "uniform_direct_F1_b6":uni6,
        "strongest_conventional_direct_F1_b12":strong,
        "native_tournament_twohop_F1_b12":aggregate(12,"native_tournament","native","twohop"),
        "strong_conventional_components":{
            "conventional_active_family_aware":aggregate(12,"conventional_active","fully_fitted_family_aware"),
            "uniform_family_aware":aggregate(12,"uniform","fully_fitted_family_aware"),
            "uniform_independent_MLE":aggregate(12,"uniform","fully_fitted_independent_MLE")},
        "world_results":results,
        "elapsed_DEV_only":times,
        "hidden_world_graph_provided_to_learner":False,
        "protected_scientific_first_use":False,
        "accepted_native_source_changed":False,
        "scientific_pass":False,
        "deployed":False
    }


if __name__=="__main__":
    v=run()
    print("F47_CAUSAL_HYPOTHESIS_TOURNAMENT_DEV_RESULT="+
          json.dumps(v,sort_keys=True,separators=(",",":")))
    print("F47_NO_ACCEPTED_NATIVE_OR_PROTECTED_FIRST_USE=PASS")
