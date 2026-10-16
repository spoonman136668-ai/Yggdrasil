"""Y-F55 source-free causal replay, exact record witness, score and gate audit.

No import of study/generator. Independently replays each online policy against
time-ordered PUBLIC events; future query is consulted ONLY after every memory
state is sealed. Independently decodes all persistent 12-byte receipts and
reconstructs each edge-labeled compositional path from the public graph.
"""
import argparse,json,math,random
from pathlib import Path
ARMS=("learned_global_relational_memory","F54_frozen_global_memory",
      "fixed_public_triple_chunks","fixed_public_pair_chunks",
      "public_DAG_compression","public_connected_component_chunks",
      "raw_degree","raw_FIFO","public_hash","private_future_query_oracle_unfair")
F54=(-16,24,18,26,-3,89,-1,26,127,12,18,-10)
def decode(s):
    raw=bytes.fromhex(s)
    assert len(raw)==12
    start=int.from_bytes(raw[:4],"little");end=int.from_bytes(raw[4:8],"little")
    bits=int.from_bytes(raw[8:11],"little");n=raw[11]
    assert 1<=n<=6 and bits>>(3*n)==0
    return start,end,tuple((bits>>(3*i))&7 for i in range(n))
def inv(r):
    a,b,c=r
    return b,a,tuple(z^1 for z in reversed(c))
def compose(left,right,lim):
    if left[1]!=right[0] or len(left[2])+len(right[2])>lim:return None
    return left[0],right[1],left[2]+right[2]
def opts(mem,event,lim):
    raw=(event[0],event[2],(2*event[1],))
    seen={raw,*mem}
    for old in mem:
        for left,right in ((old,raw),(raw,old),
                           (inv(old),raw),(raw,inv(old))):
            z=compose(left,right,lim)
            if z is not None and z[0]!=z[1]:seen.add(z)
    return tuple(sorted(seen,key=lambda z:(z[0],z[1],z[2])))
def feat(rec,pool):
    a,b,c=rec
    deg=sum(int(p[0]==a)+int(p[1]==a)+
            int(p[0]==b)+int(p[1]==b) for p in pool)
    joins=sum(int(p[1]==a or p[0]==b) for p in pool)
    return (1.,len(c)/6,min(deg,32)/32,min(joins,20)/20,
            len(set(x//2 for x in c))/4,
            sum(x%2 for x in c)/len(c),
            (len(c)-1)/5,min(len(pool),128)/128)
def rank(rec,pool,arm,q):
    f=feat(rec,pool);L=len(rec[2])
    if arm==ARMS[0]:return sum((q[j]/32)*f[j] for j in range(8))
    if arm==ARMS[1]:return sum((F54[j]/127)*f[j] for j in range(8))
    if arm in (ARMS[2],ARMS[3]):return 3*f[1]+f[3]/8+f[2]/8
    if arm==ARMS[4]:return f[1]*3+f[4]+f[3]/4
    if arm==ARMS[5]:return f[2]*3+f[3]+f[1]/5
    if arm==ARMS[6]:return f[2]+f[3]/4
    if arm==ARMS[7]:return 0.
    if arm==ARMS[8]:
        return random.Random(rec[0]*17+rec[1]*23+L*127+55051).random()
    raise AssertionError("arm identity")
def replay_online(events,arm,q):
    maximum=(1 if arm in ARMS[6:9] else
             2 if arm==ARMS[3] else 3 if arm==ARMS[2] else 6)
    mem=[];work=0
    for event in events:
        pool=opts(mem,event,maximum);work+=len(pool)
        mem=sorted(pool,key=lambda z:(rank(z,pool,arm,q),
                      z[0],z[1],z[2]),reverse=True)[:12]
    return mem,work
def solve(mem,question):
    seq=tuple(2*r+(direction==-1) for r,direction in question["ops"])
    at=question["start"];seen=set()
    while seq:
        matches=set()
        for r in mem:
            for a,b,c in (r,inv(r)):
                if a==at and seq[:len(c)]==c:matches.add((a,b,c))
        if len(matches)!=1:return None
        a,b,c=next(iter(matches))
        at=b;seq=seq[len(c):]
        if (at,seq) in seen:return None
        seen.add((at,seq))
    return at
def public_witness(mem,events):
    edges=[tuple(e[:3]) for e in events]
    for a,b,code in mem:
        assert 0<=a<2**32 and 0<=b<2**32 and 1<=len(code)<=6
        reachable={a}
        for v in code:
            role=v//2;direction=-1 if v%2 else 1
            reachable={edge[2] if direction==1 else edge[0]
               for node in reachable for edge in edges
               if edge[1]==role and (edge[0] if direction==1 else edge[2])==node}
            assert reachable,"unsupported public path"
        assert b in reachable,"fabricated composed relation"
def audit(doc,pr):
    assert pr["schema"]=="yggdrasil.f55.public-feasible-query-blind-memory.prereg.v1"
    assert doc["schema"]=="yggdrasil.f55.learned-causal-queryblind-memory.trainonly.v1"
    assert doc["stage"]=="TRAIN_ONLY_CAUSAL_ONLINE_MEMORY_FRESH_DIAGNOSTIC"
    assert pr["controls"]==list(ARMS)
    assert doc["fit_seeds"]==pr["fit"]["seeds"]
    assert doc["fit_families"]==pr["fit"]["families"]
    assert doc["diagnostic_seeds"]==pr["diagnostic"]["seeds"]
    assert doc["diagnostic_families"]==pr["diagnostic"]["families"]
    assert doc["original_seeds_NOT_RESERVED"]==pr["future_original_NOT_RESERVED"]["seeds"]
    q=doc["learned_model_weights_int8"]
    assert len(q)==8 and all(type(z)==int and -127<=z<=127 for z in q)
    assert doc["serialized_payload_max_bytes"]==144 and doc["per_record_bytes"]==12
    assert doc["F54_frozen_control_ADAPTED_NOT_IDENTICAL"] is True
    assert doc["query_hidden_until_retention_complete"] is True
    assert doc["physical_native_576B_unverified"] is True
    assert doc["public_reference_extra_work_noncompetitive"] is True
    assert doc["full_public_optimality_NOT_CLAIMED"] is True
    for field in ("independent_F3","primary_original_executed","accepted_ref_mutation",
                  "live_optimizer_promotion"):assert doc[field] is False
    assert doc["paid_api_calls"]==0
    assert doc["cases"]==len(doc["rows"])==64
    scores={arm:0 for arm in ARMS};seen=set()
    by={str(f):{arm:0 for arm in ARMS} for f in doc["diagnostic_families"]}
    ref_correct=0;ablation=0
    for row in doc["rows"]:
        seed,fam=row["seed"],row["family"]
        assert (seed,fam) not in seen;seen.add((seed,fam))
        assert 611100<=seed<611116 and fam in (1124,1125,1126,1127)
        events=row["public_events"]
        assert len(events)==72 and len(set(tuple(e[:3]) for e in events))==72
        assert all(len(e)==4 and e[3] in (0,1) and 0<=e[1]<=3 for e in events)
        assert sum(e[3] for e in events)==36
        future=row["question"]
        assert len(future["ops"]) in (4,6,8)
        assert set(row["answers"])==set(ARMS)
        assert set(row["receipts"])==set(ARMS[:-1])
        assert set(row["online_candidate_count"])==set(ARMS[:-1])
        assert row["answers"][ARMS[-1]]==1
        scores[ARMS[-1]]+=1;by[str(fam)][ARMS[-1]]+=1
        for arm in ARMS[:-1]:
            receipts=row["receipts"][arm]
            assert len(receipts)<=12 and len(receipts)*12<=144
            persisted=[decode(v) for v in receipts]
            public_witness(persisted,events)
            repeat,work=replay_online(events,arm,q)
            assert persisted==repeat,"not causally replayable from only public events"
            assert work==row["online_candidate_count"][arm]
            answer=int(solve(persisted,future)==future["answer"])
            assert row["answers"][arm]==answer
            scores[arm]+=answer;by[str(fam)][arm]+=answer
            if arm==ARMS[0]:
                ablation+=int(solve([r for r in persisted if len(r[2])==1],future)
                              ==future["answer"])
        offline=[decode(z) for z in row["public_offline_reference_receipts"]]
        assert len(offline)==12
        public_witness(offline,events)
        refhit=int(solve(offline,future)==future["answer"])
        assert row["public_offline_reference_correct"]==refhit
        assert row["public_offline_reference_work"]>72
        ref_correct+=refhit
    assert len(seen)==64 and doc["by_family"]==by
    for arm in ARMS:
        metric=doc["scores"][arm]
        assert metric["correct"]==scores[arm] and metric["total"]==64
        assert math.isclose(metric["accuracy"],scores[arm]/64,abs_tol=1e-12)
    fair=ARMS[1:-1];best=max(fair,key=lambda a:scores[a])
    gain=(scores[ARMS[0]]-scores[best])/64
    ablgain=(scores[ARMS[0]]-ablation)/64
    family_safe=all(by[str(f)][ARMS[0]]>=max(by[str(f)][a] for a in fair)
        for f in pr["diagnostic"]["families"])
    passed=ref_correct>=16 and gain>=.05 and ablgain>0 and family_safe
    assert doc["strongest_equal_byte_fair"]==best
    assert math.isclose(doc["candidate_gain"],gain,abs_tol=1e-12)
    assert math.isclose(doc["composition_ablation_gain"],ablgain,abs_tol=1e-12)
    assert doc["per_family_nondegradation"]==family_safe
    assert doc["public_constructive_reference_correct"]==ref_correct
    assert doc["frozen_gate_met"]==passed
    assert doc["verdict"]==("TRAIN_ONLY_CAUSAL_ONLINE_MEMORY_SUPPORTED" if passed
                           else "TRAIN_ONLY_CAUSAL_ONLINE_MEMORY_NEGATIVE")
    return dict(schema="yggdrasil.f55.source-free-causal-recount.v1",
        rows=len(seen),candidate_correct=scores[ARMS[0]],strongest_fair=best,
        strongest_correct=scores[best],
        public_reference_correct=ref_correct,
        compositional_ablation_gain=ablgain,
        gain_percentage_points=round(100*gain,6),
        per_family_nondegradation=family_safe,
        train_gate_passed=passed,independent_F3=False,primary_original_executed=False)
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("result");parser.add_argument("prereg");args=parser.parse_args()
    print(json.dumps(audit(json.loads(Path(args.result).read_text()),
             json.loads(Path(args.prereg).read_text())),sort_keys=True))
