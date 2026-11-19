"""Opt-in public action-conditional archive vs new-native evidence recall.

All old native and six-head checkpoints are immutable. This is inference-only
selection over the existing CAP01 trained archive and native segment; it does
not control actions, update training, infer hidden phases or promote a policy.
"""
from __future__ import annotations
import json
from yggdrasil.native_context_basis import canonical, digest, pin

SCHEMA="yggdrasil.cap02.evidence-recall.v1"
MIN_PUBLIC_WITNESSES=4
CLIP_LOW=0.05
CLIP_HIGH=0.95
MAX_WITNESSES=256

def check(test,label):
    if not test:
        raise ValueError("CAP02_RECALL_"+label)

def bit(v):
    check(type(v) is int and v in (0,1),"PUBLIC_BIT")
    return v

def prob(v):
    check(type(v) in (int,float) and 0<=v<=1,"EXPERT_PROB")
    return float(v)

def context(stage,view,first,state=None,second=None):
    check(type(view) is tuple and len(view)==2,"PUBLIC_VIEW")
    v=bit(view[0])
    bit(view[1])
    a=bit(first)
    if stage=="transition":
        check(state is None and second is None,"STAGE_ONE_CLOCK")
        return ("transition",v,a)
    check(stage=="terminal","STAGE_NAME")
    return ("terminal",v,a,bit(state),bit(second))

class EvidenceRecall:
    def __init__(self):
        self._events=()
        self._keys={}
        self._used=set()

    def predict(self,stage,view,first,archive,active,state=None,second=None):
        key=context(stage,view,first,state,second)
        x=prob(archive)
        y=prob(active)
        old,new,count=self._keys.get(key,(1.,1.,0))
        # Reads cannot change evidence. Weak support always returns the
        # preregistered 50/50 backoff, irrespective of accidental key matches.
        weight=old/(old+new) if count>=MIN_PUBLIC_WITNESSES else .5
        return {"archive_weight":weight,"prob":weight*x+(1-weight)*y,
                "support":count,"public_key":key}

    def witness(self,source_id,stage,view,first,truth,
                archive,active,state=None,second=None):
        check(pin(source_id),"WITNESS_ID")
        key=context(stage,view,first,state,second)
        label=bit(truth)
        x,y=prob(archive),prob(active)
        identity=(source_id,stage)
        check(identity not in self._used,"WITNESS_REPLAY")
        check(len(self._events)<MAX_WITNESSES,"WITNESS_CAPACITY")
        a,b,count=self._keys.get(key,(1.,1.,0))
        qa=min(CLIP_HIGH,max(CLIP_LOW,x))
        qb=min(CLIP_HIGH,max(CLIP_LOW,y))
        a*=qa if label else 1-qa
        b*=qb if label else 1-qb
        # Renormalize both experts together; exactly preserves their
        # relative public evidence ratio and avoids underflow.
        scale=max(a,b)
        a,b=a/scale,b/scale
        record=(source_id,stage,key,label,x,y)
        self._events+= (record,)
        self._keys[key]=(a,b,count+1)
        self._used.add(identity)

    def checkpoint(self):
        return canonical({"schema":SCHEMA,"events":self._events})

    @classmethod
    def restore(cls,raw,sha):
        check(type(raw) is bytes and pin(sha) and digest(raw)==sha,
              "CHECKPOINT_PIN")
        try:
            d=json.loads(raw.decode("ascii"))
            check(type(d) is dict and set(d)=={"schema","events"} and
                  d["schema"]==SCHEMA and canonical(d)==raw,
                  "CHECKPOINT_SCHEMA")
            result=cls()
            for item in d["events"]:
                check(type(item) is list and len(item)==6,"COLD_EVIDENCE_ROW")
                identifier,stage,k,label,x,y=item
                check(type(k) is list and len(k) in (3,5),"COLD_KEY")
                if stage=="transition":
                    check(len(k)==3 and k[0]=="transition","COLD_STAGE")
                    result.witness(identifier,stage,(k[1],0),k[2],label,x,y)
                else:
                    check(len(k)==5 and k[0]=="terminal","COLD_STAGE")
                    result.witness(identifier,stage,(k[1],0),k[2],label,x,y,
                                   k[3],k[4])
            check(result.checkpoint()==raw,"COLD_WITNESSES_TAMPERED")
            return result
        except (KeyError,ValueError,TypeError,IndexError,UnicodeError) as exc:
            raise ValueError("CAP02_RECALL_COLD_REJECTED") from exc


def restore_original_sealed_native(raw, expected_sha):
    """Accept the exact original CAP01 learned weights, source-audited.

    The historical CAP01 replay contract demands identical floating-point
    serialization after retraining across machines; that is too strict for
    libm/NumPy last-ULP platform differences. Preserve the ORIGINAL weights
    byte-exactly. Independently replay the complete previously witnessed
    source to verify that all expert weights agree numerically within 1e-8,
    while source IDs, native banks, old archive, step counts and metadata
    must match exactly. Never generate a second development outcome.
    """
    from yggdrasil.native_segmented_continuation import (
        SegmentedNativeJEPA, EVENT_FIELDS, SCHEMA as NATIVE_SCHEMA,
        MAX_CHECKPOINT_BYTES, MAX_SHARDS, MAX_SHARD,
    )
    from yggdrasil.native_episode_experience import NativeEpisodeExperience
    from yggdrasil.native_jepa2_multilearner import ActionLatentSpecialist
    from yggdrasil.native_jepa_temporal import TemporalLatentSpecialist
    from yggdrasil.native_jepa_future import FutureStateHead
    check(type(raw) is bytes and len(raw) <= MAX_CHECKPOINT_BYTES and
          pin(expected_sha) and digest(raw)==expected_sha,
          "PORTABLE_SOURCE_SHA")
    try:
        d=json.loads(raw.decode("ascii"))
        check(type(d) is dict and set(d)=={
            "schema","archive_sha256","archive_ascii","original_count",
            "total_count","segments","events","offsets","one",
            "temporal","future",
        } and d["schema"]==NATIVE_SCHEMA and canonical(d)==raw,
              "PORTABLE_SCHEMA")
        archive=d["archive_ascii"].encode("ascii")
        base=SegmentedNativeJEPA.from_archive(archive,d["archive_sha256"])
        check(type(d["events"]) is list and
              len(d["events"])<=MAX_SHARDS*MAX_SHARD,
              "PORTABLE_EVENT_CAP")
        episodes=[]
        for item in d["events"]:
            check(type(item) is dict and set(item)==set(EVENT_FIELDS),
                  "PORTABLE_EVENT_FIELDS")
            episodes.append((
                item["identifier"],
                tuple(tuple(x) for x in item["views"]),
                item["first"],item["state"],item["second"],item["reward"],
                tuple(item["post"]),
            ))
        shards=[]
        for item in d["segments"]:
            check(type(item) is dict and set(item)=={"ascii","sha256"},
                  "PORTABLE_SHARD_FIELDS")
            blob=item["ascii"].encode("ascii")
            shards.append(NativeEpisodeExperience.restore(blob,item["sha256"]))
        check(len(shards) in range(1,MAX_SHARDS+1),
              "PORTABLE_SHARD_COUNT")
        one=(ActionLatentSpecialist.from_data(d["one"][0],"transition"),
             ActionLatentSpecialist.from_data(d["one"][1],"reward"))
        temporal=(TemporalLatentSpecialist.from_data(
                      d["temporal"][0],"transition"),
                  TemporalLatentSpecialist.from_data(
                      d["temporal"][1],"reward"))
        future=tuple(FutureStateHead.restore(v) for v in d["future"])
        offsets=tuple(tuple(v) for v in d["offsets"])
        original=SegmentedNativeJEPA(
            archive,base._source,tuple(shards),tuple(episodes),
            one,temporal,future,offsets
        )
        check(original.total_count==d["total_count"] and
              original.original_count==d["original_count"] and
              original.checkpoint()==raw,
              "PORTABLE_RAW_BYTES")
        # Replay original actual witnessed source for independent weight
        # provenance; this DOES NOT change the returned original weights.
        replay=SegmentedNativeJEPA.from_archive(
            archive,d["archive_sha256"])
        for source_id,views,a,s,b,y,post in episodes:
            replay=replay.observe(source_id,views,{
                "s1":views[0][0],"x1":a,"s2":s,"x2":b,"y":y
            },post)
        expected=json.loads(replay.checkpoint())
        def equivalent(x,y,path="$"):
            check(type(x) is type(y),"PORTABLE_NUMERIC_TYPE_"+path)
            if type(x) is dict:
                check(set(x)==set(y),"PORTABLE_FIELD_"+path)
                for key in sorted(x):
                    equivalent(x[key],y[key],path+"."+key)
            elif type(x) is list:
                check(len(x)==len(y),"PORTABLE_LENGTH_"+path)
                for i,(a,b) in enumerate(zip(x,y)):
                    equivalent(a,b,path+"["+str(i)+"]")
            elif type(x) is float:
                check(abs(x-y)<=1e-8,
                      "PORTABLE_TOLERANCE_"+path)
            else:
                check(x==y,"PORTABLE_CUSTODY_"+path)
        equivalent(d,expected)
        return original
    except (TypeError,ValueError,KeyError,AttributeError,IndexError,
            UnicodeError,OverflowError,RecursionError) as exc:
        raise ValueError("YGG_CAP02_PORTABLE_REPLAY_REJECTED") from exc
