"""V23 frozen source-public synthetic new-reward transfer and lesion audit.

No learner modification or original-world training. These external task laws
never enter the V22 learner. New *reward mappings on familiar public features*
are NOT independently unfamiliar causal environments or scientific first-use.
"""
import hashlib
import itertools
import json
import math
import subprocess
import time
import tracemalloc
from pathlib import Path

from research.itd02_v18_intermediate_plasticity_audit import (
    target as source_target, linear_solve,
)
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import (
    ACTIONS, ACTION_SITES, CELLS, PUBLIC_CUES, RING, canonical,
)
from yggdrasil.itd02_v22_shared_context_ring_dev import (
    SharedContextRingDev, HEAD_FEATURES, HOPS, LEARNED_SCALARS,
    _site_features, SOURCE_SIGNAL_PER_PASS, EDGE_SIGNAL_PER_PASS,
)

PARENT = "c17567365db1c0e401843c3151d375361af15806"
PREREG = "adfba157d11b656f11e77b9ba2153801b3124f85"
BLOBS = {
    "yggdrasil/itd02_native_task_bridge_dev.py": "71eff80e3cfabb627e9d08d558b63f4043ce1fd5",
    "yggdrasil/itd02_local_ring_memory_dev.py": "1db0835d5c99456bcf99a013d4836f49314a9d39",
    "research/itd02_v18_intermediate_plasticity_audit.py": "7a8f361ff13cf75f716c544add192c2ff9c5aae9",
    "yggdrasil/itd02_v20_causal_credit_dev.py": "c7eb9cfc0a4820400fb3c8b78febeb11ae035570",
    "yggdrasil/itd02_v22_shared_context_ring_dev.py": "73dc4d7580f7f0b8ed8de1119b06504c44b0818f",
    "research/itd02_v22_shared_ring_learning_audit.py": "050f7b521907656eae596c659a44c5702a226b5f",
}
CONTEXTS = tuple(itertools.product(PUBLIC_CUES, ACTIONS, ACTIONS))
SOURCE_EPOCHS = 16
RIDGE = 1e-4
U = (1.0, -1.0, -1.0, 1.0)
V = (1.0, 0.0, -1.0)
B = (1.0, -1.0, 0.5)
FAMILIES = ("cue_second", "triple_parity")
EDGE_LESION = frozenset((0, 1))


def git(*args):
    return subprocess.check_output(
        ("git",) + args, cwd=Path(__file__).resolve().parents[1],
        text=True,
    ).strip()


def verify():
    for ancestor in (PARENT, PREREG):
        assert git("merge-base", "--is-ancestor", ancestor, "HEAD") == ""
    for path, blob in BLOBS.items():
        assert git("hash-object", path) == blob, ("IMMUTABLE_SOURCE_DRIFT", path)
    assert CELLS == 8 and HOPS == 4 and LEARNED_SCALARS == 163
    assert len(CONTEXTS) == 36 and len(set(CONTEXTS)) == 36
    assert all(set(RING[i]) == {(i-1)%8, (i+1)%8}
               for i in range(CELLS))


def new_target(family, cue, first, second):
    """Two explicitly synthetic TARGET laws, external audit ONLY."""
    if family not in FAMILIES:
        raise ValueError("INVALID_TARGET_FAMILY")
    ci, ai, bi = (PUBLIC_CUES.index(cue), ACTIONS.index(first),
                  ACTIONS.index(second))
    if family == "cue_second":
        reward = (0.2 + 0.65*U[ci]*V[ai] + 0.60*B[bi] +
                  0.75*U[ci]*B[bi])
    else:
        reward = (-0.1 + 0.8*(1.0 if (ci+2*ai+bi)%3 == 0 else -1.0) +
                  0.5*(1.0 if ci%2 == ai%2 else -1.0))
    assert -4.0 <= reward <= 4.0
    return reward


def target_split():
    observed = [
        (cue, first, ACTIONS[(ci+2*ai)%3])
        for ci, cue in enumerate(PUBLIC_CUES)
        for ai, first in enumerate(ACTIONS)
    ]
    withheld = [case for case in CONTEXTS if case not in set(observed)]
    assert len(observed) == 12 and len(set(observed)) == 12
    assert len(withheld) == 24 and len(set(withheld)) == 24
    assert not set(observed).intersection(withheld)
    assert {case[2] for case in observed} == set(ACTIONS)
    return observed, withheld


def episode(model, context, reward, *, fit):
    cue, first, second = context
    model.start_observation(cue)
    model.accept_first(first)
    if fit:
        model.accept_second(second, reward, learning=True)
        return None
    prediction = model.score(second)
    model.accept_second(second, 0.0, learning=False)
    return prediction


def evaluate(model, contexts, feedback, *, freeze=True):
    raw = model.checkpoint()
    recovered = SharedContextRingDev.restore(raw)
    assert recovered.checkpoint() == raw
    if freeze:
        recovered.start_frozen_evaluation()
    frozen_hash = recovered.parameters_sha256()
    preds = [episode(recovered, c, feedback(*c), fit=False) for c in contexts]
    assert recovered.parameters_sha256() == frozen_hash
    assert recovered.native_ids == model.native_ids
    return preds


def features80(cue, first, second):
    ci, ai, bi = (
        PUBLIC_CUES.index(cue), ACTIONS.index(first),
        ACTIONS.index(second))
    feat = ([1.0] +
            [float(ci == i) for i in range(4)] +
            [float(ai == i) for i in range(3)] +
            [float(bi == i) for i in range(3)] +
            [float(ci == i and ai == j)
             for i in range(4) for j in range(3)] +
            [float(ci == i and bi == j)
             for i in range(4) for j in range(3)] +
            [float(ai == i and bi == j)
             for i in range(3) for j in range(3)] +
            [float(ci == i and ai == j and bi == k)
             for i in range(4) for j in range(3) for k in range(3)])
    assert len(feat) == 80
    return feat


def conventional_weights(observed, target):
    inputs = [features80(*case) for case in observed]
    labels = [target(*case) for case in observed]
    size = 80
    lhs = [[
        sum(row[i]*row[j] for row in inputs) +
        (RIDGE if i == j else 0.0)
        for j in range(size)] for i in range(size)]
    rhs = [sum(row[i]*y for row,y in zip(inputs,labels))
           for i in range(size)]
    weights = linear_solve(lhs,rhs)
    assert len(weights) == 80 and all(math.isfinite(x) for x in weights)
    return weights


def ridge_predict(weights, context):
    return sum(w*x for w,x in zip(weights, features80(*context)))


def damaged_scalar(values, *, broken=False, hops=4):
    assert len(values) == CELLS
    assert type(hops) is int and 0 <= hops <= HOPS
    states = list(values)
    for _ in range(hops):
        old = states
        next_states = []
        for cell in range(CELLS):
            neighbors = [
                0.0 if broken and frozenset((cell,nbr)) == EDGE_LESION
                else old[nbr] for nbr in RING[cell]
            ]
            next_states.append((old[cell]+sum(neighbors))/3.0)
        states = next_states
    return states


def damaged_readout(model, context):
    """Reconstruct original output ring, then remove ONLY output edge (0,1)."""
    cue, first, selected = context
    site = ACTION_SITES[ACTIONS.index(selected)]
    local = _site_features(cue, first)
    scalar = [
        sum(w*x for w,x in zip(model.cell_weights[i],local[i]))
        for i in range(CELLS)
    ]
    full = damaged_scalar(scalar)[site] + model.action_biases[ACTIONS.index(selected)]
    lesion = damaged_scalar(scalar,broken=True)[site] + model.action_biases[ACTIONS.index(selected)]
    zero_hop = damaged_scalar(scalar,hops=0)[site] + model.action_biases[ACTIONS.index(selected)]
    return full, lesion, zero_hop


def policy_regret(model, family):
    clone = SharedContextRingDev.restore(model.checkpoint())
    clone.start_frozen_evaluation()
    total = 0.0
    exact = 0
    records = []
    for cue, first in itertools.product(PUBLIC_CUES, ACTIONS):
        clone.start_observation(cue)
        clone.accept_first(first)
        scores = clone.scores()
        selected = max(range(len(ACTIONS)),key=lambda i:scores[i])
        chosen = ACTIONS[selected]
        values = [new_target(family,cue,first,action) for action in ACTIONS]
        regret = max(values)-values[selected]
        assert regret >= -1e-12
        total += regret
        exact += int(regret <= 1e-12)
        clone.accept_second(chosen,0.0,learning=False)
        records.append({
            "cue":cue,"actual_first":first,
            "selected_action":chosen,"regret":round(regret,12),
        })
    return {"total_regret":total,"optimal_context_count":exact,
            "cases":records}


def baseline_policy(weights, family):
    total = 0.0
    exact = 0
    for cue, first in itertools.product(PUBLIC_CUES, ACTIONS):
        scores = [ridge_predict(weights,(cue,first,a)) for a in ACTIONS]
        actual = [new_target(family,cue,first,a) for a in ACTIONS]
        chosen = max(range(3),key=lambda i:scores[i])
        regret = max(actual)-actual[chosen]
        total += regret
        exact += int(regret <= 1e-12)
    return {"total_regret":total,"optimal_context_count":exact}


def train_source():
    shared = SharedContextRingDev(mode="shared")
    private = SharedContextRingDev(mode="action_partition")
    for _ in range(SOURCE_EPOCHS):
        for case in CONTEXTS:
            r = source_target(*case,nonlinear=True)
            episode(shared,case,r,fit=True)
            episode(private,case,r,fit=True)
    assert shared.updates == private.updates == 36 * SOURCE_EPOCHS
    assert shared.transitions == private.transitions == 2 * 36 * SOURCE_EPOCHS
    assert shared.native_ids == private.native_ids
    saved = {"pretrained_shared":shared.checkpoint(),
             "pretrained_partition":private.checkpoint()}
    assert all(SharedContextRingDev.restore(x).checkpoint() == x
               for x in saved.values())
    return saved


def run_family(family, frozen_source, observed, withheld):
    clock_start = time.perf_counter()
    cpu_start = time.process_time()
    target = lambda *c:new_target(family,*c)
    models = {
        "pretrained_shared":SharedContextRingDev.restore(frozen_source["pretrained_shared"]),
        "scratch_shared":SharedContextRingDev(mode="shared"),
        "pretrained_partition":SharedContextRingDev.restore(frozen_source["pretrained_partition"]),
    }
    assert all(len(m.cell_weights)*HEAD_FEATURES+len(m.action_biases)==163
               for m in models.values())
    zero_shot = {}
    zero_shot_predictions = {}
    retention_before = {}
    snapshots = {}
    for name,m in models.items():
        assert m.native_ids == models["pretrained_shared"].native_ids
        if name != "scratch_shared":
            source_pred = evaluate(m,CONTEXTS,lambda *c:source_target(*c,nonlinear=True))
            retention_before[name] = sum(abs(
                p-source_target(*case,nonlinear=True))
                for p,case in zip(source_pred,CONTEXTS))
        z = evaluate(m,withheld,target)
        zero_shot_predictions[name] = z
        zero_shot[name] = sum(abs(p-target(*case))
                             for p,case in zip(z,withheld))
        snapshots[name]=m.parameters_sha256()
    for context in observed:
        reward = target(*context)
        for m in models.values():
            episode(m,context,reward,fit=True)
    assert all(models[n].parameters_sha256()!=snapshots[n] for n in models)
    assert (models["pretrained_shared"].updates ==
            models["pretrained_partition"].updates == 588)
    assert models["scratch_shared"].updates == 12
    for name,m in models.items():
        raw=m.checkpoint()
        assert SharedContextRingDev.restore(raw).checkpoint()==raw
        assert len(raw)<=8192

    weights = conventional_weights(observed,target)
    mean_reward = sum(target(*c) for c in observed)/12
    fixed_ridge = [ridge_predict(weights,c) for c in withheld]
    predictions = {n:evaluate(m,withheld,target)
                   for n,m in models.items()}
    errors = {
        n:sum(abs(p-target(*case))
              for p,case in zip(pred,withheld))
        for n,pred in predictions.items()
    }
    errors["conventional_12_label_ridge"]=sum(
        abs(p-target(*c)) for p,c in zip(fixed_ridge,withheld))
    errors["zero_constant"]=sum(abs(target(*c)) for c in withheld)
    errors["mean_of_12_observed"]=sum(
        abs(mean_reward-target(*c)) for c in withheld)
    retention_after={}
    for name,m in models.items():
        if name!="scratch_shared":
            preds=evaluate(
                m,CONTEXTS,lambda *c:source_target(*c,nonlinear=True))
            retention_after[name]=sum(
                abs(p-source_target(*case,nonlinear=True))
                for p,case in zip(preds,CONTEXTS))
    regret={n:policy_regret(m,family) for n,m in models.items()}
    regret["conventional_12_label_ridge"]=baseline_policy(weights,family)

    # Exact source reconstruction and single known edge lesion: no native
    # learner code or trained checkpoint changed, no re-fit after lesion.
    shared = models["pretrained_shared"]
    clone=SharedContextRingDev.restore(shared.checkpoint())
    clone.start_frozen_evaluation()
    lesion_losses={"intact":0.0,"one_edge_0_1_removed":0.0,"zero_output_hops":0.0}
    lesion_changes=0
    records=[]
    for i,case in enumerate(withheld):
        cue,first,second=case
        clone.start_observation(cue)
        clone.accept_first(first)
        original=clone.score(second)
        intact,lesion,zero=damaged_readout(clone,case)
        assert abs(intact-original)<=1e-9,("RING_SOURCE_EXACT_RECONSTRUCTION",case,intact,original)
        clone.accept_second(second,0.0,learning=False)
        if abs(intact-lesion)>1e-10:
            lesion_changes+=1
        truth=target(*case)
        lesion_losses["intact"]+=abs(intact-truth)
        lesion_losses["one_edge_0_1_removed"]+=abs(lesion-truth)
        lesion_losses["zero_output_hops"]+=abs(zero-truth)
        records.append({
            "family":family,"cue":cue,"actual_first":first,
            "selected_second":second,"target":round(truth,12),
            "zero_shot":{
                n:round(zero_shot_predictions[n][i],12)
                for n in models
            },
            "after_12_target_feedback":{n:round(predictions[n][i],12)
                                        for n in models},
            "ridge_target_only":round(fixed_ridge[i],12),
            "lesion_output_edge_0_1":round(lesion,12),
            "zero_output_hops":round(zero,12),
        })
    assert lesion_changes>0, "PREDECLARED_SINGLE_EDGE_LESION_CAUSALLY_INERT"
    assert abs(lesion_losses["intact"]-errors["pretrained_shared"])<1e-8
    assert clone.parameters_sha256()==shared.parameters_sha256()
    checkpoint_sizes={n:len(m.checkpoint()) for n,m in models.items()}
    message_counts={n:{
        "input":m.forward_input_messages,
        "output":m.forward_output_messages,
        "reverse":m.reverse_credit_messages}
        for n,m in models.items()}
    duration=time.perf_counter()-clock_start
    cpu=time.process_time()-cpu_start
    return {
        "family":family,
        "zero_shot_errors":zero_shot,
        "after_12_feedback_errors":errors,
        "source_retention_before":retention_before,
        "source_retention_after":retention_after,
        "action_selection_regret":{
            n:{"total_regret":v["total_regret"],
               "optimal_context_count":v["optimal_context_count"]}
            for n,v in regret.items()
        },
        "lesion":dict(lesion_losses,changed_heldout_predictions=lesion_changes,
                      original_directed_edges_per_output_hop=16,
                      surviving_directed_edges_per_output_hop=14),
        "checkpoint_bytes":checkpoint_sizes,
        "edge_scalar_messages":message_counts,
        "cases":records,
        "resource":{"wall_seconds":duration,"cpu_seconds":cpu},
    }


def main():
    verify()
    tracemalloc.start()
    begin_wall=time.perf_counter()
    begin_cpu=time.process_time()
    saved=train_source()
    source_bytes={k:len(v) for k,v in saved.items()}
    observed,withheld=target_split()
    family_results={}
    for family in FAMILIES:
        family_results[family]=run_family(family,saved,observed,withheld)
    # Both target families must satisfy an independently pre-registered
    # threshold. Do not select only the successful family.
    qualifies={}
    beats_ridge={}
    for name,r in family_results.items():
        e=r["after_12_feedback_errors"]
        s=e["pretrained_shared"]
        qualifies[name]=(
            s<=0.90*e["scratch_shared"] and
            s<=0.95*e["pretrained_partition"])
        beats_ridge[name]=s<e["conventional_12_label_ridge"]
    if not all(qualifies.values()):
        label="V23_UNFAMILIAR_SYNTHETIC_TRANSFER_NOT_ESTABLISHED__NO_SCIENCE"
    elif not all(beats_ridge.values()):
        label="V23_SYNTHETIC_TRANSFER_GAIN_STRONG_CONTROL_NOT_BEATEN__NO_SCIENCE"
    else:
        label="V23_SYNTHETIC_TRANSFER_BOUNDED_ENGINEERING_POSITIVE__NO_SCIENCE"
    cases=[r for family in FAMILIES
           for r in family_results[family]["cases"]]
    assert len(cases)==48 and len(observed)==12 and len(withheld)==24
    assert all(len(family_results[n]["cases"])==24 for n in FAMILIES)
    current,peak=tracemalloc.get_traced_memory()
    resource={
        "wall_seconds":time.perf_counter()-begin_wall,
        "cpu_seconds":time.process_time()-begin_cpu,
        "tracemalloc_peak_bytes":peak,
        "python_tracemalloc_current_bytes":current,
        "source_pretraining_checkpoint_bytes":source_bytes,
        "per_family_resource":{
            k:r["resource"] for k,r in family_results.items()
        },
        "environment":"CI runner Python3.12, not certified retail Windows GPU/energy",
    }
    result={
        "schema":"ygg.itd02.v23.unfamiliar_synthetic_reward_map_transfer.source_only.v1",
        "classification":label,"source_only":True,
        "scientific_first_use":False,"original_world_training":False,
        "original_native_genome_modified":False,
        "same_original_public_history_domain":True,
        "target_mappings_disjoint_from_pretraining":True,
        "independent_unfamiliar_world_transfer_proven":False,
        "original_ring_cells":CELLS,
        "learned_scalars_per_v22_arm":LEARNED_SCALARS,
        "source_pretraining_updates":36*SOURCE_EPOCHS,
        "target_public_feedback_labels_per_family":len(observed),
        "target_heldout_action_outcomes_per_family":len(withheld),
        "target_action_choice_contexts_per_family":12,
        "target_family_names":FAMILIES,
        "met_predeclared_two_family_transfer_threshold":qualifies,
        "beats_target_only_strong_ridge":beats_ridge,
        "target_family_metrics":{
            k:{field:value for field,value in res.items()
               if field not in ("cases","resource")}
            for k,res in family_results.items()
        },
        "source_only_48_case_sha256":hashlib.sha256(canonical(cases)).hexdigest(),
        "qualification":"SYNTHETIC_PUBLIC_MAPPING_ONLY_NOT_ORIGINAL_WORLD_SCIENCE",
        "host_specific_resource_probes":resource,
    }
    print(json.dumps(result,sort_keys=True,separators=(",",":")))


if __name__=="__main__":
    main()
