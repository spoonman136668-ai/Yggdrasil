"""G41 development-only score report for G40 toy rule-reversal adaptation.

Emits all positive/negative control scores without scientific efficacy claims.
The frozen primary research gate remains blocked; no protected data are used.
"""
import json
from g40_adaptation import CONDITIONS, adapt

SCHEMA = "yggdrasil.g41.synthetic-development-report.v1"

def build_report():
    rows = []
    for pretrained in (False, True):
        for condition in CONDITIONS:
            result = adapt(condition, pretrained=pretrained)
            rows.append({
                "condition": condition,
                "pretrained": pretrained,
                "source_before": result.source_before,
                "target_before": result.target_before,
                "target_after": result.target_after,
                "target_delta": round(result.target_after - result.target_before, 12),
                "interactions": result.interactions,
                "frames": result.frames,
                "gradient_calls": result.gradient_calls
            })
    get = lambda pretrained, condition: next(row for row in rows if
        row["pretrained"] is pretrained and row["condition"] == condition)
    warm, cold = get(True, "mapped"), get(False, "mapped")
    # Diagnostic labels describe the computed toy signal, not a hypothesis test.
    warm_gain = warm["target_delta"]
    cold_gain = cold["target_delta"]
    controls = [get(True, c)["target_delta"] for c in
                ("reversed", "sham", "no_feedback", "decoder_ablation")]
    signal = ("WARM_MAPPED_GAIN_EXCEEDS_COLD_AND_WARM_CONTROLS"
              if warm_gain > cold_gain and all(warm_gain > x for x in controls)
              else "NO_DISTINCT_WARM_MAPPED_GAIN")
    return {
        "schema": SCHEMA,
        "evidence": "SELF_AUTHORED_SYNTHETIC_DEVELOPMENT_ONLY",
        "primary_execution_allowed": False,
        "scientific_acceptance": "NO_GO",
        "genuine_transfer": "UNVERIFIED",
        "decoder": "FIXED_ENGINEERED_PERIODICITY_TAG",
        "warm_start_has_unmatched_source_pretraining": True,
        "task": "TWO_CUE_BINARY_RULE_REVERSAL_INTERPOLATION",
        "diagnostic_signal": signal,
        "rows": rows,
    }

def serialize_report(report):
    return json.dumps(report, sort_keys=True, separators=(",", ":"), allow_nan=False)

if __name__ == "__main__":
    print("YGG_G41_DEV_REPORT_JSON=" + serialize_report(build_report()), flush=True)
