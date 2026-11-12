"""WSP54 exploratory gradientless causal compiler: raw bits -> grounded circuit.

No generator/source import, pretrained representations, oracle word boundaries,
latent semantic labels or gradient updates. Uses learner-visible physical states,
a declared bounded prefix-free three-segment prior, modular additive hypothesis
class and exact bounded constraint search. NONCOMMUTING is fail-closed pending
a separately identified operator-hypothesis compiler; not a scientific result.
"""
from __future__ import annotations
from hashlib import sha256
from itertools import product
import json

MAX_NODES=300000
MAX_MODELS=512
MAX_ACTIONS=60
MAX_SNAPSHOT=3000000
FAMILIES=("anchored_effect","noncommuting_order")

def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True)

def validate_state(row,family):
    if family not in FAMILIES or type(row) is not tuple:
        raise ValueError("invalid family or physical state")
    n=16 if family=="anchored_effect" else 8
    if len(row)!=n or any(type(v) is not int for v in row):
        raise ValueError("invalid physical dimensions")
    if any(v<0 or v>=(4 if family=="anchored_effect" else 7) for v in row[:8]):
        raise ValueError("bad position")
    if family=="anchored_effect" and any(v<0 or v>=3 for v in row[8:]):
        raise ValueError("bad orientation")
    return row

def validate_raw(raw):
    if type(raw) is not str or not 12<=len(raw)<=18 or set(raw)-{"0","1"}:
        raise ValueError("invalid raw acoustic stream")
    return raw

def splits(raw):
    validate_raw(raw)
    return tuple((raw[:a],raw[a:a+b],raw[a+b:]) for a,b,c in
                 product((4,5,6),repeat=3) if a+b+c==len(raw))

def grounded_entity(before,after):
    changed={i%8 for i in range(len(before)) if before[i]!=after[i]}
    return next(iter(changed)) if len(changed)==1 else None

def prefix_compatible(code,existing):
    return all(not (code.startswith(x) or x.startswith(code)) for x in existing)

class BudgetExceeded(Exception):
    pass

class GradientlessCausalCompiler:
    """Finite evidence-consistent A circuit; B phase role re-binding.

    Each hypothesis stores integer matrices as a factorized physical update:
    position = (destination_bias + verb_offset) mod4, orientation += verb_delta
    mod3. These values are inferred from charged observations, not initialized
    with the source world's destination/verb labels.
    """
    gradient_steps=0

    def __init__(self,*,family):
        validate_state((0,)*(16 if family=="anchored_effect" else 8),family)
        self.family=family
        self.a=[]
        self.b=[]
        self.sealed_a=False
        self.sealed_b=False
        self.incomplete=False
        self.nodes=0
        self.hypotheses=[]
        self.b_hypotheses=[]
        self.phase="A"

    @property
    def actions(self):
        return len(self.a)+len(self.b)

    def observe(self,row):
        if self.sealed_b or self.actions>=MAX_ACTIONS:
            raise ValueError("intervention limit or finalized model")
        b=validate_state(row.before,self.family)
        a=validate_state(row.after,self.family)
        s=validate_raw(row.acoustic_bits)
        if type(row.action_cost) is not int or row.action_cost!=1 or type(row.reset_cost) is not int or row.reset_cost!=0:
            raise ValueError("unaccounted action")
        if not self.sealed_a and len(self.a)>=48:
            raise ValueError("seal A after exactly 48 interventions")
        if self.sealed_a and len(self.b)>=12:
            raise ValueError("B intervention limit")
        (self.b if self.sealed_a else self.a).append((b,s,a))

    def _tick(self):
        self.nodes+=1
        if self.nodes>MAX_NODES:
            raise BudgetExceeded("candidate node bound")

    def _entity_options(self, rows,slot):
        labeled=[(grounded_entity(b,a),splits(s)) for b,s,a in rows]
        by_e={e:[parts for label,parts in labeled if label==e]
              for e in range(8)}
        if any(not v for v in by_e.values()):
            return []
        options={}
        for e,choices in by_e.items():
            common=set(p[slot] for p in choices[0])
            for row in choices[1:]:
                common.intersection_update(p[slot] for p in row)
            if not common:
                return []
            ranked=sorted(common,key=lambda w:(
                sum(any(w==p[slot] for p in arr)
                    for other,other_rows in by_e.items() if other!=e
                    for arr in other_rows),-len(w),w))
            options[e]=ranked[:3]
        out=[]
        for chosen in product(*(options[e] for e in range(8))):
            self._tick()
            if all(prefix_compatible(w,chosen[:i]) for i,w in enumerate(chosen)):
                out.append({w:i for i,w in enumerate(chosen)})
            if len(out)>MAX_MODELS:
                raise BudgetExceeded("too many entity maps")
        return out

    def _learn_anchored(self):
        candidates=[]
        for entity_slot in range(3):
            for entity_map in self._entity_options(self.a,entity_slot):
                entries=[]
                for b,s,a in self.a:
                    entity=grounded_entity(b,a)
                    if entity is None:
                        continue
                    word=next((w for w,e in entity_map.items() if e==entity),None)
                    parts=[p for p in splits(s) if p[entity_slot]==word]
                    if not parts:
                        break
                    entries.append((parts,entity,(a[8+entity]-b[8+entity])%3,a[entity]))
                else:
                    if len(entries)<24:
                        continue
                    for verb_slot in range(3):
                        if verb_slot==entity_slot:
                            continue
                        dest_slot=3-entity_slot-verb_slot
                        for f1 in range(4):
                            for f2 in range(4):
                                offsets=(0,f1,f2)
                                # Build all evidence-consistent word->physical-effect
                                # assignments. Fail closed if enumeration hits caps.
                                def dfs(pending,verbs,dests):
                                    self._tick()
                                    if not pending:
                                        if len(verbs)!=3 or len(dests)!=4:
                                            return
                                        h={"entity_slot":entity_slot,"verb_slot":verb_slot,
                                           "entity_map":entity_map,"verbs":verbs.copy(),
                                           "destinations":dests.copy(),"offsets":offsets}
                                        candidates.append(h)
                                        if len(candidates)>MAX_MODELS:
                                            raise BudgetExceeded("hypothesis cap")
                                        return
                                    chosen=None;valid=None
                                    for index,(parts,_,delta,target) in enumerate(pending):
                                        matches=[]
                                        for p in parts:
                                            word_v,word_d=p[verb_slot],p[dest_slot]
                                            base=(target-offsets[delta])%4
                                            if (word_v in verbs and verbs[word_v]!=delta) or (word_d in dests and dests[word_d]!=base):
                                                continue
                                            if word_v not in verbs and (len(verbs)==3 or
                                                    not prefix_compatible(word_v,tuple(entity_map)+tuple(verbs)+tuple(dests))):
                                                continue
                                            if word_d not in dests and (len(dests)==4 or
                                                    not prefix_compatible(word_d,tuple(entity_map)+tuple(verbs)+tuple(dests)+(word_v,))):
                                                continue
                                            matches.append((word_v,word_d,base))
                                        if not matches:
                                            return
                                        if valid is None or len(matches)<len(valid):
                                            chosen=index;valid=matches
                                            if len(matches)==1:
                                                break
                                    rest=pending[:chosen]+pending[chosen+1:]
                                    for v,d,base in valid:
                                        v2=verbs.copy();d2=dests.copy()
                                        v2[v]=pending[chosen][2];d2[d]=base
                                        dfs(rest,v2,d2)
                                dfs(entries,{}, {})
        return candidates

    def seal_a(self):
        if self.sealed_a or len(self.a)!=48:
            raise ValueError("exactly 48 A interventions required")
        try:
            if self.family=="anchored_effect":
                self.hypotheses=self._learn_anchored()
            else:
                # No defensible noncommuting operator model implemented yet.
                # An explicit abstention is safer than inferring the wrong order.
                self.hypotheses=[]
        except BudgetExceeded:
            self.incomplete=True;self.hypotheses=[]
        self.sealed_a=True
        return {"nodes":self.nodes,"hypotheses":len(self.hypotheses),
                "incomplete":self.incomplete,"gradient_steps":self.gradient_steps}

    @staticmethod
    def _infer(before,raw,h):
        answers=set()
        entity_slot=h["entity_slot"];verb_slot=h["verb_slot"]
        destination_slot=3-entity_slot-verb_slot
        for p in splits(raw):
            if (p[entity_slot] not in h["entity_map"] or
                p[verb_slot] not in h["verbs"] or
                p[destination_slot] not in h["destinations"]):
                continue
            entity=h["entity_map"][p[entity_slot]]
            delta=h["verbs"][p[verb_slot]]
            val=(h["destinations"][p[destination_slot]]+h["offsets"][delta])%4
            out=list(before)
            out[entity]=val
            out[8+entity]=(before[8+entity]+delta)%3
            answers.add(tuple(out))
        return next(iter(answers)) if len(answers)==1 else None

    def seal_b(self):
        if not self.sealed_a or self.sealed_b or len(self.b)!=12:
            raise ValueError("exactly 12 B interventions required")
        if not self.incomplete and self.hypotheses and self.family=="anchored_effect":
            for h in self.hypotheses:
                for e_slot in range(3):
                    for v_slot in range(3):
                        if e_slot==v_slot:
                            continue
                        candidate={**h,"entity_slot":e_slot,"verb_slot":v_slot}
                        self._tick()
                        if all(self._infer(b,s,candidate)==a for b,s,a in self.b):
                            self.b_hypotheses.append(candidate)
                            if len(self.b_hypotheses)>MAX_MODELS:
                                self.incomplete=True;self.b_hypotheses=[]
                                break
                    if self.incomplete:
                        break
                if self.incomplete:
                    break
        self.sealed_b=True
        return {"hypotheses_b":len(self.b_hypotheses),"incomplete":self.incomplete}

    def use_phase(self,phase):
        if phase not in ("A","B") or phase=="B" and not self.sealed_b:
            raise ValueError("phase unavailable")
        self.phase=phase

    def predict(self,before,raw):
        validate_state(before,self.family);validate_raw(raw)
        if self.incomplete or not self.sealed_a:
            return None
        hyps=self.hypotheses if self.phase=="A" else self.b_hypotheses
        if not hyps:
            return None
        results={self._infer(before,raw,h) for h in hyps}
        if len(results)==1:
            return next(iter(results))
        return None

    def numeric_weight_count(self):
        # Count only nonblank numeric coefficients in circuit tables.
        return sum(len(h["entity_map"])+len(h["verbs"])+len(h["destinations"])+
                   len(h["offsets"]) for h in self.hypotheses)

    def snapshot(self):
        data={"schema":"wsp54.compiler.v1","family":self.family,
              "a":[[list(b),s,list(a)] for b,s,a in self.a],
              "b":[[list(b),s,list(a)] for b,s,a in self.b],
              "sealed_a":self.sealed_a,"sealed_b":self.sealed_b,
              "phase":self.phase,"incomplete":self.incomplete,
              "nodes":self.nodes,"hypotheses":self.hypotheses,
              "b_hypotheses":self.b_hypotheses}
        payload=canonical(data)
        if len(payload)>MAX_SNAPSHOT:
            raise OverflowError("snapshot memory ceiling")
        return canonical({"payload":data,"sha256":sha256(payload.encode("ascii")).hexdigest()})

    @classmethod
    def restore(cls,raw):
        if type(raw) is not str or len(raw)>MAX_SNAPSHOT+1000:
            raise ValueError("invalid snapshot size")
        try:
            env=json.loads(raw)
            if type(env) is not dict or set(env)!={"payload","sha256"}:
                raise ValueError("invalid envelope")
            p=env["payload"]
            if (type(p) is not dict or set(p)!={"schema","family","a","b",
                    "sealed_a","sealed_b","phase","incomplete","nodes",
                    "hypotheses","b_hypotheses"} or
                p["schema"]!="wsp54.compiler.v1" or
                sha256(canonical(p).encode("ascii")).hexdigest()!=env["sha256"]):
                raise ValueError("invalid snapshot signature")
            obj=cls(family=p["family"])
            if type(p["a"]) is not list or type(p["b"]) is not list or (
                len(p["a"])>48 or len(p["b"])>12 or p["sealed_a"]!=(len(p["a"])==48)
                or p["sealed_b"]!=(len(p["b"])==12)):
                raise ValueError("invalid evidence boundaries")
            for index,items in enumerate((p["a"],p["b"])):
                if index==1 and len(obj.a)==48:
                    obj.seal_a()
                for item in items:
                    if type(item) is not list or len(item)!=3:
                        raise ValueError("invalid evidence")
                    b,s,a=item
                    if type(b) is not list or type(a) is not list:
                        raise ValueError("invalid physical evidence")
                    class Observation:
                        pass
                    o=Observation()
                    o.before,o.acoustic_bits,o.after=tuple(b),s,tuple(a)
                    o.action_cost,o.reset_cost=1,0
                    obj.observe(o)
            if p["sealed_a"] and not obj.sealed_a:
                obj.seal_a()
            if p["sealed_b"]:
                obj.seal_b()
            if p["phase"]=="B":
                obj.use_phase("B")
            if obj.snapshot()!=raw:
                raise ValueError("noncanonical or impossible compiler snapshot")
            return obj
        except (TypeError,KeyError,IndexError,UnicodeError,json.JSONDecodeError) as ex:
            raise ValueError("malformed snapshot") from ex

    def capacity_bits(self):
        return len(self.snapshot().encode("ascii"))*8
