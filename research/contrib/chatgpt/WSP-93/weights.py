"""WSP93 explicit raw-character question->source evidence binding program.

The candidate does NOT learn a bag of hashed answer-context trigrams. It edits
interpretable operator weights joining (question intent, source shared-anchor,
relative direction, answer shape). It emits a cited raw substring, not tokens.
"""
from __future__ import annotations

from collections import Counter
from functools import lru_cache
import hashlib
import json
import math
import re
import unicodedata

MAX_CHARS=55
SPAN_LIMIT=4
SCHEMA="wsp93.direct-question-evidence-binding-v1"
EPOCHS=120
LEARNING_RATE=0.5
L2=0.002

def canonical(x:object)->str:
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False)

def digest(x:object)->str:
    return hashlib.sha256(canonical(x).encode("ascii")).hexdigest()

@lru_cache(maxsize=512)
def spans(text:str)->tuple[tuple[int,int,str],...]:
    if not isinstance(text,str) or len(text)>1900:
        raise ValueError("source article out of protocol")
    runs=list(re.finditer(r"\S+",text))
    out=[];seen=set()
    for i,match in enumerate(runs):
        for j in range(i,min(len(runs),i+SPAN_LIMIT)):
            a=match.start();b=runs[j].end()
            while a<b and text[a] in "([{“‘'\"":a+=1
            while b>a and text[b-1] in ".,;:!?)]}”’'\"":b-=1
            if not(1<=b-a<=MAX_CHARS) or (a,b) in seen:continue
            seen.add((a,b));out.append((a,b,text[a:b]))
    return tuple(out)

def intent(question:str)->str:
    q=unicodedata.normalize("NFC",question).strip().casefold()
    for prefix in ("how many","how much","who","when","where","which","why","how","what"):
        if q.startswith(prefix+" ") or q.startswith(prefix+"?"):
            return prefix.replace(" ","_")
    return "other"

def shape(text:str)->str:
    if not text:return "empty"
    chars=[c for c in text if c.isalnum()]
    if not chars:return "punctuation"
    if all(c.isdigit() for c in chars):return "numeric"
    if any(c.isdigit() for c in chars):return "mixed_digit"
    if text.isupper() and len(text)<=8:return "acronym"
    if text[0].isupper() and any(c.islower() for c in chars):return "proper"
    return "lower"

def source_signature(row:dict)->bool:
    if not isinstance(row,dict):return False
    context=row.get("context")
    return (isinstance(context,str) and 60<=len(context)<=1900 and
            isinstance(row.get("question"),str) and bool(row["question"].strip())
            and isinstance(row.get("qa_id"),str) and
            hashlib.sha256(context.encode("utf-8")).hexdigest()==row.get("context_sha256"))

@lru_cache(maxsize=1024)
def anchors(question:str,context:str)->tuple[tuple[int,int,str],...]:
    """Source character positions shared with the question, not word IDs.

    Long rare letter fragments outrank repeated short phrases. The binding
    operator reads these source indices; no answer identity is used.
    """
    q=unicodedata.normalize("NFC",question).casefold()
    s=unicodedata.normalize("NFC",context).casefold()
    fragments=set()
    for n in (6,5,4):
        for i in range(max(0,len(q)-n+1)):
            frag=q[i:i+n]
            if len(frag)==n and sum(c.isalpha() for c in frag)>=n-1:
                fragments.add(frag)
    ranked=sorted((f for f in fragments if f in s),
                  key=lambda f:(-len(f),s.count(f),f))[:24]
    found=[]
    for f in ranked:
        start=0
        while len(found)<64:
            p=s.find(f,start)
            if p<0:break
            found.append((p,p+len(f),f))
            start=p+len(f)
    return tuple(sorted(set(found),key=lambda x:(x[0],x[1],x[2])))

@lru_cache(maxsize=32000)
def features(question:str,context:str,a:int,b:int,ablate:bool=False)->tuple[str,...]:
    if not(0<=a<b<=len(context)):
        raise ValueError("invalid candidate offsets")
    value=context[a:b]
    sh=shape(value)
    lg=min(4,(b-a)//12)
    # Baseline shape and span length are independent of the question.
    f=["shape:"+sh,"size:"+str(lg),"shape_size:"+sh+"/"+str(lg)]
    if ablate:
        return tuple(f)
    typ=intent(question)
    found=anchors(question,context)
    # Explicitly match source anchor to candidate start (evidence binding).
    # Reject anchors wholly inside the candidate itself.
    scored=[]
    for start,end,fragment in found:
        if start>=a and end<=b:
            continue
        gap=(a-end) if end<=a else ((start-b) if start>=b else 0)
        side="after" if end<=a else ("before" if start>=b else "overlap")
        scored.append((abs(gap),start,side,fragment))
    if scored:
        gap,_,side,_=min(scored,key=lambda x:(x[0],x[1]))
        distance="0_12" if gap<=12 else ("13_35" if gap<=35 else (
                 "36_85" if gap<=85 else ("86_160" if gap<=160 else "far")))
    else:
        side="no_anchor";distance="none"
    local=context[max(0,a-10):a].casefold()
    # Anchored structural connectors use literal character cues; they are
    # NOT model tokens and are not predicted or reconstructed.
    if local.endswith(" by "):connector="by"
    elif local.endswith(" in "):connector="in"
    elif local.endswith(" at "):connector="at"
    elif local.endswith(" to "):connector="to"
    elif local.endswith(" of "):connector="of"
    elif local.endswith(" on "):connector="on"
    elif local.endswith(" is "):connector="is"
    elif local.endswith(" was "):connector="was"
    else:connector="none"
    f.extend([
        "question:"+typ,"intent_shape:"+typ+"/"+sh,
        "anchor_side:"+side,"anchor_distance:"+distance,
        "operator:"+typ+"/"+side+"/"+distance,
        "binding:"+typ+"/"+sh+"/"+side+"/"+distance,
        "intent_connector:"+typ+"/"+connector,
        "pointer_connector:"+typ+"/"+side+"/"+connector,
    ])
    return tuple(f)

def proof(row:dict,a:int,b:int)->dict:
    return {"answer":row["context"][a:b],"start":a,"end":b,
            "qa_id":row["qa_id"],"article_title":row["article_title"],
            "article_url":row["article_url"],
            "context_sha256":row["context_sha256"]}

def train_pairs(row:dict,gold:dict)->tuple[tuple[str,...],tuple[tuple[str,...],...]]:
    a=gold.get("answer_start");value=gold.get("answer_text")
    if (type(a) is not int or not isinstance(value,str) or
        row["context"][a:a+len(value)]!=value):
        raise ValueError("annotation must match exact source offsets")
    gold_end=a+len(value)
    if not any(x==a and y==gold_end for x,y,_ in spans(row["context"])):
        raise ValueError("source answer not reachable by frozen candidate spans")
    positive=features(row["question"],row["context"],a,gold_end)
    choices=[(x,y) for x,y,_ in spans(row["context"]) if (x,y)!=(a,gold_end)]
    ordered=sorted(choices,key=lambda v:hashlib.sha256(
        ("WSP93/negative/"+row["qa_id"]+"/"+str(v[0])).encode("ascii")).digest())
    negatives=tuple(features(row["question"],row["context"],x,y)
                    for x,y in ordered[:12])
    if not negatives:raise ValueError("no distinct negative source candidates")
    return positive,negatives

class DirectBinding:
    def __init__(self):
        self.weights:dict[str,float]={}
        self.observed=0
        self.skipped_unreachable=0

    def observe(self,row:dict,gold:dict)->None:
        if not source_signature(row):raise ValueError("unverified source context")
        try:
            positive,negatives=train_pairs(row,gold)
        except ValueError as error:
            if "not reachable" in str(error):
                self.skipped_unreachable+=1
                return
            raise
        for key in positive:
            self.weights[key]=self.weights.get(key,0.0)+1.0
        for neg in negatives:
            for key in neg:
                self.weights[key]=self.weights.get(key,0.0)-1.0/len(negatives)
        self.observed+=1

    def answer(self,row:dict,*,ablate:bool=False)->dict|None:
        if not source_signature(row) or not self.weights:
            return None
        text=row["context"];q=row["question"]
        best=None
        for a,b,_ in spans(text):
            score=sum(self.weights.get(k,0.0) for k in features(q,text,a,b,ablate))
            key=(score,-a,-(b-a))
            if best is None or key>best[0]:
                best=(key,a,b)
        if best is None or best[0][0]<=0:
            return None
        return proof(row,best[1],best[2])

    def snapshot(self)->str:
        payload={"weights":dict(sorted(self.weights.items())),
                 "observed":self.observed,"skipped_unreachable":self.skipped_unreachable}
        return canonical({"schema":SCHEMA,"payload":payload,"sha256":digest(payload)})

    @classmethod
    def restore(cls,value:str)->"DirectBinding":
        env=json.loads(value);data=env.get("payload")
        if env.get("schema")!=SCHEMA or not isinstance(data,dict) or digest(data)!=env.get("sha256"):
            raise ValueError("invalid or altered program snapshot")
        obj=cls()
        if (type(data.get("observed")) is not int or
            type(data.get("skipped_unreachable")) is not int or
            min(data["observed"],data["skipped_unreachable"])<0):
            raise ValueError("bad source observations")
        obj.observed=data["observed"];obj.skipped_unreachable=data["skipped_unreachable"]
        for k,v in data.get("weights",{}).items():
            if not isinstance(k,str) or type(v) is not float or not math.isfinite(v):
                raise ValueError("invalid operator weight")
            obj.weights[k]=v
        return obj

class ConventionalLogistic:
    """Gradient-trained ordinary comparator on exactly the same operator keys."""
    def __init__(self):
        self.weights:dict[str,float]={}
        self.used=0

    def fit(self,pairs:list[tuple[dict,dict]]):
        samples=[]
        for row,gold in pairs:
            try:pos,negs=train_pairs(row,gold)
            except ValueError as exc:
                if "not reachable" in str(exc):continue
                raise
            samples.append((pos,negs))
        self.used=len(samples)
        weights={}
        for epoch in range(EPOCHS):
            for pos,negs in samples:
                for f,y in ((pos,1),)+tuple((n,0) for n in negs):
                    z=sum(weights.get(k,0.0) for k in f)
                    pred=1/(1+math.exp(-max(-40,min(40,z))))
                    for key in f:
                        old=weights.get(key,0.0)
                        weights[key]=old+LEARNING_RATE*((y-pred)-L2*old)
        self.weights=weights

    def answer(self,row:dict)->dict|None:
        if not source_signature(row) or not self.weights:return None
        best=None
        for a,b,_ in spans(row["context"]):
            score=sum(self.weights.get(k,0.0) for k in
                      features(row["question"],row["context"],a,b))
            cand=(score,-a,-(b-a))
            if best is None or cand>best[0]:best=(cand,a,b)
        return proof(row,best[1],best[2]) if best else None

class AnchorRetrieval:
    def answer(self,row:dict)->dict|None:
        if not source_signature(row):return None
        q,c=row["question"],row["context"]
        found=anchors(q,c);pool=spans(c)
        if not found or not pool:return None
        def metric(item):
            a,b,_=item
            distances=[min(abs(a-e),abs(b-s)) for s,e,_ in found
                       if not(s>=a and e<=b)]
            return (min(distances) if distances else 9999,a,b)
        a,b,_=min(pool,key=metric)
        return proof(row,a,b)

class SymbolicTypeControl:
    def answer(self,row:dict)->dict|None:
        if not source_signature(row):return None
        q,c=row["question"],row["context"]
        it=intent(q);found=anchors(q,c)
        pool=spans(c)
        if not pool:return None
        def rank(item):
            a,b,v=item
            sh=shape(v)
            pref= (sh=="numeric") if it in ("when","how_many","how_much") else (
                sh in ("proper","acronym") if it in ("who","where") else True)
            near=min([abs(a-e) for _,e,_ in found]+[1000])
            return (0 if pref else 1,near,a)
        a,b,_=min(pool,key=rank)
        return proof(row,a,b)

class RandomCandidate:
    def answer(self,row:dict)->dict|None:
        if not source_signature(row):return None
        pool=spans(row["context"])
        if not pool:return None
        n=int.from_bytes(hashlib.sha256(("WSP93/random/"+row["qa_id"]).encode("ascii")).digest()[:8],"big")
        a,b,_=pool[n%len(pool)]
        return proof(row,a,b)
