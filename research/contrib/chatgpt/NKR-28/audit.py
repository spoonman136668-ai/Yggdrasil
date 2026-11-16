"""Engineering application of frozen repaired full-image factual memory."""
from __future__ import annotations
import argparse
import importlib.util
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT))
spec=importlib.util.spec_from_file_location("nkr25_composition_cache",HERE.parent/"NKR-25/campaign.py")
cache=importlib.util.module_from_spec(spec);spec.loader.exec_module(cache)
from yggdrasil.native_factual_weights import NativeFactualWeights,canonical,digest
from yggdrasil.native_bounded_fact_repair import BoundedFactRepair
from yggdrasil.native_knowledge_activation import NativeKnowledgeSession,PINNED_MANIFEST_SHA,_check_pinned

FAULT_PIN="c4e6a3c81733e117e9d5c163e28e0e117b2082b21317bb56431f71e8ca792594"
REPAIR_PIN="779a41789f9ac28f900a082950244e25630fdbaee55fc7c8ec570af9faf1977c"

def need(ok,reason):
    if not ok: raise ValueError("NKR28_"+reason)

def project(base,removed,added,s,p,limit):
    # Independent raw-row projection: no candidate objects()/two-hop call.
    at=base._lower(s,p,1)
    values=set()
    while at<len(base) and len(values)<limit:
        triple=base.row_at(at);at+=1
        if triple[:2]!=(s,p): break
        if triple not in removed: values.add(triple[2])
    values.update(added.get((s,p),()))
    return sorted(values)[:limit]

def reference(base,removed,added,s,p,q):
    out=[];seen=set()
    for mid in project(base,removed,added,s,p,16):
        for obj in project(base,removed,added,mid,q,64):
            if obj not in seen:
                seen.add(obj);out.append(obj)
                if len(out)==64: return out
    return out

def contexts(base,bad):
    eligible=[];seen=set();prefixes={}
    for index in bad._faults:
        s,p,mid=base.row_at(index)
        if (s,p) not in prefixes:
            prefixes[s,p]=project(base,set(),{},s,p,16)
        if mid not in prefixes[s,p]: continue
        at=base._lower(mid,1,1)
        if at>=len(base): continue
        source=base.row_at(at)
        if source[0]!=mid: continue
        q=source[1];key=(s,p,q)
        if key not in seen: seen.add(key);eligible.append(key)
    need(eligible,"NO_ELIGIBLE_CONTEXTS")
    count=min(512,len(eligible))
    selected=(eligible if len(eligible)<=512 else
              [eligible[(i*(len(eligible)-1))//511] for i in range(512)])
    need(len(set(selected))==count,"QUERY_DUPLICATE")
    return eligible,selected

def run(base):
    start=time.monotonic()
    _check_pinned(base)
    bad_raw=(HERE.parent/"NKR-25/frozen-fault-checkpoint.json").read_bytes()
    good_raw=(HERE.parent/"NKR-26/max-repaired-checkpoint.json").read_bytes()
    bad=BoundedFactRepair(base,bad_raw,FAULT_PIN)
    good=BoundedFactRepair(base,good_raw,REPAIR_PIN)
    eligible,queries=contexts(base,bad)
    need(len(queries)>0,"EMPTY_QUERY_SET")
    results={};outputs={}
    for name,layer in (("base",base),("faulted",bad),("repaired",good)):
        t=time.monotonic()
        removed=set() if name=="base" else set(layer._removed)
        added=set() if name=="base" else set(layer._added)
        # Build independent indexes once; raw-row reference remains independent.
        by_added={}
        for s,p,o in added: by_added.setdefault((s,p),set()).add(o)
        answers=[]
        session=NativeKnowledgeSession(layer,{})
        for s,p,q in queries:
            actual=session.hypothesize(s,p,q,max_intermediates=16,max_candidates=64)
            expected=reference(base,removed,by_added,s,p,q)
            need(actual["objects"]==expected,"INDEPENDENT_JOIN_DRIFT")
            need(actual["classification"]=="UNVERIFIED_PATH_HYPOTHESES"
                 and actual["verified_new_knowledge"] is False
                 and actual["native_accepted"] is False
                 and actual["can_write_causal_consequence"] is False,
                 "UNSUPPORTED_KNOWLEDGE_CLAIM")
            answers.append(actual["objects"])
        outputs[name]=answers
        results[name]={"queries":len(queries),"reference_matches":len(queries),
                       "nonempty_outputs":sum(bool(a) for a in answers),
                       "returned_hypotheses":sum(map(len,answers)),
                       "output_sha256":digest(canonical(answers)),
                       "seconds":time.monotonic()-t}
    differences=sum(a!=b for a,b in zip(outputs["base"],outputs["faulted"]))
    repaired_diff=sum(a!=b for a,b in zip(outputs["base"],outputs["repaired"]))
    need(repaired_diff==0,"REPAIRED_KNOWLEDGE_APPLICATION_DRIFT")
    need(differences>0,"FAULT_COVERAGE_INSUFFICIENT_DO_NOT_RETUNE")
    need(bad.checkpoint()==bad_raw and good.checkpoint()==good_raw,"FROZEN_CANDIDATE_MUTATION")
    image_sha=cache.file_sha(base.path)
    need(image_sha==base.manifest["packed_sha256"],"SOURCE_MUTATION")
    result={"schema":"yggdrasil.nkr28.full-image-repaired-composition.result.v1",
            "classification":"ENGINEERING_STORED_KNOWLEDGE_COMPOSITION_RESTORED",
            "scientific_pass":False,"native_accepted":False,
            "new_operator_learned":False,"new_factual_knowledge_learned":False,
            "full_base_rows":len(base),"base_relations":base.manifest["distinct_relation_types"],
            "full_base_image_sha256":image_sha,"fault_checkpoint_sha256":FAULT_PIN,
            "repaired_checkpoint_sha256":REPAIR_PIN,
            "eligible_contexts":len(eligible),"query_count":len(queries),
            "query_sha256":digest(canonical(queries)),"max_intermediates":16,"max_candidates":64,
            "arms":results,"faulted_different_from_base_queries":differences,
            "repaired_different_from_base_queries":repaired_diff,
            "strong_symbolic_control_gain":0,"new_original_source_actions":0,
            "source_unchanged":True,"original_failure_unchanged":True,
            "wall_seconds":time.monotonic()-start}
    return result

def stable(result):
    d=json.loads(json.dumps(result))
    for key in ("wall_seconds","setup_seconds","environment","source_candidate_sha"):
        d.pop(key,None)
    for arm in d["arms"].values(): arm.pop("seconds",None)
    return d

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--compiled-image-zip",required=True)
    p.add_argument("--output",required=True)
    p.add_argument("--verify-env",action="store_true")
    args=p.parse_args();start=time.monotonic()
    with tempfile.TemporaryDirectory(prefix="nkr28-full-image-") as temp:
        image=cache.unpack_cache(args.compiled_image_zip,Path(temp)/"source")
        with NativeFactualWeights(image/"facts.uint32le",image/"manifest.json",PINNED_MANIFEST_SHA) as base:
            setup=time.monotonic()-start
            result=run(base)
    result["setup_seconds"]=setup
    result["environment"]={"python":sys.version,"platform":platform.platform()}
    result["source_candidate_sha"]=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    need(time.monotonic()-start<=120,"WHOLE_AUDIT_TIME_BUDGET")
    result["stable_sha256"]=digest(canonical(stable(result)))
    if args.verify_env:
        need(stable(result)==stable(json.loads(os.environ["NKR28_EXPECTED_RESULT"])),"WINDOWS_DRIFT")
    Path(args.output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"],"a") as f:
            f.write("result="+json.dumps(result,separators=(",",":"),sort_keys=True)+"\n")
    print("NKR28_WIDE_COMPOSITION="+json.dumps(result,sort_keys=True),flush=True)

if __name__=="__main__": main()
