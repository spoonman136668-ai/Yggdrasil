"""V28 source-only shadow selector: fixed context-diversity counterfactual.

A shadow readout over actual public V27 error traces is legitimate here because
both protected and fast V22 banks receive the identical selected observations
regardless of active readout. It is NOT a deployed V28 memory module.
"""
import hashlib,json,subprocess
from pathlib import Path
from research.itd02_v23_unfamiliar_mapping_audit import train_source
from research.itd02_v26_calibrated_return_audit import STREAMS
from research.itd02_v27_return_evidence_falsification import replay
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import canonical

PARENT="24f2f3919c8bb378831f48f8c7bd0a6e2423e45f"
PREREG="adc8ee5ce606740edceda943f86a8a0a9ef5b25b"

def select(public_events):
    fast=False;recent=[];records=[]
    for event in public_events:
        # Existing V26 actual pre-update learner errors. All action
        # opportunities and learner updates are identical in this shadow.
        advantage=event["advantage"]
        context=tuple(event["public"])
        recent=(recent+[(advantage,context)])[-4:]
        previous=fast
        if len(recent)>=3:
            for_fast=[(d,c) for d,c in recent if d<=-0.05]
            for_source=[(d,c) for d,c in recent if d>=0.05]
            if fast and (len(for_source)>=3 and
                all(d>=.15 for d,_ in recent[-2:]) and
                len({c for _,c in for_source})>=2):
                fast=False
            elif not fast and (len(for_fast)>=3 and
                all(d<=-.15 for d,_ in recent[-2:]) and
                len({c for _,c in for_fast})>=2):
                fast=True
        records.append({
            "public":event["public"],"advantage":advantage,
            "shadow_fast_before":previous,"shadow_fast_after":fast,
            "supporting_source_contexts":len({c for d,c in recent if d>=.05}),
            "supporting_fast_contexts":len({c for d,c in recent if d<=-.05}),
        })
    return records

def classify(rows):
    b1,b2=rows[0],rows[1]
    latency=[]
    for r in (b1,b2):
        return_window=r["records"][-12:]
        latency.append(next((i+1 for i,e in enumerate(return_window)
                             if not e["shadow_fast_after"]),None))
    false=[
        sum(not e["shadow_fast_after"] for e in r["records"][-8:])
        for r in rows[-2:]
    ]
    no_go=(any(i is None or i>4 for i in latency) or any(false))
    return latency,false,(
        "V28_CONTEXT_DIVERSE_REACTIVATION_NO_GO__NO_SCIENCE"
        if no_go else
        "V28_CONTEXT_DIVERSE_REACTIVATION_STRONG_CONTROL_NO_GO__NO_SCIENCE")

def main():
    root=Path(__file__).resolve().parents[1]
    git=lambda *args:subprocess.check_output(("git",)+args,cwd=root,text=True).strip()
    for pin in (PARENT,PREREG):
        assert git("merge-base","--is-ancestor",pin,"HEAD")==""
    source=train_source()["pretrained_shared"]
    rows=[]
    for name,segments,offset in STREAMS:
        baseline=replay(name,segments,offset,source)
        shadow=select(baseline)
        assert shadow==select(replay(name,segments,offset,source,offline_labels_reversed=True))
        assert all(tuple(b["public"])==tuple(s["public"]) for b,s in zip(baseline,shadow))
        rows.append({"name":name,"records":shadow,"original":baseline})
    # This is an exact, preregistered falsification of an abstract selector,
    # not extra scientific evidence from a hidden source label.
    repeated=[{"advantage":2.0,"public":["LRV","Backup","GoForward"]}]*4
    assert not select(repeated)[-1]["shadow_fast_after"]
    # Repeated contexts also cannot invoke a SOURCE reactivation from FAST.
    artificial=select(repeated)
    assert artificial[-1]["supporting_source_contexts"]==1
    latency,false,label=classify(rows)
    compressed=[{"name":r["name"],"records":r["records"]} for r in rows]
    digest=hashlib.sha256(canonical(compressed)).hexdigest()
    altered=json.loads(canonical(compressed));altered[0]["records"][0]["advantage"]+=.01
    assert hashlib.sha256(canonical(altered)).hexdigest()!=digest
    print(json.dumps({
        "schema":"ygg.itd02.v28.context_diverse_shadow_source_only.v1",
        "classification":label,"scientific_first_use":False,
        "source_only":True,"original_world_training":False,
        "candidate_is_shadow_counterfactual_not_deployed_module":True,
        "unmodified_original_native_and_v26_banks":True,
        "source_576_observations":True,"streams":7,
        "basic_return_latencies":latency,
        "unchanged_target_false_source":[int(x) for x in false],
        "distinct_context_negative_control":True,
        "offline_stage_label_invariant":True,
        "tamper_digest_changes":True,
        "canonical_shadow_sha256":digest,
        "summary":[{"stream":r["name"],"final_fast":r["records"][-1]["shadow_fast_after"]}
                   for r in rows]},sort_keys=True,separators=(",",":")))
if __name__=="__main__":main()
