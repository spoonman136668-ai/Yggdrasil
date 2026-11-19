"""CKAD43: two persistent source-trained causal specialists with prequential switching.

The original Yggdrasil native learner and CKAD42 learned causal controls train
cumulatively without modification. This research-only candidate learns solely
from genuinely observed two-stage public action/consequence episodes.
No hidden phases are supplied to either specialist or to the switching rule.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import sys
import time
from collections import deque
from pathlib import Path
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_episode_experience import NativeEpisodeExperience

HERE=Path(__file__).resolve().parent
E_PATH=HERE.parent/"CKAD-42"/"campaign.py"
spec=importlib.util.spec_from_file_location("ckad42_exact_source_for_43",E_PATH)
E=importlib.util.module_from_spec(spec)
spec.loader.exec_module(E)
C=E.C

SCHEMA="yggdrasil.ckad43.source-driven-recurrence-dev.v1"
PREREG="8f94cffb5e61be109038ba6f3611ee209161ce1c"
DEV=(43111,43112)
PILOT=(43211,43212)
PRIMARY=(43311,43312,43313)
EXCLUDED=(42111,42112,41101,41102,40811,40812,38911,38912,39181,39182)
WARM=48
WINDOW=12
ALARM=.21
GAIN=.035
B_MATURE=16
DWELL=8
PHASES=("stable_A","early_B","late_B","early_return_A","late_return_A")
LATE=("late_B","late_return_A")
BASELINE=(*C.CONVENTIONAL,"beta_hedge")
ARMS=("recall_two_rules","original_native","causal_full","causal_discount93",
      "causal_dual","causal_always_A","causal_never_switch_B",*BASELINE,"sham")


def mean(values):
    if not values: raise ValueError("CKAD43_EMPTY_SCORE_WINDOW")
    return sum(values)/len(values)


def pair_loss(p,q,row):
    dt=p-row["s2"]
    dy=q-row["y"]
    return (dt*dt+dy*dy)*.5


class PersistentRuleRecall:
    """One original trained A causal specialist, one fresh B specialist on alarm.

    No unobserved source, private phase identity, replayed fresh outcomes,
    or future consequence enters a read or routing decision.
    """
    def __init__(self):
        self.A=E.NativeInterventionRelations()
        self.B=None
        self.active="A"
        self.seen={}
        self.n=0
        self.switch_at=0
        self.transitions=[]
        self.score_history=deque(maxlen=WINDOW)
        self.forecasts=0

    def _model(self,key):
        if key=="A":return self.A
        if key=="B" and self.B is not None:return self.B
        raise ValueError("CKAD43_MISSING_SPECIALIST")

    def read(self,arm,view,first,next_state=None,second=None):
        if arm not in ("recall_two_rules","causal_always_A","causal_never_switch_B"):
            raise ValueError("CKAD43_INVALID_READ_ARM")
        key=(self.active if arm=="recall_two_rules" else
             "A" if arm=="causal_always_A" or self.B is None else "B")
        return self._model(key).read("short",view,first,next_state,second)

    def observe(self,identifier,views,row):
        if not isinstance(identifier,str) or not isinstance(views,tuple) or not isinstance(row,dict):
            raise ValueError("CKAD43_INVALID_PUBLIC_SOURCE")
        receipt=canonical([views,row]).decode("ascii")
        old=self.seen.get(identifier)
        if old is not None:
            if old!=receipt:raise ValueError("CKAD43_CONFLICTING_SOURCE_ID")
            return self
        if self.n>=E.MAX_EVENTS:
            raise ValueError("CKAD43_SOURCE_BUDGET")
        if self.A.n+(0 if self.B is None else self.B.n)!=self.n:
            raise AssertionError("CKAD43_SOURCE_COUNT_INVARIANT")
        view=views[0]
        scored={}
        for key in ("A","B"):
            if key=="B" and self.B is None:continue
            model=self._model(key)
            p=model.read("short",view,row["x1"])
            q=model.read("short",view,row["x1"],row["s2"],row["x2"])
            scored[key]=pair_loss(p,q,row)
        self.score_history.append(scored)
        self._model(self.active).observe(identifier,views,row)
        self.seen[identifier]=receipt
        self.n+=1
        if self.B is None:
            if self.n>=WARM and len(self.score_history)==WINDOW:
                last=[v["A"] for v in self.score_history]
                if mean(last)>ALARM:
                    self.B=E.NativeInterventionRelations()
                    self.active="B"
                    self.switch_at=self.n
                    self.transitions.append({"at":self.n,"kind":"contradiction_created_B",
                                             "evidence_window":WINDOW,
                                             "mean_active_loss":mean(last)})
                    self.score_history.clear()
        elif (self.B.n>=B_MATURE and self.n-self.switch_at>=DWELL and
              len(self.score_history)==WINDOW and
              all("B" in v for v in self.score_history)):
            alt="A" if self.active=="B" else "B"
            current_mean=mean([v[self.active] for v in self.score_history])
            other_mean=mean([v[alt] for v in self.score_history])
            if other_mean<=current_mean-GAIN:
                self.active=alt
                self.switch_at=self.n
                self.transitions.append({"at":self.n,"kind":"witnessed_loss_switch",
                                         "new_active":alt,"active_loss_prior":current_mean,
                                         "alternative_loss_prior":other_mean})
                self.score_history.clear()
        if self.A.n+(0 if self.B is None else self.B.n)!=self.n:
            raise AssertionError("CKAD43_DUPLICATED_TRAINING_RECORD")
        return self

    def checkpoint(self):
        return canonical({"schema":SCHEMA,"A":json.loads(self.A.checkpoint()),
                          "B":None if self.B is None else json.loads(self.B.checkpoint()),
                          "active":self.active,"n":self.n,"seen":self.seen,
                          "switch_at":self.switch_at,"transitions":self.transitions,
                          "score_history":list(self.score_history)})

    @classmethod
    def restore(cls,raw,sha):
        if digest(raw)!=sha:raise ValueError("CKAD43_CHECKPOINT_SHA_MISMATCH")
        obj=cls()
        data=json.loads(raw)
        if data["schema"]!=SCHEMA or data["n"]!=len(data["seen"]):
            raise ValueError("CKAD43_CHECKPOINT_SCHEMA_COUNTS")
        a=canonical(data["A"])
        obj.A=E.NativeInterventionRelations.restore(a,digest(a))
        if data["B"] is not None:
            b=canonical(data["B"])
            obj.B=E.NativeInterventionRelations.restore(b,digest(b))
        obj.active=data["active"]
        obj.n=data["n"]
        obj.seen=dict(data["seen"])
        obj.switch_at=data["switch_at"]
        obj.transitions=list(data["transitions"])
        obj.score_history=deque(data["score_history"],maxlen=WINDOW)
        if obj.active not in ("A","B") or (obj.active=="B" and obj.B is None):
            raise ValueError("CKAD43_RESTORE_INVALID_ACTIVE")
        if obj.A.n+(0 if obj.B is None else obj.B.n)!=obj.n:
            raise ValueError("CKAD43_RESTORE_SOURCE_PARITY")
        if obj.checkpoint()!=raw:raise ValueError("CKAD43_RESTORE_BYTES_CHANGED")
        return obj


def score_seed(seed):
    if seed not in DEV:raise ValueError("CKAD43_ONLY_REGISTERED_DEV")
    started=time.perf_counter()
    cpu_start=time.process_time()
    scored=[]
    worlds=[]
    for world in C.WORLDS:
        events,private=C.generator(seed,world)
        native=NativeEpisodeExperience(repair=True)
        full=E.NativeInterventionRelations()
        recall=PersistentRuleRecall()
        beta=C.Conventional()
        prefix=None
        witness=set()
        for t,(identifier,views,row,phase) in enumerate(events):
            if t==WARM:
                native=native.begin_stream()
                prefix=digest(canonical(native._ledger[:WARM]))
            view=views[0]
            if t>=WARM:
                p_native=float(native.context_forecast(view,row["x1"]))
                q_native=float(native.context_forecast(view,row["x1"],row["s2"],row["x2"]))
            else:
                p_native=float(native.forecast(view,row["x1"]))
                q_native=float(native.forecast(view,row["x1"],row["s2"],row["x2"]))
            predictions={"original_native":(p_native,q_native),"sham":(.5,.5)}
            for arm,mode in (("causal_full","full"),("causal_discount93","short"),("causal_dual","dual")):
                predictions[arm]=(full.read(mode,view,row["x1"]),
                                  full.read(mode,view,row["x1"],row["s2"],row["x2"]))
            for arm in ("recall_two_rules","causal_always_A","causal_never_switch_B"):
                predictions[arm]=(recall.read(arm,view,row["x1"]),
                                  recall.read(arm,view,row["x1"],row["s2"],row["x2"]))
            for arm in BASELINE:
                predictions[arm]=(beta.p(arm,"transition",row["s1"],row["x1"]),
                                  beta.p(arm,"terminal",row["s1"],row["x1"],
                                         row["s2"],row["x2"]))
            losses={key:pair_loss(*predictions[key],row) for key in ARMS}
            if phase in PHASES:
                # Evaluator-private phase is used *only* to group Brier results.
                scored.append({"seed":seed,"world":world,"t":t,"phase":phase,
                               "loss":losses,"active_forecast":recall.active,
                               "B_available":recall.B is not None})
            old_native=native.checkpoint()
            old_full=full.checkpoint()
            old_recall=recall.checkpoint()
            if (native.checkpoint()!=old_native or full.checkpoint()!=old_full
                  or recall.checkpoint()!=old_recall):
                raise AssertionError("CKAD43_READ_MUTATED_MODEL")
            # The same ONE real synthetic event trains each permitted arm
            # AFTER it is forecast and scored. No future data, duplicate or
            # phase tag is consumed by any learned model or comparator.
            native=native.observe(identifier,views,row)
            full.observe(identifier,views,row)
            recall.observe(identifier,views,row)
            beta.observe(row,{a:losses[a] for a in C.CONVENTIONAL})
            if identifier in witness:raise AssertionError("CKAD43_DUP_SOURCE")
            witness.add(identifier)
        if (len(witness)!=len(events) or len(native._ledger)!=len(events)
              or full.n!=len(events) or recall.n!=len(events)):
            raise AssertionError("CKAD43_SOURCE_LEDGER_INCOMPLETE")
        if digest(canonical(native._ledger[:WARM]))!=prefix:
            raise AssertionError("CKAD43_NATIVE_WARM_ERASED")
        cp_native=native.checkpoint()
        cp_full=full.checkpoint()
        cp_recall=recall.checkpoint()
        if NativeEpisodeExperience.restore(cp_native,digest(cp_native)).checkpoint()!=cp_native:
            raise AssertionError("CKAD43_NATIVE_COLD_FAIL")
        if E.NativeInterventionRelations.restore(cp_full,digest(cp_full)).checkpoint()!=cp_full:
            raise AssertionError("CKAD43_CAUSAL_COLD_FAIL")
        if PersistentRuleRecall.restore(cp_recall,digest(cp_recall)).checkpoint()!=cp_recall:
            raise AssertionError("CKAD43_RECALL_COLD_FAIL")
        last=events[-1]
        if native.observe(last[0],last[1],last[2]) is not native:
            raise AssertionError("CKAD43_NATIVE_DUPLICATE_NOT_IDEMPOTENT")
        if full.observe(last[0],last[1],last[2]) is not full:
            raise AssertionError("CKAD43_FULL_DUPLICATE_NOT_IDEMPOTENT")
        if recall.observe(last[0],last[1],last[2]) is not recall:
            raise AssertionError("CKAD43_RECALL_DUPLICATE_NOT_IDEMPOTENT")
        corrupted=dict(last[2]);corrupted["y"]^=1
        for model in (native,full,recall):
            try:model.observe(last[0],last[1],corrupted)
            except ValueError:pass
            else:raise AssertionError("CKAD43_CONFLICT_ACCEPTED")
        if (native.checkpoint()!=cp_native or full.checkpoint()!=cp_full
            or recall.checkpoint()!=cp_recall):
            raise AssertionError("CKAD43_CONFLICT_NOT_ATOMIC")
        worlds.append({"world":world,"episodes":len(events),
                       "authentic_consequences":2*len(events),
                       "original_source_prefix_exact":True,
                       "cold_exact":True,"read_only":True,"conflict_atomic":True,
                       "native_sha256":digest(cp_native),
                       "causal_full_sha256":digest(cp_full),
                       "recall_sha256":digest(cp_recall),
                       "A_train_events":recall.A.n,
                       "B_train_events":0 if recall.B is None else recall.B.n,
                       "specialist_source_event_parity":recall.A.n+(0 if recall.B is None else recall.B.n)==len(events),
                       "specialists_created":1+int(recall.B is not None),
                       "routing_transitions":recall.transitions,
                       "active_at_end":recall.active,
                       "recall_bytes":len(cp_recall),
                       "private_phase_boundary_evaluator_only":private})
    groups={}
    for phase in (*PHASES,"pooled_late_shift_and_return"):
        selected=[r for r in scored if (r["phase"] in LATE if phase=="pooled_late_shift_and_return" else r["phase"]==phase)]
        if not selected:raise AssertionError("CKAD43_NO_PHASE")
        groups[phase]={"events":len(selected),
                       "mean_brier":{a:mean([r["loss"][a] for r in selected]) for a in ARMS},
                       "candidate_A_predictions":sum(r["active_forecast"]=="A" for r in selected),
                       "candidate_B_predictions":sum(r["active_forecast"]=="B" for r in selected),
                       "available_B":sum(r["B_available"] for r in selected)}
    return {"seed":seed,"worlds":worlds,"groups":groups,
            "events":sum(w["episodes"] for w in worlds),
            "authentic_consequences":sum(w["authentic_consequences"] for w in worlds),
            "wall_seconds":round(time.perf_counter()-started,5),
            "cpu_seconds":round(time.process_time()-cpu_start,5)}


def classify(cases):
    if tuple(c["seed"] for c in cases)!=DEV:
        raise AssertionError("CKAD43_FROZEN_DEV_ORDER")
    for item in cases:
        if not all(w["cold_exact"] and w["read_only"] and w["original_source_prefix_exact"]
                   and w["conflict_atomic"] and w["specialist_source_event_parity"]
                   for w in item["worlds"]):
            return "SOURCE_INTEGRITY_FAILURE"
        if not all(w["specialists_created"]==2 for w in item["worlds"]):
            return "DEV_NO_GO"
        group=item["groups"]
        pooled=group["pooled_late_shift_and_return"]["mean_brier"]
        candidate=pooled["recall_two_rules"]
        best=min(pooled[a] for a in
                 ("original_native","causal_full","causal_discount93","causal_dual",*BASELINE))
        if candidate>.15 or candidate>best-.01:
            return "DEV_NO_GO"
        for phase,limit in (("early_return_A",.005),("late_B",.005)):
            p=group[phase]["mean_brier"]
            if p["recall_two_rules"]>p["original_native"]+limit:
                return "DEV_NO_GO"
        late=group["late_return_A"]["mean_brier"]
        if late["recall_two_rules"]>late["original_native"]-.02:
            return "DEV_NO_GO"
    return "DEV_FEASIBLE_NOT_SCIENTIFIC"


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--mode",choices=("preflight","dev"),required=True)
    parser.add_argument("--seed",type=int)
    args=parser.parse_args()
    if args.mode=="preflight":
        if args.seed is not None:raise ValueError("CKAD43_PREFLIGHT_WITH_SEED")
        print(json.dumps({"schema":SCHEMA,"prereg_commit":PREREG,
            "dev":list(DEV),"reserved_pilot":list(PILOT),
            "reserved_primary":list(PRIMARY),
            "science_pass":False,"first_use":False},sort_keys=True))
        return
    if args.seed not in DEV:raise ValueError("CKAD43_ONLY_REGISTERED_DEV")
    print("CKAD43_CASE="+json.dumps(score_seed(args.seed),sort_keys=True))


if __name__=="__main__":
    main()
