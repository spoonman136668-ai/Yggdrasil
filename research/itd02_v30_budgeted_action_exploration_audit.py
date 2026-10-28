"""V30 preregistered selected-action exploration with matched public budgets.

External toy-world reward laws are NEVER provided to chooser or learner.
This is a hand-written engineering policy, NOT native learned exploration.
"""
import copy
import hashlib
import itertools
import json
import subprocess
import time
import tracemalloc
from pathlib import Path

from research.itd02_v29_observational_equivalence_audit import (
    selected_map, law, begin, snapshot as v29_snapshot, preferred_action,
)
from research.itd02_v26_calibrated_return_audit import RidgeCUSUM
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import ACTIONS, PUBLIC_CUES, canonical
from yggdrasil.itd02_v26_calibrated_return_dev import CalibratedReturnRingDev
from yggdrasil.itd02_v30_public_probe_policy_dev import PublicProbePolicyDev
from research.itd02_v23_unfamiliar_mapping_audit import train_source

PARENT="1b91ec3c51fa81b82e1cca09d99a4558a21ab190"
PREREG="99f9a79c907b9290b3e7eaee525cd11490742509"
BUDGETS=(0,1,3)
KINDS=("A","B","B0")
NATIVE_MODES=("novelty","greedy","round_robin","random")
RLS_MODES=("rls_novelty","rls_greedy")
ALL_MODES=NATIVE_MODES+RLS_MODES

PINS={
"yggdrasil/itd02_native_task_bridge_dev.py":"71eff80e3cfabb627e9d08d558b63f4043ce1fd5",
"yggdrasil/itd02_local_ring_memory_dev.py":"1db0835d5c99456bcf99a013d4836f49314a9d39",
"yggdrasil/itd02_v22_shared_context_ring_dev.py":"73dc4d7580f7f0b8ed8de1119b06504c44b0818f",
"yggdrasil/itd02_v24_protected_dual_memory_dev.py":"9ef95a28e9060dd79105f51122d527351756a1e0",
"yggdrasil/itd02_v25_unlabeled_return_dev.py":"f90e5029b121cbfc2e361f9e0941985eb1e69e3d",
"yggdrasil/itd02_v26_calibrated_return_dev.py":"8a0417d34c6ba94a4eaef33d767da14a4a5c9709",
"research/itd02_v29_observational_equivalence_audit.py":"86e30048b336b20d15a7a2c76d87d48d205c023f",
}

def verify():
    root=Path(__file__).resolve().parents[1]
    def git(*args):
        return subprocess.check_output(("git",)+args,cwd=root,text=True).strip()
    for sha in (PARENT,PREREG):
        assert git("merge-base","--is-ancestor",sha,"HEAD")=="",("PREREG_CHRONOLOGY",sha)
    for path,sha in PINS.items():
        assert git("hash-object",path)==sha,("PROTECTED_NATIVE_DRIFT",path)

def rls_scores(rls,cue,first):
    # Public source/readout only; source bank is never trained in this call.
    return [rls.predictions((cue,first,a))[2] for a in ACTIONS]

def model_scores(m,cue,first):
    begin(m,(cue,first,ACTIONS[0]))
    return m.scores()

def selected_policy(model,which):
    """Externally evaluate action quality from a frozen checkpoint only."""
    out=[]
    if which=="native":
        frozen=CalibratedReturnRingDev.restore(model.checkpoint())
        frozen.start_frozen_evaluation()
        for cue,first in itertools.product(PUBLIC_CUES,ACTIONS):
            scores=model_scores(frozen,cue,first)
            idx=max(range(3),key=lambda i:scores[i])
            chosen=ACTIONS[idx]
            frozen.accept_second(chosen,0.0,learning=False)
            out.append((cue,first,chosen))
    else:
        frozen=copy.deepcopy(model)
        for cue,first in itertools.product(PUBLIC_CUES,ACTIONS):
            scores=rls_scores(frozen,cue,first)
            idx=max(range(3),key=lambda i:scores[i])
            out.append((cue,first,ACTIONS[idx]))
    return out

def evaluate_actions(choices,kind,mapping):
    regret=0.0
    optimal=0
    details=[]
    for cue,first,action in choices:
        outcomes=[law(kind,(cue,first,a),mapping) for a in ACTIONS]
        idx=ACTIONS.index(action)
        miss=max(outcomes)-outcomes[idx]
        assert miss>=-1e-10
        regret+=miss
        optimal+=int(miss<=1e-10)
        details.append({"public_context":[cue,first],
                        "selected":action,"regret":round(miss,12)})
    return {"total_regret":round(regret,12),
            "optimal_action_contexts":optimal,
            "offline_evaluator_cases":details}

def run_arm(kind,mode,budget,source,observed,mapping):
    """Evaluator supplies one ACTUAL selected reward after prospective choice."""
    native=mode in NATIVE_MODES
    learner=CalibratedReturnRingDev(source) if native else RidgeCUSUM(source)
    chooser=PublicProbePolicyDev(mode if native else (
        "novelty" if mode=="rls_novelty" else "greedy"))
    source_sha=learner.bank.source_sha if native else learner.source.parameters_sha256()
    observed_records=[]
    probe_records=[]
    mean=0.0
    for j,(cue,first,second) in enumerate(observed):
        case=(cue,first,second)
        if native:
            begin(learner,case)
            predicted=learner.score(second)
            learner.accept_second(second,law(kind,case,mapping))
        else:
            sp,rp,predicted,tp=learner.predictions(case)
            learner.observe(case,law(kind,case,mapping),sp,rp)
        y=law(kind,case,mapping)
        chooser.observe_selected(cue,first,second)
        mean+=(y-mean)/(j+1)
        observed_records.append({"public":case,"reward":round(y,12),
            "predicted_before":round(predicted,12)})
    assert chooser.events==12
    assert all(chooser.counts[(c,f)][ACTIONS.index(a)]==1
               for c,f,a in observed)
    if native:
        assert learner.bank.slow.parameters_sha256()==source_sha
        assert learner.bank.slow.updates==576 and learner.bank.fast.updates==12
        assert len(learner.checkpoint())<=12288
        assert CalibratedReturnRingDev.restore(learner.checkpoint()).checkpoint()==learner.checkpoint()
    else:
        assert learner.source.parameters_sha256()==source_sha
    base_state=learner.checkpoint() if native else {
        "weights":copy.deepcopy(learner.weights),
        "precision":copy.deepcopy(learner.precision),
        "cusum":learner.cusum,"events":learner.events}
    base_choice=selected_policy(learner,"native" if native else "rls")
    if native:
        assert learner.checkpoint()==base_state
    for i in range(budget):
        cue,first,_second=observed[(0,4,8)[i]]
        if native:
            scores=model_scores(learner,cue,first)
        else:
            scores=rls_scores(learner,cue,first)
        actual_action=chooser.select(cue,first,scores)
        assert actual_action in ACTIONS
        was_unselected=chooser.counts[(cue,first)][ACTIONS.index(actual_action)]==0
        case=(cue,first,actual_action)
        predicted=scores[ACTIONS.index(actual_action)]
        # Evaluator-only law accessed AFTER independent choice.
        y=law(kind,case,mapping)
        if native:
            learner.accept_second(actual_action,y)
            assert learner.bank.slow.parameters_sha256()==source_sha
            assert learner.bank.fast.updates==13+i
            assert len(learner.checkpoint())<=12288
        else:
            sp,rp,cp,tp=learner.predictions(case)
            learner.observe(case,y,sp,rp)
        chooser.observe_selected(cue,first,actual_action)
        mean+=(y-mean)/(13+i)
        probe_records.append({
            "probe":i+1,"public":case,"was_previously_unselected":was_unselected,
            "predicted_before":round(predicted,12),
            "reward_observed":round(y,12),
            "selected_absolute_error":round(abs(y-predicted),12),
            "zero_baseline_selected_absolute_error":round(abs(y),12),
            "observed_mean_baseline_selected_absolute_error":round(abs(y-(mean-(y-mean)/(13+i))),12),
        })
    assert chooser.events==12+budget
    choices=selected_policy(learner,"native" if native else "rls")
    if native:
        assert learner.bank.slow.parameters_sha256()==source_sha
        assert CalibratedReturnRingDev.restore(learner.checkpoint()).checkpoint()==learner.checkpoint()
        frozen_restore=True
        checkpoint_bytes=len(learner.checkpoint())
        signals={"input":learner.bank.fast.forward_input_messages,
                 "output":learner.bank.fast.forward_output_messages,
                 "reverse":learner.bank.fast.reverse_credit_messages}
    else:
        assert learner.source.parameters_sha256()==source_sha
        frozen_restore=False
        checkpoint_bytes=None
        signals=None
    return {
        "law_offline":kind,"mode":mode,"budget":budget,
        "common_public_events":observed_records,
        "probe_public_events":probe_records,
        "candidate_legal_public_contexts":[list(observed[i][:2]) for i in (0,4,8)],
        "chosen_actions_after":choices,
        "decisions":evaluate_actions(choices,kind,mapping),
        "base_actions":base_choice,
        "source_sha":source_sha,"source_frozen":True,
        "selected_public_reward_count":chooser.events,
        "native_fast_updates":learner.bank.fast.updates if native else None,
        "cold_checkpoint_restored":frozen_restore,
        "checkpoint_bytes":checkpoint_bytes,
        "fast_edge_signals":signals,
    }

def classify(records,observed,mapping):
    lookup={(r["law_offline"],r["mode"],r["budget"]):r for r in records}
    # Every 12-feedback public history indistinguishable before optional probing.
    for mode in ALL_MODES:
        a=lookup[("A",mode,0)]
        b=lookup[("B",mode,0)]
        b0=lookup[("B0",mode,0)]
        assert a["common_public_events"]==b["common_public_events"]==b0["common_public_events"]
        assert a["base_actions"]==b["base_actions"]==b0["base_actions"]
    # A and B0 are identical reward laws; independent same-seed states must match.
    for mode in ALL_MODES:
        for budget in BUDGETS:
            a=lookup[("A",mode,budget)];b0=lookup[("B0",mode,budget)]
            assert a["probe_public_events"]==b0["probe_public_events"]
            assert a["chosen_actions_after"]==b0["chosen_actions_after"]
    novelty_a=lookup[("A","novelty",1)]["probe_public_events"][0]
    novelty_b=lookup[("B","novelty",1)]["probe_public_events"][0]
    identifier=(novelty_a["was_previously_unselected"] and
                novelty_a["public"]==novelty_b["public"] and
                novelty_a["reward_observed"]!=novelty_b["reward_observed"])
    def regret(kind,mode,budget):
        return lookup[(kind,mode,budget)]["decisions"]["total_regret"]
    baseB=regret("B","novelty",0)
    b3=regret("B","novelty",3)
    baseA=regret("A","novelty",0)
    a3=regret("A","novelty",3)
    gains={
        "better_than_self_budget0":b3<=0.9*baseB,
        "better_than_equal_budget_greedy":b3<=0.9*regret("B","greedy",3),
        "better_than_equal_budget_round_robin":b3<=0.9*regret("B","round_robin",3),
        "better_than_equal_budget_random":b3<=0.9*regret("B","random",3),
        "better_than_equal_budget_rls_novelty":b3<=0.9*regret("B","rls_novelty",3),
        "better_than_equal_budget_rls_greedy":b3<=0.9*regret("B","rls_greedy",3),
        "source_world_regret_not_worse_10pct":a3<=1.10*baseA+1e-12,
        "native_policy_changes_after_probes":lookup[("B","novelty",3)]["chosen_actions_after"]!=lookup[("B","novelty",0)]["chosen_actions_after"],
    }
    # If source regret is zero, the hard threshold requires zero.
    if not identifier:
        label="V30_PUBLIC_PROBE_IDENTIFIABILITY_NOT_ESTABLISHED__NO_SCIENCE"
    elif not all(gains.values()):
        label="V30_EXPLORATION_WITHOUT_STRONG_DECISION_GAIN__NO_SCIENCE"
    else:
        label="V30_BOUNDED_SYNTHETIC_BUDGETED_ACTION_EXPLORATION_ENGINEERING_POSITIVE__NO_SCIENCE"
    return label,{"first_novelty_probe_distinguishes_worlds":bool(identifier),
                  "decision_utility_gates":gains,
                  "B_regret_novelty_budget0":baseB,
                  "B_regret_novelty_budget3":b3,
                  "A_regret_novelty_budget0":baseA,
                  "A_regret_novelty_budget3":a3,
                  "B_regret_equal_budget3":{m:regret("B",m,3) for m in ALL_MODES}}

def main():
    verify()
    start=time.perf_counter()
    cpu=time.process_time()
    tracemalloc.start()
    source=train_source()["pretrained_shared"]
    observed,mapping=selected_map()
    assert len(observed)==12
    records=[run_arm(kind,mode,budget,source,observed,mapping)
             for kind in KINDS for mode in ALL_MODES for budget in BUDGETS]
    assert len(records)==54
    label,gates=classify(records,observed,mapping)
    # This hash includes full offline choices and all ACTUAL public outcomes,
    # excluding resource timers/memory that vary by OS.
    digest=hashlib.sha256(canonical(records)).hexdigest()
    classification={
        "schema":"ygg.itd02.v30.budgeted_selected_action_information.source_only.v1",
        "classification":label,"source_only":True,"scientific_first_use":False,
        "native_autonomous_exploration":False,"original_world_training":False,
        "original_native_source_modified":False,"new_learned_scalars":0,
        "native_stored_learned_scalars":326,"target_fast_trainable_scalars":163,
        "worlds":KINDS,"modes":ALL_MODES,"budgets":BUDGETS,
        "independent_arm_count":len(records),
        "common_source_training_selected_rewards":576,
        "common_target_selected_rewards":12,
        "first_probe_predeclared_context":observed[0][:2],
        "information_sufficiency_gates":gates,
        "canonical_case_policy_sha256":digest,
        "worst_native_checkpoint_bytes":max(
            r["checkpoint_bytes"] for r in records if r["checkpoint_bytes"] is not None),
        "all_source_frozen":all(r["source_frozen"] for r in records),
        "all_native_cold_restore":all(r["cold_checkpoint_restored"]
                                      for r in records if r["mode"] in NATIVE_MODES),
        "probe_public_cases":[{"law":r["law_offline"],"mode":r["mode"],
                               "budget":r["budget"],"probes":r["probe_public_events"],
                               "regret":r["decisions"]["total_regret"],
                               "optimal":r["decisions"]["optimal_action_contexts"]}
                              for r in records],
        "host_specific_resources":{"wall_seconds":time.perf_counter()-start,
            "cpu_seconds":time.process_time()-cpu,
            "python_tracemalloc_peak_bytes":tracemalloc.get_traced_memory()[1],
            "not_retail_performance":True}}
    print(json.dumps(classification,sort_keys=True,separators=(",",":")))

if __name__=="__main__":
    main()
