"""CAP03 native action-consequence CONTRAST memory, not a route selector.

Learn effect contrasts from directly witnessed paired interventions at
identical public states. Stage 1 predicts next sensory bit before witnessing
it. Stage 2 predicts reward by learning the reward XOR witnessed sensory bit:
this is an explicit, testable causal residual representation, not a hidden
future-label or time/phase selector. Previously trained native model weights
and old archived readouts are never modified here.
"""
from __future__ import annotations
import json
from yggdrasil.native_context_basis import canonical,digest,pin

SCHEMA="yggdrasil.cap03.paired-native-contrast.v1"
ARMS=((0,0),(0,1),(1,0),(1,1))
MAX_STATES=32
PRIOR=4.
EFFECT_SHRINK=8.
SHAM_ORDER={(0,1):(1,0),(1,0):(1,1),(1,1):(0,1)}

def check(ok,tag):
    if not ok:
        raise ValueError("CAP03_CONTRAST_"+tag)

def bit(x):
    check(type(x) is int and x in (0,1),"PUBLIC_BIT")
    return x

def state(views):
    check(type(views) is tuple and len(views)==2 and
          all(type(v) is tuple and len(v)==2 for v in views),
          "PAIRED_SENSOR_VIEWS")
    u,v,w=bit(views[0][0]),bit(views[0][1]),bit(views[1][1])
    check(views[1][0]==v,"SHARED_SENSOR_CUSTODY")
    return (u,v,w)

def arm(action):
    check(type(action) is tuple and len(action)==2,
          "PUBLIC_ACTION_PAIR")
    pair=(bit(action[0]),bit(action[1]))
    check(pair in ARMS,"ACTION_SUPPORT")
    return pair

def forks_ok(forks):
    check(type(forks) is tuple and len(forks)==4,
          "FOUR_MATCHED_INTERVENTIONS")
    observed=[]
    for row,expected in zip(forks,ARMS):
        check(type(row) is dict and set(row)=={"action","s2","y","post"},
              "WITNESSED_FORK_KEYS")
        check(arm(row["action"])==expected,"WITNESSED_ACTION_ORDER")
        s2=bit(row["s2"]);y=bit(row["y"])
        post=row["post"]
        check(type(post) is tuple and len(post)==3 and
              all(type(z) is int and z in (0,1) for z in post)
              and post[1]==s2,"FORK_OBSERVED_POST")
        observed.append((expected,s2,y,post))
    return tuple(observed)

class PairedCausalContrast:
    def __init__(self,*,mispair=False):
        self.mispair=bool(mispair)
        self._events=()
        self._seen=set()

    @property
    def count(self):
        return len(self._events)

    def _scores(self,kind,context):
        # Prior paired witnesses are the ONLY training records. Never phase,
        # family, source ID, future state or oracle causal mechanism.
        anchor_all=[]
        anchor_context=[]
        delta={a:[] for a in ARMS[1:]}
        for _,st,rows in self._events:
            values={}
            for pair,s2,y,_ in rows:
                values[pair]=s2 if kind=="transition" else y^s2
            baseline=values[(0,0)]
            anchor_all.append(baseline)
            if st==context:
                anchor_context.append(baseline)
            for pair in ARMS[1:]:
                comparison=SHAM_ORDER[pair] if self.mispair else pair
                delta[pair].append(values[comparison]-baseline)
        global_anchor=(1.+sum(anchor_all))/(2.+len(anchor_all))
        anchored=(sum(anchor_context)+PRIOR*global_anchor)/(
                  len(anchor_context)+PRIOR)
        return anchored,{a:sum(v)/(len(v)+EFFECT_SHRINK)
                         for a,v in delta.items()}

    def forecast(self,views,action,stage,observed_s2=None):
        st=state(views);pair=arm(action)
        check(stage in ("transition","terminal"),"FORECAST_STAGE")
        if stage=="transition":
            check(observed_s2 is None,"FIRST_STAGE_NO_FUTURE_SENSOR")
        else:
            bit(observed_s2)
        baseline,effects=self._scores(
            "transition" if stage=="transition" else "residual",st)
        p=min(.98,max(.02,baseline+effects.get(pair,0.)))
        if stage=="terminal" and observed_s2==1:
            p=1.-p
        check(0<=p<=1,"PROBABILITY")
        return float(p)

    def observe(self,identifier,views,forks):
        check(pin(identifier),"SOURCE_ID")
        st=state(views)
        witness=forks_ok(forks)
        check(identifier not in self._seen,"DUPLICATE_FORK_EVENT")
        check(self.count<MAX_STATES,"MAX_DEVELOPMENT_EPISODES")
        self._events+=(identifier,st,witness),
        self._seen.add(identifier)
        return self

    def checkpoint(self):
        return canonical({
            "schema":SCHEMA,"mispair":self.mispair,
            "events":self._events
        })

    @classmethod
    def restore(cls,raw,expected_sha):
        check(type(raw) is bytes and pin(expected_sha)
              and digest(raw)==expected_sha,"COLD_SHA")
        try:
            doc=json.loads(raw.decode("ascii"))
            check(type(doc) is dict and set(doc)=={
                "schema","mispair","events"} and
                doc["schema"]==SCHEMA and
                type(doc["mispair"]) is bool and canonical(doc)==raw,
                "COLD_SCHEMA")
            obj=cls(mispair=doc["mispair"])
            for ident,st,rows in doc["events"]:
                # The original witnessed matched source is checked by an
                # independent auditor; canonical cold custody refuses
                # reordered arms, duplicate IDs and altered shapes.
                views=((st[0],st[1]),(st[1],st[2]))
                converted=tuple({
                    "action":tuple(item[0]),
                    "s2":item[1],"y":item[2],
                    "post":tuple(item[3])
                } for item in rows)
                obj.observe(ident,views,converted)
            check(obj.checkpoint()==raw,"COLD_REPLAY_MISMATCH")
            return obj
        except (ValueError,TypeError,KeyError,IndexError,
                UnicodeError,OverflowError) as exc:
            raise ValueError("YGG_CAP03_COLD_REJECTED") from exc
