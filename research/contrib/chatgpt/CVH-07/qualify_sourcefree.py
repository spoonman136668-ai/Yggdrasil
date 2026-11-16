"""CVH07 frozen source-free conventional controls: 4-arm toy qualification.

No original external CausalGym constructor, reset, do, source-private info,
paid API or third-party environment is imported or called. Every score here
belongs to an experimenter-authored toy fixture, NOT native scientific gain.
"""
from __future__ import annotations

import argparse
import functools
from hashlib import sha256
import json
from pathlib import Path
import time

from recurrent_control import (
    ConventionalPublicRNN,SeededPublicExplorer,PublicConsequence,
    training_tape,canonical,digest,EPOCHS,N_HIDDEN
)
from recurrent_control import sys as _public_baseline_sys
CVH06_IMPORT=Path(__file__).resolve().parent.parent/"CVH-06"
if str(CVH06_IMPORT) not in _public_baseline_sys.path:
    _public_baseline_sys.path.insert(0,str(CVH06_IMPORT))
from fourcell_control import (
    FourCellEarnedPolicy,PublicEarnedPolicy,independent_fourcell_public_batch,
    _canonical
)
from public_policy import _slot

HERE=Path(__file__).resolve().parent
import sys
CVH06=HERE.parent/"CVH-06"
if str(CVH06) not in sys.path:
    sys.path.insert(0,str(CVH06))
PARENT="b4ad72bad038223a722ef7e052407c26484ee0ce"
FIRST="94b04dfada301786387fd9fcf887d17a89d23f77"
TRAIN_SEEDS=tuple(range(101,197))
VALID_SEEDS=tuple(range(301,317))
TEST_SEEDS=tuple(range(501,517))
ARMS=("native","fourcell","recurrent","explorer")


def deny_original_firstuse():
    old=json.loads((HERE.parent/"CVH-06"/"source_first_use_NOT_AUTHORIZED.json").read_text())
    prereg=json.loads((HERE/"prereg.json").read_text())
    if (prereg["parent"]["sha"]!=PARENT
            or prereg["authority"]["first_use_original"] is not False
            or old["state"]!="NOT_AUTHORIZED_NO_ORIGINAL_SOURCE_ACTIONS"
            or old["owner_signed_source_lease_ref"] is not None
            or old["train_seed_ids"] or any(old["held_seed_ids_by_arm"].values())
            or any(old["transfer_seed_ids_by_arm"].values())
            or old["actual_source_interventions_this_gate"]!=0):
        raise PermissionError("CVH07_GENUINE_ORIGINAL_SOURCE_FIRST_USE_NOT_AUTHORIZED")
    return old,prereg


def fit_equal_public_training_tapes():
    """All three learned candidates consume the same 96x8 PUBLIC TRAIN logs."""
    train=tuple(training_tape(seed) for seed in TRAIN_SEEDS)
    validation=tuple(training_tape(seed) for seed in VALID_SEEDS)
    for row in train+validation:
        if len(row)!=8 or not row[-1].truncated:
            raise AssertionError("CVH07_PUBLIC_EXPOSURE_EPISODE_COUNT")

    native=PublicEarnedPolicy(min_support=2)
    fourcell=FourCellEarnedPolicy(min_support=2)
    for ep in train:
        prev_action=prev_reward=2
        for row in ep:
            k=_slot(prev_action,prev_reward,row.before,row.action)
            native.memory.observe(row)
            native.attempts[k]+=1
            prev_action,prev_reward=row.action,row.reward
    if native.memory.seen!=768 or sum(native.attempts)!=768:
        raise AssertionError("CVH07_NATIVE_SAME_PUBLIC_TRAIN_BUDGET")
    # Independent conventional exact batch fitted from identical witnessed
    # public outcomes; CVH06 model/implementation remains unchanged.
    flat=tuple(row for ep in train for row in ep)
    counts,totals=independent_fourcell_public_batch(flat)
    fourcell.count=counts;fourcell.total=totals
    for row in flat:
        fourcell.attempts[2*row.before+row.action]+=1
        six=list(row)
        fourcell.digest=sha256(bytes.fromhex(fourcell.digest)+
                               _canonical(six)).hexdigest()
    fourcell.seen=768
    if sum(fourcell.count)!=768 or sum(fourcell.attempts)!=768:
        raise AssertionError("CVH07_FOURCELL_SAME_PUBLIC_TRAIN_BUDGET")
    if FourCellEarnedPolicy.restore(fourcell.snapshot()).snapshot()!=fourcell.snapshot():
        raise AssertionError("CVH07_FOURCELL_TRAIN_COLD_FAIL")
    if PublicEarnedPolicy.restore(native.snapshot()).snapshot()!=native.snapshot():
        raise AssertionError("CVH07_NATIVE_TRAIN_COLD_FAIL")

    recurrent=ConventionalPublicRNN()
    initial=recurrent.brier(train)
    t0=time.perf_counter()
    before,after=recurrent.fit(train)
    training_wall=time.perf_counter()-t0
    if abs(before-initial)>1e-14 or recurrent.epochs_completed!=EPOCHS:
        raise AssertionError("CVH07_FULL_TRAINING_PROVENANCE")
    val=recurrent.brier(validation)
    if (initial-after)<0.02:
        # Deliberately a source-free ENGINEERING training objective;
        # do not post-tune the frozen model or declare fake science.
        raise AssertionError("CVH07_FROZEN_TRAINED_RECURRENT_CONVERGENCE_NO_GO")
    if ConventionalPublicRNN.restore(recurrent.snapshot()).snapshot()!=recurrent.snapshot():
        raise AssertionError("CVH07_RNN_TRAINED_COLD_FAIL")
    return {
        "models":{
            "native":native,"fourcell":fourcell,
            "recurrent":recurrent,"explorer":SeededPublicExplorer(1777),
        },
        "train":train,"validation":validation,
        "initial_train_brier":initial,"final_train_brier":after,
        "held_out_toy_validation_brier":val,
        "training_wall_seconds":training_wall,
    }


def toy_action_from_selected_policy(seed,index,state,action):
    """Public consequence recorded only AFTER selected action, toy fixture."""
    if type(seed) is not int or seed not in TEST_SEEDS or not 0<=index<8:
        raise PermissionError("CVH07_NO_ORIGINAL_SOURCE_OR_PROTECTED_SEED")
    hidden=seed&1
    reward=int(action==hidden)
    after=state^action^((seed+index)&1)
    return PublicConsequence(state,action,reward,after,False,index==7)


def run_four_arm_mock_validation(models):
    outputs={}
    for name in ARMS:
        policy=models[name]
        mock_rewards=0
        action_count=0
        per_episode=[]
        for seed in TEST_SEEDS:
            state=(seed*7+3)&1
            history=[]
            for step in range(8):
                action=policy.choose(state,tuple(history))
                # Only the already-chosen public binary action enters the
                # source-free toy fixture; reward hidden until after selection.
                row=toy_action_from_selected_policy(seed,step,state,action)
                policy.observe(row)
                history.append(row)
                state=row.after
                mock_rewards+=row.reward
                action_count+=1
            per_episode.append(len(history))
        if action_count!=128 or per_episode!=[8]*16:
            raise AssertionError("CVH07_SAME_ACTION_BUDGET_EACH_CONTROL")
        state=policy.snapshot()
        if type(policy).restore(state).snapshot()!=state:
            raise AssertionError("CVH07_FOUR_ARM_COLD_FINAL_TEST")
        outputs[name]={
            "mock_only":True,
            "original_source_actions":0,
            "public_actions":action_count,
            "mock_episode_count":16,
            "mock_reward_count_NON_SCIENTIFIC":mock_rewards,
            "cold_checkpoint_sha256":sha256(state).hexdigest(),
            "cold_checkpoint_bytes":len(state),
        }
    return outputs


def round_numeric_report(value):
    if type(value) is float:
        return round(value,9)
    if type(value) is list:
        return [round_numeric_report(x) for x in value]
    if type(value) is dict:
        return {k:round_numeric_report(v) for k,v in value.items()}
    return value


@functools.lru_cache(maxsize=1)
def qualify_sourcefree():
    old,prereg=deny_original_firstuse()
    frozen=fit_equal_public_training_tapes()
    before=frozen["initial_train_brier"]
    after=frozen["final_train_brier"]
    val=frozen["held_out_toy_validation_brier"]
    models=frozen["models"]
    pretest_sha={k:sha256(v.snapshot()).hexdigest() for k,v in models.items()}
    four=run_four_arm_mock_validation(models)
    if len(set(x["public_actions"] for x in four.values()))!=1:
        raise AssertionError("CVH07_PUBLIC_TEST_ACTION_BUDGET_NOT_MATCHED")
    if any(x["original_source_actions"] for x in four.values()):
        raise AssertionError("CVH07_ORIGINAL_SOURCE_ACTION_FORBIDDEN")
    out={
        "schema":"yggdrasil.cvh07.frozen-train-only-recurrent-exploration-sourcefree-qualification.v1",
        "parent":PARENT,
        "prereg_first":FIRST,
        "original_independent_source_sha":old["source_sha"],
        "training_source":"EXPERIMENTER_SYNTHETIC_FIXTURE_ONLY",
        "actual_original_source_construction":0,
        "actual_original_source_reset":0,
        "actual_original_source_do_actions":0,
        "protected_original_source_cohorts_opened":[],
        "new_original_source_firstuse_authorized":False,
        "no_source_private_field_learned":True,
        "train_episodes":96,"train_actions_per_learned_arm":768,
        "toy_validation_episodes":16,"toy_test_episodes":16,
        "toy_test_actions_per_arm":128,
        "recurrent":{"architecture":"8x6 Elman tanh full BPTT conventional",
                     "hidden_units":N_HIDDEN,
                     "train_epochs_completed":models["recurrent"].epochs_completed,
                     "initial_train_brier":before,
                     "final_train_brier":after,
                     "toy_validation_brier":val,
                     "frozen_training_brier_improvement":before-after,
                     "fully_trained_on_FROZEN_TOY_TRAIN_ONLY":True,
                     "fully_trained_on_original_external_source":False,
                     "optimizer_update_count":96*EPOCHS,
                     "weight_parameters":129,
                     "training_cpu_wall_seconds_per_runner_NOT_IN_HASH":
                         None,
                     },
        "learned_arm_public_training_actions":{
            "native":768,"fourcell":768,"recurrent":768},
        "untrained_explorer":"xorshift32 seeded public action control",
        "before_toy_test_checkpoint_sha256":pretest_sha,
        "arms":four,
        "original_model_code_unchanged":True,
        "baseline_fourcell_code_unchanged":True,
        "source_firstuse_still_DISARMED":True,
        "scientific_pass":False,
        "native_accepted":False,
        "deployment":False,
        "classification":"CONVENTIONAL_RECURRENT_TRAINED_ON_TOY_AND_EXPLORATION_CONTROLS_SOURCEFREE_ONLY",
    }
    out=round_numeric_report(out)
    out["receipt_sha256"]=digest(out)
    return out


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-json",required=True)
    cfg=parser.parse_args()
    r=qualify_sourcefree()
    out=Path(cfg.output_json)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(r,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("CVH07_SOURCEFREE_BASELINES="+json.dumps(
        {"classification":r["classification"],
         "initial_train_brier":r["recurrent"]["initial_train_brier"],
         "final_train_brier":r["recurrent"]["final_train_brier"],
         "validation_brier":r["recurrent"]["toy_validation_brier"],
         "source_actions":r["actual_original_source_do_actions"],
         "mock_test_actions_per_arm":r["toy_test_actions_per_arm"],
         "receipt_sha256":r["receipt_sha256"],
         "scientific_pass":False},
        sort_keys=True,separators=(",",":")),flush=True)


if __name__=="__main__":
    main()
