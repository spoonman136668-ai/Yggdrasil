"""WSP-116: real historical TRAIN-only connected-knowledge foundation dose response.

All 4096 masked queries and original WSP105 full-tier scores are PREVIOUSLY
CONSUMED. This is nonindependent evidence, never a new scientific first-use.
No official validation/test records, new source, hidden labels for fitting,
accepted native weights or production integration.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256
import heapq
import json
from pathlib import Path
import random
import struct
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"WSP-105"))
from subject_path_control import (
    CAPACITY, QUERY_COUNT, SUBJECT_NEIGHBORS, MAX_JOIN_UPDATES,
    NEIGHBOR_DOMAIN, PACK_TRIPLE, FROZEN_SAMPLE_SHA,
    FROZEN_WSP104_FREQUENCY, FROZEN_WSP104_SCORE_SHA,
    TRAIN_ROWS, TRAIN_BYTES, TRAIN_SHA, RELATIONS,
    ARCHIVE_SHA, EXPECTED_ARCHIVE_BYTES, group_digest, heldout,
    parse_triple, load_custody_helpers, open_train_only,
    first_correct_rank,
)
import numpy as np

TIERS=(16,64,256)
TIER_NAMES=("6.25%","25%","100%")
TIER_DOMAIN=b"WSP116-TIER-v1\x00"
MAX_WALL=1800
MAX_PACKED_BYTES=256_000_000
PACK_GROUP=struct.Struct("<II")
FROZEN_FULL=(921,1853,2,44,1190,2038)


def member_bucket(s,p,o):
    return sha256(TIER_DOMAIN+PACK_TRIPLE.pack(s,p,o)).digest()[0]


def query_priority(s,p):
    d=group_digest(s,p)
    return int.from_bytes(d[8:16],"big")


def rank_binary(ranked,answers):
    return first_correct_rank(ranked,answers)


def numpy_rank(base,frequency,votes):
    """Independent array-weight ordering, exact symbolic order expected."""
    if not base:return []
    objs=np.asarray(base,dtype=np.uint64)
    f=np.asarray([frequency.get(int(v),0) for v in objs],dtype=np.int64)
    v=np.asarray([votes.get(int(x),0) for x in objs],dtype=np.int64)
    ix=np.lexsort((objs,-f,-v))
    return [int(objs[i]) for i in ix]


def paired_bootstrap(full,quarter,iterations=10_000,seed=1160):
    if len(full)!=len(quarter) or not full:
        raise ValueError("WSP116_INVALID_PAIRED_COHORT")
    d=np.asarray(full,dtype=np.float64)-np.asarray(quarter,dtype=np.float64)
    if not np.all(np.isin(d,(-1,0,1))):
        raise ValueError("WSP116_INVALID_BINARY_RANK")
    rng=np.random.default_rng(seed)
    draws=np.empty(iterations,dtype=np.float64)
    for pos in range(0,iterations,256):
        stop=min(pos+256,iterations)
        indices=rng.integers(0,len(d),size=(stop-pos,len(d)),dtype=np.int32)
        draws[pos:stop]=d[indices].mean(axis=1)
    return [float(np.quantile(draws,0.025)),float(np.quantile(draws,0.975))]


def evaluate(open_train,*,expected_rows=TRAIN_ROWS,
             expected_bytes=TRAIN_BYTES,expected_sha=TRAIN_SHA,
             expected_relations=RELATIONS,query_count=QUERY_COUNT,
             expected_answers_sha=FROZEN_SAMPLE_SHA,
             expected_full=FROZEN_FULL,
             expected_freq_sha=FROZEN_WSP104_SCORE_SHA,
             max_wall_seconds=MAX_WALL):
    """Exactly three source passes, masked answers never affect any tier model.

    Pass 1: verify source + select existing group mask based only on subject
    and predicate. Pass 2: source numeric packing, heavy candidates, observed
    subject neighbors, sealed answer witness. Pass 3: independent exact
    counts and 2-hop joins using only retained nested tiers.
    """
    if (query_count<1 or query_count>4096 or
        expected_rows<1 or expected_bytes<1 or expected_relations<1
        or max_wall_seconds<=0):
        raise ValueError("WSP116_FROZEN_SOURCE_LIMIT")
    start=time.monotonic()
    cpu_start=time.process_time()

    def bounded(handle):
        for i,raw in enumerate(handle):
            if i%16384==0 and time.monotonic()-start>max_wall_seconds:
                raise TimeoutError("WSP116_SOURCE_TIME_BUDGET")
            yield raw

    src_hash=sha256()
    heap=[]; seen=set();rows=0;bytes_seen=0;hidden_rows=0;predicates=set()
    with open_train() as f:
        for raw in bounded(f):
            rows+=1;bytes_seen+=len(raw)
            if rows>expected_rows or bytes_seen>expected_bytes:
                raise ValueError("WSP116_SOURCE_INVENTORY_OVERFLOW")
            s,p,_=parse_triple(raw)
            src_hash.update(raw)
            predicates.add(p)
            d=group_digest(s,p)
            if not heldout(d):continue
            hidden_rows+=1
            k=(s,p)
            if k in seen:continue
            priority=query_priority(s,p)
            scalar=(s<<32)|p
            item=(-priority,-scalar,k)
            if len(heap)<query_count:
                heapq.heappush(heap,item);seen.add(k)
            elif (priority,scalar)<(-heap[0][0],-heap[0][1]):
                old=heapq.heapreplace(heap,item)
                seen.remove(old[2]);seen.add(k)
    if (rows!=expected_rows or bytes_seen!=expected_bytes or
        src_hash.hexdigest()!=expected_sha or
        len(predicates)!=expected_relations or len(heap)!=query_count):
        raise ValueError("WSP116_SOURCE_SHA_ROW_RELATION_OR_SAMPLE_DRIFT")

    selected={item[2]:set() for item in heap}
    questions=defaultdict(list)
    for k in selected:questions[k[0]].append(k)
    state=[]
    files=[]
    for fraction in TIERS:
        f=tempfile.TemporaryFile(mode="w+b")
        files.append(f)
        state.append({"fraction":fraction,"heavy":{},"subject_heaps":{},
            "subject_seen":{},"retained":0,"packed":sha256(),
            "file":f,"packed_bytes":0})
    try:
        with open_train() as f:
            for raw in bounded(f):
                s,p,o=parse_triple(raw)
                if heldout(group_digest(s,p)):
                    if (s,p) in selected:selected[(s,p)].add(o)
                    continue
                bucket=member_bucket(s,p,o)
                packed=PACK_TRIPLE.pack(s,p,o)
                for x in state:
                    if bucket>=x["fraction"]:continue
                    x["retained"]+=1
                    x["packed_bytes"]+=len(packed)
                    if x["packed_bytes"]>MAX_PACKED_BYTES:
                        raise MemoryError("WSP116_NUMERIC_FACT_CAPACITY")
                    x["file"].write(packed)
                    x["packed"].update(packed)
                    counter=x["heavy"].setdefault(p,{})
                    if o in counter:counter[o]+=1
                    elif len(counter)<CAPACITY:counter[o]=1
                    else:
                        for obj in tuple(counter):
                            count=counter[obj]-1
                            if count:counter[obj]=count
                            else:del counter[obj]
                    if s not in questions:continue
                    # Frozen WSP105 subject-neighbor hash selection, but
                    # applied strictly within each tier's retained evidence.
                    pair=(p,o)
                    seen_pairs=x["subject_seen"].setdefault(s,set())
                    if pair in seen_pairs:continue
                    priority=int.from_bytes(
                        sha256(NEIGHBOR_DOMAIN+packed).digest()[:8],"big")
                    item=(-priority,-p,-o,pair)
                    h=x["subject_heaps"].setdefault(s,[])
                    if len(h)<SUBJECT_NEIGHBORS:
                        heapq.heappush(h,item);seen_pairs.add(pair)
                    elif (priority,p,o)<(-h[0][0],-h[0][1],-h[0][2]):
                        old=heapq.heapreplace(h,item)
                        seen_pairs.remove(old[3]);seen_pairs.add(pair)
        if any(not answers for answers in selected.values()):
            raise ValueError("WSP116_MASKED_QUERY_LABEL_MISSING")
        witness=sha256()
        for (s,p),answers in sorted(selected.items()):
            witness.update(PACK_GROUP.pack(s,p))
            witness.update(struct.pack("<I",len(answers)))
            for val in sorted(answers):witness.update(struct.pack("<I",val))
        if expected_answers_sha and witness.hexdigest()!=expected_answers_sha:
            raise ValueError("WSP116_PREVIOUS_SOURCE_ANSWER_WITNESS_DRIFT")
        for x in state:
            f=x["file"];f.flush();f.seek(0)
            cold=sha256();cold_bytes=0
            while True:
                chunk=f.read(1<<20)
                if not chunk:break
                cold.update(chunk);cold_bytes+=len(chunk)
            if cold_bytes!=x["packed_bytes"] or cold.hexdigest()!=x["packed"].hexdigest():
                raise AssertionError("WSP116_NUMERIC_FACT_COLD_MISMATCH")
            x["cold_sha"]=cold.hexdigest()
            x["candidate_keys"]={p:set(counters) for p,counters in x["heavy"].items()}
            x["exact"]={p:Counter() for p in x["candidate_keys"]}
            x["candidates_by_object"]=defaultdict(set)
            query_predicates={q[1] for q in selected}
            for p,objs in x["candidate_keys"].items():
                if p not in query_predicates:continue
                for obj in objs:x["candidates_by_object"][obj].add(p)
            x["neighbor_queries"]=defaultdict(lambda:defaultdict(set))
            for s,klist in questions.items():
                for _,_,_,(r1,z) in x["subject_heaps"].get(s,()):
                    for key in klist:x["neighbor_queries"][z][key[1]].add(key)
            x["votes"]={};x["joins"]=0;x["recounted"]=0

        with open_train() as f:
            for raw in bounded(f):
                s,p,o=parse_triple(raw)
                if heldout(group_digest(s,p)):continue
                bucket=member_bucket(s,p,o)
                for x in state:
                    if bucket>=x["fraction"]:continue
                    x["recounted"]+=1
                    if o in x["candidate_keys"].get(p,()):
                        x["exact"][p][o]+=1
                    targets=x["neighbor_queries"].get(s)
                    if not targets:continue
                    for pred in x["candidates_by_object"].get(o,()):
                        for query in targets.get(pred,()):
                            votes=x["votes"].setdefault(query,Counter())
                            votes[o]+=1
                            x["joins"]+=1
                            if x["joins"]>MAX_JOIN_UPDATES:
                                raise MemoryError("WSP116_PATH_JOIN_BOUND_EXCEEDED")
        for x in state:
            if x["recounted"]!=x["retained"]:
                raise AssertionError("WSP116_SOURCE_TIER_PASS_DRIFT")

        outputs=[];rank1={}
        for x in state:
            arms={name:{"hits1":0,"hits10":0,"rr":0.}
                  for name in ("frequency","reverse","path_only","path_first")}
            freq_receipt=sha256();path_receipt=sha256();hits1=[]
            parity=0
            for question,answers in sorted(selected.items()):
                s,p=question
                freq=x["exact"].get(p,{})
                base=sorted(x["candidate_keys"].get(p,()),
                            key=lambda obj:(-freq.get(obj,0),obj))
                votes=x["votes"].get(question,{})
                ordered=sorted(base,key=lambda obj:(-votes.get(obj,0),
                                                     -freq.get(obj,0),obj))
                independent_numeric=numpy_rank(base,freq,votes)
                if ordered!=independent_numeric:
                    raise AssertionError("WSP116_NUMERIC_SYMBOLIC_RANK_DRIFT")
                parity+=1
                path_only=[obj for obj in ordered if votes.get(obj,0)>0]
                options={
                    "frequency":base,"reverse":list(reversed(base)),
                    "path_only":path_only,"path_first":ordered}
                for name,items in options.items():
                    rank=rank_binary(items,answers)
                    a=arms[name]
                    a["hits1"]+=int(rank==1)
                    a["hits10"]+=int(0<rank<=10)
                    a["rr"]+=1/rank if rank else 0
                    if name in ("frequency","reverse"):
                        freq_receipt.update(struct.pack("<II",len(items),rank))
                    else:
                        path_receipt.update(struct.pack("<II",len(items),rank))
                hits1.append(int(bool(ordered and ordered[0] in answers)))
            for values in arms.values():
                values["mrr"]=values.pop("rr")/query_count
                values["hits1_rate"]=values["hits1"]/query_count
                values["hits10_rate"]=values["hits10"]/query_count
            rank1[x["fraction"]]=hits1
            outputs.append({
                "tier":TIER_NAMES[len(outputs)],"source_fraction_num":x["fraction"],
                "retained_source_facts":x["retained"],
                "programmed_raw_uint32_fact_weights":3*x["retained"],
                "programmed_raw_numeric_bytes":x["packed_bytes"],
                "programmed_numeric_cold_sha256":x["cold_sha"],
                "source_neighbor_edges":sum(len(h) for h in x["subject_heaps"].values()),
                "path_join_updates":x["joins"],
                "numeric_symbolic_rank_parity_queries":parity,
                "frequency_score_receipt_sha256":freq_receipt.hexdigest(),
                "path_score_receipt_sha256":path_receipt.hexdigest(),
                "metrics":arms})
        full=outputs[-1]
        if expected_full is not None:
            a=full["metrics"]
            observed=(a["frequency"]["hits1"],a["frequency"]["hits10"],
                      a["reverse"]["hits1"],a["reverse"]["hits10"],
                      a["path_first"]["hits1"],a["path_first"]["hits10"])
            if tuple(expected_full)!=observed:
                raise AssertionError("WSP116_WSP105_FULL_SCORE_INTEGRITY_DRIFT")
        if expected_freq_sha and full["frequency_score_receipt_sha256"]!=expected_freq_sha:
            raise AssertionError("WSP116_WSP104_FULL_FREQUENCY_RECEIPT_DRIFT")
        improvement=full["metrics"]["path_first"]["hits1"]-outputs[1]["metrics"]["path_first"]["hits1"]
        ci=paired_bootstrap(rank1[256],rank1[64])
        diagnostics_pass=(improvement>=100 and ci[0]>0)
        return {
            "schema":"wsp116.consumed-historical-realgraph-tiered-source.v1",
            "classification":"NONINDEPENDENT_SOURCE_DOSE_RESPONSE_DIAGNOSTIC_PASS"
                if diagnostics_pass else "NONINDEPENDENT_SOURCE_DOSE_RESPONSE_NEGATIVE",
            "development_first_use":False,"protected_first_use":False,
            "official_validation_test_opened":False,"native_model_modified":False,
            "scientific_pass":False,
            "source_train_sha256":src_hash.hexdigest(),"source_rows":rows,
            "source_bytes":bytes_seen,"source_predicate_count":len(predicates),
            "masked_training_rows":hidden_rows,"masked_query_groups":len(selected),
            "known_masked_answer_receipt_sha256":witness.hexdigest(),
            "tiers":outputs,
            "full_minus_quarter_path_first_hits1_count":improvement,
            "full_minus_quarter_path_first_hits1_rate":improvement/query_count,
            "full_minus_quarter_bootstrap_world_ci95":ci,
            "fixed_diagnostic_threshold_count":100,
            "source_cpu_seconds":time.process_time()-cpu_start,
            "source_wall_seconds":time.monotonic()-start,
            "historical_noncanonical":True,
            "exact_same_information_symbolic_control_ties":True}
    finally:
        for f in files:f.close()


def real_train_only():
    # Reuse WSP102 strict archive allowlist/provenance, NEVER open valid/test.
    _download,inspect=load_custody_helpers()
    with tempfile.TemporaryDirectory(prefix="wsp116-historical-") as td:
        archive=Path(td)/"frozen-historical.tar.gz"
        before=time.monotonic()
        metadata=_download(archive)
        if (metadata["compressed_sha256"]!=ARCHIVE_SHA or
            metadata["compressed_bytes"]!=EXPECTED_ARCHIVE_BYTES):
            raise ValueError("WSP116_ARCHIVE_CUSTODY_MISMATCH")
        members={(x["path"],x["type"],x["uncompressed_bytes"])
                 for x in inspect(archive)["members"]}
        known={
            ("wikidata5m","directory",0),
            ("wikidata5m/train.txt","file",TRAIN_BYTES),
            ("wikidata5m/valid.txt","file",109498),
            ("wikidata5m/test.txt","file",108932)}
        if members!=known:
            raise ValueError("WSP116_ARCHIVE_MEMBER_ALLOWLIST_DRIFT")
        result=evaluate(lambda:open_train_only(archive))
        result["archive_sha256"]=ARCHIVE_SHA
        result["whole_process_wall_seconds"]=time.monotonic()-before
        return result


if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--consumed-historical-train-diagnostic",required=True,action="store_true")
    p.add_argument("--protected",action="store_true")
    args=p.parse_args()
    if args.protected:
        p.error("WSP116_PROTECTED_SOURCE_FIRST_USE_FORBIDDEN")
    print("WSP116_CONSUMED_TRAIN_DIAGNOSTIC="+json.dumps(
        real_train_only(),sort_keys=True,separators=(",",":")),flush=True)
