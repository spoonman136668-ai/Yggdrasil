"""Y021 preregistered assignment-order ablation on original R016 selected streams."""
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[4]
Y017=ROOT/"research/contrib/chatgpt/20261012-y017-matching-causality/probe.py"
R016=ROOT/"research/applications/plane/exp-dgr-real-utf8-minimax-matched-consolidation-016.py"
PIN="c4247f69295b25105a91cc402b123493ae63aa68"
RESULT_PIN="138d21335abc10e0eb7bddbbe5dd2a4e4b2ba5ea902d2319dc80eff637df2b29"

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None: raise RuntimeError("Y021_MODULE_UNAVAILABLE")
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def execute():
    if not R016.is_file() or not Y017.is_file():
        raise RuntimeError("Y021_PREDECESSOR_SOURCE_MISSING")
    original_sha=subprocess.run(["git","hash-object","--no-filters",str(R016)],
                               capture_output=True,text=True,check=True).stdout.strip()
    if original_sha!=PIN: raise RuntimeError("Y021_R016_SOURCE_DRIFT")
    r016=load(R016,"y021_original_r016")
    y017=load(Y017,"y021_original_y017")
    baseline=r016.run()
    raw=json.dumps(baseline,allow_nan=False,separators=(",",":")).encode()
    if hashlib.sha256(raw).hexdigest()!=RESULT_PIN:
        raise RuntimeError("Y021_A0_RESULT_IDENTITY_MISMATCH")
    builder=r016.build_matched_minimax_cells
    original_match=r016.deterministic_matching
    stages=[]
    def capture(*args):
        selected=[]
        learner=args[0]
        def observe(l,keys):
            nonlocal selected
            answer=original_match(l,keys)
            if answer is not None and len(keys)==16: selected=list(keys)
            return answer
        r016.deterministic_matching=observe
        try: result=builder(*args)
        finally: r016.deterministic_matching=original_match
        if len(selected)!=16 or result[1]!=16: raise RuntimeError("Y021_SELECTED_KEYS_UNAVAILABLE")
        if len(set(selected))!=16: raise RuntimeError("Y021_DUPLICATE_KEYS")
        a0m=original_match(learner,selected)
        a0g=y017.greedy_first_free(learner,selected)
        if a0m is None or len(a0m)!=16 or a0g is not None:
            raise RuntimeError("Y021_Y017_BASELINE_CONTROL_DRIFT")
        class ReducedLocality:
            def __init__(self, original):
                self.original=original
            def __getattr__(self,name):
                return getattr(self.original,name)
            def local_cells(self,home):
                cells=tuple(self.original.local_cells(home))
                # Preserve native cell order; restrict permitted circular distance to 1.
                return tuple(cell for cell in cells if min((cell-home)%16,(home-cell)%16)<=1)
        local=ReducedLocality(learner)
        def matching_witness(host,keys):
            owner={}
            def augment(key,seen):
                for cell in host.local_cells(host.home_cell(key)):
                    if cell in seen: continue
                    seen.add(cell)
                    previous=owner.get(cell)
                    if previous is None or augment(previous,seen):
                        owner[cell]=key
                        return True
                return False
            for key in keys: augment(key,set())
            matched_keys=set(owner.values())
            unmatched=[key for key in keys if key not in matched_keys]
            reached_keys=set(unmatched)
            reached_cells=set()
            todo=list(unmatched)
            while todo:
                key=todo.pop()
                for cell in host.local_cells(host.home_cell(key)):
                    if cell in reached_cells: continue
                    reached_cells.add(cell)
                    other=owner.get(cell)
                    if other is not None and other not in reached_keys:
                        reached_keys.add(other)
                        todo.append(other)
            neighbors=set()
            for key in reached_keys: neighbors.update(host.local_cells(host.home_cell(key)))
            if neighbors!=reached_cells: raise RuntimeError("Y021_HALL_NEIGHBORHOOD_NOT_EXACT")
            return len(owner),len(reached_keys),len(neighbors)
        one,subset,neighbors=matching_witness(local,selected)
        two,_,_=matching_witness(learner,selected)
        if two!=16 or one>=16 or not subset>neighbors or one!=16-(subset-neighbors):
            raise RuntimeError("Y021_FROZEN_HALL_CONTROL_INVALID")
        if (one,subset,neighbors)!=matching_witness(local,selected):
            raise RuntimeError("Y021_DETERMINISM_DRIFT")
        stages.append({"stage":len(stages)+1,"selected_count":16,
            "radius_one_maximum_cardinality":one,
            "hall_subset_size":subset,"hall_neighbor_count":neighbors,
            "hall_deficiency":subset-neighbors,"radius_two_maximum_cardinality":two})
        return result
    r016.build_matched_minimax_cells=capture
    second=r016.run()
    if json.dumps(second,allow_nan=False,separators=(",",":")).encode()!=raw:
        raise RuntimeError("Y021_SOURCE_REPLAY_DRIFT")
    if len(stages)!=6: raise RuntimeError("Y021_STAGES_NOT_SIX")
    return {"schema":"yggdrasil.y021-hall-witness.v1","frozen_R016_result_sha256":RESULT_PIN,
            "stages":stages,"hall_witnesses":len(stages),"source_identity_mismatch_count":0,
            "model_calls":0,"data_class":"previously_consumed",
            "classification":"SUPPORTED","independent_scientific_acceptance":False}

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    args=p.parse_args()
    result=execute()
    with open(args.output,"x",encoding="utf-8") as f:
        json.dump(result,f,sort_keys=True,indent=2,allow_nan=False)
        f.write("\n")
