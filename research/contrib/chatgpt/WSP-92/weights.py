"""WSP92 raw-character exact-source answer-span mechanism, no language model.

Candidate segmentation uses *source character boundaries* to enumerate spans,
but no learned word vocabulary, transformer, autoregressive token objective or
candidate gradient optimization. Fully trained supervised logistic comparator
receives the same hashed raw-character features and source annotations.
"""
from __future__ import annotations

from functools import lru_cache
import hashlib
import json
import math
import re
import unicodedata

WIDTH=16384
MAX_SPAN_CHARS=55
MAX_SEGMENTS=4
NEGATIVE_PER_QA=12
TRAIN_EPOCHS=60
TRAIN_LR=0.35
TRAIN_L2=0.001
SCHEMA="wsp92.character-span-direct-weight-v1"

def canonical(x:object)->str:
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False)

def hashbin(data:bytes)->int:
    return int.from_bytes(hashlib.blake2s(data,digest_size=4).digest(),"big")%WIDTH

def char_grams(text:str,size:int=3)->tuple[str,...]:
    s=unicodedata.normalize("NFC",text).casefold()
    return tuple(s[i:i+size] for i in range(max(0,len(s)-size+1)))

@lru_cache(maxsize=1024)
def span_candidates(context:str)->tuple[tuple[int,int,str],...]:
    if not isinstance(context,str) or len(context)>1900:
        raise ValueError("source context outside frozen 1900-character limit")
    # Candidate boundaries are explicit Unicode whitespace-delimited source
    # character spans, NOT linguistic tokens for model input or generation.
    chunks=list(re.finditer(r"\S+",context))
    seen=set()
    spans=[]
    for i,match in enumerate(chunks):
        for j in range(i,min(len(chunks),i+MAX_SEGMENTS)):
            a=match.start()
            b=chunks[j].end()
            # Strip boundary punctuation but preserve original char offsets.
            while a<b and context[a] in "([{“‘'\"":
                a+=1
            while b>a and context[b-1] in ".,;:!?)]}”’'\"":
                b-=1
            if not(1<=b-a<=MAX_SPAN_CHARS) or (a,b) in seen:
                continue
            seen.add((a,b))
            spans.append((a,b,context[a:b]))
    return tuple(spans)

@lru_cache(maxsize=2048)
def qanchors(question:str)->tuple[str,...]:
    grams=set(char_grams(question,3))|set(char_grams(question,4))
    return tuple(sorted(grams,key=lambda g:(hashbin(g.encode("utf-8")),g))[:12])

@lru_cache(maxsize=30000)
def features(question:str,context:str,start:int,end:int)->tuple[tuple[int,float],...]:
    if not(0<=start<end<=len(context) and end-start<=MAX_SPAN_CHARS):
        raise ValueError("invalid raw answer span")
    left=context[max(0,start-42):start]
    right=context[end:min(len(context),end+28)]
    answer=context[start:end]
    weights:dict[int,int]={}
    def add(k:bytes,v:int=1):
        idx=hashbin(k)
        weights[idx]=weights.get(idx,0)+v
    for direction,source in ((b"L",left),(b"R",right)):
        normalized=unicodedata.normalize("NFC",source).casefold()
        for n in (3,4,5):
            for i in range(max(0,len(normalized)-n+1)):
                add(direction+bytes((n,))+normalized[i:i+n].encode("utf-8"),1)
    for n in (2,3):
        for g in char_grams(answer,n):
            add(b"A"+bytes((n,))+g.encode("utf-8"),1)
    # Question-conditioning. 12 question character motifs crossed with at
    # most 8 immediate context motifs; neither component is a word/token ID.
    context_near=left[-20:]+right[:12]
    cand=sorted(set(char_grams(context_near,3)),
                key=lambda g:(hashbin(g.encode("utf-8")),g))[:8]
    for qg in qanchors(question):
        for cg in cand:
            add(b"X"+qg.encode("utf-8")+b"\x00"+cg.encode("utf-8"),1)
    add(b"Z"+bytes((min(7,(end-start)//8),)),2)
    add(b"P"+bytes((min(7,start//240),)),1)
    norm=math.sqrt(sum(v*v for v in weights.values()))
    return tuple(sorted((idx,value/norm) for idx,value in weights.items()))

def supervision(question:str,context:str,qa_id:str,truth_start:int,
                truth_text:str)->tuple[tuple[tuple[int,float],...],tuple[tuple[tuple[int,float],...],...]]:
    if (not isinstance(truth_text,str) or not(1<=len(truth_text)<=55) or
        not(0<=truth_start<truth_start+len(truth_text)<=len(context)) or
        context[truth_start:truth_start+len(truth_text)]!=truth_text):
        raise ValueError("supervision must be exact source substring")
    positive=features(question,context,truth_start,truth_start+len(truth_text))
    pool=[(a,b) for a,b,value in span_candidates(context)
          if not(a==truth_start and b==truth_start+len(truth_text))]
    if not pool:
        raise ValueError("source has no negative candidate spans")
    # Negative selection is stable and outcome-independent AFTER excluding
    # the original training annotation. No reserved labels used here.
    order=sorted(pool,key=lambda pair:hashlib.sha256(
        ("WSP92/neg/"+qa_id+"/"+str(pair[0])+":"+str(pair[1])).encode("ascii")).digest())
    negatives=tuple(features(question,context,a,b) for a,b in order[:NEGATIVE_PER_QA])
    return positive,negatives

def copy_source_proof(item:dict,a:int,b:int)->dict:
    return {
        "answer":item["context"][a:b],"start":a,"end":b,
        "qa_id":item["qa_id"],"article_title":item["article_title"],
        "article_url":item["article_url"],
        "context_sha256":item["context_sha256"],
    }

class DirectQuestionSpanWriter:
    def __init__(self):
        self.weights:dict[int,float]={}
        self.observed=0

    def observe(self,item:dict,truth:dict)->None:
        pos,negs=supervision(item["question"],item["context"],item["qa_id"],
                             truth["answer_start"],truth["answer_text"])
        for vec,delta in ((pos,1.0),)+tuple((neg,-1/len(negs)) for neg in negs):
            for idx,value in vec:
                self.weights[idx]=self.weights.get(idx,0.0)+delta*value
        self.observed+=1

    def answer(self,item:dict)->dict|None:
        if (not isinstance(item,dict) or not item.get("question") or
            not isinstance(item.get("context"),str) or not self.weights or
            not item.get("context_sha256") or
            hashlib.sha256(item["context"].encode("utf-8")).hexdigest()!=item["context_sha256"]):
            return None
        found=None
        for a,b,_ in span_candidates(item["context"]):
            feat=features(item["question"],item["context"],a,b)
            score=sum(self.weights.get(idx,0.0)*value for idx,value in feat)
            if found is None or (score,-a,-b)>(found[0],-found[1],-found[2]):
                found=(score,a,b)
        if found is None:
            return None
        # Low signal/source mismatches must not masquerade as knowledge.
        score,a,b=found
        return copy_source_proof(item,a,b) if score>0 else None

    def snapshot(self)->str:
        payload={"weights":{str(k):v for k,v in sorted(self.weights.items())},
                 "observed":self.observed}
        return canonical({"schema":SCHEMA,"payload":payload,
                          "sha256":hashlib.sha256(canonical(payload).encode("ascii")).hexdigest()})

    @classmethod
    def restore(cls,snapshot:str)->"DirectQuestionSpanWriter":
        env=json.loads(snapshot);payload=env.get("payload")
        if (env.get("schema")!=SCHEMA or not isinstance(payload,dict) or
            hashlib.sha256(canonical(payload).encode("ascii")).hexdigest()!=env.get("sha256")):
            raise ValueError("numeric state corruption")
        if type(payload.get("observed")) is not int or payload["observed"]<0:
            raise ValueError("bad supervised count")
        obj=cls();obj.observed=payload["observed"]
        for k,v in payload.get("weights",{}).items():
            if (not k.isdecimal() or str(int(k))!=k or not(0<=int(k)<WIDTH)
                or type(v) is not float or not math.isfinite(v)):
                raise ValueError("invalid numeric weight")
            obj.weights[int(k)]=v
        return obj

class FullyTrainedLogistic:
    def __init__(self):
        self.weights:dict[int,float]={}

    def fit(self,items:list[tuple[dict,dict]])->None:
        self.weights={}
        rows=[supervision(q["question"],q["context"],q["qa_id"],
                          y["answer_start"],y["answer_text"]) for q,y in items]
        for _ in range(TRAIN_EPOCHS):
            for positive,negative in rows:
                for vec,label in ((positive,1.0),)+tuple((n,0.0) for n in negative):
                    z=sum(self.weights.get(idx,0.0)*val for idx,val in vec)
                    pred=1/(1+math.exp(-max(-60,min(60,z))))
                    for idx,value in vec:
                        prior=self.weights.get(idx,0.0)
                        self.weights[idx]=prior+TRAIN_LR*((label-pred)*value-
                                                          TRAIN_L2*prior)

    def answer(self,item:dict)->dict|None:
        if not item.get("context") or not item.get("question"):
            return None
        found=None
        for a,b,_ in span_candidates(item["context"]):
            score=sum(self.weights.get(idx,0.0)*val for idx,val in
                      features(item["question"],item["context"],a,b))
            if found is None or (score,-a,-b)>(found[0],-found[1],-found[2]):
                found=(score,a,b)
        return copy_source_proof(item,found[1],found[2]) if found else None

class RetrievalCharControl:
    """Independent question-context nearest character-gram overlap."""
    def answer(self,item:dict)->dict|None:
        question=set(char_grams(item["question"],3))
        if not question:return None
        best=None
        text=item["context"]
        for a,b,_ in span_candidates(text):
            ctx=text[max(0,a-55):a]+" "+text[b:min(len(text),b+35)]
            gs=set(char_grams(ctx,3))
            score=len(gs & question)/max(1,math.sqrt(len(gs)))
            if best is None or (score,-a,-b)>(best[0],-best[1],-best[2]):
                best=(score,a,b)
        return copy_source_proof(item,best[1],best[2]) if best else None

class SymbolicCueControl:
    """Untrained independent simple anchor: closest source span to question tail."""
    def answer(self,item:dict)->dict|None:
        q=item.get("question","").casefold()
        # Cannot access trained answer annotations.
        cue=q.strip(" ?.!").split(" ")[-1]
        text=item["context"]
        anchor=text.casefold().find(cue) if len(cue)>2 else -1
        pool=span_candidates(text)
        if not pool:return None
        a,b,_=min(pool,key=lambda s:(abs(s[0]-(anchor+len(cue))) if anchor>=0
                                     else s[0],s[0]))
        return copy_source_proof(item,a,b)

class RandomSpanControl:
    def answer(self,item:dict)->dict|None:
        pool=span_candidates(item["context"])
        if not pool:return None
        digest=hashlib.sha256(("WSP92/random/"+item["qa_id"]).encode("ascii")).digest()
        a,b,_=pool[int.from_bytes(digest[:8],"big")%len(pool)]
        return copy_source_proof(item,a,b)
