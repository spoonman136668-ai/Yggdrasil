"""Y-F102: delayed causal-value credit and stability ablations, exact F62 native action space.

PUBLIC synthetic development only. The F102 prereg was frozen before code.
No protected FIT/DIAG/ORIGINAL, Codex, CKB or model API. Unseen GUARD
outcomes never influence fitted parameters or choice of the winning variant.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import random
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
PREREG_BLOB="4f3a8bf295a2f695a039d6b71d87d3bff3939e76"
F101_BLOB="6333738872a64eb68c745bdf0973c9b111bac060"
F62_BLOB="7ed72deca5584d7c0b6562d74456fa7d4bee6712"
F99_BLOB="5de08fe74eb74dd917a7559cc3a8755185aac823"
PARENT_SHA="d5f0f5f996681ad2509170ab151333f79d2fc113"
TRAIN_START=-12001
GUARDS=((-13001,-41,"raw"),(-13101,-42,"swap_roles_and_invert"),
        (-13201,-43,"reverse_order"),(-13301,-44,"phase_and_roles"))
PARAMS=12
CAP=12
RECORD_BYTES=12

class IntegrityError(ValueError):
    pass

def require(ok,message):
    if not ok:raise IntegrityError("F102_"+message)

def blob(p):
    b=Path(p).read_bytes()
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\x00"+b).hexdigest()

def source_modules():
    require(blob(HERE/"prereg.json")==PREREG_BLOB,"PREREG_DRIFT")
    require(blob(ROOT/"20261017-y-f101"/"causal_memory.py")==F101_BLOB,
            "F101_PARENT_DRIFT")
    require(blob(ROOT/"20261015-y-f62"/"source_pilot.py")==F62_BLOB,
            "F62_ACTION_PARENT_DRIFT")
    require(blob(ROOT/"20261016-y-f99"/"causal_closure.py")==F99_BLOB,
            "F99_PARENT_DRIFT")
    cfg=json.loads((HERE/"prereg.json").read_text())
    require(cfg["schema"]=="yggdrasil.f102.delayed-causal-memory-credit-source-frozen.v1"
            and cfg["parent"]["y_f101_exact"]==PARENT_SHA and
            cfg["guard"][0]["seeds"]==[-13001,-13008] and
            cfg["guard"][3]["seeds"]==[-13301,-13308] and
            all(v is True for v in cfg["authority"].values()),"FROZEN_SCOPE_DRIFT")
    spec=importlib.util.spec_from_file_location("f102_frozen_f101",
                    ROOT/"20261017-y-f101"/"causal_memory.py")
    explain=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=explain
    spec.loader.exec_module(explain)
    f99,native=explain.frozen_sources()
    require(native.PARAMS==PARAMS and native.CAP==CAP and
            native.EVENTS==72 and native.RECORD_BYTES==RECORD_BYTES,
            "NATIVE_ACTION_OR_RESOURCE_DRIFT")
    return cfg,explain,f99,native

def episode(native,seed,family,mode,namespace):
    # Separate, unregistered NEGATIVE seed identities only. This never calls
    # native.source(), which admits reserved F62 FIT identities.
    require(seed<0 and family<0 and mode in
            ("raw","swap_roles_and_invert","reverse_order","phase_and_roles"),
            "PROTECTED_OR_UNREGISTERED_SOURCE")
    require(0<=namespace<64,"EPISODE_NAMESPACE_INVALID")
    tagged,question,_paths,_regime=native._construct(seed,family)
    stream=[tuple(x[:3]) for x in tagged]
    need_nodes=sorted({u for a,_,b in stream for u in (a,b)})
    rng=random.Random(seed*30311+family*4099+102)
    shuffled=list(range(len(need_nodes)));rng.shuffle(shuffled)
    mapped={old:1_000_000+namespace*10000+shuffled[i] for i,old in enumerate(need_nodes)}
    require(len(mapped)<1000,"GRAPH_TOO_LARGE")
    public=[(mapped[a],r,mapped[b]) for a,r,b in stream]
    query=dict(start=mapped[question["start"]],
               ops=tuple(tuple(op) for op in question["ops"]),
               answer=mapped[question["answer"]])
    if mode in ("swap_roles_and_invert","phase_and_roles"):
        roles=(2,0,3,1)
        public=[(b,roles[role],a) if mode=="swap_roles_and_invert" else
                (a,roles[role],b) for a,role,b in public]
        query["ops"]=tuple((roles[r],-d if mode=="swap_roles_and_invert" else d)
                             for r,d in query["ops"])
    if mode=="reverse_order":
        public.reverse()
    if mode=="phase_and_roles":
        public=public[::2]+public[1::2]
    require(len(public)==72 and len(set(public))==72 and
            4<=len(query["ops"])<=8,"SOURCE_GRAPH_MALFORMED")
    # No label/family/answer/seed is supplied to the online scorer.
    return tuple(public),query,hashlib.sha256(json.dumps(
        {"public":public,"query":query},sort_keys=True).encode()).hexdigest()

def source_split(native):
    train=[]
    for family_index,family in enumerate((-31,-32)):
        for offset in range(8):
            seed=TRAIN_START-offset
            public,question,identity=episode(native,seed,family,"raw",
                                            family_index*8+offset)
            train.append((seed,family,public,question,identity))
    guards=[]
    for i,(start,family,mode) in enumerate(GUARDS):
        rows=[]
        for offset in range(8):
            seed=start-offset
            public,question,identity=episode(native,seed,family,mode,
                                              16+8*i+offset)
            rows.append((seed,family,public,question,identity))
        guards.append(tuple(rows))
    allrows=train+[row for group in guards for row in group]
    require(len(train)==16 and len(allrows)==48 and
            len(set(row[4] for row in allrows))==48 and
            len({node for row in allrows for a,_,b in row[2] for node in (a,b)})==
            sum(len({node for a,_,b in row[2] for node in (a,b)})
                for row in allrows),"SOURCE_GRAPH_VERTEX_COLLISION")
    # Assert graph shape only changed by independently frozen role/order
    # transformations, not by inventing a new topology family.
    require(all(len(row[2])==72 for row in allrows),"SOURCE_EVENT_COUNT")
    return tuple(train),tuple(guards)

def diff_transform(x,rms):
    return tuple(v/a for v,a in zip(x,rms)) if rms is not None else tuple(x)

def train_examples(native,pack,train):
    rows=[]
    for seed,family,stream,q,_ in train:
        examples,counts=native.counterfactual_labels(stream,q,pack)
        require(sum(counts.values())==len(examples) and examples,
                "TRAIN_COUNTERFACTUAL_MISSING")
        rows.extend(examples)
    require(rows and all(len(x)==PARAMS and label in (-1,0,1)
                         for x,label in rows),"TRAIN_FEATURES_DRIFT")
    return tuple(rows)

def rms_from_train(rows):
    return tuple(max(.05,math.sqrt(sum(x[j]*x[j] for x,_ in rows)/len(rows)))
                 for j in range(PARAMS))

def train_linear(rows,variant,rms=None):
    require(variant in ("raw","clip","normalized","residual"),
            "TRAIN_VARIANT_UNKNOWN")
    weights=[0.]*PARAMS
    times=[]
    clipped=0
    for cycle in range(4):
        squared=0.
        update_magnitude=0.
        for raw,y in rows:
            x=diff_transform(raw,rms if variant=="normalized" else None)
            score=math.tanh(sum(w*v for w,v in zip(weights,x)))
            squared+=(score-y)**2
            grad=[.04*(y-score)*v for v in x]
            if variant=="clip":
                norm=math.sqrt(sum(g*g for g in grad))
                if norm>.08:
                    grad=[g*(.08/norm) for g in grad]
                    clipped+=1
            if variant=="residual":
                grad=[g*.25 for g in grad]
            for j,g in enumerate(grad):
                weights[j]=max(-7.9375,min(7.9375,weights[j]+g))
            update_magnitude+=math.sqrt(sum(g*g for g in grad))
        norm=math.sqrt(sum(w*w for w in weights))
        require(math.isfinite(norm) and math.isfinite(squared),
                "NONFINITE_LINEAR_STABILITY")
        times.append(dict(cycle=cycle+1,train_mse=round(squared/len(rows),8),
                          update_l2_sum=round(update_magnitude,8),
                          weights_l2=round(norm,8),nonfinite=0,
                          clipped_examples=clipped))
    return tuple(weights),tuple(times)

class TinyNeural:
    """A 12->2->1 tanh network: 29 TRAIN-only parameters, not 12."""
    def __init__(self):
        r=random.Random(102)
        self.hidden=[[r.uniform(-.10,.10) for _ in range(12)]
                     for _ in range(2)]
        self.hidden_bias=[0.,0.]
        self.head=[r.uniform(-.10,.10) for _ in range(2)]
        self.head_bias=0.
        self.cycles=[]
    def score(self,x):
        z=[math.tanh(sum(w*v for w,v in zip(wt,x))+b)
           for wt,b in zip(self.hidden,self.hidden_bias)]
        return math.tanh(sum(a*b for a,b in zip(self.head,z))+self.head_bias)
    def train(self,rows):
        for cycle in range(4):
            error=0.
            for x,y in rows:
                z=[math.tanh(sum(a*b for a,b in zip(weights,x))+bias)
                   for weights,bias in zip(self.hidden,self.hidden_bias)]
                v=math.tanh(sum(a*b for a,b in zip(self.head,z))+self.head_bias)
                error+=(y-v)**2
                residual=.04*(y-v)*(1-v*v)
                old_head=tuple(self.head)
                for i in range(2):
                    g=residual*old_head[i]*(1-z[i]*z[i])
                    for j in range(12):
                        self.hidden[i][j]+=g*x[j]
                    self.hidden_bias[i]+=g
                    self.head[i]+=residual*z[i]
                self.head_bias+=residual
                self.hidden=[[max(-7.9375,min(7.9375,v)) for v in row]
                             for row in self.hidden]
                self.hidden_bias=[max(-7.9375,min(7.9375,v))
                                  for v in self.hidden_bias]
                self.head=[max(-7.9375,min(7.9375,v)) for v in self.head]
                self.head_bias=max(-7.9375,min(7.9375,self.head_bias))
            magnitude=math.sqrt(sum(v*v for row in self.hidden for v in row)+
                sum(v*v for v in self.hidden_bias+self.head)+self.head_bias**2)
            require(math.isfinite(magnitude),"NONFINITE_MLP")
            self.cycles.append(dict(cycle=cycle+1,
                train_mse=round(error/len(rows),8),param_norm=round(magnitude,8)))
        return self
    @property
    def parameters(self):return 29

def learned_online(native,public,packing,score_fn,max_depth=None):
    memory=()
    actions=[]
    max_records=0
    for index,event in enumerate(public):
        legal=native.actions(memory,event,index,packing)
        baseline=native._f60_step(memory,event,packing)
        b=[a[4] for a in legal if a[3]==baseline]
        require(len(b)==1,"SOURCE_F60_EXACT_ACTION_PARITY")
        basis=b[0]
        admissible=[(j,a) for j,a in enumerate(legal)
                    if max_depth is None or
                    all(len(rec[2])<=max_depth for rec in a[3])]
        require(admissible,"DEPTH_BOUND_ELIMINATED_ALL_NATIVE_ACTIONS")
        def rank(j,a):
            diff=tuple(x-y for x,y in zip(a[4],basis))
            return (score_fn(diff),-j)
        j,chosen=max(admissible,key=lambda item:rank(*item))
        memory=chosen[3]
        native._valid_memory(memory,packing)
        max_records=max(max_records,len(memory))
        if index in (11,23,35,47,59,71):
            actions.append(dict(event_index=index,chosen_action_index=j,
                native_candidates=len(legal),
                action_type=chosen[0],
                source_record_index=chosen[1],dropped_record_index=chosen[2],
                native_records_after=len(memory),
                memory_packed_sha256=hashlib.sha256(b"".join(
                    packing.pack(*r) for r in memory)).hexdigest(),
                score_vs_F60=round(score_fn(tuple(x-y for x,y in zip(
                    chosen[4],basis))),8)))
    require(len(public)==72 and max_records<=12 and len(actions)==6,
            "ONLINE_BOUNDED_ACTIONS")
    return memory,tuple(actions)

def terminal_score(pack,mem,q):
    return int(pack.solve(mem,q)==q["answer"])

def evaluate(source_sha):
    require(isinstance(source_sha,str) and len(source_sha)==40 and
            all(x in "0123456789abcdef" for x in source_sha),
            "SOURCE_COMMIT_SHA_REQUIRED")
    cfg,f101,f99,native=source_modules()
    packing=native.codec()
    train,guards=source_split(native)
    labeled=train_examples(native,packing,train)
    rms=rms_from_train(labeled)
    trained={name:train_linear(labeled,name,rms=rms)
             for name in ("raw","clip","normalized","residual")}
    neural=TinyNeural().train(labeled)
    arms=("F60_native_fixed","F61_original_frozen","F62_zero_score",
          "learned_raw","learned_clip","learned_normalized",
          "learned_residual","learned_depth4","neural_MLP29")
    blocks=[]
    for group_index,group in enumerate(guards):
        rows=[]
        for case_index,(seed,family,stream,q,signature) in enumerate(group):
            def linear(name):
                weights=trained[name][0]
                scale=rms if name=="normalized" else (1.,)*PARAMS
                return lambda d:sum(w*(x/a) for w,x,a in zip(weights,d,scale))
            base_mem=()
            for event in stream:
                base_mem=native._f60_step(base_mem,event,packing)
            choices={}
            choices["F60_native_fixed"]=(base_mem,())
            p61,_=native.learned_online(stream,native.F61_WEIGHTS,packing)
            choices["F61_original_frozen"]=(p61,())
            p0,_=native.learned_online(stream,(0,)*PARAMS,packing)
            choices["F62_zero_score"]=(p0,())
            for name in ("raw","clip","normalized","residual"):
                choices["learned_"+name]=learned_online(
                    native,stream,packing,linear(name))
            choices["learned_depth4"]=learned_online(
                native,stream,packing,linear("raw"),max_depth=4)
            choices["neural_MLP29"]=learned_online(
                native,stream,packing,neural.score)
            require(tuple(choices)==arms,"ARM_IDENTITY_CHANGED")
            scores={}
            for name,(mem,trace) in choices.items():
                native._valid_memory(mem,packing)
                require(len(mem)<=CAP and
                    all(len(packing.pack(*rec))==RECORD_BYTES for rec in mem),
                    "NATIVE_PACKED_MEMORY_RESOURCE")
                scores[name]=dict(correct=terminal_score(packing,mem,q),
                  retained_records=len(mem),retained_bytes=len(mem)*RECORD_BYTES,
                  retained_memory_sha256=hashlib.sha256(
                      b"".join(packing.pack(*x) for x in mem)).hexdigest(),
                  action_trace=trace)
            structural=[]
            if case_index==0 and len(q["ops"]) in (4,6):
                asked=(q["start"],tuple(
                    2*role+int(direction==-1) for role,direction in q["ops"]),
                    q["answer"])
                for name in ("F60_native_fixed","learned_raw","neural_MLP29"):
                    proof=f101.explain(choices[name][0],asked,f99)
                    structural.append(dict(arm=name,proof=proof))
            rows.append(dict(case_id=f"{group_index}:{case_index}",
                 source_seed_OFFLINE_ONLY=seed,
                 graph_identity_sha256=signature,
                 requested_hops=len(q["ops"]),question_hidden_until_terminal=True,
                 policy_scores=scores,
                 structural_causal_provenance=structural))
        byarm={name:sum(row["policy_scores"][name]["correct"] for row in rows)
               for name in arms}
        blocks.append(dict(name=cfg["guard"][group_index]["name"],
                    transformed_arrival_or_roles=cfg["guard"][group_index]["mode"],
                    episodes=len(rows),correct_by_policy=byarm,rows=rows))
    totals={name:sum(b["correct_by_policy"][name] for b in blocks)
            for name in arms}
    raw=totals["learned_raw"]
    control=totals["F60_native_fixed"]
    positive=(raw>=control+4 and
        all(b["correct_by_policy"]["learned_raw"]>=
            b["correct_by_policy"]["F60_native_fixed"] for b in blocks) and
        raw>totals["F61_original_frozen"] and
        raw>totals["F62_zero_score"])
    return dict(
       schema="yggdrasil.f102.delayed-credit-stability-public.v1",
       exact_head=source_sha,source_kind="PUBLIC_SYNTHETIC_NATIVE_NEGATIVE_SEEDS_ONLY",
       prereg_sha256=hashlib.sha256((HERE/"prereg.json").read_bytes()).hexdigest(),
       frozen_F101_source_git_blob=F101_BLOB,
       exact_F62_native_actions_blob=F62_BLOB,
       train_episode_count=len(train),guard_episode_count=sum(map(len,guards)),
       training_labels=len(labeled),training_epochs=4,
       all_guard_results_after_training=True,
       online_scorer_receives_future_question=False,
       protected_FIT_DIAG_ORIGINAL_untouched=True,
       record_budget=CAP,native_memory_bytes=CAP*RECORD_BYTES,
       train_only_feature_rms=[round(x,8) for x in rms],
       train_cycle_diagnostics={k:v[1] for k,v in trained.items()},
       final_linear_weight_vectors={k:[round(x,7) for x in v[0]]
                                    for k,v in trained.items()},
       mlp_parameter_count=neural.parameters,
       mlp_training_cycles=neural.cycles,
       native_linear_parameter_count=PARAMS,
       mlp_not_parameter_matched=True,
       blocks=blocks,totals=totals,
       scientific_delayed_credit_screen_passed=positive,
       result=("PUBLIC_DELAYED_CREDIT_GAIN_ENGINEERING_ONLY" if positive else
               "PUBLIC_DELAYED_CREDIT_NO_QUALIFIED_GAIN"),
       no_unrelated_graph_topology_transfer_claim=True,
       learned_memory_superiority_independently_accepted=False,
       scientific_first_use=False,accepted_ref_mutations=0,
       no_automatic_optimizer_promotion=True,
       CKB_integration=False,Codex_used=False,
       MindPalace_written=False)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-ref",required=True)
    args=parser.parse_args()
    print(json.dumps(evaluate(args.source_ref),sort_keys=True,separators=(",",":")))
if __name__=="__main__":
    main()
