"""ST8 tokenless native eight-cell causal substrate with evidence-triggered growth.

Initial 36-feature quadratic GF2 model. A REAL observed future-consequence
contradiction triggers structural expansion to 92 cubic features and
replays a bounded cache of authentic public (B, residual) experiences.
Never imports the source/private true coefficients; the cubic feature
family is a declared upper inductive bias, not a discovered universal law.

The frozen no-replay ablation may eventually catch up on ample training:
that is a valid DEV_NO_GO and must not be tuned away.
"""
import json

SCHEMA="yggdrasil.nci04.st8.native-contradiction-growth.v1"
ACTOR=(3,0,1,2,3)
MAX_UPDATES=10000000
MAX_CACHE=256
VARIANTS=("growth","no_growth","no_replay","erase")


def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False)


def public_byte(v):
    if (type(v) not in (tuple,list) or len(v)!=8 or
        any(type(x) is not int or x not in (0,1) for x in v)):
        raise ValueError("ST8_NATIVE_INVALID_PUBLIC_BITS")
    return sum(z<<j for j,z in enumerate(v))


def rotate(x,k):
    if (type(x) is not int or x not in range(256) or
        type(k) is not int or k not in (1,2,3)):
        raise ValueError("ST8_NATIVE_BAD_PUBLIC_ROTATION")
    return ((x<<k)|(x>>(8-k)))&255


def features(B,degree):
    if (type(B) is not int or B not in range(256) or
        type(degree) is not int or degree not in (2,3)):
        raise ValueError("ST8_NATIVE_BAD_PUBLIC_FEATURE_REQUEST")
    bs=[(B>>j)&1 for j in range(8)]
    a=list(bs)
    a.extend(bs[j]&bs[k] for j in range(8) for k in range(j+1,8))
    if degree==3:
        a.extend(bs[j]&bs[k]&bs[l] for j in range(8)
                 for k in range(j+1,8) for l in range(k+1,8))
    if len(a)!=(36 if degree==2 else 92):
        raise ValueError("ST8_NATIVE_FEATURE_BASIS_SIZE")
    return sum(bit<<i for i,bit in enumerate(a))


class NativeGrow8:
    def __init__(self,variant="growth"):
        if variant not in VARIANTS:
            raise ValueError("ST8_NATIVE_INVALID_ABLATION")
        self.variant=variant
        self.degree=2
        self.basis=[0]*36
        self.rank=0
        self.public_buffer=[]
        self.updates=0
        self.contradictions=0
        self.post_growth_conflicts=0
        self.growths=0
        self.first_growth_on_update=None
        self.rotation=None
        self.A=None
        self.B=None
        self.step=0

    def reset_episode(self):
        if self.variant=="erase":
            self.degree=2
            self.basis=[0]*36
            self.rank=0
            self.public_buffer=[]
            self.growths=0
            self.first_growth_on_update=None
        self.rotation=None
        self.A=None
        self.B=None
        self.step=0

    def _reduce(self,feature,value=0):
        n=len(self.basis)
        if (type(feature) is not int or not 0<=feature<(1<<n) or
            type(value) is not int or value not in range(256)):
            raise ValueError("ST8_NATIVE_INCONSISTENT_FEATURE_SPACE")
        row=feature|(value<<n)
        featuremask=(1<<n)-1
        while row&featuremask:
            pivot=(row&featuremask).bit_length()-1
            if self.basis[pivot]:
                row^=self.basis[pivot]
            else:
                return "NEW",pivot,row
        if row>>n:
            return "CONTRADICTION",None,row
        return "KNOWN",None,row

    def _add(self,component,output):
        mode,pivot,row=self._reduce(features(component,self.degree),output)
        if mode=="NEW":
            self.basis[pivot]=row
            self.rank+=1
        return mode

    def _buffer(self,B,Y):
        for i,(b,value) in enumerate(self.public_buffer):
            if b==B:
                if value!=Y:
                    raise ValueError("ST8_NATIVE_PUBLIC_RULE_CHANGED_WITHIN_TRAIN")
                return
        if len(self.public_buffer)>=MAX_CACHE:
            raise ValueError("ST8_NATIVE_PUBLIC_EXPERIENCE_LIMIT")
        self.public_buffer.append([B,Y])

    def _grow(self,current_B,current_output):
        self.degree=3
        self.basis=[0]*92
        self.rank=0
        self.growths+=1
        self.first_growth_on_update=self.updates
        experiences=(
            list(self.public_buffer) if self.variant!="no_replay"
            else [[current_B,current_output]]
        )
        if self.variant=="no_replay":
            self.public_buffer=[[current_B,current_output]]
        for B,Y in experiences:
            status=self._add(B,Y)
            if status=="CONTRADICTION":
                self.post_growth_conflicts+=1

    def predict(self,public,action):
        x=public_byte(public)
        if (type(action) is not int or action not in (0,1,2,3) or
            self.step>=5 or action!=ACTOR[self.step]):
            raise ValueError("ST8_NATIVE_OUT_OF_ORDER_PUBLIC_ACTION")
        if self.step!=4 or None in (self.rotation,self.A,self.B):
            return [.5]*8
        # Inference eliminates only PUBLIC feature bits. The residual
        # output label is the learned prediction, not a contradiction.
        n=len(self.basis)
        mask=(1<<n)-1
        row=features(self.B,self.degree)
        while row&mask:
            pivot=(row&mask).bit_length()-1
            if not self.basis[pivot]:
                return [.5]*8
            row^=self.basis[pivot]
        predicted=x^rotate(x,self.rotation)^self.A^((row>>n)&255)
        return [.99 if ((predicted>>j)&1) else .01 for j in range(8)]

    def observe(self,public,action,target,after,*,train=True):
        x=public_byte(public)
        y=public_byte(after)
        t=public_byte(target)
        if (type(train) is not bool or type(action) is not int or
            self.step>=5 or action!=ACTOR[self.step] or x^y!=t):
            raise ValueError("ST8_NATIVE_UNAUTHENTIC_PUBLIC_ACTION_CONSEQUENCE")
        pred=self.predict(public,action)
        if self.step==0:
            opts=[k for k in (1,2,3) if rotate(x,k)==y]
            self.rotation=opts[0] if len(opts)==1 else None
        elif self.step==1 and self.rotation is not None:
            self.A=y^rotate(x,self.rotation)
        elif self.step==2 and self.rotation is not None:
            self.B=y^rotate(x,self.rotation)
        elif self.step==4 and train and None not in (
            self.rotation,self.A,self.B
        ):
            if self.updates>=MAX_UPDATES:
                raise ValueError("ST8_NATIVE_TRAIN_BUDGET_EXCEEDED")
            self.updates+=1
            residual=y^rotate(x,self.rotation)^self.A
            self._buffer(self.B,residual)
            status=self._add(self.B,residual)
            if status=="CONTRADICTION":
                if self.degree==2:
                    self.contradictions+=1
                    if self.variant!="no_growth":
                        self._grow(self.B,residual)
                else:
                    self.post_growth_conflicts+=1
        self.step+=1
        return pred

    def snapshot(self):
        return canonical({
            "schema":SCHEMA,"variant":self.variant,
            "degree":self.degree,"basis":self.basis,"rank":self.rank,
            "public_buffer":self.public_buffer,
            "updates":self.updates,"contradictions":self.contradictions,
            "post_growth_conflicts":self.post_growth_conflicts,
            "growths":self.growths,
            "first_growth_on_update":self.first_growth_on_update,
            "rotation":self.rotation,"A":self.A,"B":self.B,
            "step":self.step
        })

    @classmethod
    def restore(cls,raw):
        if type(raw) is not str or len(raw)>12500:
            raise ValueError("ST8_NATIVE_INVALID_COLD_LENGTH")
        try:
            d=json.loads(raw)
            keys={"schema","variant","degree","basis","rank","public_buffer",
                  "updates","contradictions","post_growth_conflicts",
                  "growths","first_growth_on_update","rotation","A","B","step"}
            if (type(d) is not dict or set(d)!=keys or
                d["schema"]!=SCHEMA or d["variant"] not in VARIANTS or
                type(d["degree"]) is not int or d["degree"] not in (2,3) or
                type(d["basis"]) is not list or
                len(d["basis"])!=(36 if d["degree"]==2 else 92) or
                any(type(row) is not int or not 0<=row<
                    (1<<(len(d["basis"])+8)) for row in d["basis"]) or
                type(d["public_buffer"]) is not list or
                len(d["public_buffer"])>MAX_CACHE or
                any(type(pair) is not list or len(pair)!=2 or
                    any(type(v) is not int or v not in range(256)
                        for v in pair) for pair in d["public_buffer"]) or
                len({pair[0] for pair in d["public_buffer"]})!=len(d["public_buffer"]) or
                any(type(d[k]) is not int or not 0<=d[k]<=MAX_UPDATES
                    for k in ("rank","updates","contradictions",
                              "post_growth_conflicts","growths","step")) or
                d["rank"]>len(d["basis"]) or d["step"]>5 or
                d["growths"]>1 or
                (d["first_growth_on_update"] is not None and
                 (type(d["first_growth_on_update"]) is not int or
                  not 0<=d["first_growth_on_update"]<=d["updates"])) or
                (d["degree"]==2)!=(d["growths"]==0) or
                (d["growths"]==0)!=(d["first_growth_on_update"] is None) or
                (d["rotation"] is not None and
                 (type(d["rotation"]) is not int or
                  d["rotation"] not in (1,2,3))) or
                any(d[k] is not None and
                    (type(d[k]) is not int or d[k] not in range(256))
                    for k in ("A","B")) or
                sum(int(row!=0) for row in d["basis"])!=d["rank"] or
                any(row and (row&((1<<len(d["basis"]))-1)).bit_length()-1!=i
                    for i,row in enumerate(d["basis"]))):
                raise ValueError("ST8_NATIVE_COLD_SHAPE")
            m=cls(d["variant"])
            for k in keys-{"schema","variant"}:
                setattr(m,k,d[k])
            if m.snapshot()!=raw:
                raise ValueError("ST8_NATIVE_NONCANONICAL_SNAPSHOT")
            return m
        except (TypeError,KeyError,OverflowError) as e:
            raise ValueError("ST8_NATIVE_RESTORE_FAILED") from e

    def accounting(self):
        return {
            "native_cells":8,
            "initial_quadratic_features":36,
            "maximum_cubic_features":92,
            "learned_GF2_augmented_bits_max":92*100,
            "learned_GF2_rows_aligned_bytes_max":92*13,
            "learned_public_replay_pair_bytes_max":MAX_CACHE*2,
            "cached_public_pairs":len(self.public_buffer),
            "growth_event_count":self.growths,
            "cold_snapshot_json_bytes":len(self.snapshot().encode("utf-8")),
            "source_private_coefficients_seen":False,
            "constant_correct_polynomial_oracle_menu":0,
            "integer_state_only":True
        }
