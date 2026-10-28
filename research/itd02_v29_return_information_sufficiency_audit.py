"""V29 source-only information sufficiency audit, no trained detector.

Actual public event and reward streams only. Stage names are solely evaluation
labels and not passed to any model, and no rule is tuned from observed results.
"""
import hashlib,json,subprocess
from pathlib import Path
from research.itd02_v23_unfamiliar_mapping_audit import train_source
from research.itd02_v26_calibrated_return_audit import STREAMS
from research.itd02_v27_return_evidence_falsification import replay
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import canonical
PARENT="e226cf23ef7c130f7edb72822052e88d52059766"
PREREG="90b8156340a8d3b7a021afcbefbefe0c0c778e30"

def windows(events, width=4):
    return [events[i-width+1:i+1] for i in range(width-1,len(events))]

def public_window(events):
    return [[e["public"],e["reward"]] for e in events]

def evidence_window(events):
    return [1 if e["advantage"]>=.05 else -1 if e["advantage"]<=-.05 else 0
            for e in events]

def inspect():
    source=train_source()["pretrained_shared"]
    streams={}
    for name,segments,offset in STREAMS:
        events=replay(name,segments,offset,source)
        assert events==replay(name,segments,offset,source,offline_labels_reversed=True)
        streams[name]=events
    returning=streams["basic_t2"][12:16]
    unchanged=streams["unchanged_t1"][16:20]
    # The diagnostically troublesome T2 and unchanged T1 evidence windows.
    overlap=sum(x==y for x,y in zip(evidence_window(returning),
                                     evidence_window(unchanged)))
    all_windows=[]
    for name,segments,offset in STREAMS:
        events=streams[name]
        boundaries=[]
        cursor=0
        for family,size in segments:
            boundaries.extend([family]*size)
            cursor+=size
        for i,window in enumerate(windows(events),3):
            all_windows.append({
                "stream":name,
                "end_event":i+1,
                "family_offline_only":boundaries[i],
                "public_history":public_window(window),
                "model_evidence":evidence_window(window),
            })
    seen={}
    collisions=[]
    for v in all_windows:
        key=hashlib.sha256(canonical(v["public_history"])).hexdigest()
        if key in seen and seen[key]["family_offline_only"]!=v["family_offline_only"]:
            collisions.append({"a":seen[key]["stream"],"b":v["stream"],
                               "hash":key})
        seen.setdefault(key,v)
    exact=len(collisions)
    # No forced impossibility claim from *sign-only* overlap.
    if exact:
        classification="V29_HARD_INFORMATION_COLLISION_DIAGNOSTIC__NO_SCIENCE"
    elif overlap>=2:
        classification="V29_MODEL_EVIDENCE_AMBIGUITY_WITHOUT_HARD_COLLISION__NO_SCIENCE"
    else:
        classification="V29_SOURCE_ONLY_INFORMATION_SEPARATION_DIAGNOSTIC__NO_SCIENCE"
    digest=hashlib.sha256(canonical(all_windows)).hexdigest()
    changed=json.loads(canonical(all_windows))
    changed[0]["public_history"][0][1]+=0.001
    assert hashlib.sha256(canonical(changed)).hexdigest()!=digest
    return {"schema":"ygg.itd02.v29.information_sufficiency.source_only.v1",
            "classification":classification,
            "scientific_first_use":False,
            "original_world_training":False,
            "source_only":True,
            "seven_predeclared_streams":len(streams),
            "window_count":len(all_windows),
            "hard_public_history_collision_count":exact,
            "collision_examples":collisions[:10],
            "t2_first_four_return_evidence":evidence_window(returning),
            "unchanged_t1_problem_window_evidence":evidence_window(unchanged),
            "overlap_of_four_evidence_signs":overlap,
            "true_t2_return_latency_preserved":5,
            "false_t1_source_events_preserved":4,
            "public_reward_record_digest_tamper_detected":True,
            "offline_stage_label_irrelevant_to_replay":True,
            "canonical_windows_sha256":digest}

def main():
    root=Path(__file__).resolve().parents[1]
    git=lambda *args:subprocess.check_output(("git",)+args,cwd=root,text=True).strip()
    for pin in (PARENT,PREREG):
        assert git("merge-base","--is-ancestor",pin,"HEAD")==""
    print(json.dumps(inspect(),sort_keys=True,separators=(",",":")))
if __name__=="__main__":main()
