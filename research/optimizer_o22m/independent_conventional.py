"""Independent conventional recency/count public effect baseline.

O22-M source-free fairness control. Does NOT import the O22-L learner.
All evidence comes only from completed original R10 public-interface events.
"""
from __future__ import annotations
import hashlib
import json
import math

from research.native.itd02.r10.public_adapter import (
    ACTION_NAMES, DoorKeyPublicAdapter, canonical, digest, public_cues,
)

SCHEMA = "optimizer.o22m.conventional-temporal-public-effect.v1"
LIMIT = 4096


def cue_key(front, carry, action):
    if type(action) is not int or not 0 <= action < 7:
        raise ValueError("M_INVALID_ACTION")
    if type(front) is not list or len(front) != 3:
        raise ValueError("M_INVALID_FRONT")
    c = [0, 0] if carry is None else carry[:2]
    return canonical([front, c, action]).decode()


def observed_label(event):
    old, new = event["front_before"], event["front_after"]
    a, d0, d1 = event["action"], event["heading_before"], event["heading_after"]
    opening = (bool(event["visible_door_opened"]) and a == 5 and d0 == d1
               and old[0] == new[0] == 4 and old[1] == new[1]
               and old[2] in (1, 2) and new[2] == 0)
    if opening:
        reason = "R10_WITNESSED_VISIBLE_OPEN"
    elif a in (0, 1) and d0 != d1:
        reason = "CHANGED_VIEW_NOT_WORLD_EFFECT"
    elif old != new:
        reason = "UNKNOWN_TARGET_IDENTITY"
    else:
        reason = "NO_VERIFIED_WORLD_EFFECT"
    return canonical([new, event["carried_after"], d1,
                      opening, bool(event["visible_key_pickup"]),
                      event["reward"] > 0, bool(event["terminated"]),
                      bool(event["truncated"]), reason]).decode()


class ConventionalTemporal:
    """Separate count/discounted empirical process; equal info and costs."""

    def __init__(self, discount=0.5, fast_weight=0.85):
        if (type(discount) not in (float, int) or not 0 < discount < 1
            or type(fast_weight) not in (float, int) or not 0 <= fast_weight <= 1):
            raise ValueError("M_RULE_INVALID")
        self.discount = float(discount)
        self.fast_weight = float(fast_weight)
        self.history = {}
        self.recent = {}
        self.total = 0
        self.session = None
        self.cursor = 0
        self.sessions = []
        self.last_digest = None

    def start(self, owner, identity):
        if (type(owner) is not DoorKeyPublicAdapter or owner.current is None
            or owner.pending is not None or owner.events or owner.ledger or owner.terminal
            or type(identity) is not str or not 0 < len(identity) <= 100
            or identity in self.sessions or len(self.sessions) >= 100):
            raise ValueError("M_OWNER_SESSION_INVALID")
        self.session = identity
        self.sessions.append(identity)
        self.cursor = 0
        self.last_digest = digest(owner.current)

    def learn(self, owner):
        if (type(owner) is not DoorKeyPublicAdapter or owner.current is None
            or owner.pending is not None or self.session is None
            or owner.events != self.cursor + 1 or not owner.ledger
            or self.total >= LIMIT):
            raise ValueError("M_SOURCE_EVENT_INVALID")
        e = owner.ledger[-1]
        if (e["ordinal"] != owner.events
            or e["action_name"] != ACTION_NAMES[e["action"]]
            or e["before_public_sha256"] != self.last_digest
            or e["after_public_sha256"] != digest(owner.current)):
            raise ValueError("M_PROVENANCE_INCONSISTENCY")
        k = cue_key(e["front_before"], e["carried_before"], e["action"])
        v = observed_label(e)
        if k not in self.history and len(self.history) >= 512:
            raise ValueError("M_CONTEXT_LIMIT")
        old = self.history.get(k, {})
        next_hist = dict(old)
        next_hist[v] = next_hist.get(v, 0) + 1
        recent = {label: weight * self.discount for label, weight
                  in self.recent.get(k, {}).items()
                  if weight * self.discount > 1e-12}
        recent[v] = recent.get(v, 0.0) + 1.0
        self.history[k], self.recent[k] = next_hist, recent
        self.total += 1
        self.cursor += 1
        self.last_digest = e["after_public_sha256"]

    def predict(self, obs, action, scheme="blend"):
        if scheme not in ("blend", "lifetime", "recent", "disabled"):
            raise ValueError("M_SCHEME_INVALID")
        c = public_cues(obs)
        k = cue_key(c["front"], c["carried"], action)
        h = self.history.get(k)
        if not h or scheme == "disabled":
            return None
        f = self.recent[k]
        hs, fs = sum(h.values()), sum(f.values())
        q = {}
        for label, count in h.items():
            p_old, p_recent = count / hs, f.get(label, 0) / fs
            if scheme == "lifetime":p = p_old
            elif scheme == "recent":p = p_recent
            else:p = self.fast_weight * p_recent + (1 - self.fast_weight) * p_old
            q[label] = p
        return {"sample_count": hs,
                "verified_open_probability":
                    sum(p for label, p in q.items() if json.loads(label)[3]),
                "next_public_fronts": sorted({
                    tuple(json.loads(label)[0]) for label in q
                }),
                "outcome_probabilities": q}

    def select(self, obs, costs=None, scheme="blend"):
        if costs is None:costs=[0.0]*7
        if (type(costs) not in (list,tuple) or len(costs)!=7
            or any(type(v) not in (float,int) or not math.isfinite(v)
                   or v<0 or v>1 for v in costs)):
            raise ValueError("M_COSTS_INVALID")
        candidates=[]
        for a in range(7):
            row=self.predict(obs,a,scheme)
            if row is None:continue
            p=row["verified_open_probability"]
            if p>0 and p>costs[a]:
                candidates.append((-(p-costs[a]),a,p))
        if not candidates:return None
        _,action,p=min(candidates)
        return {"action":action,"p":p}

    def checkpoint(self):
        data={"schema":SCHEMA,"discount":self.discount,"fast_weight":self.fast_weight,
              "history":self.history,"recent":self.recent,"total":self.total,
              "session":self.session,"sessions":self.sessions,"cursor":self.cursor,
              "last_digest":self.last_digest}
        b=canonical(data)
        if len(b)>180000:raise ValueError("M_BYTES_CAP")
        return canonical({"state":data,"sha256":hashlib.sha256(b).hexdigest()})

    @classmethod
    def restore(cls, raw):
        try:
            if type(raw) is not bytes or not 0<len(raw)<=180000:
                raise ValueError("M_BYTES_INVALID")
            e=json.loads(raw)
            if type(e) is not dict or set(e)!={"state","sha256"}:
                raise ValueError("M_WIRE_INVALID")
            s=e["state"]
            required={"schema","discount","fast_weight","history","recent",
                      "total","session","sessions","cursor","last_digest"}
            if (type(s) is not dict or set(s)!=required or s["schema"]!=SCHEMA
                or e["sha256"]!=hashlib.sha256(canonical(s)).hexdigest()
                or type(s["total"]) is not int or not 0<=s["total"]<=LIMIT
                or type(s["cursor"]) is not int or not 0<=s["cursor"]<=s["total"]
                or type(s["history"]) is not dict or len(s["history"])>512
                or type(s["recent"]) is not dict
                or set(s["recent"])!=set(s["history"])
                or type(s["sessions"]) is not list or len(s["sessions"])>100
                or any(type(x) is not str or not 0<len(x)<=100 for x in s["sessions"])
                or len(set(s["sessions"])) != len(s["sessions"])
                or (s["sessions"] and s["session"] != s["sessions"][-1])):
                raise ValueError("M_STATE_INVALID")
            out=cls(s["discount"],s["fast_weight"])
            total=0
            for k,row in s["history"].items():
                key=json.loads(k)
                if (type(key) is not list or len(key)!=3 or type(key[2]) is not int
                    or not 0<=key[2]<=6 or type(row) is not dict
                    or not 1<=len(row)<=128 or type(s["recent"][k]) is not dict
                    or not set(s["recent"][k]).issubset(row)):
                    raise ValueError("M_ROW_INVALID")
                for label,count in row.items():
                    payload=json.loads(label)
                    if (type(payload) is not list or len(payload)!=9
                        or type(payload[3]) is not bool
                        or type(count) is not int or not 1<=count<=LIMIT):
                        raise ValueError("M_COUNTER_INVALID")
                    total+=count
                for weight in s["recent"][k].values():
                    if (type(weight) not in (float,int) or not math.isfinite(weight)
                        or weight<=0):
                        raise ValueError("M_WEIGHT_INVALID")
            if total!=s["total"]:raise ValueError("M_COUNTER_TOTAL_DRIFT")
            for k in ("history","recent","total","session","cursor","sessions","last_digest"):
                setattr(out,k,s[k])
            return out
        except (ValueError,KeyError,TypeError,OverflowError,AttributeError) as exc:
            raise ValueError("M_UNTRUSTED_CHECKPOINT") from exc
