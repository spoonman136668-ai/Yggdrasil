"""NKR25: immutable, bounded restoration of injected factual-memory faults.

This OPTIONAL RESEARCH overlay keeps the entire historical image read-only.
It is not semantic truth correction, accepted model admission or causal learning.
Fault injection is explicitly synthetic. Repairs restore exact frozen source
membership from row witnesses; they never invent verified real-world facts.
"""
from __future__ import annotations
import json
import re
from yggdrasil.native_factual_weights import NativeFactualWeights,canonical,digest,_id

SCHEMA="yggdrasil.nkr25.bounded-factual-repair.v1"
BUNDLE="yggdrasil.nkr25.source-row-restoration.v1"
MODE="engineering_injected_membership_faults_only"
MAX_FAULTS=32768
MAX_OPERATIONS=65536
MAX_BYTES=8*1024*1024
MAX_TRANSACTIONS=8
REF=re.compile(r"[a-z][a-z0-9_-]{2,79}\Z")

def need(ok,reason):
    if not ok:
        raise ValueError("NKR25_"+reason)

def parse(raw,pin):
    need(type(raw) is bytes and 0<len(raw)<=MAX_BYTES,"BYTES")
    need(type(pin) is str and re.fullmatch(r"[0-9a-f]{64}",pin) is not None
         and digest(raw)==pin,"SHA_PIN")
    def unique(pairs):
        d={}
        for k,v in pairs:
            need(k not in d,"DUPLICATE_JSON_KEY")
            d[k]=v
        return d
    try:
        d=json.loads(raw.decode("ascii"),object_pairs_hook=unique)
    except (ValueError,UnicodeError) as exc:
        raise ValueError("NKR25_JSON") from exc
    need(type(d) is dict and canonical(d)==raw,"CANONICAL_JSON")
    return d

def binding(base):
    need(isinstance(base,NativeFactualWeights),"NATIVE_FACTUAL_BASE_REQUIRED")
    return {"manifest_sha256":digest(canonical(base.manifest)),
            "image_sha256":base.manifest["packed_sha256"],"records":len(base)}

class BoundedFactRepair:
    """Source-backed facts plus bounded, explicitly injected fault membership."""
    __slots__=("base","_raw","_sha","_faults","_removed","_added","_extra","_doc")

    def __init__(self,base,raw,expected_sha256):
        d=parse(raw,expected_sha256)
        need(set(d)=={"schema","base","faults","repair_history","mode",
                      "scientific_pass","accepted_native"}
             and d["schema"]==SCHEMA and d["base"]==binding(base)
             and d["mode"]==MODE and d["scientific_pass"] is False
             and d["accepted_native"] is False,"CHECKPOINT_CONTRACT")
        faults=d["faults"];history=d["repair_history"]
        need(type(faults) is list and len(faults)<=MAX_FAULTS
             and type(history) is list and len(history)<=MAX_TRANSACTIONS,"CAPACITY")
        fault_map={};removed=set();added=set();extra={}
        previous=-1
        for record in faults:
            need(type(record) is list and len(record)==2,"FAULT_ROW")
            index,wrong=record
            need(type(index) is int and previous<index<len(base),"FAULT_INDEX_ORDER")
            _id(wrong)
            true=base.row_at(index)
            need(wrong==(true[2]^0x80000000),"ONLY_DECLARED_FAULT_INJECTION")
            false=(true[0],true[1],wrong)
            need(not base.has_fact(*false),"INJECTED_OBJECT_ALREADY_SOURCE_FACT")
            need(true not in removed and false not in added,"DUPLICATE_FAULT_MEMBERSHIP")
            fault_map[index]=wrong;removed.add(true);added.add(false)
            extra.setdefault((true[0],true[1]),[]).append(wrong)
            previous=index
        need(removed.isdisjoint(added),"FAULT_SCOPE_COLLISION")
        ids=set()
        fields={"source_id","bundle_sha256","parent_checkpoint_sha256",
                "operation_budget","restored_pairs"}
        for h in history:
            need(type(h) is dict and set(h)==fields,"REPAIR_HISTORY_FIELDS")
            need(type(h["source_id"]) is str and REF.fullmatch(h["source_id"]) is not None
                 and h["source_id"] not in ids,"REPAIR_SOURCE_ID")
            ids.add(h["source_id"])
            need(all(type(h[k]) is str and re.fullmatch(r"[0-9a-f]{64}",h[k])
                     for k in ("bundle_sha256","parent_checkpoint_sha256")),"HISTORY_SHA")
            b,n=h["operation_budget"],h["restored_pairs"]
            need(type(b) is int and 0<b<=MAX_OPERATIONS and b%2==0
                 and type(n) is int and 0<n<=MAX_FAULTS and 2*n<=b,"HISTORY_BUDGET")
        self.base=base;self._raw=raw;self._sha=expected_sha256
        self._faults=fault_map;self._removed=frozenset(removed);self._added=frozenset(added)
        self._extra={k:tuple(sorted(v)) for k,v in extra.items()};self._doc=d

    @classmethod
    def inject_fixture_faults(cls,base,indices):
        need(type(indices) is list and len(indices)<=MAX_FAULTS,"FAULT_CAPACITY")
        need(all(type(i) is int and 0<=i<len(base) for i in indices)
             and indices==sorted(set(indices)),"FAULT_INDEX_SET")
        d={"schema":SCHEMA,"base":binding(base),
           "faults":[[i,base.row_at(i)[2]^0x80000000] for i in indices],
           "repair_history":[],"mode":MODE,"scientific_pass":False,"accepted_native":False}
        raw=canonical(d)
        return cls(base,raw,digest(raw))

    @property
    def fault_count(self):
        return len(self._faults)

    @property
    def checkpoint_sha256(self):
        return self._sha

    def checkpoint(self):
        return self._raw

    def has_fact(self,subject,predicate,obj):
        fact=(_id(subject),_id(predicate),_id(obj))
        if fact in self._added:
            return True
        if fact in self._removed:
            return False
        return self.base.has_fact(*fact)

    def objects(self,subject,predicate,*,limit=64,after=0):
        _id(subject);_id(predicate)
        need(type(limit) is int and 1<=limit<=256,"QUERY_LIMIT")
        need(type(after) is int and 0<=after<=0xFFFFFFFF,"QUERY_CURSOR")
        if not self._faults:
            return self.base.objects(subject,predicate,limit=limit,after=after)
        values=[];cursor=after
        while len(values)<limit:
            page=self.base.objects(subject,predicate,limit=256,after=cursor)
            if not page:
                break
            values.extend(o for o in page if (subject,predicate,o) not in self._removed)
            cursor=page[-1]
            if len(page)<256:
                break
        additions=[o for o in self._extra.get((subject,predicate),()) if o>after]
        return sorted(set(values).union(additions))[:limit]

    def stage_repair(self,raw,expected_source_sha256,*,operation_budget):
        d=parse(raw,expected_source_sha256)
        need(type(operation_budget) is int and 0<operation_budget<=MAX_OPERATIONS
             and operation_budget%2==0,"OPERATION_BUDGET")
        need(set(d)=={"schema","base","source_id","parent_checkpoint_sha256",
                      "operation_budget","records","source_kind"}
             and d["schema"]==BUNDLE and d["base"]==binding(self.base)
             and d["source_kind"]=="frozen_historical_row_witness"
             and d["operation_budget"]==operation_budget,"WITNESS_CONTRACT")
        ident=d["source_id"]
        need(type(ident) is str and REF.fullmatch(ident) is not None,"WITNESS_SOURCE_ID")
        for h in self._doc["repair_history"]:
            if h["source_id"]==ident:
                need(h["bundle_sha256"]==expected_source_sha256,"SOURCE_ID_REBOUND")
                return self,{"classification":"DUPLICATE_REPAIR_NO_CHANGE",
                             "operations":0,"remaining_faults":self.fault_count,
                             "checkpoint_sha256":self._sha}
        need(d["parent_checkpoint_sha256"]==self._sha,"FROZEN_PARENT_DRIFT")
        need(len(self._doc["repair_history"])<MAX_TRANSACTIONS,"TRANSACTION_LIMIT")
        rows=d["records"]
        need(type(rows) is list and 0<len(rows)<=MAX_FAULTS
             and 2*len(rows)<=operation_budget,"WITNESS_BUDGET")
        selected=[];previous=-1
        for r in rows:
            need(type(r) is list and len(r)==3,"WITNESS_ROW")
            index,true,wrong=r
            need(type(index) is int and previous<index<len(self.base)
                 and index in self._faults,"WITNESS_INDEX")
            need(type(true) is list and len(true)==3
                 and all(type(v) is int and 0<v<=0xFFFFFFFF for v in true),
                 "WITNESS_TRIPLE_TYPES")
            need(tuple(true)==self.base.row_at(index),"WITNESS_NOT_EXACT_SOURCE_ROW")
            need(type(wrong) is int and wrong==self._faults[index],"WITNESS_FAULT_DRIFT")
            selected.append(index);previous=index
        # All validation is complete before a candidate is staged.
        chosen=set(selected)
        out=dict(self._doc)
        out["faults"]=[r for r in self._doc["faults"] if r[0] not in chosen]
        out["repair_history"]=self._doc["repair_history"]+[{
            "source_id":ident,"bundle_sha256":expected_source_sha256,
            "parent_checkpoint_sha256":self._sha,"operation_budget":operation_budget,
            "restored_pairs":len(selected)}]
        packed=canonical(out)
        new=BoundedFactRepair(self.base,packed,digest(packed))
        return new,{"classification":"BOUNDED_HISTORICAL_SOURCE_RESTORATION",
                    "source_id":ident,"operations":2*len(selected),
                    "restored_pairs":len(selected),"remaining_faults":new.fault_count,
                    "frozen_parent_sha256":self._sha,"checkpoint_sha256":new._sha,
                    "scientific_pass":False,"accepted_native":False,
                    "real_world_semantic_repair_proved":False}

    @property
    def manifest(self):
        # Compatible source identity for existing read-only factual consumers.
        return dict(self.base.manifest)

    def two_hop_candidates(self,subject,first_relation,second_relation,
                           *,max_intermediates=16,max_candidates=64):
        # Reuse the EXISTING bounded operator with this candidate's objects().
        # Returned paths remain hypotheses; no new fact is installed.
        return NativeFactualWeights.two_hop_candidates(
            self,subject,first_relation,second_relation,
            max_intermediates=max_intermediates,max_candidates=max_candidates)
