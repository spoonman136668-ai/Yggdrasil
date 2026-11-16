"""CVH08: public TRAIN episode admission for pre-existing qualified policies.

SOURCE-FREE ONLY. A *trusted* future operator must separately enforce original
seed leases and source first-use; this data-only interface grants no authority.
Learner sees only FKP24's six public fields, never source-private info.
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
import random
import sys

HERE=Path(__file__).resolve().parent
for p in (HERE.parent/"CVH-07",HERE.parent/"CVH-06",HERE.parent/"CVH-02"):
    if str(p) not in sys.path:
        sys.path.insert(0,str(p))
from recurrent_control import (
    ConventionalPublicRNN,PublicConsequence,EPOCHS,canonical,digest
)
from public_policy import PublicEarnedPolicy,_event,_slot
from fourcell_control import FourCellEarnedPolicy,independent_fourcell_public_batch,_canonical

TRAIN_EPISODES=64
MAX_ACTIONS=32
PARENT="94550530cb8ebce3f7d878932973d70b8dc8f114"
PREREG_FIRST="987a413bce8722f43458a654f78271cad6e70372"
TRAIN_ONLY="SOURCE_FREE_PUBLIC_LOG_TRAIN_ONLY"


def validate_completed_train(episodes):
    """Validate the entire unprivileged tape BEFORE any model is updated.

    This cannot establish that a real source seed was untouched or authorized;
    a separately qualified owner must enforce that on the original source.
    """
    if type(episodes) is not tuple or len(episodes)!=TRAIN_EPISODES:
        raise ValueError("CVH08_FROZEN_64_PUBLIC_TRAIN_EPISODES")
    packed=[]
    for episode in episodes:
        if type(episode) is not tuple or not 1<=len(episode)<=MAX_ACTIONS:
            raise ValueError("CVH08_PUBLIC_EPISODE_LENGTH")
        normalized=[]
        for step,row in enumerate(episode):
            x=_event(row)
            if step and x[0]!=normalized[-1][3]:
                raise ValueError("CVH08_IN_EPISODE_PUBLIC_STATE_DISCONTINUITY")
            if step<len(episode)-1 and (x[4] or x[5]):
                raise ValueError("CVH08_PUBLIC_EPISODE_PREMATURE_END")
            if step==len(episode)-1 and not (x[4] or x[5]):
                raise ValueError("CVH08_UNCLOSED_PUBLIC_EPISODE_NO_REPLAY")
            normalized.append(x)
        packed.append(tuple(PublicConsequence(*x) for x in normalized))
    return tuple(packed)


class SourceIndependentPublicTrainRNN(ConventionalPublicRNN):
    """Frozen CVH07 8-unit/48-epoch BPTT, without 96-toy exact-fit gate.

    This NEW data-only training entrance never constructs the original source.
    The inherited fit() stays unchanged and still requires 96 original toy
    tapes, so CVH07's historical qualification remains reproducible.
    """
    def fit_public(self,episodes):
        if self.trained or self.epochs_completed or self.seen or self.history or self.outstanding:
            raise ValueError("CVH08_TRAIN_ONCE_NO_POST_HOLD_RETUNING")
        clean=validate_completed_train(episodes)
        baseline=self.brier(clean)
        for epoch in range(EPOCHS):
            for ep in clean:
                self._sgd_full_episode(ep)
            self.epochs_completed+=1
        final=self.brier(clean)
        if not math.isfinite(baseline) or not math.isfinite(final):
            raise ArithmeticError("CVH08_TRAIN_NONFINITE")
        self.trained=True
        return baseline,final


def fit_all_learned_arms_on_public(episodes):
    """One frozen complete public TRAIN exposure, three distinct original arms.

    The conventional explorer requires no training. No source or held data
    accepted. All policy snapshots must reflect the same TRAIN public tape.
    """
    clean=validate_completed_train(episodes)
    flat=tuple(r for ep in clean for r in ep)
    native=PublicEarnedPolicy(min_support=2)
    fourcell=FourCellEarnedPolicy(min_support=2)
    for ep in clean:
        for r in ep:
            k=_slot(native.memory.prev_action,native.memory.prev_reward,r.before,r.action)
            native.memory.observe(r)
            native.attempts[k]+=1
    count,total=independent_fourcell_public_batch(flat)
    fourcell.count=count
    fourcell.total=total
    for r in flat:
        fourcell.attempts[2*r.before+r.action]+=1
        fourcell.digest=hashlib.sha256(
            bytes.fromhex(fourcell.digest)+_canonical(list(r))).hexdigest()
    fourcell.seen=len(flat)
    recurrent=SourceIndependentPublicTrainRNN()
    before,after=recurrent.fit_public(clean)
    models={"native":native,"fourcell":fourcell,"recurrent":recurrent}
    for model in models.values():
        raw=model.snapshot()
        if type(model).restore(raw).snapshot()!=raw:
            raise AssertionError("CVH08_COLD_TRAINING_SNAPSHOT_MISMATCH")
    if native.memory.seen!=len(flat) or fourcell.seen!=len(flat):
        raise AssertionError("CVH08_EQUAL_PUBLIC_TRAINING_BUDGET_MISMATCH")
    if sum(fourcell.count)!=len(flat) or sum(fourcell.attempts)!=len(flat):
        raise AssertionError("CVH08_FOURCELL_TRAINING_CUSTODY")
    return models,{"train_public_episode_count":len(clean),
                   "train_public_event_count":len(flat),
                   "public_training_tape_sha256":digest([[list(r) for r in ep] for ep in clean]),
                   "brier_before":baseline_round(before),
                   "brier_after":baseline_round(after),
                   "brier_improvement":baseline_round(before-after),
                   "train_epoch_count":recurrent.epochs_completed,
                   "training_model_hashes":{
                      k:hashlib.sha256(v.snapshot()).hexdigest() for k,v in models.items()
                   }}


def baseline_round(x):
    return float(format(x,".9f"))


def synthetic_public_episode(index):
    """Fabricated source-FREE public TRAIN of differing source-like lengths.

    Not the real Causal-Gymnasium MDP and no claim about its reward dynamics.
    No seed selection passed to model: only six witnessed public variables.
    """
    if type(index) is not int or not 0<=index<TRAIN_EPISODES:
        raise PermissionError("CVH08_SYNTHETIC_TRAIN_ONLY")
    lengths=(1,4,8,31,32)
    length=lengths[index%len(lengths)]
    state=(index*7+1)&1
    hidden=index&1
    rng=random.Random(91843+index*313)
    rows=[]
    for step in range(length):
        a=rng.randrange(2)
        r=int(a==hidden)
        nxt=state^a^((index+step)&1)
        rows.append(PublicConsequence(state,a,r,nxt,False,step==length-1))
        state=nxt
    return tuple(rows)


def sourcefree_training_receipt():
    p=json.loads((HERE/"prereg.json").read_text())
    deny=json.loads((HERE.parent/"CVH-06"/"source_first_use_NOT_AUTHORIZED.json").read_text())
    if (p["parent"]["sha"]!=PARENT or
            p["science"]["original_source_first_use_authorized"] is not False or
            deny["state"]!="NOT_AUTHORIZED_NO_ORIGINAL_SOURCE_ACTIONS" or
            deny["owner_signed_source_lease_ref"] is not None or
            deny["train_seed_ids"] or any(deny["held_seed_ids_by_arm"].values()) or
            any(deny["transfer_seed_ids_by_arm"].values())):
        raise PermissionError("CVH08_ORIGINAL_SOURCE_FIRST_USE_NOT_AUTHORIZED")
    tapes=tuple(synthetic_public_episode(i) for i in range(TRAIN_EPISODES))
    models,report=fit_all_learned_arms_on_public(tapes)
    if report["brier_improvement"]<.02:
        raise AssertionError("CVH08_FROZEN_DEVELOPMENT_CONVERGENCE_NO_GO")
    out={"schema":"yggdrasil.cvh08.sealed-64-public-episode-sourcefree-training.v1",
         "parent":PARENT,"prereg_first":PREREG_FIRST,
         "training_source":"SYNTHETIC_PUBLIC_EVENTS_ONLY",
         "recurrent_architecture":"UNCHANGED_CVH07_8TANH_48EPOCH_FULL_BPTT",
         "original_causalgym_reset_calls":0,"original_causalgym_do_calls":0,
         "source_original_first_use_authorized":False,
         "source_owner_seed_lease_present":False,
         "source_real_training_read":False,
         "science_pass":False,"native_accepted":False,"deployed":False,
         "classification":"SOURCE_FREE_PUBLIC_TRAINING_ADAPTER_ENGINEERING_ONLY",
         "full_public_source_train":report}
    out["receipt_sha256"]=digest(out)
    return out


if __name__=="__main__":
    import argparse
    a=argparse.ArgumentParser()
    a.add_argument("--output-json",required=True)
    args=a.parse_args()
    x=sourcefree_training_receipt()
    path=Path(args.output_json)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("CVH08_SOURCEFREE_PUBLIC_TRAIN="+json.dumps(
        {"classification":x["classification"],"train_events":x["full_public_source_train"]["train_public_event_count"],
         "before":x["full_public_source_train"]["brier_before"],"after":x["full_public_source_train"]["brier_after"],
         "source_actions":0,"receipt":x["receipt_sha256"]},sort_keys=True,separators=(",",":")),flush=True)
