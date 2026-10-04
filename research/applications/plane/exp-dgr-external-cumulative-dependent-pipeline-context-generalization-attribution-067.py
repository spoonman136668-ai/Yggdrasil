"""EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-GENERALIZATION-ATTRIBUTION-067."""
import argparse
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT="EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-GENERALIZATION-ATTRIBUTION-067"
PRIOR_PATH=Path("research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-context-indexed-collateral-generalization-066.py")

def load_prior():
    s=importlib.util.spec_from_file_location("ygg066",PRIOR_PATH)
    if s is None or s.loader is None: raise RuntimeError("PRIOR_IMPORT_SPEC_FAILED")
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def run(root):
    p66=load_prior()
    original=p66.run(root)
    m=original["metrics"]
    out={
      "source_identity_mismatch_count":float(m["source_identity_mismatch_count"]),
      "transfer_manifest_identity_mismatch_count":float(m["transfer_manifest_identity_mismatch_count"]),
      "base_training_identity_mismatch_count":float(m["base_training_identity_mismatch_count"]),
      "history_byte_budget_mismatch_count":float(m["history_byte_budget_mismatch_count"]),
      "candidate_selection_heldout_use_count":float(m["candidate_selection_heldout_use_count"]),
      "retained_memory_donor_missing_count":float(m["retained_memory_donor_missing_count"]),
      "gate_context_incompatible_schedule_count":float(m["gate_context_incompatible_schedule_count"]),
      "candidate_reserved_key_missing_count":float(m["candidate_reserved_key_missing_count"]),
      "candidate_required_union_over_capacity_count":float(m["candidate_required_union_over_capacity_count"]),
      "candidate_state_capacity_failure_count":float(m["candidate_state_capacity_failure_count"]),
      "matched_assignment_failure_count":float(m["matched_assignment_failure_count"]),
      "capacity_growth_event_count":float(m["capacity_growth_event_count"]),
      "row_mutation_event_count":float(m["row_mutation_event_count"]),
      "tokenizer_use_count":float(m["tokenizer_use_count"]),
      "external_model_call_count":float(m["external_model_call_count"]),
      "original_invalid_evaluation_rows":float(m["invalid_evaluation_rows"]),
      "preserved_state_structure_count_min":float(m["preserved_state_structure_count_min"]),
      "preserved_state_structure_count_max":float(m["preserved_state_structure_count_max"]),
      "active_structure_count_min":float(m["active_structure_count_min"]),
      "active_structure_count_max":float(m["active_structure_count_max"]),
      "retained_structure_count_min":float(m["retained_structure_count_min"]),
      "retained_structure_count_max":float(m["retained_structure_count_max"]),
      "source_count":float(m["source_count"]),
      "total_source_bytes":float(m["total_source_bytes"]),
      "affected_schedule_count":float(m["affected_schedule_count"]),
      "packet_budget_per_schedule":float(m["packet_budget_per_schedule"]),
      "attribution_replay_mutation_count":0.0,
    }
    assert all(math.isfinite(float(v)) for v in out.values())
    return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"metrics":out,"original_066_result":original}

def main():
    p=argparse.ArgumentParser();p.add_argument("--root",required=True);p.add_argument("--out",required=True);a=p.parse_args()
    with open(a.out,"w",encoding="utf-8",newline="\n") as f: json.dump(run(a.root),f,allow_nan=False,separators=(",",":"))

if __name__=="__main__":main()
