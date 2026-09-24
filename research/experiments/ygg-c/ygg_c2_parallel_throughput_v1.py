#!/usr/bin/env python3
import concurrent.futures as cf
import hashlib, json, multiprocessing as mp, sys, time
from pathlib import Path

import torch
import lu2v_task4_independent_confirmation_v1 as lu2v

PREREG="44a6f5ff63c6ef93eef53f6193d51adbb03432ed"
LU2VF1="e832853554e813db2e185d6b607543541f32d887"
WORKERS=(1,2,4,8)

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()

def worker_init():
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)

def worker_run(m):
    return lu2v.run_pair(m)

def integrity(rows):
    for row in rows:
        for arm in ("a0","a25"):
            r=row[arm]
            if r["matching_duplicate_cell"]!=0 or r["matching_duplicate_request"]!=0:
                return False
    return True

def scored(pool,manifests):
    t0=time.perf_counter()
    rows=list(pool.map(worker_run,manifests))
    dt=time.perf_counter()-t0
    return {
        "seconds":dt,
        "worlds_per_second":len(rows)/dt,
        "evidence_sha256":hashlib.sha256(canonical(rows)).hexdigest(),
        "integrity":integrity(rows),
    }

def run():
    manifests=lu2v.primary_manifests(LU2VF1)
    mechanical=lu2v.mechanical_manifest()
    ctx=mp.get_context("spawn")
    groups=[]
    for workers in WORKERS:
        with cf.ProcessPoolExecutor(max_workers=workers,mp_context=ctx,initializer=worker_init) as pool:
            # Warm every worker with unscored accepted mechanical work.
            list(pool.map(worker_run,[mechanical for _ in range(workers)]))
            p1=scored(pool,manifests)
            p2=scored(pool,manifests)
        groups.append({"workers":workers,"passes":[p1,p2]})

    hashes=[p["evidence_sha256"] for g in groups for p in g["passes"]]
    all_integrity=all(p["integrity"] for g in groups for p in g["passes"])
    evidence_identical=len(set(hashes))==1

    one=[g for g in groups if g["workers"]==1][0]
    base=sorted(p["seconds"] for p in one["passes"])[len(one["passes"])//2]
    # With two observations, report arithmetic midpoint as the scored one-worker reference.
    base=sum(p["seconds"] for p in one["passes"])/2.0
    for g in groups:
        for p in g["passes"]:
            p["speedup_vs_one_worker_reference"]=base/p["seconds"]

    return {
        "schema":1,
        "experiment":"YGG-C2",
        "prereg":PREREG,
        "shared_baseline":"878464cf84833d06a1ac7e45988bfb79608547dc",
        "lu2vf1":LU2VF1,
        "worker_counts":list(WORKERS),
        "torch_num_threads_per_worker":1,
        "all_evidence_identical":evidence_identical,
        "all_integrity_pass":all_integrity,
        "reference_one_worker_seconds":base,
        "groups":groups,
        "valid":bool(evidence_identical and all_integrity),
    }

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: OUT")
    out=run()
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    mp.freeze_support()
    main()
