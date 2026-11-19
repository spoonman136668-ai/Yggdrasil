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
