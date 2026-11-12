"""WSP53 source-isolated integer sparse-weight prototype. SELFTEST only.

Raw acoustic binary streams are never converted to supplied word/token IDs.
Only learner-visible observations and the public physical action family enter.
There is no hidden generator import, trained neural model, or science claim.
"""
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import product
import json
from controls import MAX_ACTIONS, bits, canonical, observation, state

MAX_WEIGHTS = 80000
MODES = ("pure_direct", "count_only", "random_address")

def segment(raw):
    bits(raw)
    return tuple((raw[:a],raw[a:a+b],raw[a+b:]) for a,b,c in
                 product((4,5,6),repeat=3) if a+b+c==len(raw))

def grounded_change(family, before, after):
    changed = [i for i in range(8) if before[i]!=after[i] or
               (family=="anchored_effect" and before[8+i]!=after[8+i])]
    if len(changed)!=1:
        return None
    entity=changed[0]
    if family=="anchored_effect":
        return entity,(-1,after[entity],(after[8+entity]-before[8+entity])%3)
    return entity,(before[entity],after[entity],-1)

class SparseAcousticWriter:
    """Provisional direct/count-only/random-address numerical controls.

    Direct mode abstains unless evidence supports exactly one semantic outcome.
    Count mode selects a strict maximum; random mode uses a fixed hash address.
    None of these is a trained or qualified language-understanding model.
    """
    def __init__(self, *, family, mode="pure_direct"):
        state((0,)*(16 if family=="anchored_effect" else 8),family)
        if mode not in MODES:
            raise ValueError("invalid mode")
        self.family,self.mode=family,mode
        self.actions=self.informative=0
        self.entities=Counter()
        self.effects=Counter()
        self.by_address=defaultdict(Counter)
        self.seen={}
        self.conflicts=set()

    def observe(self,row):
        before,raw,after=observation(row,self.family)
        if self.actions>=MAX_ACTIONS:
            raise ValueError("action budget exceeded")
        pieces=segment(raw)
        key=before,raw
        if key in self.seen and self.seen[key]!=after:
            self.conflicts.add(key)
        if key not in self.seen:
            self.seen[key]=after
        signal=grounded_change(self.family,before,after)
        self.actions+=1
        if signal is None or key in self.conflicts:
            return
        self.informative+=1
        entity,effect=signal
        for parts in pieces:
            for slot in range(3):
                others=tuple(parts[i] for i in range(3) if i!=slot)
                self.entities[(slot,parts[slot],entity)]+=1
                self.effects[(slot,*others,*effect)]+=1
                self.by_address[(slot,*others)][effect]+=1
        if len(self.entities)+len(self.effects)>MAX_WEIGHTS:
            raise OverflowError("numeric weight budget exceeded")

    def select(self,votes, minimum=2):
        if not votes:
            return None
        ranking=sorted(votes.items(),key=lambda x:(-x[1],x[0]))
        if ranking[0][1]<minimum:
            return None
        if self.mode=="pure_direct":
            return ranking[0][0] if len(ranking)==1 else None
        return ranking[0][0] if len(ranking)==1 or ranking[0][1]>ranking[1][1] else None

    def predict(self,before,raw):
        state(before,self.family)
        bits(raw)
        if (before,raw) in self.conflicts:
            return None
        pieces=segment(raw)
        votes=Counter()
        for parts in pieces:
            for slot in range(3):
                for entity in range(8):
                    n=self.entities.get((slot,parts[slot],entity),0)
                    if n:
                        votes[entity]+=n
        if self.mode=="random_address":
            entity=int(sha256(raw.encode("ascii")).hexdigest(),16)%8
            if not votes[entity]:
                return None
        else:
            entity=self.select(votes)
        if entity is None:
            return None
        effects=Counter()
        for parts in pieces:
            for slot in range(3):
                if not self.entities.get((slot,parts[slot],entity),0):
                    continue
                others=tuple(parts[i] for i in range(3) if i!=slot)
                for effect,n in self.by_address.get((slot,*others),{}).items():
                    first,_,_=effect
                    if self.family=="anchored_effect" or first==before[entity]:
                        effects[effect]+=n
        picked=self.select(effects)
        if picked is None:
            return None
        _,after_location,orientation_delta=picked
        after=list(before)
        after[entity]=after_location
        if self.family=="anchored_effect":
            after[8+entity]=(before[8+entity]+orientation_delta)%3
        return tuple(after)

    def numeric_weight_count(self):
        return len(self.entities)+len(self.effects)

    def snapshot(self):
        payload={
            "schema":"wsp53.sparse-writer.v1","family":self.family,
            "mode":self.mode,"actions":self.actions,"informative":self.informative,
            "entities":[[list(k),v] for k,v in sorted(self.entities.items())],
            "effects":[[list(k),v] for k,v in sorted(self.effects.items())],
            "seen":[[list(k[0]),k[1],list(v)] for k,v in sorted(self.seen.items())],
            "conflicts":[[list(b),s] for b,s in sorted(self.conflicts)]
        }
        raw=canonical(payload)
        if len(raw)>8000000:
            raise OverflowError("snapshot cap")
        return canonical({"payload":payload,"sha256":sha256(raw.encode("ascii")).hexdigest()})

    @classmethod
    def restore(cls,text):
        if type(text) is not str or len(text)>9000000:
            raise ValueError("invalid snapshot size")
        try:
            obj=json.loads(text)
            if type(obj) is not dict or set(obj)!={"payload","sha256"}:
                raise ValueError("bad envelope")
            p=obj["payload"]
            if (type(p) is not dict or set(p)!={"schema","family","mode","actions",
                    "informative","entities","effects","seen","conflicts"} or
                p["schema"]!="wsp53.sparse-writer.v1" or
                sha256(canonical(p).encode("ascii")).hexdigest()!=obj["sha256"]):
                raise ValueError("bad snapshot payload")
            model=cls(family=p["family"],mode=p["mode"])
            if (type(p["actions"]) is not int or
                not 0<=p["actions"]<=MAX_ACTIONS or
                type(p["informative"]) is not int or
                not 0<=p["informative"]<=p["actions"]):
                raise ValueError("invalid counters")
            for field,width in (("entities",3),("effects",6)):
                table=getattr(model,field)
                if type(p[field]) is not list:
                    raise ValueError("bad table")
                for key,value in p[field]:
                    if (type(key) is not list or len(key)!=width or
                        type(value) is not int or not 0<value<=MAX_ACTIONS):
                        raise ValueError("bad numeric weight")
                    k=tuple(key)
                    if k in table:
                        raise ValueError("duplicate key")
                    table[k]=value
                    if field=="effects":
                        model.by_address[k[:3]][k[3:]]+=value
            if model.numeric_weight_count()>MAX_WEIGHTS:
                raise ValueError("weight cap")
            for b,s,a in p["seen"]:
                key=state(tuple(b),model.family),bits(s)
                if key in model.seen:
                    raise ValueError("duplicate evidence")
                model.seen[key]=state(tuple(a),model.family)
            for b,s in p["conflicts"]:
                key=state(tuple(b),model.family),bits(s)
                if key not in model.seen or key in model.conflicts:
                    raise ValueError("bad conflict")
                model.conflicts.add(key)
            model.actions=p["actions"]
            model.informative=p["informative"]
            if len(model.seen)>model.actions or model.snapshot()!=text:
                raise ValueError("noncanonical snapshot")
            return model
        except (KeyError,TypeError,IndexError,UnicodeError,json.JSONDecodeError) as ex:
            raise ValueError("invalid snapshot") from ex

    def capacity_bits(self):
        return len(self.snapshot().encode("ascii"))*8
