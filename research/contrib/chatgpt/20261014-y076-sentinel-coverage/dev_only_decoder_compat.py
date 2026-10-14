"""Y077 dev-only proof that fixed-budget public sensor addresses reach the causal decoder."""
import importlib.util
import json
from pathlib import Path
p=Path(__file__).resolve().parent/"execute.py"
spec=importlib.util.spec_from_file_location("y076_fixed",p)
assert spec and spec.loader
y076=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y076)
m=y076.m
SEED=9440
FAMILY=y076.FAMILIES[0]

def public_decoder_any_pinned_public_address(observed,episode):
    b0=observed[0]["0"]
    a=(observed[0]["1"]-b0)%16
    d=(observed[1]["0"]-b0)%16
    assert a%2==1 and observed[1]["1"]==(b0+d+a)%16
    inverse=pow(a,-1,16)
    history={}
    first=None
    for checked_episode in (5,7):
        if checked_episode>episode: break
        for key in sorted(observed[checked_episode],key=int):
            address=int(key)
            if address in (0,1):continue
            now=observed[checked_episode][key]
            inferred=(inverse*(now-(b0+checked_episode*d)))%16
            if inferred!=address:
                assert inferred not in (0,1,address)
                if history and history!={address:inferred,inferred:address}:
                    raise AssertionError("UNQUALIFIED_SECOND_INDEPENDENT_SWAP")
                history={address:inferred,inferred:address}
                if first is None:first=checked_episode
    return {"a":a,"b0":b0,"d":d,"inverse":inverse,
            "detected_pair":history,"first_detection_episode":first}

def candidate_new(seed,family,policy,corrected):
    saved_sampler=m.y64.dual_public_samples
    saved_decoder=m.y61.y60.public_decoder
    called={"sample":0,"decoder":0}
    def observed_sample(s,f):
        called["sample"]+=1
        return y076.new_public_samples(s,f)
    def public_decode(s,ep):
        called["decoder"]+=1
        return public_decoder_any_pinned_public_address(s,ep)
    try:
        m.y64.dual_public_samples=observed_sample
        m.y61.y60.public_decoder=public_decode
        arm="dual_sentinel_decoder_corrected" if corrected else "dual_sentinel_detect_only"
        result=m.candidate(seed,family,policy,arm)
    finally:
        m.y64.dual_public_samples=saved_sampler
        m.y61.y60.public_decoder=saved_decoder
    assert called["sample"]==1 and called["decoder"]>0
    return result,called

report=[]
for pair,onset in (((5,12),1),((5,12),4),((4,11),1)):
    integrity={"anchor_pair_checks":0}
    m.y58.install_transposition(onset,pair,integrity)
    try:
        old=m.candidate(SEED,FAMILY,"full","dual_sentinel_decoder_corrected")
        changed,calls=candidate_new(SEED,FAMILY,"full",True)
        oldfirst=next((r["public_detected_swap_first_episode"]
                       for r in reversed(old["rows"])
                       if r["public_detected_swap_first_episode"] is not None),None)
        newfirst=next((r["public_detected_swap_first_episode"]
                       for r in reversed(changed["rows"])
                       if r["public_detected_swap_first_episode"] is not None),None)
        assert changed["public_scalar_reads"]==old["public_scalar_reads"]==10
        assert newfirst is not None, "PUBLIC_DECODER_CANNOT_DETECT_TARGET_ON_DEVELOPMENT_DATA"
        report.append({"pair":pair,"onset":onset,"old_first":oldfirst,
                       "new_first":newfirst,"calls":calls})
    finally:
        m.y49.restore_environment()
print(json.dumps({"classification":"DEVELOPMENT_ONLY_MECHANICAL_PROOF",
                  "sealed_science_replayed":False,"report":report},sort_keys=True))
