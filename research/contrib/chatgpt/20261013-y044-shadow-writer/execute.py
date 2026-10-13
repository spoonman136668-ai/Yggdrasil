"""Y044: shadow-writer-matched moving motif-key reader ablation."""
import importlib.util
import json
from pathlib import Path

PARENT=Path(__file__).resolve().parent.parent/"20261013-y043-key-frame"/"execute.py"
spec=importlib.util.spec_from_file_location("y043_frozen",PARENT)
assert spec and spec.loader
y43=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y43)
y25=y43.y25

DEV=tuple(range(1016,1024))
HELDOUT=tuple(range(1024,1040))
REGIMES=("drift1","drift3","alternating")
POLICIES=("matched_sham","full","quorum2")
FRAMES=y43.FRAMES


def codec(frame):
    return ("additive" if "additive" in frame else
            "affine" if "affine" in frame else None)


def reader_lookup(records, working_active, adjacency, frame, seed,episode):
    """Reader sees only stored alias+value+birth; writer-only true_key is excluded."""
    law=codec(frame)
    aware=("identity_aware" in frame)
    candidates={}
    for key in working_active:
        for record in reversed(records):
            stored=record["alias"]
            if aware:
                stored=y43.decode(stored,seed,record["birth"],law)
            if stored!=key:
                continue
            if record["cell"] in adjacency[key]:
                candidates[key]=record["cell"]
                break
    return candidates


def shadow_writer(records, physical_active, old_physical_active,
                  old_physical_assignment, seed, episode, law):
    """Evaluator-controlled identical physical departure schedule in all frames.
    raw reader never receives or uses the private physical_key field."""
    active_set=set(physical_active)
    records[:]=[r for r in records if r["physical_key"] not in active_set]
    departing=sorted(old_physical_active.difference(active_set))
    writes=0
    if episode>0:
        for key in departing:
            assert key in old_physical_assignment
            alias=key if law is None else y43.encode(key,seed,episode-1,law)
            records.append({"alias":alias,"cell":old_physical_assignment[key],
                            "birth":episode-1,"physical_key":key})
            writes+=1
            if len(records)>9:
                records.pop(0)
    assert len(records)<=9
    assert all(r["physical_key"] not in active_set for r in records)
    return writes


def evaluate(seed,regime,policy,frame):
    law=codec(frame)
    aware="identity_aware" in frame
    records=[]
    previous_physical_active=set()
    previous_physical_assignment={}
    evaluator_history={}
    rows=[]
    for episode in range(8):
        physical_active=y25.active_keys(seed,episode)
        physical_neighbors=y43.neighbors(seed,episode,physical_active,regime)
        assert y25.hall_cardinality(physical_active,physical_neighbors)==7
        if law is None:
            public_active=list(physical_active)
            public_neighbors=physical_neighbors
        else:
            public_active=[y43.encode(k,seed,episode,law) for k in physical_active]
            public_neighbors={y43.encode(k,seed,episode,law):cells
                              for k,cells in physical_neighbors.items()}
            assert all(y43.decode(y43.encode(k,seed,episode,law),
                                  seed,episode,law)==k for k in range(16))
            assert y25.hall_cardinality(public_active,public_neighbors)==7
        if aware:
            working_active=[y43.decode(key,seed,episode,law)
                            for key in public_active]
            adjacency={y43.decode(key,seed,episode,law):cells
                       for key,cells in public_neighbors.items()}
        else:
            working_active=public_active
            adjacency=public_neighbors
        legal=reader_lookup(records,working_active,adjacency,frame,seed,episode)
        threshold={"matched_sham":999,"full":1,"quorum2":2}[policy]
        preferred=legal if len(legal)>=threshold else {}
        assigned,calls=y25.match(working_active,adjacency,preferred)
        assert len(assigned)==7 and len(set(assigned.values()))==7
        physical=(dict(assigned) if law is None or aware else
                  {y43.decode(k,seed,episode,law):v for k,v in assigned.items()})
        assert set(physical)==set(physical_active)
        returning=[k for k in physical_active if k in evaluator_history]
        churn=sum(physical[k]!=evaluator_history[k] for k in returning)
        for k in physical_active:
            evaluator_history[k]=physical[k]
        writes=shadow_writer(records,physical_active,previous_physical_active,
                             previous_physical_assignment,seed,episode,law)
        previous_physical_active=set(physical_active)
        previous_physical_assignment=dict(physical)
        rows.append({"episode":episode,"physical_assignment":{
                         str(k):physical[k] for k in sorted(physical)},
                     "churn":churn,"cache_writes":writes,
                     "cache_occupancy":len(records),
                     "legal_preferences":len(legal),
                     "applied_preferences":len(preferred),
                     "search_calls":calls,"matched":len(assigned)})
    return {"seed":seed,"frame":frame,"policy":policy,"regime":regime,
            "churn":sum(r["churn"] for r in rows),
            "cache_writes":sum(r["cache_writes"] for r in rows),
            "search_calls":sum(r["search_calls"] for r in rows),
            "rows":rows}


def run():
    discrepancies={frame:0 for frame in FRAMES if frame.endswith("_raw")}
    aware_discrepancies={frame:0 for frame in FRAMES if frame.endswith("_identity_aware")}
    totals={regime:{policy:{frame:0 for frame in FRAMES}
                    for policy in POLICIES} for regime in REGIMES}
    by_regime=[]
    for regime in REGIMES:
        seed_rows=[]
        for seed in DEV+HELDOUT:
            for policy in POLICIES:
                arms={frame:evaluate(seed,regime,policy,frame) for frame in FRAMES}
                reference=arms["reference"]
                for frame,result in arms.items():
                    assert reference["cache_writes"]==result["cache_writes"]
                    for a,b in zip(reference["rows"],result["rows"]):
                        assert a["cache_writes"]==b["cache_writes"]
                        assert a["cache_occupancy"]==b["cache_occupancy"]
                        assert a["matched"]==b["matched"]==7
                        if frame.endswith("_identity_aware"):
                            assert a["physical_assignment"]==b["physical_assignment"]
                        if seed in HELDOUT and a["physical_assignment"]!=b["physical_assignment"]:
                            if frame in discrepancies:
                                discrepancies[frame]+=1
                            elif frame in aware_discrepancies:
                                aware_discrepancies[frame]+=1
                    if seed in HELDOUT:
                        totals[regime][policy][frame]+=result["churn"]
                seed_rows.append({"seed":seed,
                                  "cohort":"development" if seed in DEV else "heldout",
                                  "policy":policy,
                                  "churn":{frame:arm["churn"] for frame,arm in arms.items()},
                                  "cache_writes":reference["cache_writes"]})
        by_regime.append({"regime":regime,"seed_rows":seed_rows})
    any_raw_churn_drift=any(totals[g][p][frame]!=totals[g][p]["reference"]
                            for g in REGIMES for p in POLICIES for frame in discrepancies)
    if all(v==0 for v in aware_discrepancies.values()) and any(v>0 for v in discrepancies.values()) and any_raw_churn_drift:
        classification="READER_BINDING_CAUSAL"
    elif all(v==0 for v in aware_discrepancies.values()) and all(v==0 for v in discrepancies.values()):
        classification="BOOKKEEPING_DOMINANT"
    else:
        classification="PARTIAL"
    return {"schema":"yggdrasil.y044-shadow-matched-key-binding.v1",
            "parent_head":"0f9e6151e2b6e4d9727a343557748ab4039d7d2d",
            "classification":classification,
            "development_seeds":DEV,"sealed_heldout_seeds":HELDOUT,
            "raw_assignment_mismatch_count":discrepancies,
            "aware_assignment_mismatch_count":aware_discrepancies,
            "heldout_churn":totals,"by_regime":by_regime,
            "shadow_writer_privileged":True,
            "model_calls":0,
            "claim_limit":"Mechanistic reader ablation with privileged matched writer, not deployable autonomous raw-ID semantics."}


if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
