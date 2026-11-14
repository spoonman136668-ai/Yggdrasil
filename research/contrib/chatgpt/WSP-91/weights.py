"""WSP91 tokenless character-span reader with direct numeric weight edits.

This learner uses a fixed question relation, a retrieved Wikipedia excerpt,
and raw character boundary candidates. No pretrained model, token vocabulary,
next-token generation, or gradient updates in the direct writer.
"""
from __future__ import annotations

from collections import Counter
from functools import lru_cache
import hashlib
import json
import math
import re
import unicodedata

WIDTH = 16384
RELATIONS = ("symbol", "atomic_number")
GRAMS = (3, 4, 5)
SGD_EPOCHS = 160
SGD_RATE = 0.75
SGD_L2 = 0.001
SNAPSHOT_SCHEMA = "wsp91.direct-numeric-span-reader.v1"

def canonical(value: object) -> str:
    return json.dumps(value,sort_keys=True,separators=(",",":"),
                      ensure_ascii=True,allow_nan=False)

def spans(text: str, relation: str) -> tuple[tuple[int,int,str], ...]:
    if not isinstance(text,str) or len(text)>2400:
        raise ValueError("bounded article excerpt required")
    if relation not in RELATIONS:
        return ()
    out=[]
    is_field=(lambda c:c.isascii() and c.isalpha()) if relation=="symbol" else (
        lambda c:c.isascii() and c.isdigit())
    for start,char in enumerate(text):
        if not is_field(char) or (start>0 and is_field(text[start-1])):
            continue
        end=start
        while end<len(text) and is_field(text[end]):
            end+=1
        value=text[start:end]
        if 1<=len(value)<=(2 if relation=="symbol" else 3):
            out.append((start,end,value))
    return tuple(out)

@lru_cache(maxsize=8192)
def raw_context(text: str, relation: str, start: int, end: int)->tuple[tuple[int,float],...]:
    if relation not in RELATIONS or not(0<=start<end<=len(text)):
        raise ValueError("bad span/relation")
    local=unicodedata.normalize("NFC",
        text[max(0,start-48):start]+"\u241a"+text[end:min(len(text),end+24)]).casefold()
    counts: Counter[int]=Counter()
    for n in GRAMS:
        for i in range(max(0,len(local)-n+1)):
            item=bytes((n,))+local[i:i+n].encode("utf-8")
            idx=int.from_bytes(hashlib.blake2s(item,digest_size=4).digest(),"big")%WIDTH
            counts[idx]+=1
    # Preserve relative cue position without lexical word tokens.
    pivot=local.index("\u241a")
    for n in (3,4):
        for gap in (0,2,4,6,8):
            left=local[max(0,pivot-gap-n):max(0,pivot-gap)]
            if len(left)==n:
                frag=b"\xf1"+bytes((gap,n))+left.encode("utf-8")
                idx=int.from_bytes(hashlib.blake2s(frag,digest_size=4).digest(),"big")%WIDTH
                counts[idx]+=3
    norm=math.sqrt(sum(k*k for k in counts.values()))
    return tuple(sorted((i,float(v)/norm) for i,v in counts.items()))

def document_candidates(text: str, relation: str):
    return tuple((start,end,value,raw_context(text,relation,start,end))
                 for start,end,value in spans(text,relation))

def learning_examples(text: str, relation: str, truth: str):
    pool=document_candidates(text,relation)
    positives=[v for v in pool if v[2]==truth]
    negatives=[v for v in pool if v[2]!=truth]
    # Correct answer must be a raw substring in the source; never invent it.
    if not positives:
        raise ValueError("grounded training answer not located in source")
    # Every negative candidate is seen with the same information as the
    # conventional control; no matching answer is externally provided in DEV.
    return tuple((vec,1 if val==truth else 0) for _,_,val,vec in pool)

class DirectSpanWriter:
    def __init__(self)->None:
        self.weights={relation:{} for relation in RELATIONS}
        self.observed_fields=0

    def observe(self,text:str,relation:str,answer:str)->None:
        if relation not in RELATIONS or not isinstance(answer,str):
            raise ValueError("invalid supervised factual answer")
        pairs=learning_examples(text,relation,answer)
        pos=[vec for vec,y in pairs if y]
        neg=[vec for vec,y in pairs if not y]
        if not neg:
            raise ValueError("no source-negative candidates")
        row=self.weights[relation]
        # Equal positive/negative total mass avoids easy class-imbalance wins.
        for examples,sign in ((pos,1.0),(neg,-1.0)):
            for vec in examples:
                for idx,value in vec:
                    row[idx]=row.get(idx,0.0)+sign*value/len(examples)
        self.observed_fields+=1

    def scores(self,text:str,relation:str)->tuple[tuple[float,int,int,str],...]:
        if relation not in RELATIONS:
            return ()
        row=self.weights[relation]
        if self.observed_fields==0 or not row:
            return ()
        return tuple((sum(row.get(i,0.0)*v for i,v in vec),start,end,val)
                     for start,end,val,vec in document_candidates(text,relation))

    def extract(self,article:dict,relation:str)->dict|None:
        if relation not in RELATIONS or not isinstance(article,dict):
            return None
        text=article.get("text")
        if not isinstance(text,str):
            return None
        scores=self.scores(text,relation)
        if not scores:
            return None
        score,start,end,value=max(scores,key=lambda p:(p[0],-p[1],-p[2]))
        if score<=0:
            return None
        return {"value":value,"start":start,"end":end,
                "page_id":article["page_id"],
                "reported_revision_id":article["reported_revision_id"],
                "source_page_url":article["source_page_url"],
                "source_text_sha256":article["text_sha256"]}

    def snapshot(self)->str:
        payload={"weights":{rel:{str(i):v for i,v in sorted(row.items())}
                            for rel,row in self.weights.items()},
                 "observed_fields":self.observed_fields}
        body=canonical(payload)
        return canonical({"schema":SNAPSHOT_SCHEMA,"payload":payload,
                          "sha256":hashlib.sha256(body.encode("ascii")).hexdigest()})

    @classmethod
    def restore(cls,snapshot:str)->"DirectSpanWriter":
        env=json.loads(snapshot)
        if env.get("schema")!=SNAPSHOT_SCHEMA:
            raise ValueError("unknown weight-source schema")
        payload=env.get("payload")
        if not isinstance(payload,dict) or (
           hashlib.sha256(canonical(payload).encode("ascii")).hexdigest()!=env.get("sha256")):
            raise ValueError("cold weight snapshot altered")
        if set(payload.get("weights",{}))!=set(RELATIONS) or (
            type(payload.get("observed_fields")) is not int or
            payload["observed_fields"]<0):
            raise ValueError("malformed snapshot")
        x=cls()
        x.observed_fields=payload["observed_fields"]
        for relation,row in payload["weights"].items():
            if not isinstance(row,dict):
                raise ValueError("malformed weight row")
            for key,value in row.items():
                if (not key.isdecimal() or str(int(key))!=key or
                    not 0<=int(key)<WIDTH or
                    type(value) is not float or not math.isfinite(value)):
                    raise ValueError("nonfinite or invalid weight")
                x.weights[relation][int(key)]=value
        return x

    def occupied_weights(self)->int:
        return sum(len(row) for row in self.weights.values())

class TrainedSpanLogistic:
    """Converged linear logistic span ranker on exactly same source contexts."""

    def __init__(self):
        self.weights={relation:{} for relation in RELATIONS}
        self.train_exact=0

    def fit(self,rows:tuple[tuple[str,str,str], ...])->None:
        cached={relation:[] for relation in RELATIONS}
        for text,relation,truth in rows:
            cached[relation].extend(learning_examples(text,relation,truth))
        self.weights={relation:{} for relation in RELATIONS}
        for relation in RELATIONS:
            observations=cached[relation]
            if not observations:
                raise ValueError("no training source observations")
            w=self.weights[relation]
            for _ in range(SGD_EPOCHS):
                for vec,target in observations:
                    z=sum(w.get(idx,0.0)*val for idx,val in vec)
                    probability=1/(1+math.exp(-max(-80,min(80,z))))
                    for idx,val in vec:
                        previous=w.get(idx,0.0)
                        w[idx]=previous+SGD_RATE*((target-probability)*val-
                                                   SGD_L2*previous)
        # Exact training fit is evaluated at source/question level in the
        # comparison harness, not at skewed individual span accuracy.

    def extract(self,article:dict,relation:str)->dict|None:
        text=article["text"]
        scored=((sum(self.weights[relation].get(i,0.0)*v for i,v in vec),
                 start,end,value)
                for start,end,value,vec in document_candidates(text,relation))
        try:
            _,start,end,value=max(scored,key=lambda p:(p[0],-p[1],-p[2]))
        except ValueError:
            return None
        return {"value":value,"start":start,"end":end,
                "page_id":article["page_id"],"reported_revision_id":article["reported_revision_id"],
                "source_page_url":article["source_page_url"],"source_text_sha256":article["text_sha256"]}

class SymbolicParser:
    def extract(self,article:dict,relation:str)->dict|None:
        text=article["text"]
        patterns={
            "symbol":r"\b(?:chemical\s+)?symbol\s+([A-Z][a-z]?)\b",
            "atomic_number":r"\batomic\s+number\s+([0-9]{1,3})\b",
        }
        if relation not in patterns:
            return None
        match=re.search(patterns[relation],text,re.IGNORECASE)
        if not match:
            return None
        start,end=match.span(1)
        return {"value":text[start:end],"start":start,"end":end,
                "page_id":article["page_id"],"reported_revision_id":article["reported_revision_id"],
                "source_page_url":article["source_page_url"],"source_text_sha256":article["text_sha256"]}

class LexicalCue:
    def extract(self,article:dict,relation:str)->dict|None:
        text=article["text"]
        anchor="symbol" if relation=="symbol" else "atomic number"
        if relation not in RELATIONS:
            return None
        cue=text.casefold().find(anchor)
        pool=[s for s in spans(text,relation) if s[0]>=cue+len(anchor)] if cue>=0 else []
        if not pool:
            return None
        start,end,value=min(pool,key=lambda s:s[0])
        return {"value":value,"start":start,"end":end,
                "page_id":article["page_id"],"reported_revision_id":article["reported_revision_id"],
                "source_page_url":article["source_page_url"],"source_text_sha256":article["text_sha256"]}
