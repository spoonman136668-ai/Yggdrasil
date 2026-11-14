#!/usr/bin/env python3
"""QTR-01 F09: fixed fitted-artifact license and checkpoint metadata only."""
import argparse
import hashlib
import json
import re
import sys
import urllib.request

REPO="neuronpedia/icalens-qwen3.6-27b"
REV="3e83450ee5d6cb172ae11f2da06500be326c16ad"
MODEL="Qwen/Qwen3.6-27B"
HASH="656f4a1e1a2243264ef270654ba1162cd392c301b363b57aeb885c46f5f52b5f"
ROOT="https://huggingface.co/api/models/"+REPO+"/tree/"+REV
README="https://huggingface.co/"+REPO+"/resolve/"+REV+"/README.md"
BOUND=131072
SHA40=re.compile(r"\b[0-9a-f]{40}\b",re.I)
LICENSE=re.compile(r"^license\s*:\s*([A-Za-z0-9.-]+)\s*$",re.I)

class Blocked(ValueError):
    pass

def get(url):
    if url not in (ROOT, README):
        raise Blocked("UNFROZEN_URL")
    req=urllib.request.Request(url,headers={"User-Agent":"qtr01-f09-provenance/1.0"})
    with urllib.request.urlopen(req,timeout=20) as resp:
        body=resp.read(BOUND+1)
    if not 0<len(body)<=BOUND:
        raise Blocked("INVALID_BOUND")
    return body

def inspect_tree(blob):
    try:
        arr=json.loads(blob.decode("utf-8"))
    except (UnicodeError,ValueError) as e:
        raise Blocked("INVALID_TREE_JSON") from e
    if not isinstance(arr,list) or len(arr)>1000:
        raise Blocked("INVALID_TREE_SHAPE")
    paths=[]
    for x in arr:
        if not isinstance(x,dict) or not isinstance(x.get("path"),str):
            raise Blocked("INVALID_TREE_ENTRY")
        p=x["path"]
        if len(p)>512 or ".." in p or p.startswith("/"):
            raise Blocked("INVALID_TREE_PATH")
        paths.append(p)
    return {"root_entries":len(paths),"readme_listed":"README.md" in paths,
            "icalens_manifest_listed":"icalens.json" in paths,
            "other_json_manifest_candidates":sorted(x for x in paths if x.lower().endswith(".json"))[:12]}

def inspect_readme(blob):
    sha=hashlib.sha256(blob).hexdigest()
    if sha!=HASH:
        raise Blocked("PINNED_README_SHA256_MISMATCH")
    try:
        lines=blob.decode("utf-8-sig").splitlines()
    except UnicodeError as e:
        raise Blocked("README_NOT_UTF8") from e
    declared=set()
    source_shas=set()
    for line in lines:
        s=line.strip()
        m=LICENSE.fullmatch(s)
        if m:
            declared.add(m.group(1).lower())
        if MODEL.lower() in line.lower():
            source_shas.update(m.group(0).lower() for m in SHA40.finditer(line))
    return {"sha256":sha,"lines":len(lines),"artifact_license_claims":sorted(declared),
            "explicit_qwen_source_revision_claims":sorted(source_shas),
            "rights_verified_independently":False,"source_revision_verified_independently":False}

def classify(root,readme):
    if not root["readme_listed"]:
        raise Blocked("PINNED_README_NOT_LISTED")
    licensed=len(readme["artifact_license_claims"])==1
    sourced=len(readme["explicit_qwen_source_revision_claims"])==1
    return {"schema":"yggdrasil.qtr01.f09.license-source-readiness.v1",
            "repo":REPO,"revision":REV,"root":root,"readme":readme,
            "artifact_license_claim_present":licensed,
            "source_model_revision_claim_present":sourced,
            "matrix_downloaded":False,"donor_inference":False,"recipient_edit":False,
            "causal_semantics_validated":False,"native_alignment_validated":False,
            "transplant_ready":False,
            "decision":("DECLARATIONS_EXIST_NOT_VERIFIED" if licensed and sourced
                        else "NO_GO_SOURCE_RIGHTS_OR_CHECKPOINT")}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--fixed-readonly-metadata",action="store_true",required=True)
    p.parse_args()
    try:
        out=classify(inspect_tree(get(ROOT)),inspect_readme(get(README)))
    except (Blocked,OSError,TimeoutError) as e:
        print("QTR01_F09_FAIL_CLOSED: "+str(e),file=sys.stderr)
        return 2
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
