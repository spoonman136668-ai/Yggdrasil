"""ST9 independent conventionally coded strongest exact GF2 causal controls.

8x8 unknown true rule coefficients fit on genuine public outcomes only.
LOW-pivot independent Gaussian implementation, not the native code.
Adaptive conventional receives identical 8 interventions, replay cache
and upper prior. Full conventional uses same 8 probes from the start.
Two strong/weak passive conventional arms receive 8 real actions each,
but different unoptimized B choices (explicitly disclosed).

No source or true private coefficient imported.
"""
import json

SCHEMA="yggdrasil.nci04.st9.independent-conventional-gf2.v1"
ACTOR_GROUPS={
    "candidate":"active","no_replay":"active",
    "no_growth":"active","erase":"active",
    "full_active":"active","adaptive_conventional":"active",
    "blind_dispersed":"dispersed","blind_repeat":"repeat",
}
PASSIVE_REPEAT=(1,2,4,8,1,2,4,8)
PASSIVE_DISPERSED=(1,3,5,7,9,11,13,15)
FROZEN_ACTIVE=(1,2,3,4,6,8,9,12)
MODES=("full_active","adaptive_conventional","blind_dispersed","blind_repeat")
MAX_UPDATES=1000000


def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False)


def publicbyte(x):
    if (type(x) not in (tuple,list) or len(x)!=8 or
        any(type(v) is not int or v not in (0,1) for v in x)):
        raise ValueError("ST9_CONVENTIONAL_BAD_PUBLIC")
    return sum(v<<i for i,v in enumerate(x))


def rotated(x,r):
    if (type(x) is not int or x not in range(256) or
        type(r) is not int or r not in (1,2,3)):
        raise ValueError("ST9_CONVENTIONAL_BAD_ROTATION")
    return ((x<<r)|(x>>(8-r)))&255


def quadratic(B,degree=2):
    if (type(B) is not int or B not in range(16) or
        type(degree) is not int or degree not in (1,2)):
        raise ValueError("ST9_CONVENTIONAL_BAD_PUBLIC_FEATURE")
    bs=[(B>>j)&1 for j in range(4)]
    f=list(bs)
    if degree==2:
        f.extend((bs[0]*bs[1],bs[1]*bs[2],
                  bs[2]*bs[3],bs[3]*bs[0]))
    return sum(t<<i for i,t in enumerate(f))


def select_active(history):
    if (type(history) not in (tuple,list) or
        len(history)>=8 or
        any(type(v) is not int or not 1<=v<=15 for v in history) or
        len(set(history))!=len(history)):
        raise ValueError("ST9_CONVENTIONAL_PUBLIC_PROBE_HISTORY_INVALID")
    def insert(basis,vector):
        while vector:
            low=vector&-vector
            p=low.bit_length()-1
            if basis[p]:
                vector^=basis[p]
            else:
                basis[p]=vector
                return True
        return False
    rows=[0]*8
    for v in history:
        if not insert(rows,quadratic(v,2)):
            raise ValueError("ST9_CONVENTIONAL_ACTOR_HISTORY_NOT_INDEPENDENT")
    for B in range(1,16):
        if B in history:
            continue
        r=list(rows)
        if insert(r,quadratic(B,2)):
            return B
    raise ValueError("ST9_CONVENTIONAL_PUBLIC_ACTOR_EXHAUSTED")


def active_plan():
    seen=[]
    while len(seen)<8:
        seen.append(select_active(seen))
    if tuple(seen)!=FROZEN_ACTIVE:
        raise ValueError("ST9_CONVENTIONAL_ACTOR_PREREG_DRIFT")
    return tuple(seen)


class ConventionalGF2:
    def __init__(self,mode="full_active"):
        if mode not in MODES:
            raise ValueError("ST9_CONVENTIONAL_INVALID_MODE")
        self.mode=mode
        self.degree=1 if mode=="adaptive_conventional" else 2
        self.rows=[0]*(4 if self.degree==1 else 8)
        self.rank=0
        self.buffer=[]
        self.updates=0
        self.contradictions=0
        self.growth_events=0
        self.first_growth_on_update=None
        self.public_replay_count=0
        self.post_growth_conflicts=0
        self.rotation=None
        self.phase=0

    def reset_episode(self):
        self.rotation=None
        self.phase=0

    def _reduce(self,F,Y=0):
        n=len(self.rows);mask=(1<<n)-1
        if (type(F) is not int or not 0<=F<(1<<n) or
            type(Y) is not int or Y not in range(256)):
            raise ValueError("ST9_CONVENTIONAL_BAD_EVIDENCE")
        row=F|(Y<<n)
        while row&mask:
            low=(row&mask)&-(row&mask)
            p=low.bit_length()-1
            if self.rows[p]:
                row^=self.rows[p]
            else:
                return "NEW",p,row
        return ("CONTRADICTION" if row>>n else "KNOWN"),None,row

    def _add(self,B,Y):
        status,p,row=self._reduce(quadratic(B,self.degree),Y)
        if status=="NEW":
            self.rows[p]=row
            self.rank+=1
        return status

    def _remember(self,B,Y):
        for b,v in self.buffer:
            if b==B:
                if v!=Y:
                    raise ValueError("ST9_CONVENTIONAL_ORIGINAL_RULE_SWITCH")
                return
        if len(self.buffer)>=8:
            raise ValueError("ST9_CONVENTIONAL_ORIGINAL_EIGHT_PROBE_BUDGET")
        self.buffer.append([B,Y])

    def predict(self,public,action):
        x=publicbyte(public)
        if (type(action) is not int or self.phase not in (0,1) or
            (self.phase==0 and action!=0) or
            (self.phase==1 and action not in range(1,17))):
            raise ValueError("ST9_CONVENTIONAL_ANNOUNCED_ACTION_INVALID")
        if self.phase==0 or self.rotation is None:
            return [.5]*8
        F=quadratic(action-1,self.degree)
        mask=(1<<len(self.rows))-1
        row=F
        while row&mask:
            low=(row&mask)&-(row&mask)
            p=low.bit_length()-1
            if not self.rows[p]:
                return [.5]*8
            row^=self.rows[p]
        y=x^rotated(x,self.rotation)^((row>>len(self.rows))&255)
        return [.99 if (y>>i)&1 else .01 for i in range(8)]

    def observe(self,public,action,target,after,*,train=True):
        x=publicbyte(public);y=publicbyte(after);t=publicbyte(target)
        if type(train) is not bool or x^y!=t:
            raise ValueError("ST9_CONVENTIONAL_PUBLIC_ACTION_FAKE")
        pred=self.predict(public,action)
        if self.phase==0:
            opts=[r for r in (1,2,3) if rotated(x,r)==y]
            self.rotation=opts[0] if len(opts)==1 else None
        elif self.phase==1 and train and self.rotation is not None:
            if self.updates>=MAX_UPDATES:
                raise ValueError("ST9_CONVENTIONAL_EXCEEDED_TRAIN_BUDGET")
            self.updates+=1
            B=action-1
            Y=y^rotated(x,self.rotation)
            if self.mode=="adaptive_conventional":
                self._remember(B,Y)
            status=self._add(B,Y)
            if status=="CONTRADICTION":
                if self.degree==1:
                    self.contradictions+=1
                    self.degree=2
                    self.rows=[0]*8
                    self.rank=0
                    self.growth_events+=1
                    self.first_growth_on_update=self.updates
                    self.public_replay_count=max(0,len(self.buffer)-1)
                    for b,v in self.buffer:
                        if self._add(b,v)=="CONTRADICTION":
                            self.post_growth_conflicts+=1
                else:
                    self.post_growth_conflicts+=1
        self.phase+=1
        return pred

    def snapshot(self):
        return canonical({
            "schema":SCHEMA,"mode":self.mode,"degree":self.degree,
            "rows":self.rows,"rank":self.rank,"buffer":self.buffer,
            "updates":self.updates,"contradictions":self.contradictions,
            "growth_events":self.growth_events,
            "first_growth_on_update":self.first_growth_on_update,
            "public_replay_count":self.public_replay_count,
            "post_growth_conflicts":self.post_growth_conflicts,
            "rotation":self.rotation,"phase":self.phase
        })

    @classmethod
    def restore(cls,raw):
        if type(raw) is not str or len(raw)>3600:
            raise ValueError("ST9_CONVENTIONAL_CHECKPOINT_TOO_LARGE")
        try:
            d=json.loads(raw)
            keys={"schema","mode","degree","rows","rank","buffer",
                  "updates","contradictions","growth_events",
                  "first_growth_on_update","public_replay_count",
                  "post_growth_conflicts","rotation","phase"}
            if (type(d) is not dict or set(d)!=keys or
                d["schema"]!=SCHEMA or d["mode"] not in MODES or
                type(d["degree"]) is not int or d["degree"] not in (1,2) or
                (d["mode"]!="adaptive_conventional" and d["degree"]!=2) or
                type(d["rows"]) is not list or
                len(d["rows"])!=(4 if d["degree"]==1 else 8) or
                any(type(row) is not int or not 0<=row<
                    (1<<(len(d["rows"])+8)) for row in d["rows"]) or
                type(d["buffer"]) is not list or len(d["buffer"])>8 or
                any(type(pair) is not list or len(pair)!=2 or
                    type(pair[0]) is not int or pair[0] not in range(16) or
                    type(pair[1]) is not int or pair[1] not in range(256)
                    for pair in d["buffer"]) or
                len({p[0] for p in d["buffer"]})!=len(d["buffer"]) or
                any(type(d[k]) is not int or not 0<=d[k]<=MAX_UPDATES
                    for k in ("rank","updates","contradictions",
                              "growth_events","public_replay_count","post_growth_conflicts",
                              "phase")) or
                d["rank"]>len(d["rows"]) or d["phase"]>2 or
                d["growth_events"]>1 or
                (d["growth_events"]==0)!=(d["first_growth_on_update"] is None) or
                (d["first_growth_on_update"] is not None and
                 (type(d["first_growth_on_update"]) is not int or
                  not 1<=d["first_growth_on_update"]<=d["updates"])) or
                (d["mode"]=="adaptive_conventional" and
                 (d["degree"]==1)!=(d["growth_events"]==0)) or
                (d["rotation"] is not None and
                 (type(d["rotation"]) is not int or d["rotation"] not in (1,2,3))) or
                sum(int(row!=0) for row in d["rows"])!=d["rank"] or
                any(row and
                    ((row&((1<<len(d["rows"]))-1))&
                     -(row&((1<<len(d["rows"]))-1))).bit_length()-1!=i
                    for i,row in enumerate(d["rows"]))):
                raise ValueError("ST9_CONVENTIONAL_COLD_SHAPE")
            m=cls(d["mode"])
            for k in keys-{"schema","mode"}:
                setattr(m,k,d[k])
            if m.snapshot()!=raw:
                raise ValueError("ST9_CONVENTIONAL_NONCANONICAL_COLD")
            return m
        except (KeyError,TypeError,OverflowError) as e:
            raise ValueError("ST9_CONVENTIONAL_COLD_INVALID") from e

    def accounting(self):
        return {
            "max_GF2_learned_augmented_bits":8*16,
            "max_public_replay_bytes":16
                if self.mode=="adaptive_conventional" else 0,
            "stored_public_B_outcome_pairs":len(self.buffer),
            "inferred_source_private_coefficients_seen":False,
            "fixed_true_rule_menu":0,
            "checkpoint_json_bytes":len(self.snapshot().encode("utf-8"))
        }


def make_models():
    from research.nci04_st9.native_repair import NativeRepair8
    return {
        "candidate":NativeRepair8("repair"),
        "no_replay":NativeRepair8("no_replay"),
        "no_growth":NativeRepair8("no_growth"),
        "erase":NativeRepair8("erase"),
        "full_active":ConventionalGF2("full_active"),
        "adaptive_conventional":ConventionalGF2("adaptive_conventional"),
        "blind_dispersed":ConventionalGF2("blind_dispersed"),
        "blind_repeat":ConventionalGF2("blind_repeat")
    }


def restore_one(name,blob):
    from research.nci04_st9.native_repair import NativeRepair8
    if name in MODES:
        x=ConventionalGF2.restore(blob)
        if x.mode!=name:raise ValueError("ST9_CONVENTIONAL_WRONG_MODE_COLD")
        return x
    x=NativeRepair8.restore(blob)
    variant="repair" if name=="candidate" else name
    if x.variant!=variant:raise ValueError("ST9_NATIVE_WRONG_ABLATION_COLD")
    return x


def restore_all(blobs):
    if type(blobs) is not dict or set(blobs)!=set(make_models()):
        raise ValueError("ST9_INCOMPLETE_TRAINED_MODEL_COHORT")
    xs={k:restore_one(k,v) for k,v in blobs.items()}
    if any(xs[k].snapshot()!=blobs[k] for k in blobs):
        raise ValueError("ST9_RESTORED_MODEL_BYTES_CHANGED")
    return xs
