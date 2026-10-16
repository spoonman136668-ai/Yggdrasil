"""Y-F57 FIT-only, source-independent bounded public-memory decoder audit.

Consumes records and public events only. Verifies every stored compressed
relationship is supported by a path of observed public edges and reconstructs
each future answer from frozen records. Does not run source or use DIAG.
"""
import json
import math
import pathlib
import sys

ARMS=("incremental_boundary_merge","frozen_greedy_merge","raw_fifo",
      "full_public_offline_extra_work")
def decode(raw):
    data=bytes.fromhex(raw)
    assert len(data)==12
    start=int.from_bytes(data[:4],"little")
    end=int.from_bytes(data[4:8],"little")
    bits=int.from_bytes(data[8:11],"little")
    size=data[11]
    assert 1<=size<=4 and bits>>(3*size)==0
    return start,end,tuple((bits>>(3*i))&7 for i in range(size))
def inverse(record):
    a,b,steps=record
    return b,a,tuple(code^1 for code in reversed(steps))
def witnessed(record,public):
    a,b,codes=record
    frontier={a}
    for code in codes:
        role=code//2
        reverse=code%2
        assert 0<=role<=3
        nxt=set()
        for u,r,v,_ in public:
            if r!=role:continue
            src,dst=(v,u) if reverse else (u,v)
            if src in frontier:nxt.add(dst)
        assert nxt
        frontier=nxt
    return b in frontier
def answer(records,q):
    seq=tuple(2*role+(direction==-1) for role,direction in q["ops"])
    states={(q["start"],0)}
    for _ in range(len(seq)):
        nxt=set(states)
        for node,i in states:
            for item in records:
                for a,b,codes in (item,inverse(item)):
                    if node==a and seq[i:i+len(codes)]==codes:
                        nxt.add((b,i+len(codes)))
        if nxt==states:break
        states=nxt
    return int((q["answer"],len(seq)) in states)
def audit(d,p):
    assert p["schema"]=="yggdrasil.f57.causal-incremental-component-memory.prereg.v1"
    assert d["schema"]=="yggdrasil.f57.new-online-component-state.fitonly.v1"
    assert d["stage"]=="FIT_ONLY_SOURCE_FEASIBILITY_NO_DIAG_OR_ORIGINAL"
    assert d["fit_seeds"]==p["fit"]["seed_range"]
    assert d["fit_families"]==p["fit"]["families"]
    assert d["cases"]==p["fit"]["cases"]==64
    assert d["diag_unconsumed"] and d["original_unconsumed"]
    assert d["future_question_hidden_during_ingestion"] is True
    assert d["native_total_576B_unverified"] is True
    assert d["offline_reference_is_extra_work_noncompetitive"] is True
    assert len(d["rows"])==64
    seen=set();tally={a:0 for a in ARMS};regime={}
    for row in d["rows"]:
        key=(row["seed"],row["family"])
        assert key not in seen
        seen.add(key)
        assert p["fit"]["seed_range"][0]<=key[0]<p["fit"]["seed_range"][1]
        assert key[1] in p["fit"]["families"]
        assert row["regime"] in p["fit"]["arrival"]
        events=row["public_events"];q=row["question"]
        assert len(events)==72 and len({tuple(e[:3]) for e in events})==72
        assert sum(e[3] for e in events)==36
        assert len(q["ops"]) in p["resource"]["question_hops"]
        assert set(row["scores"])==set(ARMS)
        assert set(row["retained_records"])==set(ARMS)
        assert set(row["serialized_bytes"])==set(ARMS)
        for arm in ARMS:
            held=[decode(r) for r in row["retained_records"][arm]]
            assert len(held)<=p["resource"]["retained_records_max"]
            assert row["serialized_bytes"][arm]==12*len(held)<=144
            assert all(witnessed(rec,events) for rec in held)
            value=answer(held,q)
            assert value==row["scores"][arm]
            tally[arm]+=value
            regime.setdefault(row["regime"],{}).setdefault(arm,0)
            regime[row["regime"]][arm]+=value
    assert len(seen)==64
    assert tally==d["correct"]
    gate=(tally["full_public_offline_extra_work"]/64>=p["FIT_gate_before_diagnostic"]["full_public_offline_accuracy_min"]
       and tally["frozen_greedy_merge"]/64>=p["FIT_gate_before_diagnostic"]["online_constructive_accuracy_min"])
    return {"schema":"yggdrasil.f57.source-free-public-memory-FIT-audit.v1",
        "fit_cases":64,"scores":tally,"regimes":regime,
        "public_source_gate_frozen":gate,
        "source_only_reference_not_learned":True,
        "online_policy_improvement_proven":False,
        "F3_independent":False,
        "heldout_diagnostic_executed":False,
        "protected_original_executed":False}
if __name__=="__main__":
    assert len(sys.argv)==3
    d=json.loads(pathlib.Path(sys.argv[1]).read_text())
    p=json.loads(pathlib.Path(sys.argv[2]).read_text())
    print(json.dumps(audit(d,p),sort_keys=True))
