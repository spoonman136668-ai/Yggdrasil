"""Y020 preregistered assignment-order ablation on original R016 selected streams."""
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
    if spec is None or spec.loader is None: raise RuntimeError("Y020_MODULE_UNAVAILABLE")
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def execute():
    if not R016.is_file() or not Y017.is_file():
        raise RuntimeError("Y020_PREDECESSOR_SOURCE_MISSING")
    original_sha=subprocess.run(["git","hash-object","--no-filters",str(R016)],
                               capture_output=True,text=True,check=True).stdout.strip()
    if original_sha!=PIN: raise RuntimeError("Y020_R016_SOURCE_DRIFT")
    r016=load(R016,"y020_original_r016")
    y017=load(Y017,"y020_original_y017")
    baseline=r016.run()
    raw=json.dumps(baseline,allow_nan=False,separators=(",",":")).encode()
    if hashlib.sha256(raw).hexdigest()!=RESULT_PIN:
        raise RuntimeError("Y020_A0_RESULT_IDENTITY_MISMATCH")
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
        if len(selected)!=16 or result[1]!=16: raise RuntimeError("Y020_SELECTED_KEYS_UNAVAILABLE")
        if len(set(selected))!=16: raise RuntimeError("Y020_DUPLICATE_KEYS")
        a0m=original_match(learner,selected)
        a0g=y017.greedy_first_free(learner,selected)
        if a0m is None or len(a0m)!=16 or a0g is not None:
            raise RuntimeError("Y020_Y017_BASELINE_CONTROL_DRIFT")
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
        def maximum_cardinality(host,keys):
            owners={}
            def augment(key,seen):
                for cell in host.local_cells(host.home_cell(key)):
                    if cell in seen: continue
                    seen.add(cell)
                    previous=owners.get(cell)
                    if previous is None or augment(previous,seen):
                        owners[cell]=key
                        return True
                return False
            return sum(int(augment(key,set())) for key in keys)
        one=maximum_cardinality(local,selected)
        two=maximum_cardinality(learner,selected)
        if one!=maximum_cardinality(local,selected) or two!=maximum_cardinality(learner,selected):
            raise RuntimeError("Y020_DETERMINISM_DRIFT")
        if two!=16:
            raise RuntimeError("Y020_FROZEN_RADIUS_TWO_CONTROL_INVALID")
        stages.append({"stage":len(stages)+1,"selected_count":16,
            "radius_one_maximum_cardinality":one,
            "radius_two_maximum_cardinality":two})
        return result
    r016.build_matched_minimax_cells=capture
    second=r016.run()
    if json.dumps(second,allow_nan=False,separators=(",",":")).encode()!=raw:
        raise RuntimeError("Y020_SOURCE_REPLAY_DRIFT")
    if len(stages)!=6: raise RuntimeError("Y020_STAGES_NOT_SIX")
    return {"schema":"yggdrasil.y020-cardinality-witness.v1","frozen_R016_result_sha256":RESULT_PIN,
            "stages":stages,"radius_one_below_full_count":sum(int(v["radius_one_maximum_cardinality"]<16) for v in stages),
            "radius_two_full_count":sum(int(v["radius_two_maximum_cardinality"]==16) for v in stages),
            "source_identity_mismatch_count":0,"model_calls":0,"data_class":"previously_consumed",
            "classification":"SUPPORTED" if all(v["radius_one_maximum_cardinality"]<16 and v["radius_two_maximum_cardinality"]==16 for v in stages) else "NEGATIVE",
            "independent_scientific_acceptance":False}

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    args=p.parse_args()
    result=execute()
    with open(args.output,"x",encoding="utf-8") as f:
        json.dump(result,f,sort_keys=True,indent=2,allow_nan=False)
        f.write("\n")
