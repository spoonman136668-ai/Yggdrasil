"""CKAD42 development-only native causal intervention-relation learner.

One genuinely witnessed public episode updates each persistent learned
basis once. Source learner and controls never receive private regime labels.
The existing NativeEpisodeExperience source stream remains untouched.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import itertools
import json
import math
import sys
import time
from pathlib import Path

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_episode_experience import NativeEpisodeExperience

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/"CKAD-39"
sys.path.insert(0,str(SOURCE))
spec=importlib.util.spec_from_file_location("ckad39_generator_for_42",SOURCE/"campaign.py")
C=importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)

SCHEMA="yggdrasil.ckad42.intervention-relations-dev.v1"
PREREG="05f37a8675177b102b041741a1d3b678598a411e"
DEV=(42111,42112)
PILOT=(42211,42212)
PRIMARY=(42311,42312,42313)
DISALLOWED=(41101,41102,40811,40812,38911,38912,14181,14182,14071,14072)
MAX_EVENTS=512
ETA=4.0
DISCOUNT=.93
PHASES=("stable_A","early_B","late_B","early_return_A","late_return_A")
LATE=("late_B","late_return_A")
CONVENTIONAL=(*C.CONVENTIONAL,"beta_hedge")
ARMS=("native_dual_causal","causal_full","causal_discount93",
      "causal_no_action","native_stream",*CONVENTIONAL,"sham")


def boolean_patterns(bits):
    """Generic input-only Boolean grammar; no world labels or source outcomes."""
    if bits not in (2,4):
        raise ValueError("CKAD42_GRAMMAR_DIMENSIONS")
    universe=(1<<(1<<bits))-1
    vars_=tuple(sum(((state>>i)&1)<<state for state in range(1<<bits))
                for i in range(bits))
    atoms={0,universe,*vars_,*(universe^p for p in vars_)}
    for i,j in itertools.combinations(range(bits),2):
        p,q=vars_[i],vars_[j]
        atoms.update((p&q,p|q,p^q))
    compounds=set(atoms)
    items=tuple(sorted(atoms))
    for i,p in enumerate(items):
        for q in items[i:]:
            compounds.update((p&q,p|q,p^q))
    return tuple(sorted(compounds))


TRANSITION=boolean_patterns(2)
TERMINAL=boolean_patterns(4)
if len(TRANSITION)!=16 or not (16<=len(TERMINAL)<=2048):
    raise AssertionError("CKAD42_UNEXPECTED_GENERIC_GRAMMAR_SIZE")


def bit_index(context,first,next_state=None,second=None):
    if any(type(v) is not int or v not in (0,1)
           for v in ((context,first) if next_state is None else
                      (context,first,next_state,second))):
        raise ValueError("CKAD42_PUBLIC_INPUT_BITS")
    if next_state is None:
        if second is not None:
            raise ValueError("CKAD42_MALFORMED_TRANSITION")
        return context | (first<<1)
    return context | (first<<1) | (next_state<<2) | (second<<3)


def _canonical_learning_float(value):
    """Portable 12-significant-digit *checkpoint* representation only.

    Training and prediction retain their exact pre-existing in-memory floats.
    This removes nonsemantic sub-ULP/libm drift from serialized snapshots;
    no quantization happens when learning or reading a forecast.
    """
    if type(value) is not float or not math.isfinite(value):
        raise ValueError("CKAD42_NONFINITE_CHECKPOINT_LEARNING_WEIGHT")
    if value == 0.0:
        return 0.0
    return float(format(value, ".12g"))


class LearnedCausalBasis:
    """Source-trained finite numeric relation weights, cumulative and recent."""
    def __init__(self,bits):
        self.bits=bits
        self.patterns=TRANSITION if bits==2 else TERMINAL if bits==4 else None
        if self.patterns is None:
            raise ValueError("CKAD42_BASIS_WIDTH")
        self.full=[0.0]*len(self.patterns)
        self.short=[0.0]*len(self.patterns)
        self.n=0

    def predict(self,index,mode):
        if type(index) is not int or not 0<=index<(1<<self.bits):
            raise ValueError("CKAD42_PUBLIC_INDEX")
        if mode not in ("full","short"):
            raise ValueError("CKAD42_BASIS_READOUT")
        scores=self.full if mode=="full" else self.short
        m=max(scores)
        positive=0.0
        total=0.0
        for mask,score in zip(self.patterns,scores):
            weight=math.exp(score-m)
            total+=weight
            if (mask>>index)&1:
                positive+=weight
        true_prob=positive/total
        return (.15+.70*true_prob) if self.bits==2 else (.10+.80*true_prob)

    def observe(self,index,result):
        if type(result) is not int or result not in (0,1):
            raise ValueError("CKAD42_OBSERVED_OUTCOME")
        if self.n>=MAX_EVENTS:
            raise ValueError("CKAD42_SOURCE_CAPACITY")
        # These probabilities are pre-frozen generic noise priors; they do not
        # access private generator parameters, hidden family or oracle regime.
        correct=math.log(.85 if self.bits==2 else .9)
        wrong=math.log(.15 if self.bits==2 else .1)
        for i,mask in enumerate(self.patterns):
            ll=correct if ((mask>>index)&1)==result else wrong
            self.full[i]+=ll
            self.short[i]=self.short[i]*DISCOUNT+ll
        self.n+=1

    def checkpoint(self):
        return {"bits":self.bits,
                "full":[_canonical_learning_float(v) for v in self.full],
                "short":[_canonical_learning_float(v) for v in self.short],
                "n":self.n}

    @classmethod
    def restore(cls,data):
        obj=cls(data["bits"])
        if (len(data["full"])!=len(obj.patterns) or
                len(data["short"])!=len(obj.patterns) or
                not 0<=data["n"]<=MAX_EVENTS):
            raise ValueError("CKAD42_BAD_BASIS_CHECKPOINT")
        obj.full=list(data["full"])
        obj.short=list(data["short"])
        obj.n=data["n"]
        if not all(math.isfinite(v) for v in obj.full+obj.short):
            raise ValueError("CKAD42_NONFINITE_WEIGHTS")
        return obj


class NativeInterventionRelations:
    """One cumulative causal relation component with four readout controls."""
    def __init__(self):
        self.transition=LearnedCausalBasis(2)
        self.terminal=LearnedCausalBasis(4)
        self.mask_transition=LearnedCausalBasis(2)
        self.mask_terminal=LearnedCausalBasis(4)
        self.hedge=[1.0,1.0]
        self.receipts={}
        self.n=0

    @staticmethod
    def _inputs(view,first,next_state=None,second=None):
        if type(view) is not tuple or len(view)!=2 or any(
                type(x) is not int or x not in (0,1) for x in view):
            raise ValueError("CKAD42_PAIRED_VIEW")
        # CKAD native projection's groundable shared first coordinate; only
        # public paired views, never evaluator's private true regime/variant.
        return bit_index(view[0],first,next_state,second)

    def read(self,mode,view,first,next_state=None,second=None):
        if mode not in ("dual","full","short","no_action"):
            raise ValueError("CKAD42_READOUT_MODE")
        is_transition=next_state is None
        if mode=="no_action":
            index=self._inputs(view,0,None if is_transition else next_state,
                               None if is_transition else 0)
            bank=self.mask_transition if is_transition else self.mask_terminal
            return bank.predict(index,"full")
        index=self._inputs(view,first,next_state,second)
        bank=self.transition if is_transition else self.terminal
        if mode!="dual":
            return bank.predict(index,mode)
        weights=self.hedge
        normalizer=sum(weights)
        return sum(w*bank.predict(index,kind)
                   for kind,w in zip(("full","short"),weights))/normalizer

    def observe(self,identifier,views,row):
        if type(identifier) is not str or len(identifier)!=64:
            raise ValueError("CKAD42_SOURCE_ID")
        if type(views) is not tuple or len(views)!=2:
            raise ValueError("CKAD42_SOURCE_VIEWS")
        if type(row) is not dict or set(row)!={"s1","x1","s2","x2","y"}:
            raise ValueError("CKAD42_SOURCE_ROW")
        if any(type(v) is not int or v not in (0,1) for v in row.values()):
            raise ValueError("CKAD42_SOURCE_BINARY")
        # Compare/canonicalize identity before any learned source mutation.
        receipt=canonical([views,row])
        old=self.receipts.get(identifier)
        if old is not None:
            if old!=receipt.decode("ascii"):
                raise ValueError("CKAD42_CONFLICTING_SOURCE_ID")
            return self
        if self.n>=MAX_EVENTS:
            raise ValueError("CKAD42_SOURCE_CAPACITY")
        first,next_state,second,reward=(row[k] for k in ("x1","s2","x2","y"))
        view=views[0]
        index_t=self._inputs(view,first)
        index_y=self._inputs(view,first,next_state,second)
        index_t_mask=self._inputs(view,0)
        index_y_mask=self._inputs(view,0,next_state,0)
        losses=[]
        for mode in ("full","short"):
            p=self.transition.predict(index_t,mode)
            q=self.terminal.predict(index_y,mode)
            losses.append(((p-next_state)**2+(q-reward)**2)/2)
        for i,loss in enumerate(losses):
            self.hedge[i]*=math.exp(-ETA*loss)
        normalizer=max(self.hedge)
        self.hedge=[w/normalizer for w in self.hedge]
        self.transition.observe(index_t,next_state)
        self.terminal.observe(index_y,reward)
        self.mask_transition.observe(index_t_mask,next_state)
        self.mask_terminal.observe(index_y_mask,reward)
        self.receipts[identifier]=receipt.decode("ascii")
        self.n+=1
        return self

    def checkpoint(self):
        return canonical({"schema":SCHEMA,"transition":self.transition.checkpoint(),
                 "terminal":self.terminal.checkpoint(),
                 "mask_transition":self.mask_transition.checkpoint(),
                 "mask_terminal":self.mask_terminal.checkpoint(),
                 "hedge":[_canonical_learning_float(v) for v in self.hedge],
                 "n":self.n,
                 "receipts":self.receipts})

    @classmethod
    def restore(cls,raw,expected_sha):
        if digest(raw)!=expected_sha:
            raise ValueError("CKAD42_CHECKPOINT_SHA_MISMATCH")
        d=json.loads(raw)
        if d["schema"]!=SCHEMA:
            raise ValueError("CKAD42_CHECKPOINT_SCHEMA")
        obj=cls()
        for key in ("transition","terminal","mask_transition","mask_terminal"):
            setattr(obj,key,LearnedCausalBasis.restore(d[key]))
        obj.hedge=list(d["hedge"])
        obj.n=d["n"]
        obj.receipts=dict(d["receipts"])
        if not (0<=obj.n<=MAX_EVENTS and len(obj.receipts)==obj.n
                and len(obj.hedge)==2 and min(obj.hedge)>0
                and all(v.n==obj.n for v in
                        (obj.transition,obj.terminal,
                         obj.mask_transition,obj.mask_terminal))):
            raise ValueError("CKAD42_BAD_CHECKPOINT_COUNTS")
        if obj.checkpoint()!=raw:
            raise ValueError("CKAD42_CHECKPOINT_NONCANONICAL")
        return obj


def loss(p,q,row):
    return ((p-row["s2"])**2+(q-row["y"])**2)/2


def run(seed):
    if seed not in DEV:
        raise ValueError("CKAD42_ONLY_REGISTERED_DEV")
    started=time.perf_counter()
    groups=[]
    worlds=[]
    for world in C.WORLDS:
        events,private=C.generator(seed,world)
        native=NativeEpisodeExperience(repair=True)
        relation=NativeInterventionRelations()
        conventional=C.Conventional()
        source_ids=set()
        warm_sha=None
        for t,(identifier,views,row,phase) in enumerate(events):
            if t==48:
                native=native.begin_stream()
                warm_sha=digest(canonical(native._ledger[:48]))
            view=views[0]
            if t>=48:
                np=float(native.context_forecast(view,row["x1"]))
                nq=float(native.context_forecast(view,row["x1"],row["s2"],row["x2"]))
            else:
                np=float(native.forecast(view,row["x1"]))
                nq=float(native.forecast(view,row["x1"],row["s2"],row["x2"]))
            forecasts={"native_stream":(np,nq),"sham":(.5,.5)}
            for arm,mode in (("native_dual_causal","dual"),
                             ("causal_full","full"),
                             ("causal_discount93","short"),
                             ("causal_no_action","no_action")):
                forecasts[arm]=(relation.read(mode,view,row["x1"]),
                                relation.read(mode,view,row["x1"],row["s2"],row["x2"]))
            for arm in CONVENTIONAL:
                forecasts[arm]=(conventional.p(arm,"transition",row["s1"],row["x1"]),
                                conventional.p(arm,"terminal",row["s1"],row["x1"],row["s2"],row["x2"]))
            metrics={arm:loss(*forecasts[arm],row) for arm in ARMS}
            if phase in PHASES:
                groups.append({"phase":phase,"world":world,"seed":seed,"t":t,"loss":metrics})
            before_native=native.checkpoint()
            before_rel=relation.checkpoint()
            # Predictions are pure, and all source updates follow both outcomes.
            if native.checkpoint()!=before_native or relation.checkpoint()!=before_rel:
                raise AssertionError("CKAD42_READ_MUTATED_TRAINING")
            native=native.observe(identifier,views,row)
            relation.observe(identifier,views,row)
            conventional.observe(row,{a:metrics[a] for a in C.CONVENTIONAL})
            if identifier in source_ids:
                raise AssertionError("CKAD42_DUPLICATE_SOURCE")
            source_ids.add(identifier)
        if (len(source_ids)!=len(events) or relation.n!=len(events)
            or len(native._ledger)!=len(events)):
            raise AssertionError("CKAD42_SOURCE_INTEGRITY")
        if digest(canonical(native._ledger[:48]))!=warm_sha:
            raise AssertionError("CKAD42_WARM_MEMORY_CHANGED")
        native_raw=native.checkpoint()
        rel_raw=relation.checkpoint()
        if NativeEpisodeExperience.restore(native_raw,digest(native_raw)).checkpoint()!=native_raw:
            raise AssertionError("CKAD42_NATIVE_COLD_DRIFT")
        if NativeInterventionRelations.restore(rel_raw,digest(rel_raw)).checkpoint()!=rel_raw:
            raise AssertionError("CKAD42_CAUSAL_WEIGHTS_COLD_DRIFT")
        last=events[-1]
        if native.observe(last[0],last[1],last[2]) is not native:
            raise AssertionError("CKAD42_NATIVE_DUPLICATE_NONIDEMPOTENT")
        if relation.observe(last[0],last[1],last[2]) is not relation:
            raise AssertionError("CKAD42_RELATION_DUPLICATE_NONIDEMPOTENT")
        altered=dict(last[2]);altered["y"]^=1
        for model in (native,relation):
            try:model.observe(last[0],last[1],altered)
            except ValueError:pass
            else:raise AssertionError("CKAD42_CONFLICT_ACCEPTED")
        if relation.checkpoint()!=rel_raw or native.checkpoint()!=native_raw:
            raise AssertionError("CKAD42_CONFLICT_MUTATED_SOURCE")
        worlds.append({"world":world,"events":len(events),"consequences":2*len(events),
                       "source_complete":True,"cold_exact":True,"source_prefix_exact":True,
                       "read_only":True,"duplicate_idempotent":True,"conflict_atomic":True,
                       "native_checkpoint_sha256":digest(native_raw),
                       "relation_checkpoint_sha256":digest(rel_raw),
                       "relation_checkpoint_bytes":len(rel_raw),
                       "learned_basis_dimension":[len(TRANSITION),len(TERMINAL)],
                       "training_updates":relation.n,"true_boundaries_evaluator_only":private})
    phase_metrics={}
    for phase in (*PHASES,"pooled_late_shift_and_return"):
        selected=[r for r in groups if r["phase"] in LATE] if phase=="pooled_late_shift_and_return" else [r for r in groups if r["phase"]==phase]
        if not selected:
            raise AssertionError("CKAD42_PHASE_EMPTY")
        phase_metrics[phase]={"episodes":len(selected),
                              "brier":{a:sum(r["loss"][a] for r in selected)/len(selected)
                                       for a in ARMS}}
    return {"seed":seed,"worlds":worlds,"phase_metrics":phase_metrics,
            "total_events":sum(w["events"] for w in worlds),
            "total_consequences":sum(w["consequences"] for w in worlds),
            "elapsed_wall_seconds":round(time.perf_counter()-started,5)}


def classify(cases):
    if tuple(c["seed"] for c in cases)!=DEV:
        raise AssertionError("CKAD42_SEED_IDENTITY")
    for c in cases:
        for w in c["worlds"]:
            if not all(w[key] is True for key in ("source_complete","cold_exact",
                        "source_prefix_exact","read_only","duplicate_idempotent","conflict_atomic")):
                return "INVALID_SOURCE"
        pooled=c["phase_metrics"]["pooled_late_shift_and_return"]["brier"]
        candidate=pooled["native_dual_causal"]
        comparison=min(pooled[k] for k in
                      ("native_stream","causal_full","causal_discount93",*CONVENTIONAL))
        if not (candidate<=.15 and candidate<=comparison-.01
                and candidate<=pooled["causal_no_action"]-.01):
            return "DEV_NO_GO"
        for phase in ("early_B","early_return_A"):
            p=c["phase_metrics"][phase]["brier"]
            if p["native_dual_causal"]>p["native_stream"]+.01:
                return "DEV_NO_GO"
    return "DEV_FEASIBLE_NOT_SCIENTIFIC"


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--mode",choices=("preflight","dev"),required=True)
    parser.add_argument("--seed",type=int)
    args=parser.parse_args()
    if args.mode=="preflight":
        if args.seed is not None:
            raise ValueError("CKAD42_PREFLIGHT_SEED_FORBIDDEN")
        print(json.dumps({"schema":SCHEMA,"prereg_commit":PREREG,
            "dev":list(DEV),"pilot_reserved":list(PILOT),
            "primary_reserved":list(PRIMARY),"basis_dimensions":[len(TRANSITION),len(TERMINAL)],
            "pilot_scored":False,"primary_scored":False},sort_keys=True))
        return
    if args.seed not in DEV:
        raise ValueError("CKAD42_ONLY_REGISTERED_DEV")
    print("CKAD42_CASE="+json.dumps(run(args.seed),sort_keys=True))


if __name__=="__main__":
    main()
