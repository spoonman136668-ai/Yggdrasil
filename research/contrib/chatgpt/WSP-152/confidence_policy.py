"""WSP152 source-free confidence ceiling and confidence-aware action selection.

The WSP151 model and its frozen 99% threshold are used unchanged. No experiment
source owner, protected data, hidden generator labels or scientific first use.
"""
from fractions import Fraction
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from json import dumps
from math import lcm
from pathlib import Path
from time import perf_counter_ns, process_time_ns
import sys

ROOT=Path(__file__).resolve().parents[1]
_spec=spec_from_file_location("_wsp152_pinned_wsp151",ROOT/"WSP-151"/"overhypothesis.py")
M=module_from_spec(_spec)
sys.modules[_spec.name]=M
_spec.loader.exec_module(M)

HYP=tuple((g,s) for g in M.FORMS for s in M.SUBSETS)
ONES=tuple(tuple(x for x in range(64) if M.law(g,s,x)) for g,s in HYP)
PRED=tuple(tuple(M.law(g,s,x) for x in range(64)) for g,s in HYP)
CONF=Fraction(99,100)
Q_MAX=Fraction(1,50)
WARM=(1,2,4,8)

def _digest(obj):
    return sha256(dumps(obj,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def ceiling(model):
    """A posterior UNKNOWN component implies q/2 <= P(y=1|x) <= 1-q/2."""
    q=model["unknown"]/model["denominator"]
    if not 0<q<=1:
        raise AssertionError("WSP152_UNKNOWN_MIXTURE_OUT_OF_RANGE")
    return {"unknown":q,"maximum_confidence":1-q/2,
            "globally_blocked":q>Q_MAX}

def _integers(model):
    divisor=1
    for g,s,w in model["weights"]:
        divisor=lcm(divisor,w.denominator)
    ws=tuple(int(w*divisor) for g,s,w in model["weights"])
    u=int(model["unknown"]*divisor)
    if len(ws)!=126 or u<=0 or sum(ws)+u<=0:
        raise AssertionError("WSP152_INVALID_INTEGER_POSTERIOR")
    return ws,u

def _coverage(ws,u,exclude):
    """Count exact 99%-confident predictions on currently uncharged x."""
    d=sum(ws)+u
    pos=[0]*64
    for j,w in enumerate(ws):
        for x in ONES[j]:
            pos[x]+=w
    return sum(1 for x,p in enumerate(pos)
               if x not in exclude and
               (100*(2*p+u)>=198*d or 100*(2*p+u)<=2*d))

def _future(ws,u,x,y):
    # WSP151 known weight grows by 2*(19 if correct else 1).
    # UNKNOWN grows by 20. Divide every weight by 2 exactly.
    return tuple(w*(19 if PRED[j][x]==y else 1)
                 for j,w in enumerate(ws)),10*u

def choose_next(rows,mem=None):
    """Maximize posterior-expected *future confident coverage*.

    This policy sees only the paid rows, current WSP151 posterior and possible
    candidate actions. It never opens the answer to a candidate action.
    """
    rows=M.validate_rows(rows)
    if len(rows)>=8:
        raise ValueError("WSP152_ACTION_BUDGET_EXHAUSTED")
    model=M.fit(rows,mem)
    ws,u=_integers(model)
    den=sum(ws)+u
    spent={x for x,_,_ in rows}
    best=None
    best_score=-1
    for x in range(64):
        if x in spent:continue
        n1=2*sum(ws[j] for j in range(126) if PRED[j][x])+u
        n0=2*den-n1
        if not (0<n0<2*den and 0<n1<2*den):
            raise AssertionError("WSP152_BAD_PROBABILITY_MASS")
        excluded=spent|{x}
        w0,u0=_future(ws,u,x,0)
        w1,u1=_future(ws,u,x,1)
        c0=_coverage(w0,u0,excluded)
        c1=_coverage(w1,u1,excluded)
        score=n0*c0+n1*c1
        if score>best_score:
            best,best_score=x,score
    if best is None:raise AssertionError("WSP152_NO_ELIGIBLE_ACTION")
    return best

def _effect(kind,subset,x):
    if kind in M.FORMS:return M.law(kind,subset,x)
    if kind=="XOR":return (x&subset).bit_count()%2
    raise ValueError("WSP152_FAKE_KIND_ONLY")

def _subset(tag,i,off=False):
    h=sha256(("WSP152|FAKE|"+tag+"|"+str(i)).encode()).digest()
    if off:
        a=h[0]%6
        b=(a+1+h[1]%5)%6
        return (1<<a)|(1<<b)
    return 1+int.from_bytes(h[:4],"big")%63

def _fixed_tail():
    return tuple(sorted((x for x in range(64) if x not in WARM),
        key=lambda x:(sha256(("WSP152|FAKE|FIXED|"+str(x)).encode()).digest(),x))[:4])

def _read(kind,subset,x,i):
    return (x,_effect(kind,subset,x),"observed_do" if i<4 else "do")

def _policy(kind,subset,name,mem):
    rows=tuple(_read(kind,subset,x,i) for i,x in enumerate(WARM))
    for step in range(4):
        if name=="fixed":x=_fixed_tail()[step]
        elif name=="eig":x=M.propose_next(rows,mem)
        elif name=="coverage":x=choose_next(rows,mem)
        else:raise ValueError("WSP152_BAD_POLICY")
        if x in {a for a,_,_ in rows}:
            raise AssertionError("WSP152_DUPLICATE_ACTION")
        rows=rows+(_read(kind,subset,x,4+step),)
    model=M.fit(rows,mem)
    return rows,model,M.readout(model)

def fabricated_study():
    """Development-only fabricated cohorts; no protected original source use."""
    wall=perf_counter_ns();cpu=process_time_ns()
    mem=M.empty_memory()
    for i in range(16):
        kind="OR" if i%2==0 else "AND"
        s=_subset("FIT",i)
        xs=(1,2,4,8,16,32,21,42)
        rows=tuple(_read(kind,s,x,k) for k,x in enumerate(xs))
        mem=M.remember(mem,rows,world_id=i)
    mem=M.freeze(mem)
    if M.restore(mem)!=mem:
        raise AssertionError("WSP152_COLD_PRIOR_INTEGRITY_FAIL")
    counts={p:{"correct":0,"wrong":0,"abstain":0,
               "held":0,"globally_blocked_worlds":0,
               "confidence_eligible_worlds":0} for p in ("fixed","eig","coverage")}
    world_rows=[]
    for i in range(16):
        kind=("OR" if i%2==0 else "AND") if i<12 else "XOR"
        s=_subset("TRANSFER" if i<12 else "OFF",i,off=i>=12)
        arms={p:_policy(kind,s,p,mem) for p in counts}
        paid=set(x for r,model,preds in arms.values() for x,y,prov in r)
        held=tuple(x for x in range(64) if x not in paid)
        if len(held)<40:raise AssertionError("WSP152_SHARED_HELD_TOO_SMALL")
        result={"index":i,"cohort":"on" if i<12 else "off",
                "held":len(held),"arms":{}}
        # All prediction vectors were constructed before these truth reads.
        for name,(rows,model,preds) in arms.items():
            c=ceiling(model)
            if c["globally_blocked"]:
                counts[name]["globally_blocked_worlds"]+=1
                if any(v is not None for v in preds):
                    raise AssertionError("WSP152_CONFIDENCE_CEILING_VIOLATION")
            else:counts[name]["confidence_eligible_worlds"]+=1
            good=bad=abst=0
            for x in held:
                y=preds[x]
                if y is None:abst+=1
                elif y==_effect(kind,s,x):good+=1
                else:bad+=1
            for metric,v in (("correct",good),("wrong",bad),
                             ("abstain",abst),("held",len(held))):
                counts[name][metric]+=v
            result["arms"][name]={
                "correct":good,"wrong":bad,"abstain":abst,
                "unknown_num":c["unknown"].numerator,
                "unknown_den":c["unknown"].denominator,
                "blocked":c["globally_blocked"],
                "actions":tuple(x for x,_,_ in rows),
                "prediction_seal":_digest(preds)}
        world_rows.append(result)
    den=sum(w["held"] for w in (world_rows))
    if den<16*40 or any(v["held"]!=den for v in counts.values()):
        raise AssertionError("WSP152_COHORT_SCORE_DRIFT")
    baseline=max(counts["fixed"]["correct"],counts["eig"]["correct"])
    improved=counts["coverage"]["correct"]
    gain_pp=100*(improved-baseline)/den
    wrong_extra=counts["coverage"]["wrong"]-min(counts["fixed"]["wrong"],counts["eig"]["wrong"])
    label=("SOURCEFREE_CONFIDENCE_POLICY_DEVELOPMENT_GAIN"
           if gain_pp>=5 and wrong_extra<=0
           else "SOURCEFREE_CONFIDENCE_POLICY_NO_GO")
    science={"classification":label,"gain_pp_vs_best":round(gain_pp,6),
             "wrong_increase_vs_safest":wrong_extra,
             "worlds":16,"on":12,"off":4,"held_total":den,
             "per_policy":counts,"memory_sha256":mem["digest"],
             "world_receipt_sha256":_digest(world_rows),
             "cpu_s":round((process_time_ns()-cpu)/1e9,4),
             "wall_s":round((perf_counter_ns()-wall)/1e9,4),
             "scientific_pass":False,"protected_first_use":False}
    return science,tuple(world_rows)
