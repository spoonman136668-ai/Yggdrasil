"""Archive-only independent Y073 trial aggregation; no sealed experiment replay."""
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
p=Path("evidence/Y073-original.json")
raw=p.read_bytes()
z=json.loads(raw)
assert z["schema"]=="yggdrasil.y073-fresh-cross-gap-topology.v1"
assert z["parent_head"]=="6a2bafd89b4500ac700d04415f41e2552f87014c"
assert z["sealed_heldout_seeds"]==list(range(9104,9120))
assert z["pairs"]==[[4,11],[5,12]]
assert z["model_calls"]==0 and z["accepted_ref_mutation"] is False
inner=z["original_y070_unchanged_trial_evidence"]
assert inner["steady_zero_mismatches"] is True
records=inner["complete_heldout_records"]
assert len(records)==768
arms=("original_rotating_detect_only","dual_sentinel_detect_only","dual_sentinel_decoder_corrected")
agg=defaultdict(lambda:defaultdict(lambda:{"mismatch_episodes":0,"post_detection_mismatch_episodes":0,"illegal_physical_assignments":0}))
identities=set()
for trial in records:
    pair=tuple(trial["pair"])
    assert pair in ((4,11),(5,12))
    regime=trial["regime"]
    assert regime in ("steady","onset1")
    assert trial["seed"] in range(9104,9120)
    key=(pair,regime,tuple(trial["family"]),trial["seed"],trial["policy"])
    assert key not in identities
    identities.add(key)
    assert set(trial["arms"])==set(arms)
    for arm in arms:
        v=trial["arms"][arm]
        assert v["illegal_physical_assignments"]==0
        assert v["mismatch_episodes"]>=v["post_detection_mismatch_episodes"]>=0
        for field in ("mismatch_episodes","post_detection_mismatch_episodes","illegal_physical_assignments"):
            agg[(pair,regime)][arm][field]+=v[field]
assert len(identities)==768
comparisons=[]
for pair in ((4,11),(5,12)):
    for regime in ("steady","onset1"):
        group=inner["groups"][f"{pair[0]}_{pair[1]}:{regime}"]
        for arm in arms:
            for field,v in agg[(pair,regime)][arm].items():
                assert group["totals"][arm][field]==v
            if regime=="steady":
                assert agg[(pair,regime)][arm]["mismatch_episodes"]==0
    group=agg[(pair,"onset1")]
    baseline=group["dual_sentinel_detect_only"]["post_detection_mismatch_episodes"]
    corrected=group["dual_sentinel_decoder_corrected"]["post_detection_mismatch_episodes"]
    original_total=group["original_rotating_detect_only"]["mismatch_episodes"]
    corrected_total=group["dual_sentinel_decoder_corrected"]["mismatch_episodes"]
    comparisons.append({"case":f"{pair[0]}_{pair[1]}:onset1",
        "uncorrected_post":baseline,"corrected_post":corrected,
        "original_total":original_total,"corrected_total":corrected_total,
        "post_gain":None if baseline==0 else 1-corrected/baseline,
        "strict":baseline>0 and corrected<=.5*baseline and corrected_total<original_total,
        "partial":baseline>0 and corrected<=.8*baseline})
assert len(comparisons)==2
for recorded,derived in zip(z["comparisons"],comparisons):
    for field,v in derived.items():
        if isinstance(v,float):
            assert math.isclose(v,recorded[field],abs_tol=1e-12)
        else:
            assert v==recorded[field]
if all(x["strict"] for x in comparisons):
    label="TOPOLOGY_TRANSFER"
elif any(x["partial"] for x in comparisons):
    label="PARTIAL_TOPOLOGY_TRANSFER"
elif all(x["uncorrected_post"]==0 for x in comparisons):
    label="NO_POSTDETECTION_OPPORTUNITY"
else:
    label="NO_GAIN"
assert label==z["classification"]
witness={"schema":"research.archived-evidence-witness.v1",
         "experiment":"Y073","classification":label,"source_run":38530057504,
         "source_artifact_id":11877910560,"original_json_sha256":hashlib.sha256(raw).hexdigest(),
         "independent_recomputed_trials":len(records),"comparisons":comparisons,
         "sealed_execution_replayed":False,
         "scope":"Read-only archive-only independent recalculation; not external FSA authority"}
Path("Y073-witness.json").write_text(json.dumps(witness,sort_keys=True,indent=2)+"\n")
print("WITNESS_PASS",json.dumps(witness,sort_keys=True))
