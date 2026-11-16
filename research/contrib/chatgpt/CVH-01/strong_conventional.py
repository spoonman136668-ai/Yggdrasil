"""CVH-01 independent conventional batch n-step return-to-go estimator.

Uses exactly the same observed public events as EarnedReturnMemory but
constructs finite-horizon returns by scanning completed and open episodes
after observation. No import of candidate model, source, or future oracle.
"""
from __future__ import annotations

def batch_public_returns(events):
    if type(events) not in (tuple,list):
        raise ValueError("CVH01_BATCH_SOURCE_TYPE")
    counts=[0]*36
    totals=[0]*36
    current=[]
    prior_action=2
    prior_reward=2
    after=None

    def close(episode,complete):
        # An unended episode has no supported full-horizon return for its
        # last three actions; ended episodes have actual shorter returns.
        for i,(row,key) in enumerate(episode):
            if not complete and len(episode)-i<4:
                continue
            units=0
            for lag in range(min(4,len(episode)-i)):
                units+=episode[i+lag][0].reward*(8>>lag)
            counts[key]+=1
            totals[key]+=units

    for row in events:
        if tuple(getattr(row,"_fields",())) != (
            "before","action","reward","after","terminated","truncated"):
            raise ValueError("CVH01_BATCH_PUBLIC_SCHEMA")
        b,a,r,n,done,truncated=row
        if (any(type(x) is not int or x not in (0,1) for x in (b,a,r,n)) or
            type(done) is not bool or type(truncated) is not bool or
            (done and truncated) or (after is not None and b!=after)):
            raise ValueError("CVH01_BATCH_INVALID_PUBLIC")
        # Independent two-prefix/trial-state key, no learner implementation used.
        key=(((prior_action*3+prior_reward)*2+b)*2+a)
        current.append((row,key))
        if done or truncated:
            close(current,True)
            current=[]
            prior_action=prior_reward=2
            after=None
        else:
            prior_action=a
            prior_reward=r
            after=n
    close(current,False)
    return counts,totals

def immediate_only_public_returns(events):
    """Same observed features but deliberately ablate future reward credit."""
    counts=[0]*36;totals=[0]*36
    prev_a=prev_r=2
    after=None
    for row in events:
        if tuple(getattr(row,"_fields",()))!=(
            "before","action","reward","after","terminated","truncated"):
            raise ValueError("CVH01_IMMEDIATE_BAD_PUBLIC")
        b,a,r,n,d,t=row
        if any(type(x) is not int or x not in (0,1) for x in (b,a,r,n)):
            raise ValueError("CVH01_IMMEDIATE_NONBINARY")
        if type(d) is not bool or type(t) is not bool or (d and t):
            raise ValueError("CVH01_IMMEDIATE_BAD_TERMINAL")
        if after is not None and b!=after:
            raise ValueError("CVH01_IMMEDIATE_CONTINUITY")
        k=(((prev_a*3+prev_r)*2+b)*2+a)
        counts[k]+=1;totals[k]+=8*r
        if d or t:
            prev_a=prev_r=2;after=None
        else:
            prev_a=a;prev_r=r;after=n
    return counts,totals
