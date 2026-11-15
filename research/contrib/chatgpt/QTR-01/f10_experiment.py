#!/usr/bin/env python3
"""F10 preregistered synthetic DEV only. External causal map is supplied, not learned."""
import argparse
import json
import time
from f10_fixture import SEEDS,events,relation,shuffled,truth
from f10_transfer import PublicCausalCells,Link,NativeTransfer,ExactRetrieval
PREREG="3b93f0a4725c6a01f4f20f9bb3eb47bd88174edc"
def links(rows): return {t:Link(*pair) for t,pair in rows.items()}
def run():
    begin=time.perf_counter_ns()
    result=dict.fromkeys(("native","retrieval","shuffled","cold","interference"),0)
    no_map_answers=0
    corrections=0
    map_sizes=[]
    for seed in SEEDS:
        data=events(seed);cells=PublicCausalCells()
        for s,a,y in data:cells.observe(s,a,y)
        frozen=cells.snapshot()
        graph=links(relation(seed))
        map_sizes.append(len(json.dumps({str(t):(e.source,e.flip) for t,e in graph.items()},
                                        sort_keys=True,separators=(",",":")).encode("ascii")))
        native=NativeTransfer(cells,graph)
        lookup=ExactRetrieval(data,graph)
        random_map=NativeTransfer(cells,links(shuffled(seed)))
        cold=NativeTransfer(PublicCausalCells.restore(frozen),graph)
        for target in range(4):
            correct=truth(seed,target)
            result["native"]+=native.choose_target(target)==correct
            result["retrieval"]+=lookup.choose_target(target)==correct
            result["shuffled"]+=random_map.choose_target(target)==correct
            result["cold"]+=cold.choose_target(target)==correct
            no_map_answers+=cells.choose(target,retained=True) is not None
        if cells.snapshot()!=frozen: raise ValueError("READOUT_MUTATION")
        for address in (4,5,6):
            for a in (0,1):cells.observe(address,a,a)
        for a in (0,1):cells.observe(8,a,a,retained=True)
        for target in range(4):
            result["interference"]+=native.choose_target(target)==truth(seed,target)
        t=next(t for t,e in graph.items() if e.source==0)
        before=native.choose_target(t)
        original_source_action=before^graph[t].flip
        for _ in range(9):
            cells.observe(0,original_source_action,0)
            cells.observe(0,original_source_action^1,1)
        corrections+=native.choose_target(t)==(before^1)
    expected={"native":32,"retrieval":32,"shuffled":16,"cold":32,"interference":32}
    feasible=result==expected and no_map_answers==0 and corrections==8
    return {"schema":"yggdrasil.qtr01.f10.dev.v1","preregistration_commit":PREREG,
            "classification":"DEV_INTERFACE_PARITY_ONLY" if feasible else "DEV_NEGATIVE",
            "scientific_pass":False,"donor_qwen_used":False,"source_map_supplied_not_learned":True,
            "native_source":"yggdrasil.public_causal_cells.PublicCausalCells",
            "seeds":len(SEEDS),"public_action_outcome_events":len(SEEDS)*32,"target_queries":32,
            "correct_counts":result,"no_transfer_target_answers":no_map_answers,
            "contradiction_source_updates_reached_targets":corrections,
            "native_memory_bytes":PublicCausalCells.LEARNED_BYTES,
            "native_checkpoint_bytes":PublicCausalCells.CHECKPOINT_BYTES,
            "external_map_bytes_min":min(map_sizes),"external_map_bytes_max":max(map_sizes),
            "elapsed_wall_ns":time.perf_counter_ns()-begin,
            "unique_gain_over_strongest_retrieval":result["native"]>result["retrieval"],
            "note":"Explicit structural mapping is privileged prior available to BOTH candidate and exact retrieval control; a tie is not native intelligence gain."}
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--fixed-dev-only",action="store_true",required=True)
    p.parse_args()
    print(json.dumps(run(),indent=2,sort_keys=True))
