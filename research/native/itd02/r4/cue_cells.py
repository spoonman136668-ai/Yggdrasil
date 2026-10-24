"""Yggdrasil ITD-02 R4 native delayed cue binding and reward-conditioned local cells.

Source-only independent memory learner. Inductive bias: cue/candidate equality;
actual correspondence to reward is acquired exclusively from FIT physical
terminal rewards. Comparison to matched one-bit conventional lookup mandatory.
"""
import hashlib
import json
import math

SCHEMA="yggdrasil.itd02.r4.reward_associative_cue_cells.v1"
TOKENS=("key","ball")

def canon(o):
    return json.dumps(o,sort_keys=True,separators=(",",":"),allow_nan=False).encode()

class CueCells:
    def __init__(self):
        self.cue=None
        self.counts={"match":[0,0],"different":[0,0]}
        self.outcomes=0

    def begin(self,cue):
        if cue not in TOKENS:raise ValueError("R4_UNSUPPORTED_PUBLIC_CUE")
        self.cue=cue

    def end(self):
        self.cue=None

    def _score(self,candidate):
        if candidate not in TOKENS:raise ValueError("R4_NONPUBLIC_CANDIDATE")
        if self.cue not in TOKENS:raise ValueError("R4_CUE_NOT_REMEMBERED")
        k="match" if self.cue==candidate else "different"
        yes,no=self.counts[k]
        return (yes+1)/(yes+no+2)

    def choose(self,top,bottom):
        a=self._score(top);b=self._score(bottom)
        return 0 if a>=b else 1

    def observe(self,selected,reward,terminated):
        if selected not in TOKENS or self.cue not in TOKENS:
            raise ValueError("R4_INVALID_PUBLIC_CAUSAL_OBSERVATION")
        if type(terminated)is not bool or not terminated:
            raise ValueError("R4_NO_PHYSICAL_TERMINAL_OUTCOME")
        if type(reward) not in (int,float) or not math.isfinite(float(reward)) or reward<0 or reward>1:
            raise ValueError("R4_REAL_REWARD_INVALID")
        if self.outcomes>=2**52:raise ValueError("R4_CAUSAL_COUNTER_SATURATED")
        k="match" if self.cue==selected else "different"
        if reward>0:self.counts[k][0]+=1
        else:self.counts[k][1]+=1
        self.outcomes+=1
        self.end()

    def snapshot(self):
        d={"schema":SCHEMA,"cue":self.cue,"counts":self.counts,"outcomes":self.outcomes}
        raw=canon(d)
        return canon({"data":d,"sha256":hashlib.sha256(raw).hexdigest()})

    @classmethod
    def restore(cls,raw):
        if type(raw)is not bytes or not 0<len(raw)<=16384:
            raise ValueError("R4_CHECKPOINT_SIZE")
        try:
            o=json.loads(raw)
            if set(o)!={"data","sha256"}:raise ValueError("R4_CHECKPOINT_ENVELOPE")
            d=o["data"]
            if (set(d)!={"schema","cue","counts","outcomes"}
              or d["schema"]!=SCHEMA
              or hashlib.sha256(canon(d)).hexdigest()!=o["sha256"]
              or d["cue"] not in (*TOKENS,None)
              or set(d["counts"])!={"match","different"}
              or type(d["outcomes"])is not int or not 0<=d["outcomes"]<2**52):
                raise ValueError("R4_CHECKPOINT_AUTH_OR_STRUCT")
            v=cls();v.cue=d["cue"];v.outcomes=d["outcomes"]
            for k,a in d["counts"].items():
                if type(a)is not list or len(a)!=2 or any(type(z)is not int or z<0 or z>2**52 for z in a):
                    raise ValueError("R4_CHECKPOINT_COUNT_STRUCTURE")
                v.counts[k]=a
            if sum(sum(x) for x in v.counts.values())!=v.outcomes:
                raise ValueError("R4_CHECKPOINT_COUNT_TOTAL")
            return v
        except (ValueError,KeyError,TypeError,OverflowError) as e:
            raise ValueError("R4_CHECKPOINT_AUTHENTICATION_FAILED") from e
