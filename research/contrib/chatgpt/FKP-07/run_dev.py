"""Frozen FKP-07 public DEV experiment, no protected-first-use or native merge.

This source-only test actually executes source.observe(action) for all 64 paid
interventions per context, seals predictions at all preregistered prefixes,
and evaluates original/revision held states only AFTER predictions and law
selection are complete. The 64-query exact family reference is conventional,
not evidence of inventing an outside-family causal mechanism.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import random
import statistics
import sys
import time
import tracemalloc

sys.path.insert(0, str(Path(__file__).resolve().parent))
from source import SourceOwnerWorld, ORIGINAL, REVISIONS, public
from repair import SharedWeights, ReplayControl, NaiveOverwrite, PAIRS, RAW_LEARNED_BYTES, CHECKPOINT_BYTES

PREFIXES=(4,8,12,16,32,64)
LAW_COUNT=107880
SOURCE_LABELS_NEVER_USED_FOR_FIT=True


def chosen_action(alive: int, masks: list[int], picked: set[int]):
    """Frozen FKP-06 exact entropy/balance greedy, no hidden source inputs."""
    n=alive.bit_count()
    if n<=0:raise AssertionError("FKP07_EMPTY_LAW_POSTERIOR")
    best=-1;winner=-1
    for idx,mask in enumerate(masks):
        if idx in picked:continue
        n1=(alive&mask).bit_count()
        score=min(n1,n-n1)
        if score>best:best=score;winner=idx
    if winner<0:raise AssertionError("FKP07_ACTION_POOL_EXHAUSTED")
    return winner


def independent_exact_replay(observations: tuple[tuple[int,int], ...], laws: list[tuple[int,...]]) -> list[int]:
    """Independent conventional exact solver using only witnessed feedback."""
    return [i for i,law in enumerate(laws)
            if all(public.consequence(law,x)==y for x,y in observations)]


def run() -> dict:
    wall=time.perf_counter()
    cpu=time.process_time()
    tracemalloc.start()
    hypotheses=public.laws()
    assert len(hypotheses)==LAW_COUNT
    action_pool, held=public.inputs()
    pool_masks=[public.response_mask(a,hypotheses) for a in action_pool]
    held_masks=[public.response_mask(a,hypotheses) for a in held]
    assert len(set(action_pool+held))==384
    hypothesis_cost=time.perf_counter()-wall

    direct=SharedWeights()
    replay=ReplayControl()
    naive=NaiveOverwrite()
    prediction_receipt=hashlib.sha256()
    scores={k:[] for k in PREFIXES}
    evidence_rows=[]
    direct_edit_s=0.0
    replay_edit_s=0.0
    conventional_inference_s=0.0
    old_held_by_slot={}
    old_programs={}
    updated_slots=set()
    witnessed_count=0
    repair_identified=0
    source_visible_actions=0
    all_witnesses=[]

    for seed in (*ORIGINAL,*REVISIONS):
        source=SourceOwnerWorld(seed,tuple(hypotheses))
        view=source.public_view()
        assert tuple(action_pool)==view.action_pool and tuple(held)==view.held_inputs
        alive=(1<<LAW_COUNT)-1
        indices=[]
        source_transcript=[]
        prefix_predictions={}
        prefix_counts={}
        for step in range(64):
            j=chosen_action(alive,pool_masks,set(indices))
            indices.append(j)
            action=action_pool[j]
            effect=source.observe(action)  # only admissible observed consequence
            source_transcript.append((action,effect))
            witnessed_count+=1
            alive &= pool_masks[j] if effect else ~pool_masks[j]
            if alive==0:raise AssertionError("FKP07_TRUE_LAW_ELIMINATED")
            if (step+1) in PREFIXES:
                prefix_predictions[step+1]=tuple(public.posterior_predictions(alive,held_masks))
                prefix_counts[step+1]=alive.bit_count()
        assert source.used_actions==64
        source_visible_actions+=source.used_actions
        # Seal every prediction before any DEV held consequence is requested.
        for prefix in PREFIXES:
            prediction_receipt.update(bytes(prefix_predictions[prefix]))
        if alive.bit_count()==1:
            program=hypotheses[alive.bit_length()-1]
        else:
            program=None  # explicit abstention, no optimistic extrapolation
        independent_start=time.perf_counter()
        control_options=independent_exact_replay(tuple(source_transcript),hypotheses)
        conventional_inference_s += time.perf_counter()-independent_start
        assert len(control_options)==alive.bit_count()
        if program is not None:
            assert control_options==[alive.bit_length()-1]
        # Score now, after source/strong-conventional predictions have frozen.
        labels=source.dev_held_labels(tuple(held))
        family_accuracies={prefix:sum(p==v for p,v in zip(prefix_predictions[prefix],labels))/len(held)
                           for prefix in PREFIXES}
        for k,v in family_accuracies.items():scores[k].append(v)

        slot=view.context_id-800
        assert 0<=slot<24
        if seed in REVISIONS:
            updated_slots.add(slot)
            # Evaluation-only label difference, never used in direct learning.
            prior=old_programs[slot]
            changed=sum(public.consequence(prior,x)!=y for x,y in zip(held,labels))
        else:
            changed=None
        if program is not None:
            start=time.perf_counter();direct.update(slot,program)
            direct_edit_s+=time.perf_counter()-start
            start=time.perf_counter();replay.update(slot,program)
            replay_edit_s+=time.perf_counter()-start
            naive.update(slot,program)
            assert tuple(direct.counters)==tuple(replay.counters)
            assert direct.program(slot)==replay.records[slot]
            assert all(direct.predict(slot,x)==public.consequence(program,x)
                       for x in held)
            if seed in ORIGINAL:
                old_held_by_slot[slot]=tuple(direct.predict(slot,x) for x in held)
                old_programs[slot]=program
            else:
                repair_identified+=1
        # A learned program is NOT the source-private coefficient map.
        evidence_rows.append({
            "seed":seed,"context_slot":slot,"revision":seed in REVISIONS,
            "paid_actions":source.used_actions,"posterior_sizes_by_prefix":prefix_counts,
            "held_accuracy_by_prefix":family_accuracies,
            "unique_law_after_64":program is not None,
            "held_revision_changed_actions":changed,
            "sealed_prediction_sha256":hashlib.sha256(b''.join(bytes(prefix_predictions[k]) for k in PREFIXES)).hexdigest(),
            "all_action_indices_sha256":hashlib.sha256(bytes(indices)).hexdigest(),
        })
        all_witnesses.append(tuple(source_transcript))

    # Unchanged still-live contexts must survive 8 contradictory SOURCE revisions.
    retained=sum(all(tuple(direct.predict(slot,x) for x in held)==old_held_by_slot[slot]
                     for slot in range(8,24)))
    if len(updated_slots)!=8:raise AssertionError("FKP07_REVISION_COHORT_MISMATCH")
    assert direct.occupied.bit_count()<=24
    # The same *shared* learned weights are repaired, never allocated 8 new slots.
    assert sum(direct.counters)==2*direct.occupied.bit_count()
    snap=direct.snapshot()
    restored=SharedWeights.restore(snap)
    assert restored.snapshot()==snap
    assert tuple(restored.counters)==tuple(replay.counters)
    assert all(restored.predict(slot,x)==direct.predict(slot,x)
               for slot in range(24) for x in held)
    tamper=bytearray(snap);tamper[15]^=1
    try:SharedWeights.restore(bytes(tamper))
    except ValueError:pass
    else:raise AssertionError("FKP07_TAMPER_ACCEPTED")

    # Destructive unscoped update negative for still-live earlier laws.
    baseline_last=sum(naive.predict(slot,x)==direct.predict(slot,x)
                      for slot in range(8,24) for x in held)/(16*len(held))
    means={str(k):statistics.mean(scores[k]) for k in PREFIXES}
    revision_64=statistics.mean(row['held_accuracy_by_prefix'][64] for row in evidence_rows if row['revision'])
    source_good=(sum(row['unique_law_after_64'] for row in evidence_rows)>=29 and
                 means['64']>=0.98 and repair_identified==8)
    repair_good=(source_good and retained==16 and tuple(direct.counters)==tuple(replay.counters)
                 and len(snap)==CHECKPOINT_BYTES and baseline_last<1)
    _,peak=tracemalloc.get_traced_memory()
    tracemalloc.stop()
    total=time.perf_counter()-wall
    return {
      'schema':'fkp07.public-dev-direct-shared-repair.v1',
      'classification':'DEV_REPAIR_FEASIBLE_ONLY' if repair_good else 'DEV_NO_GO',
      'protected_first_use':False,'native_accepted_model_changed':False,
      'source_parent':'FKP-06 PR #1097 at 845cc614915fa26f3377136b4635bae2a16276f5',
      'original_worlds':24,'revision_worlds':8,'genuine_observed_consequences':witnessed_count,
      'paid_actions_per_world':64,'unseen_held_actions_per_world':256,
      'exact_law_identified_64':sum(row['unique_law_after_64'] for row in evidence_rows),
      'per_prefix_mean_held_accuracy':means,'mean_revised_world_accuracy_64':revision_64,
      'shared_weight_bytes_fixed':RAW_LEARNED_BYTES,
      'checkpoint_bytes_fixed':len(snap),'checkpoint_sha256':hashlib.sha256(snap).hexdigest(),
      'unaffected_contexts_retained':retained,'unaffected_contexts_total':16,
      'revisions_repaired':repair_identified,'occupied_context_slots_after_revisions':direct.occupied.bit_count(),
      'independent_replay_weight_parity':tuple(direct.counters)==tuple(replay.counters),
      'unscoped_naive_accuracy_on_16_untouched_contexts':baseline_last,
      'source_hypothesis_precompute_seconds':hypothesis_cost,
      'direct_edit_total_seconds':direct_edit_s,'independent_replay_edit_total_seconds':replay_edit_s,
      'strong_conventional_inference_seconds':conventional_inference_s,
      'full_process_wall_seconds':total,'full_process_cpu_seconds':time.process_time()-cpu,
      'peak_tracemalloc_bytes':peak,'sealed_predictions_sha256':prediction_receipt.hexdigest(),
      'scientific_status':'UNVERIFIED_EQUAL_INFO_REFERENCE_TIES_NO_PROTECTED_SOURCE',
      'outside_family_invention':False,
      'source_headroom_pass':source_good,'repair_dev_gate_pass':repair_good,
      'world_receipts':evidence_rows,
    }


if __name__=='__main__':
    print(json.dumps(run(),sort_keys=True,indent=2))
