"""C34: action-history conditional public belief with matched conventional controls.

Source-only processing of real returned-action public C28 original FIT events.
No original MiniGrid imports/resets/steps, future action hints, hidden tile data,
or generated counterfactual action outcomes.
"""
from __future__ import annotations
import hashlib
import json
import math
from collections import Counter,defaultdict
from pathlib import Path

from research.native.itd02.r1.native_policy import PublicGrid,canonical,features
from research.mass_r7c29.effects import NativeCellEffect, data_event
from research.mass_r7c30.independent_logistic import IndependentPublicLogistic

HERE=Path(__file__).resolve().parent
P=json.loads((HERE/"PREREG.json").read_text(encoding="utf-8"))
SCHEMA="itd02.c34.source-public-causal-history-model.v1"


def public(e):
    s,a,y=data_event(e)
    return s,a,y


def distance(x):
    return abs(x.goal_x-x.x)+abs(x.goal_y-x.y)


def source_sequences(events):
    if type(events) is not list or len(events)!=P["source_dataset"]["selected_events"]:
        raise ValueError("C34_FROZEN_ORIGINAL_SOURCE_EVENT_COUNT_DRIFT")
    episodes=defaultdict(list)
    for e in events:
        before,a,y=public(e)
        after=PublicGrid(**e["returned_after"])
        features(after)
        key=(e["family"],e["seed"])
        if type(e["seed"]) is not int or type(e["family"]) is not str:
            raise ValueError("C34_SOURCE_ROLE_TYPE")
        group=episodes[key]
        if e["step"]!=len(group):
            raise ValueError("C34_SOURCE_RETURN_STEP_GAP")
        if group:
            prior=group[-1]
            if prior["returned_after"]!=e["before"]:
                raise ValueError("C34_SOURCE_OBSERVATION_HISTORY_NOT_CONTIGUOUS")
            if prior["terminated"] or prior["truncated"]:
                raise ValueError("C34_SOURCE_ACTION_AFTER_TERMINAL")
        group.append(e)
    if len(episodes)!=24:
        raise ValueError("C34_FROZEN_SOURCE_EPISODE_COUNT_CHANGED")
    return episodes


def prior_token(before,previous):
    features(before)
    if previous is None:
        return None
    prior_before=PublicGrid(**previous["before"])
    prior_after=PublicGrid(**previous["returned_after"])
    features(prior_before);features(prior_after)
    a=previous["chosen_action"]
    if type(a) is not int or a not in (0,1,2):
        raise ValueError("C34_NON_ORIGINAL_SELECTED_PREVIOUS_ACTION")
    moved=abs(prior_after.x-prior_before.x)+abs(prior_after.y-prior_before.y)
    if moved not in (0,1):
        raise ValueError("C34_ILLEGAL_PHYSICAL_DISPLACEMENT")
    return (a,int(prior_before.front_blocked),moved)


def all_records(episodes):
    out=[]
    for (family,seed),group in episodes.items():
        for i,e in enumerate(group):
            s,a,y=public(e)
            after=PublicGrid(**e["returned_after"])
            features(after)
            hist=prior_token(s,group[i-1] if i else None)
            out.append({"family":family,"seed":seed,"ordinal":i,
             "before":s,"chosen_action":a,"returned_front":y,
             "returned_after":after,"prior_history":hist,
             "reward":e["returned_reward"]})
    return out


def key_current(record):
    s=record["before"]
    features(s)
    a=record["chosen_action"]
    if type(a) is not int or a not in (0,1,2):
        raise ValueError("C34_ILLEGAL_CURRENT_SELECTED_ACTION")
    return f"{a}:{s.direction}:{int(s.front_blocked)}"


class SourceBeliefBeta:
    """Independent conventional Bayesian current-vs-history predictive posterior.

    Posterior shrinkage 2 pseudo-events, prospectively frozen. History is
    strictly previous source-returned action/consequence; never current target.
    """
    def __init__(self,with_history):
        if type(with_history) is not bool: raise ValueError("C34_MODEL_KIND")
        self.with_history=with_history
        self.base={}
        self.conditional={}
        self.updates=0

    @staticmethod
    def _p(pair):
        return (pair[0]+1)/(pair[1]+2) if pair else .5

    def predict(self,record):
        base_key=key_current(record)
        p0=self._p(self.base.get(base_key))
        if not self.with_history or record["prior_history"] is None:
            return p0
        hist_key=base_key+":"+":".join(map(str,record["prior_history"]))
        observed=self.conditional.get(hist_key)
        if not observed:return p0
        positive,total=observed
        return (positive+2*p0)/(total+2)

    def observe(self,record,history_override=None):
        k=key_current(record)
        y=record["returned_front"]
        if type(y) is not int or y not in (0,1):
            raise ValueError("C34_RETURN_FRONT_TARGET_UNQUALIFIED")
        history=record["prior_history"] if history_override is None else history_override
        if history is not None and (type(history) is not tuple or len(history)!=3 or
            type(history[0]) is not int or history[0] not in (0,1,2) or
            any(type(x) is not int or x not in (0,1) for x in history[1:])):
            raise ValueError("C34_MALFORMED_PUBLIC_PRIOR_HISTORY")
        if self.with_history and history is not None:
            extended=k+":"+":".join(map(str,history))
            hist=self.conditional.setdefault(extended,[0,0])
            hist[0]+=y;hist[1]+=1
        base=self.base.setdefault(k,[0,0])
        base[0]+=y;base[1]+=1
        self.updates+=1

    def snapshot(self):
        return {"schema":SCHEMA,"with_history":self.with_history,
                "base":self.base,"conditional":self.conditional,
                "updates":self.updates}

    def checkpoint(self):
        raw=self.snapshot()
        data=canonical(raw)
        if len(data)>1000000:raise ValueError("C34_UNBOUNDED_BELIEF_MEMORY")
        return canonical({"payload":raw,"sha256":hashlib.sha256(data).hexdigest()})

    @classmethod
    def restore(cls,blob):
        if type(blob) is not bytes or not 0<len(blob)<=1000000:
            raise ValueError("C34_BAD_COLD_INPUT")
        try:
            frame=json.loads(blob)
            if type(frame) is not dict or set(frame)!={"payload","sha256"}:
                raise ValueError("C34_BAD_SNAPSHOT_WIRE")
            x=frame["payload"]
            if type(x) is not dict or set(x)!={"schema","with_history","base",
               "conditional","updates"} or x["schema"]!=SCHEMA or (
               hashlib.sha256(canonical(x)).hexdigest()!=frame["sha256"]):
                raise ValueError("C34_TAMPERED_BELIEF")
            if type(x["with_history"]) is not bool or type(x["updates"]) is not int or (
                 not 0<=x["updates"]<=1000000):
                raise ValueError("C34_CORRUPT_UPDATE_COUNTER")
            model=cls(x["with_history"])
            for name in ("base","conditional"):
                raw=x[name]
                if type(raw) is not dict or len(raw)>10000:
                    raise ValueError("C34_CORRUPT_MEMORY")
                for k,v in raw.items():
                    parts=k.split(":")
                    if (type(k) is not str or len(parts)!=(6 if name=="conditional" else 3) or
                        not all(t.isdecimal() for t in parts) or
                        int(parts[0]) not in (0,1,2) or
                        int(parts[1]) not in range(4) or
                        int(parts[2]) not in (0,1)):
                        raise ValueError("C34_PRIVATE_OR_INVALID_MEMORY_KEY")
                    if name=="conditional" and (int(parts[3]) not in (0,1,2) or
                       int(parts[4]) not in (0,1) or int(parts[5]) not in (0,1)):
                        raise ValueError("C34_INVALID_PRIOR_ACTION_EVIDENCE")
                    if (type(v) is not list or len(v)!=2 or
                        any(type(i) is not int for i in v) or
                        not 0<=v[0]<=v[1]<=x["updates"]):
                        raise ValueError("C34_INVALID_POSTERIOR_COUNTS")
            if not x["with_history"] and x["conditional"]:
                raise ValueError("C34_MARKOV_MODEL_HAS_HIDDEN_HISTORY")
            if sum(v[1] for v in x["base"].values())!=x["updates"]:
                raise ValueError("C34_BASE_TOTAL_NOT_EQUAL_SOURCE_STEPS")
            if sum(v[1] for v in x["conditional"].values())>x["updates"]:
                raise ValueError("C34_HISTORY_EVENTS_EXCEED_SOURCE_STEPS")
            model.base=x["base"];model.conditional=x["conditional"];model.updates=x["updates"]
            return model
        except (TypeError,KeyError,OverflowError,AttributeError) as exc:
            raise ValueError("C34_MALFORMED_BELIEF_CHECKPOINT") from exc


def split_fit_roles(records):
    from research.mass_r7c28.run import P as C28
    learn={(fam,seed) for fam,seeds in C28["new_fit_episodes"].items() for seed in seeds[:8]}
    check={(fam,seed) for fam,seeds in C28["new_fit_episodes"].items() for seed in seeds[8:]}
    if learn&check or len(learn)!=16 or len(check)!=8:
        raise ValueError("C34_FROZEN_FIT_SPLIT_UNQUALIFIED")
    train=[r for r in records if (r["family"],r["seed"]) in learn]
    verify=[r for r in records if (r["family"],r["seed"]) in check]
    if len(train)+len(verify)!=len(records) or not train or not verify:
        raise ValueError("C34_UNQUALIFIED_TRAIN_CHECK_SOURCE_ROLES")
    return train,verify


def shuffled_histories(train):
    # Preserve first action episode start as UNKNOWN, rotate only eligible
    # PUBLIC already observed prior history tokens within each source family.
    buckets=defaultdict(list)
    for r in train:
        if r["prior_history"] is not None:
            buckets[r["family"]].append(r["prior_history"])
    index=Counter()
    output=[]
    for r in train:
        fam=r["family"]
        if r["prior_history"] is None:
            output.append(None)
            continue
        tokens=buckets[fam]
        if len(tokens)<2:raise ValueError("C34_NOT_ENOUGH_SOURCE_HISTORY_TO_SHUFFLE")
        j=index[fam]
        output.append(tokens[(j+1)%len(tokens)])
        index[fam]+=1
    return output


def sample_metrics(pairs):
    if not pairs:return {"n":0,"brier":None,"logloss":None}
    n=len(pairs)
    brier=sum((p-y)**2 for p,y in pairs)/n
    nll=-sum(y*math.log(p)+(1-y)*math.log1p(-p) for p,y in pairs)/n
    return {"n":n,"brier":round(brier,9),"logloss":round(nll,9)}


def sequence_support(episodes,records):
    pairs=Counter();triples=Counter()
    all_two=all_three=0;progress_two=0;no_motion_two=0;inverse_two=0
    for key,group in episodes.items():
        for i in range(len(group)-1):
            a,b=group[i:i+2]
            if a["returned_after"]!=b["before"]:
                raise ValueError("C34_SOURCE_TWO_STEP_RETURN_GAP")
            pair=f'{a["chosen_action"]}{b["chosen_action"]}'
            pairs[pair]+=1;all_two+=1
            origin=PublicGrid(**a["before"])
            ending=PublicGrid(**b["returned_after"])
            if distance(ending)<distance(origin):progress_two+=1
            if (origin.x,origin.y)==(ending.x,ending.y):no_motion_two+=1
            if a["chosen_action"] in (0,1) and b["chosen_action"]==1-a["chosen_action"]:
                inverse_two+=1
        for i in range(len(group)-2):
            chunk=group[i:i+3]
            triples["".join(str(e["chosen_action"]) for e in chunk)]+=1
            all_three+=1
    signature={}
    for r in records:
        s=r["before"]
        # One exact publicly seen state+actually chosen legal action, NO hidden
        # map, source seed or episode identity in the state key.
        k=(s.x,s.y,s.goal_x,s.goal_y,s.direction,int(s.front_blocked),r["chosen_action"])
        signature.setdefault(k,Counter())[r["returned_front"]]+=1
    repeated=[v for v in signature.values() if sum(v.values())>=2]
    conflict=[v for v in repeated if v[0] and v[1]]
    return {"original_physical_two_action_windows":all_two,
        "original_physical_three_action_windows":all_three,
        "observed_two_action_pair_counts":dict(sorted(pairs.items())),
        "observed_three_action_triplet_counts":dict(sorted(triples.items())),
        "two_action_windows_with_true_goal_progress":progress_two,
        "two_action_windows_without_translation":no_motion_two,
        "two_action_adjacent_inverse_turns":inverse_two,
        "exact_six_public_fields_plus_selected_action_distinct_keys":len(signature),
        "exact_public_selected_action_repeated_keys":len(repeated),
        "exact_public_selected_action_conflicting_next_front_keys":len(conflict),
        "exact_public_alias_ambiguity_demonstrated":bool(conflict),
        "no_conflicting_repeats_do_not_prove_markov_sufficiency":True}
