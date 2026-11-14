"""Static integrity gate for completed WSP98 PUBLIC first-use, never re-evaluates worlds."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
FROZEN = "eee67aee99ae074b45cdf56b94ce1a133151d808"
FIRST_USE = "22da8ab85e4a4c5ee05ef03c2e56d704b4e5e4d0"
RUN = 43596821829


def verify():
    p = json.loads((HERE / "PUBLIC_PASS.json").read_text(encoding="utf-8"))
    c = p.get("correct", {})
    checks = p.get("checks", {})
    if (p.get("schema") != "wsp98.original-public-dual-os-admission.v1" or
        p.get("prereg_commit") != FROZEN or p.get("first_use_sha") != FIRST_USE or
        p.get("first_use_run_id") != RUN or
        p.get("classification") != "PUBLIC_FEASIBLE" or
        not p.get("deterministic_cross_os_equal") or
        set(p.get("deterministic_fields_compared", [])) != {
          "schema","cohort","world_ids","worlds","passive_rows","active_actions",
          "random_actions","queries","diagnostic_queries","identifiable_active",
          "identifiable_passive","correct","diagnostic_correct","cold_restores",
          "tamper_rejections","replay_rejections","unknown_refusals","interleaved_memory",
          "source_fit","receipts","classification","checks","science_superiority",
          "reserved_untouched"} or
        p.get("world_ids") != list(range(98011, 98031)) or
        p.get("worlds") != 20 or p.get("queries") != 400 or
        p.get("passive_rows") != 480 or p.get("active_actions") != 160 or
        p.get("random_actions") != 160 or
        p.get("identifiable_active", 0) < 600 or
        p.get("identifiable_active", 0) - p.get("identifiable_passive", 99999) < 240 or
        c.get("direct_active", 0) < 1920 or
        c.get("direct_active", 0) - c.get("passive_only", 99999) < 120 or
        c.get("direct_active", 0) - c.get("direct_random", 99999) < 72 or
        not all(checks.values()) or len(checks) != 5 or
        p.get("cold_restores") != 20 or p.get("tamper_rejections") != 20 or
        p.get("replay_rejections") != 20 or p.get("unknown_refusals") != 20 or
        p.get("interleaved_memory") is not True or
        p.get("scientific_superiority") is not False or
        p.get("reserved_worlds_untouched") is not True or
        len(p.get("original_public_world_receipts", [])) != 20 or
        [x.get("world_id") for x in p["original_public_world_receipts"]] != list(range(98011, 98031)) or
        any(not isinstance(x.get(k), str) or len(x[k]) != 64
            for x in p["original_public_world_receipts"]
            for k in ("source_sha256", "active_plans_sha256", "random_plans_sha256",
                      "original_targets_sha256", "pre_scoring_predictions_sha256")) or
        set(p.get("platforms", {})) != {"ubuntu", "windows"} or
        any(v.get("conclusion") != "success" or v.get("whole_process_cpu_ns", 0) <= 0
            for v in p["platforms"].values())):
        raise ValueError("original WSP98 public qualification evidence invalid")
    return p


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--public-pass", required=True, action="store_true")
    parser.parse_args()
    p = verify()
    print("WSP98_PUBLIC_ADMISSION_VERIFIED=" + json.dumps(
        {"run_id": p["first_use_run_id"], "sha": p["first_use_sha"],
         "classification": p["classification"],
         "scientific_superiority": p["scientific_superiority"]},
        sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
