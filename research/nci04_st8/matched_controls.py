"""ST8 independent conventional GF2 cubic and adaptive public-evidence controls.

Neither the true source coefficients nor correct rule outcome names are
provided. Conventional full cubic fits a known 92-feature representation
from the start; adaptive fits the same data and can expand upon observed
quadratic contradiction with exactly the same public replay allowance.
Distinct LOW pivot elimination from the native HIGH pivot substrate.
"""
import json

from research.nci04_st7.native_induction import NativeInductive8

SCHEMA="yggdrasil.nci04.st8.conventional-low-pivot-gf2.v1"
ACTION_SEQUENCE=(3,0,1,2,3)
MODES=("full_cubic","adaptive")
MAX_UPDATES=10000000


def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),allow_nan=False)


def pack(x):
    if (type(x) not in (tuple,list) or len(x)!=8 or
        any(type(y) is not int or y not in (0,1) for y in x)):
        raise ValueError("ST8_CONTROL_INVALID_PUBLIC")
    return sum(v<<i for i,v in enumerate(x))


def rotated(x,k):
    if (type(x) is not int or x not in range(256) or
        type(k) is not int or k not in (1,2,3)):
        raise ValueError("ST8_CONTROL_INVALID_ROTATION")
    return ((x<<k)|(x>>(8-k)))&255


def public_features(B,degree=3):
    if (type(B) is not int or B not in range(256) or
        type(degree) is not int or degree not in (2,3)):
        raise ValueError("ST8_CONTROL_INVALID_COMPONENT")
    bits=[(B>>k)&1 for k in range(8)]
    F=bits+[bits[i]*bits[j] for i in range(8) for j in range(i+1,8)]
    if degree==3:
        F.extend(bits[i]*bits[j]*bits[k] for i in range(8)
                 for j in range(i+1,8) for k in range(j+1,8))
    assert len(F)==(36 if degree==2 else 92)
    return sum(bit<<i for i,bit in enumerate(F))


class ConventionalGF2:
    def __init__(self,mode="full_cubic"):
        if mode not in MODES:
            raise ValueError("ST8_CONTROL_UNAUTHORIZED_MODE")
        self.mode=mode
        self.degree=3 if mode=="full_cubic" else 2
        self.rows=[0]*(92 if self.degree==3 else 36)
        self.rank=0
        self.buffer=[]
        self.examples=0
        self.contradictions=0
        self.growths=0
        self.first_growth_on_example=None
        self.rotation=None
        self.A=None
        self.B=None
        self.phase=0

    def reset_episode(self):
        self.rotation=None;self.A=None;self.B=None;self.phase=0

    def _reduce(self,F,Y=0):
        n=len(self.rows)
        if (type(F) is not int or not 0<=F<(1<<n) or
            type(Y) is not int or Y not in range(256)):
            raise ValueError("ST8_CONTROL_FEATURE_RANK_OR_RESULT_DRIFT")
        row=F|(Y<<n)
        mask=(1<<n)-1
        while row&mask:
            low=(row&mask)&-(row&mask)
            i=low.bit_length()-1
            if self.rows[i]:
                row^=self.rows[i]
            else:
                return ("NEW",i,row)
        return ("CONTRADICTION" if row>>n else "KNOWN",None,row)

    def _insert(self,B,Y):
        kind,i,row=self._reduce(public_features(B,self.degree),Y)
        if kind=="NEW":
            self.rows[i]=row
            self.rank+=1
        return kind

    def _record(self,B,Y):
        for p,v in self.buffer:
            if p==B:
                if v!=Y:
                    raise ValueError("ST8_CONVENTIONAL_PUBLIC_LAW_SWITCH")
                return
        if len(self.buffer)>=256:
            raise ValueError("ST8_CONVENTIONAL_ORIGINAL_EXPERIENCE_OVERFLOW")
        self.buffer.append([B,Y])

    def predict(self,public,action):
        x=pack(public)
        if (type(action) is not int or action not in (0,1,2,3) or
            self.phase>=5 or action!=ACTION_SEQUENCE[self.phase]):
            raise ValueError("ST8_CONVENTIONAL_PUBLIC_ACTOR_DRIFT")
        if self.phase!=4 or None in (self.rotation,self.A,self.B):
            return [.5]*8
        n=len(self.rows)
        mask=(1<<n)-1
        row=public_features(self.B,self.degree)
        while row&mask:
            low=(row&mask)&-(row&mask)
            i=low.bit_length()-1
            if not self.rows[i]:
                return [.5]*8
            row^=self.rows[i]
        delta=x^rotated(x,self.rotation)^self.A^((row>>n)&255)
        return [.99 if ((delta>>i)&1) else .01 for i in range(8)]

    def observe(self,public,action,target,after,*,train=True):
        x=pack(public);y=pack(after);truth=pack(target)
        if (type(train) is not bool or
            type(action) is not int or self.phase>=5 or
            action!=ACTION_SEQUENCE[self.phase] or x^y!=truth):
            raise ValueError("ST8_CONVENTIONAL_UNAUTHENTIC_ORIGINAL_STEP")
        prediction=self.predict(public,action)
        if self.phase==0:
            r=[k for k in (1,2,3) if rotated(x,k)==y]
            self.rotation=r[0] if len(r)==1 else None
        elif self.phase==1 and self.rotation is not None:
            self.A=y^rotated(x,self.rotation)
        elif self.phase==2 and self.rotation is not None:
            self.B=y^rotated(x,self.rotation)
        elif self.phase==4 and train and None not in (
            self.rotation,self.A,self.B
        ):
            if self.examples>=MAX_UPDATES:
                raise ValueError("ST8_CONTROL_TRAIN_LIMIT")
            self.examples+=1
            output=y^rotated(x,self.rotation)^self.A
            if self.mode=="adaptive":
                self._record(self.B,output)
            kind=self._insert(self.B,output)
            if kind=="CONTRADICTION":
                self.contradictions+=1
                if self.degree==2:
                    self.degree=3
                    self.rows=[0]*92
                    self.rank=0
                    self.growths+=1
                    self.first_growth_on_example=self.examples
                    for b,v in self.buffer:
                        if self._insert(b,v)=="CONTRADICTION":
                            raise ValueError("ST8_CONVENTIONAL_CUBIC_CONFLICT")
        self.phase+=1
        return prediction

    def snapshot(self):
        return canonical({
            "schema":SCHEMA,"mode":self.mode,"degree":self.degree,
            "rows":self.rows,"rank":self.rank,"buffer":self.buffer,
            "examples":self.examples,"contradictions":self.contradictions,
            "growths":self.growths,
            "first_growth_on_example":self.first_growth_on_example,
            "rotation":self.rotation,"A":self.A,"B":self.B,
            "phase":self.phase
        })

    @classmethod
    def restore(cls,raw):
        if type(raw) is not str or len(raw)>14000:
            raise ValueError("ST8_CONVENTIONAL_COLD_SIZE")
        try:
            d=json.loads(raw)
            keys={"schema","mode","degree","rows","rank","buffer",
                  "examples","contradictions","growths",
                  "first_growth_on_example","rotation","A","B","phase"}
            if (type(d) is not dict or set(d)!=keys or
                d["schema"]!=SCHEMA or d["mode"] not in MODES or
                type(d["degree"]) is not int or d["degree"] not in (2,3) or
                (d["mode"]=="full_cubic" and d["degree"]!=3) or
                type(d["rows"]) is not list or
                len(d["rows"])!=(36 if d["degree"]==2 else 92) or
                any(type(row) is not int or not 0<=row<
                    (1<<(len(d["rows"])+8)) for row in d["rows"]) or
                type(d["buffer"]) is not list or len(d["buffer"])>256 or
                any(type(pair) is not list or len(pair)!=2 or
                    any(type(z) is not int or z not in range(256)
                        for z in pair) for pair in d["buffer"]) or
                len({v[0] for v in d["buffer"]})!=len(d["buffer"]) or
                any(type(d[k]) is not int or not 0<=d[k]<=MAX_UPDATES
                    for k in ("rank","examples","contradictions",
                              "growths","phase")) or
                d["rank"]>len(d["rows"]) or d["phase"]>5 or
                d["growths"]>1 or
                (d["mode"]=="adaptive" and
                 (d["degree"]==2)!=(d["growths"]==0)) or
                (d["growths"]==0)!=(d["first_growth_on_example"] is None) or
                (d["first_growth_on_example"] is not None and
                 (type(d["first_growth_on_example"]) is not int or
                  not 0<=d["first_growth_on_example"]<=d["examples"])) or
                (d["rotation"] is not None and
                 (type(d["rotation"]) is not int or
                  d["rotation"] not in (1,2,3))) or
                any(d[k] is not None and
                    (type(d[k]) is not int or d[k] not in range(256))
                    for k in ("A","B")) or
                sum(int(z!=0) for z in d["rows"])!=d["rank"] or
                any(row and ((row&((1<<len(d["rows"]))-1))&
                    -(row&((1<<len(d["rows"]))-1))).bit_length()-1!=i
                    for i,row in enumerate(d["rows"]))):
                raise ValueError("ST8_CONVENTIONAL_BAD_CHECKPOINT")
            m=cls(d["mode"])
            for k in keys-{"schema","mode"}:
                setattr(m,k,d[k])
            if m.snapshot()!=raw:
                raise ValueError("ST8_CONVENTIONAL_NONCANONICAL_STATE")
            return m
        except (TypeError,KeyError,OverflowError) as e:
            raise ValueError("ST8_CONVENTIONAL_COLD_RESTORE_FAIL") from e

    def accounting(self):
        return {
            "GF2_full_cubic_rows_max":92,
            "learned_augmented_bits_max":92*100,
            "learned_rows_aligned_bytes_max":92*13,
            "learned_public_replay_pair_bytes_max":512
                if self.mode=="adaptive" else 0,
            "stored_public_pairs":len(self.buffer),
            "original_frozen_source_private_law_seen":False,
            "checkpoint_json_bytes":len(self.snapshot().encode("utf-8"))
        }


def models():
    from research.nci04_st8.native_growth import NativeGrow8
    return {
        "candidate":NativeGrow8("growth"),
        "full_cubic":ConventionalGF2("full_cubic"),
        "adaptive_conventional":ConventionalGF2("adaptive"),
        "st7_quadratic":NativeInductive8("causal"),
        "no_growth":NativeGrow8("no_growth"),
        "no_replay":NativeGrow8("no_replay"),
        "erase":NativeGrow8("erase")
    }


def restore_one(name,raw):
    from research.nci04_st8.native_growth import NativeGrow8
    if name in ("full_cubic","adaptive_conventional"):
        m=ConventionalGF2.restore(raw)
        if m.mode!=("full_cubic" if name=="full_cubic" else "adaptive"):
            raise ValueError("ST8_INVALID_CONVENTIONAL_CUSTODY")
        return m
    if name=="st7_quadratic":
        m=NativeInductive8.restore(raw)
        if m.variant!="causal":
            raise ValueError("ST8_WRONG_PARENT_QUADRATIC_MODEL")
        return m
    m=NativeGrow8.restore(raw)
    if m.variant!=("growth" if name=="candidate" else name):
        raise ValueError("ST8_WRONG_NATIVE_ABLATION")
    return m


def restored_models(snapshot):
    if type(snapshot) is not dict or set(snapshot)!=set(models()):
        raise ValueError("ST8_INCOMPLETE_FROZEN_TRAINED_COHORT")
    restored={n:restore_one(n,raw) for n,raw in snapshot.items()}
    if any(restored[n].snapshot()!=snapshot[n] for n in restored):
        raise ValueError("ST8_TRAINEE_COLD_CUSTODY_MISMATCH")
    return restored
