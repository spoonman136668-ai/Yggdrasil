"""V29 matched-feedback observational non-identifiability: source-only toy witness.

The two evaluator reward laws deliberately agree on all twelve selected public
rewards and disagree on unobserved actions. No agent can distinguish worlds
from those identical observations. The 13th action is a SEPARATE external
probe, not automatically learned exploration or original-world science.
"""
import copy
import hashlib
import itertools
import json
import math
import subprocess
import time
import tracemalloc
from pathlib import Path

from research.itd02_v18_intermediate_plasticity_audit import target
from research.itd02_v23_unfamiliar_mapping_audit import train_source, target_split
from research.itd02_v26_calibrated_return_audit import RidgeCUSUM
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import ACTIONS, PUBLIC_CUES, canonical
from yggdrasil.itd02_v22_shared_context_ring_dev import SharedContextRingDev
from yggdrasil.itd02_v25_unlabeled_return_dev import UnlabeledReturnRingDev
from yggdrasil.itd02_v26_calibrated_return_dev import CalibratedReturnRingDev

PARENT="e226cf23ef7c130f7edb72822052e88d52059766"
PREREG="752e708080fa7a2e6b5c9e30ad5cff7274ae3ba6"
PINS={
 "yggdrasil/itd02_native_task_bridge_dev.py":"71eff80e3cfabb627e9d08d558b63f4043ce1fd5",
 "yggdrasil/itd02_local_ring_memory_dev.py":"1db0835d5c99456bcf99a013d4836f49314a9d39",
 "yggdrasil/itd02_v22_shared_context_ring_dev.py":"73dc4d7580f7f0b8ed8de1119b06504c44b0818f",
 "yggdrasil/itd02_v24_protected_dual_memory_dev.py":"9ef95a28e9060dd79105f51122d527351756a1e0",
 "yggdrasil/itd02_v25_unlabeled_return_dev.py":"f90e5029b121cbfc2e361f9e0941985eb1e69e3d",
 "yggdrasil/itd02_v26_calibrated_return_dev.py":"8a0417d34c6ba94a4eaef33d767da14a4a5c9709",
 "research/itd02_v28_context_diverse_shadow_audit.py":"844efa1e5a618f770f9ea4b642f1fb519a85953a",
}
ALL_CASES=tuple(itertools.product(PUBLIC_CUES,ACTIONS,ACTIONS))

def selected_map():
    observed,withheld=target_split()
    assert len(observed)==12 and len(withheld)==24
    m={(cue,first):second for cue,first,second in observed}
    assert len(m)==12 and set(m)==set(itertools.product(PUBLIC_CUES,ACTIONS))
    return observed,m

def preferred_action(selected):
    # Always previously unselected; never source's optimal ACTIONS[2].
    return ACTIONS[0] if selected!=ACTIONS[0] else ACTIONS[1]

def law(kind,case,mapping):
    original=target(*case,nonlinear=True)
    if kind in ("A","B0"):
        return original
    if kind!="B":
        raise ValueError("INVALID_V29_EVALUATOR_ONLY_WORLD")
    cue,first,action=case
    prior_selected=mapping[(cue,first)]
    if action==prior_selected:
        return original
    return 4.0 if action==preferred_action(prior_selected) else -4.0

def begin(model,case):
    model.start_observation(case[0])
    model.accept_first(case[1])

def make_arm(source):
    return {"v26":CalibratedReturnRingDev(source),
            "v25":UnlabeledReturnRingDev(source),
            "scratch":SharedContextRingDev(mode="shared"),
            "rls":RidgeCUSUM(source)}

def snapshot(arm):
    q=arm["rls"]
    state={"source":q.source.checkpoint().decode("utf-8"),
           "weights":q.weights,"precision":q.precision,
           "cusum":q.cusum,"use_ridge":q.use_ridge,
           "source_loss":q.source_loss,"ridge_loss":q.ridge_loss,
           "events":q.events}
    return {
        "v26":arm["v26"].checkpoint(),
        "v25":arm["v25"].checkpoint(),
        "scratch":arm["scratch"].checkpoint(),
        "rls":canonical(state),
    }

def pair_history(kind,source,observed,mapping):
    models=make_arm(source)
    record=[]
    frozen_source=models["v26"].bank.source_sha
    for index,case in enumerate(observed):
        y=law(kind,case,mapping)
        predicted={}
        for name in ("v26","v25","scratch"):
            begin(models[name],case)
            predicted[name]=models[name].score(case[2])
        src,ridge,cs,two=models["rls"].predictions(case)
        predicted["rls_source"]=src
        predicted["rls_direct"]=ridge
        predicted["rls_cusum"]=cs
        predicted["rls_two_expert"]=two
        for name in ("v26","v25","scratch"):
            models[name].accept_second(case[2],y)
        models["rls"].observe(case,y,src,ridge)
        assert models["v26"].bank.slow.parameters_sha256()==frozen_source
        assert models["v25"].bank.slow.parameters_sha256()==frozen_source
        assert models["v26"].bank.fast.parameters_sha256()==models["scratch"].parameters_sha256()
        assert models["v25"].bank.fast.parameters_sha256()==models["scratch"].parameters_sha256()
        assert len(models["v26"].checkpoint())<=12288
        assert len(models["v25"].checkpoint())<=12288
        assert CalibratedReturnRingDev.restore(models["v26"].checkpoint()).checkpoint()==models["v26"].checkpoint()
        assert UnlabeledReturnRingDev.restore(models["v25"].checkpoint()).checkpoint()==models["v25"].checkpoint()
        record.append({"index":index+1,"public":case,"reward":round(y,12),
            "predictions":{k:round(v,12) for k,v in predicted.items()},
            "v26_fast":models["v26"].fast,
            "v25_fast":models["v25"].use_fast,
            "v26_evidence":[round(v,12) for v in models["v26"].evidence],
            "rls_cusum":round(models["rls"].cusum,12),
            "rls_uses_ridge":models["rls"].use_ridge})
    return models,record,snapshot(models)

def policy(model,which,observed_mapping):
    # Complete 12-context prospective action policy after the 12 public updates.
    m=type(model).restore(model.checkpoint())
    m.start_frozen_evaluation()
    choices=[]
    for cue,first in itertools.product(PUBLIC_CUES,ACTIONS):
        begin(m,(cue,first,ACTIONS[0]))
        if which=="v26":
            scores=m.scores()
        elif which=="v25":
            scores=m.scores()
        elif which=="scratch":
            scores=m.scores()
        else:
            raise ValueError("INVALID_PUBLIC_POLICY")
        selected=ACTIONS[max(range(len(ACTIONS)),key=lambda i:scores[i])]
        m.accept_second(selected,0.0,learning=False)
        choices.append(((cue,first),selected))
    return choices

def rls_policy(rls):
    c=copy.deepcopy(rls)
    choices=[]
    for cue,first in itertools.product(PUBLIC_CUES,ACTIONS):
        scores=[]
        for second in ACTIONS:
            _s,_r,cs,_t=c.predictions((cue,first,second))
            scores.append(cs)
        choices.append(((cue,first),ACTIONS[max(range(3),key=lambda i:scores[i])]))
    return choices

def paired_regret(choice_map,mapping):
    totals={"A":0.0,"B":0.0}
    details=[]
    for cue,first in itertools.product(PUBLIC_CUES,ACTIONS):
        selected=choice_map[(cue,first)]
        case=(cue,first,selected)
        per={}
        for kind in ("A","B"):
            value=law(kind,case,mapping)
            optimal=max(law(kind,(cue,first,a),mapping) for a in ACTIONS)
            regret=optimal-value
            assert regret>=-1e-12
            totals[kind]+=regret
            per[kind]=round(regret,12)
        details.append({"context":[cue,first],"selected":selected,
                        "regret":per})
    return {k:round(v,12) for k,v in totals.items()},details

def verify():
    root=Path(__file__).resolve().parents[1]
    def git(*args):
        return subprocess.check_output(("git",)+args,cwd=root,text=True).strip()
    for sha in (PARENT,PREREG):
        assert git("merge-base","--is-ancestor",sha,"HEAD")=="",("CHRONOLOGY",sha)
    for path,sha in PINS.items():
        assert git("hash-object",path)==sha,("SOURCE_BLOB_DRIFT",path)

def main():
    verify()
    start=time.perf_counter()
    cpu=time.process_time()
    tracemalloc.start()
    observed,mapping=selected_map()
    assert len(ALL_CASES)==36
    # Counterfactual outcomes are consulted only by the evaluator, not agents.
    for case in observed:
        assert law("A",case,mapping)==law("B",case,mapping)==law("B0",case,mapping)
    manifest={kind:[{"context":case,"reward":law(kind,case,mapping)}
                     for case in ALL_CASES] for kind in ("A","B","B0")}
    manifest_hash={kind:hashlib.sha256(canonical(rows)).hexdigest()
                   for kind,rows in manifest.items()}
    assert manifest_hash["A"]==manifest_hash["B0"]!=manifest_hash["B"]
    policy_optima={}
    min_joint=0.0
    for cue,first in itertools.product(PUBLIC_CUES,ACTIONS):
        decisions={}
        regrets={}
        for kind in ("A","B","B0"):
            values=[law(kind,(cue,first,a),mapping) for a in ACTIONS]
            decisions[kind]=ACTIONS[max(range(3),key=lambda i:values[i])]
            regrets[kind]=[max(values)-v for v in values]
        assert decisions["A"]==decisions["B0"]==ACTIONS[2]
        assert decisions["B"]!=decisions["A"]
        lower=min(regrets["A"][i]+regrets["B"][i] for i in range(3))
        assert lower>0
        min_joint+=lower
        policy_optima[(cue,first)]=decisions
    assert len(policy_optima)==12 and min_joint>0
    source=train_source()["pretrained_shared"]
    a,ar,asnap=pair_history("A",source,observed,mapping)
    b,br,bsnap=pair_history("B",source,observed,mapping)
    b0,b0r,b0snap=pair_history("B0",source,observed,mapping)
    assert ar==br==b0r
    assert asnap==bsnap==b0snap
    observed_sha=hashlib.sha256(canonical(ar)).hexdigest()
    for models in (a,b,b0):
        assert models["v26"].bank.slow.parameters_sha256()==models["v25"].bank.slow.parameters_sha256()
        assert models["v26"].bank.slow.updates==576
        assert models["v26"].bank.fast.updates==12
        assert models["v25"].bank.fast.updates==12
    policies={}
    for name in ("v26","v25","scratch","rls"):
        choices=(rls_policy(a["rls"]) if name=="rls" else policy(a[name],name,mapping))
        selection=dict(choices)
        assert len(selection)==12
        totals,detail=paired_regret(selection,mapping)
        assert totals["A"]+totals["B"]+1e-9>=min_joint
        assert (rls_policy(b["rls"]) if name=="rls" else policy(b[name],name,mapping))==choices
        policies[name]={"paired_regret":totals,"per_context":detail,
                        "identical_actions_in_both_worlds":True}
    # A single EXTRA legal selected probe, not evaluator-only reward and not
    # part of the original common twelve. Not an autonomous exploration claim.
    cue,first,selected=observed[0]
    probe=(cue,first,preferred_action(selected))
    assert probe not in observed and law("A",probe,mapping)!=law("B",probe,mapping)
    probe_records={}
    for kind,arm in (("A",a),("B",b)):
        y=law(kind,probe,mapping)
        before=arm["v26"].checkpoint()
        begin(arm["v26"],probe)
        before_prediction=arm["v26"].score(probe[2])
        arm["v26"].accept_second(probe[2],y)
        after=arm["v26"].checkpoint()
        assert before!=after
        probe_records[kind]={"selected":probe,"reward":y,
           "pre_probe_prediction":round(before_prediction,12),
           "post_probe_checkpoint_sha":hashlib.sha256(after).hexdigest()}
    assert probe_records["A"]["pre_probe_prediction"]==probe_records["B"]["pre_probe_prediction"]
    assert probe_records["A"]["reward"]!=probe_records["B"]["reward"]
    assert probe_records["A"]["post_probe_checkpoint_sha"]!=probe_records["B"]["post_probe_checkpoint_sha"]
    assert hashlib.sha256(canonical(ar+[probe_records["A"]])).hexdigest()!=hashlib.sha256(canonical(br+[probe_records["B"]])).hexdigest()
    # All checked equalities give a SYNTHETIC NEGATIVE information witness,
    # never an engineering positive or evidence of native exploration.
    case_payload={
        "observed_12_public_selected":ar,
        "world_manifests":manifest,
        "paired_optima":[{"context":list(k),"A":v["A"],"B":v["B"]} for k,v in policy_optima.items()],
        "regrets":policies,
        "probe":probe_records,
    }
    print(json.dumps({
        "schema":"ygg.itd02.v29.observational_equivalence.source_only.v1",
        "classification":"V29_SYNTHETIC_PUBLIC_INFORMATION_INSUFFICIENCY_WITNESSED__NO_SCIENCE",
        "source_only":True,"scientific_first_use":False,
        "original_world_training":False,
        "new_native_exploration_policy":False,
        "original_native_source_unchanged":True,
        "source_pretraining_selected_rewards":576,
        "common_selected_rewards":len(ar),
        "unobserved_second_action_counterfactuals":24,
        "changed_optimal_actions":len(policy_optima),
        "source_action_optimum_A":ACTIONS[2],
        "observed_public_sha256":observed_sha,
        "world_manifest_sha256":manifest_hash,
        "model_and_full_matrix_rls_state_identical_before_probe":True,
        "strictly_positive_theoretical_joint_regret_lower_bound":round(min_joint,12),
        "paired_regrets":{k:v["paired_regret"] for k,v in policies.items()},
        "probe_selected_public_action":probe,
        "probe_rewards":{"A":probe_records["A"]["reward"],"B":probe_records["B"]["reward"]},
        "probe_separates_worlds":True,
        "canonical_case_policy_sha256":hashlib.sha256(canonical(case_payload)).hexdigest(),
        "per_host_resource":{"wall_seconds":time.perf_counter()-start,
             "cpu_seconds":time.process_time()-cpu,
             "tracemalloc_peak_bytes":tracemalloc.get_traced_memory()[1],
             "retail_pc_qualification":False},
        },sort_keys=True,separators=(",",":")))

if __name__=="__main__":
    main()
