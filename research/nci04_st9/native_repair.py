"""ST9 tokenless eight-output causal representation repair under EIGHT acts.

No private source import and no true coefficient accessor. An original
public neutral step identifies current rotation. The second, deliberately
chosen action yields a real afteraction public change. After a real
contradiction to the four linear feature prior, the native substrate
grows to eight quadratic features and replays <=8 genuine public outcomes.
All causal inference remains integer-only; cold state is canonical.
"""
import json

SCHEMA="yggdrasil.nci04.st9.native-eight-output-budgeted-repair.v1"
MODES=("repair","no_replay","no_growth","erase")
MAX_EPISODES=1000000
CACHE_LIMIT=8


def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False)


def pack(v):
    if (type(v) not in (list,tuple) or len(v)!=8 or
        any(type(x) is not int or x not in (0,1) for x in v)):
        raise ValueError("ST9_NATIVE_PUBLIC_BITS_INVALID")
    return sum(x<<i for i,x in enumerate(v))


def roll(x,r):
    if (type(x) is not int or x not in range(256) or
        type(r) is not int or r not in (1,2,3)):
        raise ValueError("ST9_NATIVE_PUBLIC_ROTATION_INVALID")
    return ((x<<r)|(x>>(8-r)))&255


def features(B,degree=2):
    if (type(B) is not int or B not in range(16) or
        type(degree) is not int or degree not in (1,2)):
        raise ValueError("ST9_NATIVE_PUBLIC_ACTION_COMPONENT_INVALID")
    a=[(B>>i)&1 for i in range(4)]
    v=list(a)
    if degree==2:
        v.extend((a[0]&a[1],a[1]&a[2],
                  a[2]&a[3],a[3]&a[0]))
    return sum(z<<i for i,z in enumerate(v))


class NativeRepair8:
    def __init__(self,variant="repair"):
        if variant not in MODES:
            raise ValueError("ST9_NATIVE_UNKNOWN_VARIANT")
        self.variant=variant
        self.degree=1
        self.rows=[0]*4
        self.rank=0
        self.experiences=[]
        self.updates=0
        self.contradictions=0
        self.growth_events=0
        self.growth_on_update=None
        self.pre_growth_replay_count=0
        self.post_growth_conflicts=0
        self.rotation=None
        self.phase=0

    def reset_episode(self):
        if self.variant=="erase":
            self.degree=1
            self.rows=[0]*4
            self.rank=0
            self.experiences=[]
            self.growth_events=0
            self.growth_on_update=None
        self.rotation=None
        self.phase=0

    def _reduce(self,vector,output=0):
        n=len(self.rows);mask=(1<<n)-1
        if (type(vector) is not int or not 0<=vector<(1<<n) or
            type(output) is not int or output not in range(256)):
            raise ValueError("ST9_NATIVE_FEATURE_OR_PUBLIC_OUTCOME_INVALID")
        row=vector|(output<<n)
        while row&mask:
            high=(row&mask).bit_length()-1
            if self.rows[high]:
                row^=self.rows[high]
            else:
                return "NEW",high,row
        return ("CONTRADICTION" if row>>n else "KNOWN"),None,row

    def _insert(self,B,actual):
        flag,pivot,row=self._reduce(features(B,self.degree),actual)
        if flag=="NEW":
            self.rows[pivot]=row
            self.rank+=1
        return flag

    def _remember(self,B,outcome):
        for b,y in self.experiences:
            if b==B:
                if y!=outcome:
                    raise ValueError("ST9_NATIVE_REAL_PUBLIC_EFFECT_CONFLICT")
                return
        if len(self.experiences)>=CACHE_LIMIT:
            raise ValueError("ST9_NATIVE_EIGHT_INTERVENTION_BUDGET")
        self.experiences.append([B,outcome])

    def _expand(self,B,outcome):
        self.degree=2
        self.rows=[0]*8
        self.rank=0
        self.growth_events+=1
        self.growth_on_update=self.updates
        if self.variant=="no_replay":
            history=[[B,outcome]]
            self.experiences=[[B,outcome]]
            self.pre_growth_replay_count=0
        else:
            history=list(self.experiences)
            self.pre_growth_replay_count=max(0,len(history)-1)
        for b,y in history:
            if self._insert(b,y)=="CONTRADICTION":
                self.post_growth_conflicts+=1

    def predict(self,public,action):
        x=pack(public)
        if (type(action) is not int or
            (self.phase==0 and action!=0) or
            (self.phase==1 and not 1<=action<=16) or
            self.phase not in (0,1)):
            raise ValueError("ST9_NATIVE_INVALID_ANNOUNCED_PUBLIC_ACTION")
        if self.phase==0 or self.rotation is None:
            return [.5]*8
        B=action-1
        vector=features(B,self.degree)
        n=len(self.rows);mask=(1<<n)-1
        row=vector
        while row&mask:
            high=(row&mask).bit_length()-1
            if not self.rows[high]:
                return [.5]*8
            row^=self.rows[high]
        expected=x^roll(x,self.rotation)^((row>>n)&255)
        return [.99 if (expected>>j)&1 else .01 for j in range(8)]

    def observe(self,public,action,target,after,*,train=True):
        x=pack(public);y=pack(after);delta=pack(target)
        if type(train) is not bool or x^y!=delta:
            raise ValueError("ST9_NATIVE_FAKE_AFTERACTION_PUBLIC_OUTCOME")
        guess=self.predict(public,action)
        if self.phase==0:
            possible=[r for r in (1,2,3) if roll(x,r)==y]
            self.rotation=possible[0] if len(possible)==1 else None
        elif self.phase==1 and train and self.rotation is not None:
            if self.updates>=MAX_EPISODES:
                raise ValueError("ST9_NATIVE_TRAIN_COUNT_EXCEEDED")
            self.updates+=1
            B=action-1
            output=y^roll(x,self.rotation)
            self._remember(B,output)
            result=self._insert(B,output)
            if result=="CONTRADICTION":
                if self.degree==1:
                    self.contradictions+=1
                    if self.variant!="no_growth":
                        self._expand(B,output)
                else:
                    self.post_growth_conflicts+=1
        self.phase+=1
        return guess

    def snapshot(self):
        return canonical({
            "schema":SCHEMA,"variant":self.variant,"degree":self.degree,
            "rows":self.rows,"rank":self.rank,"experiences":self.experiences,
            "updates":self.updates,"contradictions":self.contradictions,
            "growth_events":self.growth_events,
            "growth_on_update":self.growth_on_update,
            "pre_growth_replay_count":self.pre_growth_replay_count,
            "post_growth_conflicts":self.post_growth_conflicts,
            "rotation":self.rotation,"phase":self.phase
        })

    @classmethod
    def restore(cls,raw):
        if type(raw) is not str or len(raw)>3500:
            raise ValueError("ST9_NATIVE_COLD_PAYLOAD_TOO_LARGE")
        try:
            d=json.loads(raw)
            keys={"schema","variant","degree","rows","rank","experiences",
                  "updates","contradictions","growth_events","growth_on_update",
                  "pre_growth_replay_count","post_growth_conflicts",
                  "rotation","phase"}
            if (type(d) is not dict or set(d)!=keys or
                d["schema"]!=SCHEMA or d["variant"] not in MODES or
                type(d["degree"]) is not int or d["degree"] not in (1,2) or
                type(d["rows"]) is not list or
                len(d["rows"])!=(4 if d["degree"]==1 else 8) or
                any(type(z) is not int or not 0<=z<
                    (1<<(len(d["rows"])+8)) for z in d["rows"]) or
                type(d["experiences"]) is not list or
                len(d["experiences"])>CACHE_LIMIT or
                any(type(p) is not list or len(p)!=2 or
                    type(p[0]) is not int or p[0] not in range(16) or
                    type(p[1]) is not int or p[1] not in range(256)
                    for p in d["experiences"]) or
                len({p[0] for p in d["experiences"]})!=len(d["experiences"]) or
                any(type(d[k]) is not int or not 0<=d[k]<=MAX_EPISODES
                    for k in ("rank","updates","contradictions","growth_events",
                              "pre_growth_replay_count","post_growth_conflicts",
                              "phase")) or
                d["rank"]>len(d["rows"]) or d["phase"]>2 or
                d["growth_events"]>1 or
                (d["degree"]==1)!=(d["growth_events"]==0) or
                (d["growth_events"]==0)!=(d["growth_on_update"] is None) or
                (d["growth_on_update"] is not None and
                 (type(d["growth_on_update"]) is not int or
                  not 1<=d["growth_on_update"]<=d["updates"])) or
                (d["rotation"] is not None and
                 (type(d["rotation"]) is not int or
                  d["rotation"] not in (1,2,3))) or
                sum(bool(z) for z in d["rows"])!=d["rank"] or
                any(row and
                    (row&((1<<len(d["rows"]))-1)).bit_length()-1!=i
                    for i,row in enumerate(d["rows"]))):
                raise ValueError("ST9_NATIVE_COLD_INVALID")
            o=cls(d["variant"])
            for k in keys-{"schema","variant"}:
                setattr(o,k,d[k])
            if o.snapshot()!=raw:
                raise ValueError("ST9_NATIVE_NONCANONICAL_COLD")
            return o
        except (TypeError,KeyError,OverflowError) as e:
            raise ValueError("ST9_NATIVE_RESTORE_FAILED") from e

    def accounting(self):
        return {
            "native_output_cells":8,
            "learned_GF2_evidence_bits_max":8*(8+8),
            "public_replay_cache_bytes_max":CACHE_LIMIT*2,
            "cached_public_effects":len(self.experiences),
            "feature_family_upper_bound":8,
            "source_private_coefficients_seen":False,
            "cold_checkpoint_json_bytes":len(self.snapshot().encode("utf-8")),
            "integer_state_only":True
        }
