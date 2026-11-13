"""Separately implemented conventional exact Bayesian causal-graph learner.

Uniform prior over 16 four-bit dependency masks × two signs per action.
Uniform posterior over compatible hypotheses. Shannon entropy selects the
next public intervention, no import of the HC07 candidate implementation.
"""
from __future__ import annotations

import hashlib
import json
import math

N_ACTIONS=4
NUM_RULES=32
ALL=(1<<NUM_RULES)-1
MAX_BYTES=1024
SCHEMA="ygg.dg1-hc07.bayesian-graph-control.v1"


def valid_state(state):
    if type(state) is not int or not 0<=state<=15:
        raise ValueError("HC07_BAYES_BAD_STATE")
    return state


def valid_action(action):
    if type(action) is not int or action not in range(N_ACTIONS):
        raise ValueError("HC07_BAYES_BAD_ACTION")
    return action


def predicts_effect(state,rule):
    valid_state(state)
    if type(rule) is not int or rule<0 or rule>=NUM_RULES:
        raise ValueError("HC07_BAYES_BAD_RULE")
    selected=rule//2
    bit=rule%2
    parity=0
    for k in range(4):
        if selected & (1<<k):
            parity^=(state>>k)&1
    return parity^bit


def posterior_support(mask,public_state,effect):
    surviving=0
    for index in range(NUM_RULES):
        if mask & (1<<index):
            if predicts_effect(public_state,index)==effect:
                surviving|=1<<index
    return surviving


def effect_counts(mask,state):
    z=o=0
    for index in range(NUM_RULES):
        if mask & (1<<index):
            if predicts_effect(state,index):
                o+=1
            else:
                z+=1
    return z,o


def shannon(mask,state):
    z,o=effect_counts(mask,state)
    total=z+o
    if not total:
        return 0.0
    value=0.0
    for mass in (z,o):
        if mass:
            q=mass/total
            value-=q*math.log2(q)
    return value


def encoded(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),
                      allow_nan=False).encode("ascii")


class BayesianGraphController:
    def __init__(self):
        self.posterior_masks=[ALL,ALL,ALL,ALL]
        self.events=0
        self.incompatible_events=0

    @property
    def capacity_bits(self):
        return 128

    def choose(self,state):
        valid_state(state)
        scores=[shannon(self.posterior_masks[a],state) for a in range(4)]
        return max(range(4),key=lambda a:(scores[a],-a))

    def observe(self,before,action,after):
        valid_state(before)
        valid_action(action)
        valid_state(after)
        if after not in (before,before^(1<<action)):
            raise ValueError("HC07_BAYES_BAD_OUTCOME")
        effect=int(before!=after)
        mask=self.posterior_masks[action]
        new=posterior_support(mask,before,effect)
        if mask and not new:
            self.incompatible_events+=1
        self.posterior_masks[action]=new
        self.events+=1

    def predict(self,state,action):
        valid_state(state)
        valid_action(action)
        z,o=effect_counts(self.posterior_masks[action],state)
        if (z and o) or not (z or o):
            return None
        return state^((1 if o else 0)<<action)

    def evidence_support(self):
        return [x.bit_count() for x in self.posterior_masks]

    def snapshot(self):
        p={"schema":SCHEMA,"posterior_masks":self.posterior_masks,
           "events":self.events,"incompatible_events":self.incompatible_events}
        b=encoded({"payload":p,"sha256":hashlib.sha256(encoded(p)).hexdigest()})
        if len(b)>MAX_BYTES:
            raise ValueError("HC07_BAYES_TOO_LARGE")
        return b

    @classmethod
    def restore(cls,data):
        if type(data) is not bytes or not 0<len(data)<=MAX_BYTES:
            raise ValueError("HC07_BAYES_BAD_CHECKPOINT")
        try:
            doc=json.loads(data)
            if type(doc) is not dict or set(doc)!={"payload","sha256"}:
                raise ValueError("HC07_BAYES_BAD_DOCUMENT")
            p=doc["payload"]
            if (type(p) is not dict or
                set(p)!={"schema","posterior_masks","events","incompatible_events"} or
                p["schema"]!=SCHEMA):
                raise ValueError("HC07_BAYES_BAD_SCHEMA")
            if hashlib.sha256(encoded(p)).hexdigest()!=doc["sha256"]:
                raise ValueError("HC07_BAYES_BAD_CHECKSUM")
            masks=p["posterior_masks"]
            if (type(masks) is not list or len(masks)!=4
                or any(type(x) is not int or not 0<=x<=ALL for x in masks)):
                raise ValueError("HC07_BAYES_BAD_MASK")
            n=p["events"];bad=p["incompatible_events"]
            if type(n) is not int or type(bad) is not int or not 0<=bad<=n<=100000:
                raise ValueError("HC07_BAYES_BAD_COUNTER")
            model=cls()
            model.posterior_masks=masks[:]
            model.events=n
            model.incompatible_events=bad
            if model.snapshot()!=data:
                raise ValueError("HC07_BAYES_NOT_CANONICAL")
            return model
        except (ValueError,TypeError,UnicodeError,KeyError,OverflowError) as ex:
            raise ValueError("HC07_BAYES_BAD_CHECKPOINT") from ex
