"""EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-ORDER-AWARE-REUSE-ATTRIBUTION-043."""
import argparse, importlib.util, json, math
from pathlib import Path

E="EXP-DGR-EXTERNAL-CUMULATIVE-MULTIROW-ORDER-AWARE-REUSE-ATTRIBUTION-043"
P=Path("research/applications/plane/exp-dgr-external-cumulative-multirow-order-aware-novel-interference-reuse-042.py")

def load_prior():
    spec=importlib.util.spec_from_file_location("ygg042",P)
    if spec is None or spec.loader is None:
        raise RuntimeError("PRIOR_IMPORT_FAILED")
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def run(root):
    prior=load_prior().run(root)
    b=prior["metrics"]
    ds=prior["diagnostics"]
    fails=[d for d in ds if d["safety_failure"]]
    m={
      "source_identity_mismatch_count":float(b["source_identity_mismatch_count"]),
      "source_count":float(b["source_count"]),
      "total_source_bytes":float(b["total_source_bytes"]),
      "episode_count":float(len(ds)),
      "base_failure_count":float(len(fails)),
      "failure_order0_count":float(sum(d["target_order_index"]==0 for d in fails)),
      "failure_step1_count":float(sum(d["step_index"]==1 for d in fails)),
      "failure_unguarded_count":float(sum(not d["guard_applied"] for d in fails)),
      "failure_pair0_count":float(sum(d["target_pair_index"]==0 for d in fails)),
      "failure_pair1_count":float(sum(d["target_pair_index"]==1 for d in fails)),
      "failure_pair2_count":float(sum(d["target_pair_index"]==2 for d in fails)),
      "failure_cycle0_count":float(sum(d["cycle_index"]==0 for d in fails)),
      "failure_cycle1_count":float(sum(d["cycle_index"]==1 for d in fails)),
      "failure_cycle2_count":float(sum(d["cycle_index"]==2 for d in fails)),
      "orientation_match_count":float(sum(
          d["target_order_index"]==0 and d["step_index"]==1 and (not d["guard_applied"])
          and d["target_pair_index"] in (0,2) for d in fails
      )),
      "orientation_match_fraction":0.0,
      "positive_post_episode_target_recovery_check_count":float(b["positive_post_episode_target_recovery_check_count"]),
      "positive_post_episode_partner_recovery_check_count":float(b["positive_post_episode_partner_recovery_check_count"]),
      "attribution_accounting_error_count":0.0,
      "heldout_selection_use_count":float(b["heldout_selection_use_count"]),
      "capacity_growth_event_count":float(b["capacity_growth_event_count"]),
      "row_mutation_event_count":float(b["row_mutation_event_count"]),
      "tokenizer_use_count":float(b["tokenizer_use_count"]),
      "external_model_call_count":float(b["external_model_call_count"]),
      "invalid_evaluation_rows":float(b["invalid_evaluation_rows"]),
    }
    if fails:
        m["orientation_match_fraction"]=m["orientation_match_count"]/m["base_failure_count"]
    else:
        m["attribution_accounting_error_count"]+=1.0
    if len(ds)!=216 or len(fails)!=36:
        m["attribution_accounting_error_count"]+=1.0
    if sum(m[k] for k in ("failure_pair0_count","failure_pair1_count","failure_pair2_count"))!=m["base_failure_count"]:
        m["attribution_accounting_error_count"]+=1.0
    if sum(m[k] for k in ("failure_cycle0_count","failure_cycle1_count","failure_cycle2_count"))!=m["base_failure_count"]:
        m["attribution_accounting_error_count"]+=1.0
    assert all(math.isfinite(float(v)) for v in m.values())
    return {
      "schema":"yggdrasil.research-scientific-result.v1",
      "experiment":E,
      "metrics":m,
      "first_failure":prior.get("first_failure"),
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    with open(a.out,"w",encoding="utf-8",newline="\n") as f:
        json.dump(run(a.root),f,allow_nan=False,separators=(",",":"))

if __name__=="__main__":
    main()
