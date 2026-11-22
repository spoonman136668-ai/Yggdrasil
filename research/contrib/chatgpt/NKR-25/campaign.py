"""Full compiled-image, wide-first bounded repair campaign.

No raw source archive, official valid/test, environment, model acceptance or
historical semantic correction. The deliberately damaged candidate is separate
from the immutable 21.3M-row baseline. Every frozen result is retained.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path,PurePosixPath
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT))
from yggdrasil.native_factual_weights import NativeFactualWeights,canonical,digest
from yggdrasil.native_bounded_fact_repair import BoundedFactRepair,BUNDLE,binding
from yggdrasil.native_knowledge_activation import (
    PINNED_ROWS,PINNED_BYTES,PINNED_RELATIONS,PINNED_MANIFEST_SHA,PINNED_PACKED_SHA,_check_pinned)

ZIP_PIN="c7265cabac91b8762fb5d65209eef44fa79a8fbf3d9a6f61300ef60ded0a5275"
FAULTS=32768
BUDGETS=(65536,32768,8192,2048)

def need(ok,reason):
    if not ok:
        raise ValueError("NKR25_CAMPAIGN_"+reason)

def file_sha(path):
    with open(path,"rb") as f:
        return hashlib.file_digest(f,"sha256").hexdigest()

def unpack_cache(path,destination):
    need(Path(path).stat().st_size==256126168 and file_sha(path)==ZIP_PIN,
         "COMPILED_IMAGE_ARCHIVE_SHA")
    out=Path(destination);out.mkdir(exist_ok=False)
    with zipfile.ZipFile(path) as archive:
        infos=archive.infolist()
        need(len(infos)<=16 and sum(i.file_size for i in infos)<=PINNED_BYTES+65536,
             "IMAGE_ARCHIVE_LIMIT")
        for name in ("facts.uint32le","manifest.json","receipt.json"):
            found=[i for i in infos if PurePosixPath(i.filename).name==name]
            need(len(found)==1 and not found[0].flag_bits&1,"IMAGE_MEMBER")
            with archive.open(found[0]) as src,open(out/name,"xb") as target:
                shutil.copyfileobj(src,target,1<<20)
    return out

def source_indices(rows):
    indices=[((i+1)*rows)//(FAULTS+1) for i in range(FAULTS)]
    need(len(set(indices))==FAULTS,"SOURCE_TOO_SMALL")
    protected=set(indices)
    retained=[((2*i+1)*rows)//(2*FAULTS) for i in range(FAULTS)]
    retained=[i for i in retained if i not in protected]
    need(len(set(retained))==len(retained),"RETAINED_INDEX_DUPLICATES")
    return indices,retained

def witnesses(candidate,indices,ident,budget):
    return canonical({
        "schema":BUNDLE,"base":binding(candidate.base),"source_id":ident,
        "parent_checkpoint_sha256":candidate.checkpoint_sha256,
        "operation_budget":budget,"source_kind":"frozen_historical_row_witness",
        "records":[[i,list(candidate.base.row_at(i)),candidate._faults[i]] for i in indices]})

def membership(candidate,targets,repaired):
    right_true=wrong_false=0
    expected=set(repaired)
    for index,true,false in targets:
        a=candidate.has_fact(*true);b=candidate.has_fact(*false)
        need(a==(index in expected) and b==(index not in expected),
             "INDEPENDENT_SET_REFERENCE_DRIFT")
        right_true+=a;wrong_false+=b
    return {"source_true_memberships_present":right_true,
            "injected_false_memberships_present":wrong_false,
            "source_true_memberships_missing":len(targets)-right_true,
            "decisions":2*len(targets),
            "incorrect_memberships":len(targets)-right_true+wrong_false}

def reference_objects(base,candidate,s,p,limit,after):
    missing={o for ss,pp,o in candidate._removed if (ss,pp)==(s,p) and o>after}
    wanted=limit+len(missing)
    source=[];cursor=after
    while len(source)<wanted:
        page=base.objects(s,p,limit=min(256,wanted-len(source)),after=cursor)
        if not page:
            break
        source+=page;cursor=page[-1]
    expected={o for o in source if (s,p,o) not in candidate._removed}
    expected.update(o for ss,pp,o in candidate._added if (ss,pp)==(s,p) and o>after)
    return sorted(expected)[:limit]

def check_pagination(base,candidate,targets):
    pairs=list(dict.fromkeys((t[1][0],t[1][1]) for t in targets[:64]))
    checks=0
    for s,p in pairs:
        first=candidate.objects(s,p,limit=16)
        need(first==reference_objects(base,candidate,s,p,16,0),"OBJECT_REFERENCE")
        after=first[-1] if first else 0
        need(candidate.objects(s,p,limit=16,after=after)==
             reference_objects(base,candidate,s,p,16,after),"OBJECT_PAGINATION")
        checks+=2
    return checks

def cold_process(base,checkpoint,queries):
    code='''import json,sys
from yggdrasil.native_factual_weights import NativeFactualWeights
from yggdrasil.native_bounded_fact_repair import BoundedFactRepair
p=json.load(sys.stdin)
with NativeFactualWeights(p["image"],p["manifest"],p["manifest_sha"]) as b:
 c=BoundedFactRepair(b,bytes.fromhex(p["checkpoint_hex"]),p["checkpoint_sha"])
 print(json.dumps({"rows":len(b),"checkpoint_sha":c.checkpoint_sha256,
                   "answers":[c.has_fact(*q) for q in p["queries"]]},sort_keys=True))
'''
    doc={"image":base.path,"manifest":str(Path(base.path).with_name("manifest.json")),
         "manifest_sha":digest(canonical(base.manifest)),
         "checkpoint_hex":checkpoint.checkpoint().hex(),
         "checkpoint_sha":checkpoint.checkpoint_sha256,"queries":queries}
    env=dict(os.environ,PYTHONPATH=str(ROOT),PYTHONDONTWRITEBYTECODE="1")
    r=subprocess.run([sys.executable,"-B","-c",code],input=canonical(doc),
                     capture_output=True,env=env,cwd=ROOT.parent,check=True,timeout=180)
    return json.loads(r.stdout)

def negative_controls(candidate,first):
    original=candidate.checkpoint()
    good=witnesses(candidate,[first],"negative-control",2)
    failures=0
    def denied(raw,pin,budget):
        nonlocal failures
        try:
            candidate.stage_repair(raw,pin,operation_budget=budget)
        except ValueError:
            failures+=1
        else:
            raise AssertionError("NKR25_NEGATIVE_ACCEPTED")
        need(candidate.checkpoint()==original,"NEGATIVE_MUTATED_FROZEN_CANDIDATE")
    denied(good,"0"*64,2)
    denied(good,digest(good),65538)
    for field,value in (("parent_checkpoint_sha256","0"*64),
                        ("source_kind","unverified_external_semantic_claim")):
        d=json.loads(good);d[field]=value;raw=canonical(d)
        denied(raw,digest(raw),2)
    d=json.loads(good);d["records"][0][1][2]^=1;raw=canonical(d)
    denied(raw,digest(raw),2)
    return failures

def run_image(base,output):
    _check_pinned(base)
    start=time.monotonic()
    indices,retained=source_indices(len(base))
    targets=[]
    for i in indices:
        true=base.row_at(i);false=(true[0],true[1],true[2]^0x80000000)
        need(base.has_fact(*true) and not base.has_fact(*false),"BASE_WITNESS")
        targets.append((i,true,false))
    bad=BoundedFactRepair.inject_fixture_faults(base,indices)
    frozen=bad.checkpoint();frozen_sha=bad.checkpoint_sha256
    failed=membership(bad,targets,[])
    failed.update({"experiment":"NKR-25","classification":"FROZEN_DELIBERATE_ENGINEERING_FAULT_CANDIDATE",
                   "not_a_discovered_world_error":True,
                   "base_rows":len(base),"base_relations":base.manifest["distinct_relation_types"],
                   "queried_distinct_subjects":len({t[1][0] for t in targets}),
                   "queried_distinct_predicates":len({t[1][1] for t in targets}),
                   "fault_pairs":len(indices),"checkpoint_sha256":frozen_sha,
                   "checkpoint_bytes":len(frozen),"scientific_pass":False})
    stages=[];max_repaired=None
    for budget in BUDGETS:  # widest permitted repair FIRST, then work backward
        chosen=indices[:budget//2]
        raw=witnesses(bad,chosen,f"wide-budget-{budget}",budget)
        t=time.monotonic()
        repaired,receipt=bad.stage_repair(raw,digest(raw),operation_budget=budget)
        repair_seconds=time.monotonic()-t
        need(bad.checkpoint()==frozen,"ORIGINAL_FAILURE_REWRITTEN")
        metrics=membership(repaired,targets,chosen)
        cold=BoundedFactRepair(base,repaired.checkpoint(),repaired.checkpoint_sha256)
        need(cold.checkpoint()==repaired.checkpoint(),"COLD_REPAIR_BYTES")
        retained_ok=sum(cold.has_fact(*base.row_at(i)) for i in retained)
        need(retained_ok==len(retained),"OLD_SOURCE_KNOWLEDGE_LOST")
        repeated,dup=cold.stage_repair(raw,digest(raw),operation_budget=budget)
        need(repeated.checkpoint()==cold.checkpoint() and dup["operations"]==0,
             "DUPLICATE_REPAIR_EFFECT")
        pages=check_pagination(base,cold,targets)
        stages.append({"budget":budget,"actual_operations":receipt["operations"],
                       "metrics":metrics,"retained_unchanged":retained_ok,
                       "retention_queries":len(retained),"pagination_checks":pages,
                       "repaired_checkpoint_sha256":cold.checkpoint_sha256,
                       "repaired_checkpoint_bytes":len(cold.checkpoint()),
                       "repair_seconds":repair_seconds})
        if budget==65536:
            need(metrics["incorrect_memberships"]==0,"MAX_REPAIR_NOT_COMPLETE")
            max_repaired=cold
    # Cumulative repair is a separate lineage; history hashes may differ
    # while all restored factual memberships must agree.
    half=len(indices)//2
    one=witnesses(bad,indices[:half],"sequential-first-half",32768)
    partial,r1=bad.stage_repair(one,digest(one),operation_budget=32768)
    two=witnesses(partial,indices[half:],"sequential-second-half",32768)
    final,r2=partial.stage_repair(two,digest(two),operation_budget=32768)
    cumulative=membership(final,targets,indices)
    need(cumulative["incorrect_memberships"]==0 and bad.checkpoint()==frozen,
         "SEQUENTIAL_REPAIR_OR_FROZEN_DRIFT")
    probes=[list(t[j]) for t in targets[::max(1,len(targets)//32)] for j in (1,2)]
    fresh=cold_process(base,max_repaired,probes)
    need(fresh["rows"]==len(base) and fresh["checkpoint_sha"]==max_repaired.checkpoint_sha256
         and fresh["answers"]==[j%2==0 for j in range(len(probes))],
         "FRESH_PROCESS_FULL_BASE_RESTORE")
    negatives=negative_controls(bad,indices[0])
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    (output/"frozen-fault-checkpoint.json").write_bytes(frozen)
    (output/"max-repaired-checkpoint.json").write_bytes(max_repaired.checkpoint())
    result={"schema":"yggdrasil.nkr25-27.full-image-repair.result.v1",
            "base_rows":len(base),"base_relations":base.manifest["distinct_relation_types"],
            "base_numeric_bytes":base.manifest["numeric_bytes"],
            "base_image_sha256":base.manifest["packed_sha256"],
            "original_source_archive_downloaded":False,
            "original_valid_test_opened":False,"new_original_source_actions":0,
            "native_accepted":False,"scientific_pass":False,
            "NKR25":failed,"NKR26":{"descending_stages":stages,
              "classification":"BOUNDED_HISTORICAL_MEMBERSHIP_RESTORATION_SUPPORTED",
              "strong_exact_reference_gain":0},
            "NKR27":{"classification":"COLD_AND_SEPARATE_FACT_RETENTION_SUPPORTED",
              "cold_process_complete_image_rows":fresh["rows"],
              "cold_process_probe_decisions":len(probes),
              "sequential":cumulative,"source_negative_controls_passed":negatives,
              "source_unchanged_after_sha256":file_sha(base.path),
              "frozen_original_checkpoint_sha256":frozen_sha},
            "wall_seconds":time.monotonic()-start}
    need(result["NKR27"]["source_unchanged_after_sha256"]==base.manifest["packed_sha256"],
         "FULL_SOURCE_WAS_MUTATED")
    return result

def stable(result):
    d=json.loads(json.dumps(result))
    for k in ("environment","source_candidate_sha","wall_seconds","setup_seconds"):
        d.pop(k,None)
    for s in d["NKR26"]["descending_stages"]:
        s.pop("repair_seconds",None)
    return d

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--compiled-image-zip",required=True)
    p.add_argument("--output-directory",required=True)
    p.add_argument("--verify-env",action="store_true")
    args=p.parse_args()
    begun=time.monotonic()
    out=Path(args.output_directory);out.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="nkr25-full-image-") as temp:
        image=unpack_cache(args.compiled_image_zip,Path(temp)/"source")
        with NativeFactualWeights(image/"facts.uint32le",image/"manifest.json",
                                  PINNED_MANIFEST_SHA) as base:
            setup=time.monotonic()-begun
            result=run_image(base,out)
    result["setup_seconds"]=setup
    result["source_candidate_sha"]=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    result["environment"]={"python":sys.version,"platform":__import__("platform").platform()}
    need(time.monotonic()-begun<=600,"AUDIT_TIME_BUDGET")
    result["stable_sha256"]=digest(canonical(stable(result)))
    if args.verify_env:
        need(stable(result)==stable(json.loads(os.environ["NKR25_EXPECTED_RESULT"])),
             "PLATFORM_REPRODUCTION_DRIFT")
    (out/"campaign-result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"],"a") as f:
            f.write("result="+json.dumps(result,separators=(",",":"),sort_keys=True)+"\n")
    print("NKR25_27_WIDE_BOUNDED_REPAIR="+json.dumps(result,sort_keys=True),flush=True)

if __name__=="__main__":
    main()
