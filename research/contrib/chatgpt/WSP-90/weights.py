"""Direct raw-character weight editing for bounded Wikipedia prose-reading pilot.

No tokens, language model, gradients or pretrained representation in candidate.
The experiment supplies (article title, query country, captured raw prose).
"""
from __future__ import annotations

from collections import Counter
from functools import lru_cache
import hashlib
import json
import math
import re
import unicodedata

WIDTH = 16_384
GRAMS = (3, 4, 5)
SGD_EPOCHS = 120
SGD_LR = 1.0
SGD_L2 = 0.01
ABSTAIN_MARGIN = 0.02
SCHEMA = "wsp90.prose-character-direct-weights.v1"

def canonical(x: object) -> str:
    return json.dumps(x,sort_keys=True,separators=(",",":"),
                      ensure_ascii=True,allow_nan=False)

def normalized(s: str) -> str:
    return unicodedata.normalize("NFC", s).casefold()

def masked(text: str, city: str, country: str) -> str:
    if not all(isinstance(v,str) and len(v)>1 for v in (text,city,country)):
        raise ValueError("nonempty grounded source/city/country required")
    # Replace named mentions by raw-character placeholders; no lexical token
    # inventory. This intentionally makes general phrasing, not entity names,
    # available to the learned weights.
    s=normalized(text)
    name=normalized(city).split(",")[0].strip()
    for string, marker in sorted(((name, "\u2413"),
                                   (normalized(country), "\u2414")),
                                  key=lambda p:-len(p[0])):
        s=s.replace(string, marker)
    return s[:1350]

def has_country_evidence(text: str, country: str) -> bool:
    return normalized(country) in normalized(text)

@lru_cache(maxsize=256)
def features(text: str, city: str, country: str) -> tuple[tuple[int,float],...]:
    s=masked(text,city,country)
    if len(s)<30 or len(s)>1350:
        raise ValueError("lead excerpt outside bounded source")
    counts: Counter[int]=Counter()
    def grams(stream: str, multiplier: int):
        for n in GRAMS:
            for start in range(max(0,len(stream)-n+1)):
                raw=bytes([n])+stream[start:start+n].encode("utf-8")
                idx=int.from_bytes(hashlib.blake2s(raw,digest_size=4).digest(),"big")%WIDTH
                counts[idx]+=multiplier
    # Local context around occurrences of country is provided identically
    # to all methods, to reduce remote-name memorization.
    grams(s, 1)
    for pos,ch in enumerate(s):
        if ch=="\u2414":
            grams(s[max(0,pos-75):min(len(s),pos+75)],3)
    scale=math.sqrt(sum(v*v for v in counts.values()))
    if not scale:
        return ()
    return tuple(sorted((idx,weight/scale) for idx,weight in counts.items()))

class DirectWriter:
    def __init__(self)->None:
        self.weights:dict[int,float]={}
        self.observations=0

    def observe(self,text:str,city:str,country:str,is_national_capital:bool)->None:
        if type(is_national_capital) is not bool:
            raise ValueError("boolean feedback required")
        polarity=1 if is_national_capital else -1
        for index,value in features(text,city,country):
            self.weights[index]=self.weights.get(index,0.0)+polarity*value
        self.observations+=1

    def score(self,text:str,city:str,country:str)->float|None:
        if not has_country_evidence(text,country):
            return None
        return sum(self.weights.get(i,0.0)*v for i,v in features(text,city,country))

    def choose(self,country:str,candidates:tuple[dict,dict])->str|None:
        if len(candidates)!=2 or len({x["requested_title"] for x in candidates})!=2:
            raise ValueError("exactly two distinct source pages required")
        scored=[]
        for source in candidates:
            s=self.score(source["text"],source["requested_title"],country)
            scored.append((s,source["requested_title"]))
        if any(s is None for s,_ in scored):
            return None
        ranked=sorted(scored,key=lambda x:(-x[0],x[1]))
        return (ranked[0][1] if
                ranked[0][0]-ranked[1][0]>=ABSTAIN_MARGIN
                else None)

    def snapshot(self)->str:
        payload={"weights":{str(k):v for k,v in sorted(self.weights.items())},
                 "observations":self.observations}
        body=canonical(payload)
        return canonical({"schema":SCHEMA,"payload":payload,
                          "sha256":hashlib.sha256(body.encode("ascii")).hexdigest()})

    @classmethod
    def restore(cls,snap:str)->"DirectWriter":
        env=json.loads(snap)
        if env.get("schema")!=SCHEMA:
            raise ValueError("invalid model snapshot schema")
        payload=env.get("payload")
        if (not isinstance(payload,dict) or
            hashlib.sha256(canonical(payload).encode("ascii")).hexdigest()!=env.get("sha256")):
            raise ValueError("tampered numerical snapshot")
        w=payload.get("weights")
        if not isinstance(w,dict) or type(payload.get("observations")) is not int:
            raise ValueError("invalid snapshot fields")
        candidate=cls()
        for key,value in w.items():
            idx=int(key)
            if (not 0<=idx<WIDTH or str(idx)!=key or
                type(value) is not float or not math.isfinite(value)):
                raise ValueError("malformed numerical weight")
            candidate.weights[idx]=value
        candidate.observations=payload["observations"]
        return candidate

class TrainedLogistic:
    """Fully trained ordinary SGD control using identical feature vectors."""
    def __init__(self)->None:
        self.weights:dict[int,float]={}
        self.train_accuracy:float=0.0

    def fit(self,examples:list[tuple[str,str,str,bool]])->None:
        self.weights={}
        cached=[(features(t,c,k),int(y)) for t,c,k,y in examples]
        if not cached:
            raise ValueError("empty labeled training data")
        for _ in range(SGD_EPOCHS):
            for vec,target in cached:
                z=sum(self.weights.get(i,0.0)*v for i,v in vec)
                pred=1/(1+math.exp(-max(-80,min(80,z))))
                for idx,value in vec:
                    old=self.weights.get(idx,0.0)
                    self.weights[idx]=old+SGD_LR*((target-pred)*value-SGD_L2*old)
        self.train_accuracy=sum((self.score(t,c,k)>=0)==y for t,c,k,y in examples)/len(examples)

    def score(self,text:str,city:str,country:str)->float:
        return sum(self.weights.get(i,0.0)*v for i,v in features(text,city,country))

    def choose(self,country:str,candidates:tuple[dict,dict])->str:
        return max((x["requested_title"] for x in candidates),
                   key=lambda title:(self.score(next(x["text"] for x in candidates
                                                     if x["requested_title"]==title),
                                          title,country),title))

class LexicalParserControl:
    """Independent hand-written, country-conditional national-capital cue."""
    def score(self,text:str,city:str,country:str)->float:
        s=normalized(text)
        country=normalized(country)
        if country not in s:
            return -100.0
        found=list(re.finditer(r"\bcapital\b",s))
        result=0.0
        for match in found:
            tail=s[match.end():match.end()+110]
            if country in tail:
                result=max(result, 2.0-0.002*tail.index(country))
            else:
                result=max(result,0.1)
        return result

    def choose(self,country:str,candidates:tuple[dict,dict])->str:
        return max((x["requested_title"] for x in candidates),
                   key=lambda city:(self.score(next(x["text"] for x in candidates
                                                     if x["requested_title"]==city),
                                          city,country),city))

class RetrievalControl:
    """Conventional lexical retrieval; can tokenize, unlike candidate."""
    @staticmethod
    def terms(s:str)->set[str]:
        return set(re.findall(r"[\w]+",normalized(s)))

    def score(self,text:str,city:str,country:str)->float:
        query=self.terms("capital city of "+country)
        excerpt=self.terms(text)
        return len(query & excerpt)/math.sqrt(max(1,len(excerpt)))

    def choose(self,country:str,candidates:tuple[dict,dict])->str:
        return max((x["requested_title"] for x in candidates),
                   key=lambda city:(self.score(next(x["text"] for x in candidates
                                                     if x["requested_title"]==city),
                                          city,country),city))
