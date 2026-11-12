"""Frozen WSP37 six-regime, three-budget synthetic knowledge-frontier assay."""
import argparse,hashlib,json,platform,random,time
from model import GATES,NumericProgram,acquire,gradient_fit,independent_eval,spec_ok

ARITIES=(2,3,4)
KINDS=("arbitrary","structured")
BUDGETS=("zero","half","full")
COUNTS={"DEV":64,"PRIMARY":256}

def bits(n,width):
    return tuple((n>>i)&1 for i in range(width))
def generator(cohort,arity,kind,world):
    if cohort not in COUNTS or arity not in ARITIES or kind not in KINDS or type(world) is not int or not 0<=world<COUNTS[cohort]:
        raise ValueError("WSP37_BAD_WORLD")
    topo,tables=[],[]
    for gate in range(GATES):
        d=hashlib.sha256(f"WSP37-V1|{cohort}|{arity}|{kind}|{world}|{gate}".encode("ascii")).digest()
        possible=arity+1+gate
        route=tuple((arity+gate) if gate>0 and j==0 else d[3+j]%possible for j in range(arity))
        topo.append(route)
        width=1<<arity
        if kind=="arbitrary":
            truth=bits(int.from_bytes(d[10:12],"little"),width)
        else:
            family=d[0]%3
            if family==0:
                active=(d[1]%(width-1))+1
                truth=tuple(((k&active).bit_count()+d[2])%2 for k in range(width))
            elif family==1:
                flip=d[1]%width
                thresh=d[2]%(arity+2)
                truth=tuple(int((k^flip).bit_count()>=thresh) for k in range(width))
            else:
                selector=d[1]%arity
                a,b=(selector+1)%arity,(selector+2)%arity
                truth=tuple((k>>(b if (k>>selector)&1 else a))&1 for k in range(width))
        tables.append(truth)
    spec_ok(arity,tuple(topo))
    return tuple(topo),tuple(tables)

def schedule(cohort,arity,kind,world,budget):
    if budget not in BUDGETS: raise ValueError("WSP37_BAD_BUDGET")
    width=1<<arity
    count={"zero":0,"half":width//2,"full":width}[budget]
    out=[]
    for g in range(GATES):
        d=hashlib.sha256(f"WSP37-ROWS-V1|{cohort}|{arity}|{kind}|{world}|{g}".encode("ascii")).digest()
        rng=random.Random(int.from_bytes(d[:8],"big"))
        rows=list(range(width)); rng.shuffle(rows)
        out.append(tuple(rows[:count]))
    return tuple(out)
def inputs(arity):
    return tuple(bits(k,arity+1) for k in range(1<<(arity+1)))
def transfer_topology(cohort,arity,kind,world):
    routes=[]
    for g in range(GATES):
        d=hashlib.sha256(f"WSP37-TRANSFER-V1|{cohort}|{arity}|{kind}|{world}|{g}".encode()).digest()
        possible=arity+1+g
        routes.append(tuple((arity+g) if g>0 and j==0 else d[4+j]%possible for j in range(arity)))
    return tuple(routes)

def run(cohort="DEV"):
    if cohort not in COUNTS: raise ValueError("WSP37_BAD_COHORT")
    start=time.perf_counter()
    trace=hashlib.sha256()
    records={}
    sizes={"max_numeric_snapshot_bytes":0,"max_numeric_bits":0}
    guard={"worlds":0,"query_custody":0,"cold_restores":0,"repairs":0,"unaffected_gate_rows":0,"transfer_checks":0,"truth_row_checks":0,"composition_checks":0}
    cost={"acquire_seconds":0.0,"trained_fit_seconds":0.0,"restore_seconds":0.0,"numeric_infer_seconds":0.0,"literal_infer_seconds":0.0,"gradient_updates":0,"worst_bce":0.0,"observations":0}
    unseen_hits=unseen_total=0
    for arity in ARITIES:
      points=inputs(arity)
      for kind in KINDS:
       for budget in BUDGETS:
        key=f"a{arity}_{kind}_{budget}"
        row_total=composed_total=transfer_total=0
        score={k:0 for k in ("direct_gate","trained_gate","literal_gate","zero_gate","direct_composed","trained_composed","literal_composed","zero_composed","direct_transfer","literal_transfer")}
        for world in range(COUNTS[cohort]):
            topo,truth=generator(cohort,arity,kind,world)
            rows=schedule(cohort,arity,kind,world,budget)
            seen=[]
            def probe(g,k):
                if k not in rows[g]: raise AssertionError("WSP37_UNAUTHORIZED_QUERY")
                seen.append((g,k,truth[g][k]))
                return truth[g][k]
            t=time.perf_counter()
            direct,audit=acquire(arity,topo,rows,probe)
            cost["acquire_seconds"]+=time.perf_counter()-t
            if audit!=tuple(seen) or len(audit)!=sum(len(r) for r in rows): raise AssertionError("WSP37_PROBE_CUSTODY")
            guard["query_custody"]+=1; cost["observations"]+=len(audit)
            t=time.perf_counter()
            trained,updates,bce=gradient_fit(direct.tables,rows)
            cost["trained_fit_seconds"]+=time.perf_counter()-t
            cost["gradient_updates"]+=updates; cost["worst_bce"]=max(cost["worst_bce"],bce)
            if trained!=direct.tables: raise AssertionError("WSP37_TRAIN_PARITY")
            t=time.perf_counter()
            raw=direct.snapshot(); restored=NumericProgram.restore(raw)
            cost["restore_seconds"]+=time.perf_counter()-t
            if raw!=restored.snapshot(): raise AssertionError("WSP37_COLD_PARITY")
            sizes["max_numeric_snapshot_bytes"]=max(sizes["max_numeric_snapshot_bytes"],len(raw))
            sizes["max_numeric_bits"]=max(sizes["max_numeric_bits"],direct.bits)
            guard["cold_restores"]+=1
            for g in range(GATES):
                for k,y in enumerate(truth[g]):
                    row_total+=1
                    score["direct_gate"]+=int(restored.tables[g][k]==y)
                    score["trained_gate"]+=int(trained[g][k]==y)
                    score["literal_gate"]+=int(direct.tables[g][k]==y)
                    score["zero_gate"]+=int(y==0)
                    guard["truth_row_checks"]+=1
                    if kind=="arbitrary" and budget=="half" and k not in rows[g]:
                        unseen_hits+=int(restored.tables[g][k]==y); unseen_total+=1
            for x in points:
                actual=independent_eval(topo,truth,x)
                t=time.perf_counter()
                numeric=restored.predict(x)
                cost["numeric_infer_seconds"]+=time.perf_counter()-t
                t=time.perf_counter()
                literal=independent_eval(topo,restored.tables,x)
                cost["literal_infer_seconds"]+=time.perf_counter()-t
                if numeric!=literal: raise AssertionError("WSP37_NUMERIC_LITERAL_PARITY")
                score["direct_composed"]+=int(numeric==actual)
                score["trained_composed"]+=int(literal==actual)
                score["literal_composed"]+=int(literal==actual)
                score["zero_composed"]+=int(actual==0)
                composed_total+=1; guard["composition_checks"]+=1
                trace.update(bytes((arity,0 if kind=="arbitrary" else 1,BUDGETS.index(budget),numeric,actual)))
            new_topo=transfer_topology(cohort,arity,kind,world)
            transferred=NumericProgram(arity,new_topo,restored.tables)
            if new_topo==topo: raise AssertionError("WSP37_TRANSFER_NOT_DISTINCT")
            for x in points:
                actual=independent_eval(new_topo,truth,x)
                predicted=transferred.predict(x)
                lit=independent_eval(new_topo,transferred.tables,x)
                if predicted!=lit: raise AssertionError("WSP37_TRANSFER_VM_PARITY")
                score["direct_transfer"]+=int(predicted==actual)
                score["literal_transfer"]+=int(lit==actual)
                transfer_total+=1; guard["transfer_checks"]+=1
            if budget=="full":
                row=(world+arity)%(1<<arity)
                changed=restored.patch(GATES-1,row,1-truth[-1][row])
                if changed.tables[-1][row]!=1-truth[-1][row] or changed.snapshot()==raw: raise AssertionError("WSP37_REPAIR_NOT_EFFECTIVE")
                for g in range(GATES):
                    for k in range(1<<arity):
                        if (g,k)!=(GATES-1,row):
                            if changed.tables[g][k]!=restored.tables[g][k]: raise AssertionError("WSP37_REPAIR_CORRUPTED_OTHER")
                            guard["unaffected_gate_rows"]+=1
                if NumericProgram.restore(changed.snapshot()).tables!=changed.tables: raise AssertionError("WSP37_REPAIR_NOT_PERSISTED")
                guard["repairs"]+=1
            guard["worlds"]+=1
        records[key]={"primitive":{k:score[k] for k in ("direct_gate","trained_gate","literal_gate","zero_gate")},
                      "primitive_total":row_total,
                      "composition":{k:score[k] for k in ("direct_composed","trained_composed","literal_composed","zero_composed")},
                      "composition_total":composed_total,
                      "transfer":{k:score[k] for k in ("direct_transfer","literal_transfer")},
                      "transfer_total":transfer_total}
    full_good=all(r["primitive"]["direct_gate"]==r["primitive_total"] and r["composition"]["direct_composed"]==r["composition_total"] and r["transfer"]["direct_transfer"]==r["transfer_total"] for k,r in records.items() if k.endswith("_full"))
    comparable=all(r["primitive"]["direct_gate"]==r["primitive"]["trained_gate"]==r["primitive"]["literal_gate"] and r["composition"]["direct_composed"]==r["composition"]["trained_composed"]==r["composition"]["literal_composed"] for r in records.values())
    half_unseen=unseen_hits/unseen_total if unseen_total else -1
    unlearnable=.42<=half_unseen<=.58
    eligible=all((full_good,comparable,unlearnable,
                  guard["worlds"]==COUNTS[cohort]*len(ARITIES)*len(KINDS)*len(BUDGETS),
                  guard["repairs"]==COUNTS[cohort]*len(ARITIES)*len(KINDS),
                  cost["worst_bce"]<=.01,cost["gradient_updates"]>0))
    result={"schema":"wsp37.broad-frontier.v1","cohort":cohort,"engineering":"PASS" if eligible else "FAIL",
            "science":"SCIENTIFIC_NEGATIVE" if eligible and comparable else "INVALID",
            "reason":"Full-table direct programming ties matched trained and literal baseline; no performance superiority. Arbitrary half-observation unseen rows remain at chance. Training/copy costs do not establish a matched advantage.",
            "six_regimes_three_budgets":records,"checks":guard,
            "half_arbitrary_unseen":{"correct":unseen_hits,"total":unseen_total,"accuracy":round(half_unseen,6),"required_range":[.42,.58]},
            "capacities":sizes,"cost":{k:round(v,6) if type(v) is float else v for k,v in cost.items()},
            "trace_sha256":trace.hexdigest(),"elapsed_seconds":round(time.perf_counter()-start,6),
            "platform":platform.platform(),
            "bounds":"Public synthetic Boolean truth table memory with supplied graph and privileged row probes; no general knowledge acquisition or independently qualified scientific superiority."}
    if not eligible: raise AssertionError("WSP37_ASSAY_INVALID: "+json.dumps(result,sort_keys=True))
    return result

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--cohort",choices=COUNTS,default="DEV")
    print(json.dumps(run(parser.parse_args().cohort),indent=2,sort_keys=True))
