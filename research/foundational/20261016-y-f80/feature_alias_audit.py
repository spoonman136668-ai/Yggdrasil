"""F80 immutable public feature-signature alias audit across two arrival orders.

Offline task-answer-aware oracle used for labels and independent rescue
witnesses only. No learning, threshold selection, candidate promotion, or
protected source first-use. All public features are from frozen F79.
"""
from __future__ import annotations
import collections
import hashlib
import importlib.util
import json
import pathlib
import sys

P=pathlib.Path(__file__).resolve().parent

def gitblob(path):
    raw=path.read_bytes()
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()

assert gitblob(P/"prereg.json")=="1d3681d646ca6352366d392079f1d8ce4bf17eee"
original=P.parent/"20261016-y-f79"/"rare_interventions.py"
assert gitblob(original)=="4bba6e34d56ef96aa81515032988f9c5127fe35f"
s=importlib.util.spec_from_file_location("f80_unchanged_f79_public_features",original)
F79=importlib.util.module_from_spec(s)
sys.modules[s.name]=F79
s.loader.exec_module(F79)

F62=F79.F62
PACK=F79.PACK
AUDITOR=F79.AUDITOR
SOURCE=F79.SOURCE

def shifted(records,offset):
    return tuple((a+offset,b+offset,tuple(codes)) for a,b,codes in records)

def rename_feature_invariance(before,base,after,event,act,drop,original_vec):
    offset=1000000000
    shifted_event=(event[0]+offset,event[1],event[2]+offset)
    check=F79.public_action_features(
        shifted(before,offset),shifted(base,offset),
        shifted(after,offset),shifted_event,act,drop)
    assert check==original_vec,"F80_NUMERIC_NODE_IDENTIFIER_LEAKAGE"

def prove_single(public,q,index,after):
    mem=()
    trace=[]
    for i,event in enumerate(public):
        base=F62._f60_step(mem,event,PACK)
        if i==index:
            legal=[a[3] for a in F62.actions(mem,event,i,PACK)]
            assert after in legal and after!=base
            mem=after
        else:
            mem=base
        F62._valid_memory(mem,PACK)
        trace.append(tuple(PACK.pack(*r).hex() for r in mem))
    proof=AUDITOR.verify(public,q,trace)
    assert proof["prefixes"]==72 and proof["max_payload_bytes"]<=144
    assert PACK.solve(mem,q)==q["answer"]

def alias_counts(counter):
    mixed=[c for c in counter.values() if c["beneficial"] and c["harmful"]]
    return dict(unique_signatures=len(counter),
                conflicting_beneficial_harmful_signatures=len(mixed),
                beneficial_actions_sharing_harmful_signature=sum(c["beneficial"] for c in mixed),
                harmful_actions_sharing_beneficial_signature=sum(c["harmful"] for c in mixed))

def evaluate():
    labels=collections.defaultdict(collections.Counter)
    old_signatures=collections.defaultdict(lambda:collections.defaultdict(collections.Counter))
    new_signatures=collections.defaultdict(lambda:collections.defaultdict(collections.Counter))
    rows=[]
    renames=0
    for seed in range(-4701,-4717,-1):
        for family in (-2,-1):
            public,q,meta=SOURCE.source(seed,family)
            assert len(public)==72
            assert SOURCE.BASE.public_witness(public,q)=={q["answer"]}
            regime=meta["arrival_regime"]
            mem=()
            prefix_trace=[]
            rowlabels=collections.Counter()
            first=None
            for index,event in enumerate(public):
                baseline,alternatives=F79.unique_alternatives(mem,event,index)
                if alternatives:
                    base_end=F62._finish_fixed(baseline,public[index+1:],PACK)
                    base_good=PACK.solve(base_end,q)==q["answer"]
                    for act,drop,after,feat28 in alternatives:
                        alt_end=F62._finish_fixed(after,public[index+1:],PACK)
                        alt_good=PACK.solve(alt_end,q)==q["answer"]
                        if alt_good and not base_good:
                            lab="beneficial"
                            if first is None:
                                first=(index,after)
                        elif base_good and not alt_good:
                            lab="harmful"
                        else:
                            lab="neutral"
                        rename_feature_invariance(mem,baseline,after,event,act,drop,feat28)
                        renames+=1
                        sig12=tuple(round(float(v),8) for v in feat28[:12])
                        sig28=tuple(round(float(v),8) for v in feat28)
                        old_signatures[regime][sig12][lab]+=1
                        new_signatures[regime][sig28][lab]+=1
                        labels[regime][lab]+=1
                        rowlabels[lab]+=1
                mem=baseline
                F62._valid_memory(mem,PACK)
                prefix_trace.append(tuple(PACK.pack(*r).hex() for r in mem))
            proof=AUDITOR.verify(public,q,prefix_trace)
            assert proof["prefixes"]==72 and proof["max_payload_bytes"]<=144
            fixed_correct=PACK.solve(mem,q)==q["answer"]
            if first is not None:
                assert not fixed_correct
                prove_single(public,q,*first)
            rows.append(dict(seed=seed,family=family,
                regime=regime,kind=meta["question_type"],
                F60_correct=int(fixed_correct),
                beneficial=rowlabels["beneficial"],
                harmful=rowlabels["harmful"],
                neutral=rowlabels["neutral"],
                rescue_independently_audited=int(first is not None)))
    by={}
    for regime in ("original","local_rotate4"):
        sub=[x for x in rows if x["regime"]==regime]
        assert len(sub)==16
        by[regime]=dict(cases=len(sub),
            frozen_F60_correct=sum(x["F60_correct"] for x in sub),
            one_step_rescue_cases=sum(x["rescue_independently_audited"] for x in sub),
            label_counts=dict(labels[regime]),
            original_12_features=alias_counts(old_signatures[regime]),
            expanded_28_features=alias_counts(new_signatures[regime]),
            by_question_type={kind:dict(
                cases=sum(x["kind"]==kind for x in sub),
                frozen_F60_correct=sum(x["F60_correct"] for x in sub if x["kind"]==kind),
                rescued_cases=sum(x["rescue_independently_audited"] for x in sub if x["kind"]==kind)
            ) for kind in sorted({x["kind"] for x in sub})})
    cross={}
    for feature_count,d in ((12,old_signatures),(28,new_signatures)):
        cross[str(feature_count)]=dict(
            beneficial_original_harmful_rotated=sum(
                a["beneficial"] for key,a in d["original"].items()
                if d["local_rotate4"][key]["harmful"]>0),
            beneficial_rotated_harmful_original=sum(
                b["beneficial"] for key,b in d["local_rotate4"].items()
                if d["original"][key]["harmful"]>0),
            cross_regime_conflicting_signatures=sum(
                (a["beneficial"]>0 and d["local_rotate4"][key]["harmful"]>0)
                or (a["harmful"]>0 and d["local_rotate4"][key]["beneficial"]>0)
                for key,a in d["original"].items()))
    result=dict(
       schema="yggdrasil.f80.cross-arrival-feature-identifiability.synthetic.v1",
       stage="PREREGISTERED_UNREGISTERED_OFFLINE_DIAGNOSTIC",
       cases=len(rows),two_regimes=by,
       cross_arrival_opposite_credit_feature_aliases=cross,
       verified_public_node_relabeling_invariance_checks=renames,
       every_F60_and_rescued_full_72_prefix_audit=True,
       source_unchanged=True,
       original_F79_weights_or_thresholds_modified=False,
       model_trained=False,
       future_answers_used_only_in_offline_diagnostics=True,
       FIT_TRAIN_used=False,FIT_VALIDATE_used=False,
       DIAG_used=False,ORIGINAL_used=False,F3=False,
       optimizer_promotion=False,rows=rows)
    assert len(rows)==32
    print(json.dumps(result,sort_keys=True))

if __name__=="__main__":
    assert sys.argv[1:]==["--synthetic-only"]
    evaluate()
