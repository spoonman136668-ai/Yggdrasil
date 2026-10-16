"""Y-F55: FIT-trained causal query-blind relation-component memory.

Distinct from the historical F54: learns to select compact *online* composed
public graph paths under exactly 12 lossless 12-byte records (144 payload B).
Training may see FIT path labels; an online memory policy sees only events
arriving so far and its own retained 12 records. Future diagnostic question is
not accepted by the retention API. The 144B excludes Python runtime and is
NOT native 576B residency qualification. F54 control is a clearly marked
frozen-parameter adaptation to this novel causal candidate space, not an exact
replay of historical F54 source. The full public offline witness is costly,
noncompetitive, and not an information-theoretic optimality certificate.
"""
from __future__ import annotations
import importlib.util,json,math,random,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location("y55_public_feasibility",HERE/"source_feasibility.py")
base=importlib.util.module_from_spec(s);sys.modules[s.name]=base;s.loader.exec_module(base)
codec=base.codec
ARMS=("learned_global_relational_memory","F54_frozen_global_memory",
      "fixed_public_triple_chunks","fixed_public_pair_chunks",
      "public_DAG_compression","public_connected_component_chunks",
      "raw_degree","raw_FIFO","public_hash","private_future_query_oracle_unfair")
# Exact weights from authentic F54 first-attempt artifact 12011953258.
# Adapted scoring only; different source/feature set, NOT same method replay.
F54_ORIGINAL_INT8=(-16,24,18,26,-3,89,-1,26,127,12,18,-10)
RECORDS_MAX=12;PAYLOAD=12;MAX_SEGMENT=6
def inverse(r):
    a,b,c=r
    return (b,a,tuple(code^1 for code in reversed(c)))
def linked(u,v,max_seg):
    if u[1]!=v[0] or len(u[2])+len(v[2])>max_seg:return None
    return (u[0],v[1],u[2]+v[2])
def pub_record(e):
    a,role,b,_tag=e
    return (a,b,(2*role,))
def max_length_for_arm(arm):
    if arm in ("raw_degree","raw_FIFO","public_hash"):return 1
    if arm=="fixed_public_pair_chunks":return 2
    if arm=="fixed_public_triple_chunks":return 3
    return MAX_SEGMENT
def candidates(memory,event,maxlen):
    incoming=pub_record(event)
    results={incoming}
    for old in memory:
        for a,b in ((old,incoming),(incoming,old),
                    (inverse(old),incoming),(incoming,inverse(old))):
            z=linked(a,b,maxlen)
            if z is not None and z[0]!=z[1]:results.add(z)
    results.update(memory)
    return tuple(sorted(results,key=lambda z:(z[0],z[1],z[2])))
def features(rec,pool):
    start,end,codes=rec
    # All inputs are current public candidate/retained records, never
    # full retrospectively materialized graph or future question.
    degree=sum(int(p[0]==start)+int(p[1]==start)+
               int(p[0]==end)+int(p[1]==end) for p in pool)
    joins=sum(int(p[1]==start or p[0]==end) for p in pool)
    unique_roles=len(set(c//2 for c in codes))
    inverse_fraction=sum(c%2 for c in codes)/len(codes)
    return (1.,len(codes)/6,min(degree,32)/32,min(joins,20)/20,
            unique_roles/4,inverse_fraction,(len(codes)-1)/5,
            min(len(pool),128)/128)
def score(rec,pool,arm,w):
    f=features(rec,pool)
    L=len(rec[2])
    if arm=="learned_global_relational_memory":
        return sum(a*b for a,b in zip(w,f))
    if arm=="F54_frozen_global_memory":
        return sum((F54_ORIGINAL_INT8[k]/127)*f[k] for k in range(8))
    if arm=="fixed_public_triple_chunks" or arm=="fixed_public_pair_chunks":
        return 3*f[1]+f[3]/8+f[2]/8
    if arm=="public_DAG_compression":
        return f[1]*3+f[4]+f[3]/4
    if arm=="public_connected_component_chunks":
        return f[2]*3+f[3]+f[1]/5
    if arm=="raw_degree":return f[2]+f[3]/4
    if arm=="raw_FIFO":return 0.
    if arm=="public_hash":
        # Fixed public per-record identity, no source-label involvement.
        return random.Random(rec[0]*17+rec[1]*23+L*127+55051).random()
    raise ValueError("unregistered public online arm")
def retain_online(public,arm,quant,debug=False):
    """Only the public prefix and ≤12 packed records are ever needed.

    Does NOT accept or inspect future question, private paths or labels.
    """
    assert arm in ARMS[:-1]
    w=tuple(k/32 for k in quant)
    mem=[];maxlen=max_length_for_arm(arm);operation_count=0
    for public_event in public:
        opts=candidates(mem,public_event,maxlen)
        operation_count+=len(opts)
        ordered=sorted(opts,key=lambda z:(score(z,opts,arm,w),
                    z[0],z[1],z[2]),reverse=True)
        mem=ordered[:RECORDS_MAX]
        assert len(mem)<=RECORDS_MAX
        assert all(len(codec.pack(*r))==PAYLOAD for r in mem)
    if debug:return tuple(mem),operation_count
    return tuple(mem)
def valid_label_records(paths):
    # FIT-only privately annotated paths, never used in inference/online.
    valid=set()
    for path in paths:
        nodes=path["nodes"];steps=tuple(2*r+(direction==-1) for r,direction in path["ops"])
        for at in range(8):
            for L in range(1,min(6,8-at)+1):
                r=(nodes[at],nodes[at+L],steps[at:at+L])
                valid.add(r);valid.add(inverse(r))
    return valid
def train():
    # Offline FIT supervised pairwise candidate preferences. Label as
    # recoverable contiguous true-path fragment. The online scorer itself
    # sees ONLY the current record/pool features.
    samples=[];positive=0
    for seed in base.FIT:
        for fam in base.FIT_FAM:
            events,_future,paths=base.source(seed,fam)
            truth=valid_label_records(paths)
            state=[]
            for event in events:
                opts=candidates(state,event,MAX_SEGMENT)
                for rec in opts:
                    y=int(rec in truth)
                    positive+=y
                    samples.append((features(rec,opts),y))
                # Training proposal generation uses a deterministic fixed
                # public baseline, NEVER question or true path membership.
                state=sorted(opts,key=lambda r:(len(r[2]),r[0],r[1],r[2]),
                             reverse=True)[:RECORDS_MAX]
    assert len(samples)>1000 and positive>0
    w=[0.]*8
    for epoch in range(4):
        for f,y in samples:
            z=max(-16,min(16,sum(a*b for a,b in zip(w,f))))
            p=1/(1+math.exp(-z))
            # Positive class is sparse under the bounded memory cap.
            err=(p-y)*(4 if y else 1)
            for j in range(8):w[j]-=.015*(err*f[j]+.0001*w[j])
    return tuple(max(-127,min(127,round(v*32))) for v in w),len(samples),positive
def fit_only_report():
    quant,n,pos=train()
    scored=[]
    for seed,fam in ((611000,1120),(611001,1121),(611002,1122),(611003,1123)):
        public,query,paths=base.source(seed,fam)
        record,ops=retain_online(public,ARMS[0],quant,debug=True)
        b=sum(len(codec.pack(*z)) for z in record)
        scored.append(dict(seed=seed,family=fam,
            learned_correct=int(codec.solve(record,query)==query["answer"]),
            retained_records=len(record),serialized_bytes=b,ops=ops))
    return dict(schema="yggdrasil.f55.learned-online-memory-fit-preflight.v1",
        model_weights_int8=list(quant),fit_labeled_records=n,
        fit_positive_records=pos,fit_sample_cases=scored,
        fit_seeds=[base.FIT.start,base.FIT.stop],
        diagnostic_seeds_NOT_TOUCHED=[base.DIAG.start,base.DIAG.stop],
        original_seeds_NOT_RESERVED=[base.ORIGINAL.start,base.ORIGINAL.stop],
        query_blind_retention=True,source_independent_F3=False)
def run_diagnostic():
    quant,n,pos=train();rows=[]
    for seed in base.DIAG:
        for family in base.DIAG_FAM:
            public,q,_private_paths=base.source(seed,family)
            answers={};receipt={};works={}
            for arm in ARMS[:-1]:
                mem,ops=retain_online(public,arm,quant,debug=True)
                answers[arm]=int(codec.solve(mem,q)==q["answer"])
                receipt[arm]=[codec.pack(*r).hex() for r in mem]
                works[arm]=ops
            answers[ARMS[-1]]=1 # evaluator future-query oracle, UNFAIR
            offline,offline_work=base.witness(public)
            offline_correct=int(codec.solve(offline,q)==q["answer"])
            rows.append(dict(seed=seed,family=family,
                public_events=[list(v) for v in public],
                question=dict(start=q["start"],ops=[list(x) for x in q["ops"]],
                              answer=q["answer"]),
                answers=answers,receipts=receipt,online_candidate_count=works,
                public_offline_reference_correct=offline_correct,
                public_offline_reference_work=offline_work,
                public_offline_reference_receipts=[codec.pack(*r).hex() for r in offline]))
    scores={a:dict(correct=sum(r["answers"][a] for r in rows),total=len(rows))
            for a in ARMS}
    for sc in scores.values():sc["accuracy"]=sc["correct"]/sc["total"]
    by={str(f):{a:sum(r["answers"][a] for r in rows if r["family"]==f)
                for a in ARMS} for f in base.DIAG_FAM}
    fair=ARMS[1:-1];candidate=ARMS[0];strongest=max(fair,key=lambda a:scores[a]["correct"])
    gain=(scores[candidate]["correct"]-scores[strongest]["correct"])/len(rows)
    byf=all(by[str(f)][candidate]>=max(by[str(f)][a] for a in fair)
            for f in base.DIAG_FAM)
    # Ablation strips composed records *after* causal retention, without
    # giving the future query back to the selection policy.
    ablation=0
    for row in rows:
        q=dict(start=row["question"]["start"],ops=tuple(tuple(x) for x in row["question"]["ops"]),
               answer=row["question"]["answer"])
        full=[codec.unpack(bytes.fromhex(h)) for h in row["receipts"][candidate]]
        ablation+=int(codec.solve([r for r in full if len(r[2])==1],q)==q["answer"])
    abl=(scores[candidate]["correct"]-ablation)/len(rows)
    offline=sum(r["public_offline_reference_correct"] for r in rows)
    passed=offline>=16 and gain>=.05 and abl>0 and byf
    return dict(schema="yggdrasil.f55.learned-causal-queryblind-memory.trainonly.v1",
        stage="TRAIN_ONLY_CAUSAL_ONLINE_MEMORY_FRESH_DIAGNOSTIC",
        fit_seeds=[base.FIT.start,base.FIT.stop],fit_families=list(base.FIT_FAM),
        diagnostic_seeds=[base.DIAG.start,base.DIAG.stop],
        diagnostic_families=list(base.DIAG_FAM),
        original_seeds_NOT_RESERVED=[base.ORIGINAL.start,base.ORIGINAL.stop],
        rows=rows,cases=len(rows),scores=scores,by_family=by,
        strongest_equal_byte_fair=strongest,candidate_gain=gain,
        composition_ablation_gain=abl,per_family_nondegradation=byf,
        public_constructive_reference_correct=offline,
        public_reference_extra_work_noncompetitive=True,
        full_public_optimality_NOT_CLAIMED=True,
        serialized_payload_max_bytes=144,per_record_bytes=12,
        learned_model_weights_int8=list(quant),fit_labeled_candidates=n,
        fit_positive_candidates=pos,F54_frozen_control_ADAPTED_NOT_IDENTICAL=True,
        query_hidden_until_retention_complete=True,
        physical_native_576B_unverified=True,frozen_gate_met=passed,
        verdict=("TRAIN_ONLY_CAUSAL_ONLINE_MEMORY_SUPPORTED" if passed
                 else "TRAIN_ONLY_CAUSAL_ONLINE_MEMORY_NEGATIVE"),
        independent_F3=False,primary_original_executed=False,
        accepted_ref_mutation=False,live_optimizer_promotion=False,paid_api_calls=0)
if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("flag required; no automatic diagnostic")
    if sys.argv[1]=="--fit-only":report=fit_only_report()
    elif sys.argv[1]=="--diagnostic-train":report=run_diagnostic()
    else:raise SystemExit("protected original denied")
    print(json.dumps(report,sort_keys=True))
