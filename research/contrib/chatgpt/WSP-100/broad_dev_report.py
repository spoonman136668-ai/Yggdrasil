"""One-shot original-free development diagnostics: exact wide-catalogue uncertainty.

No model is fitted, no heldout outcome is requested and no primary scientific
experiment is run. Prints small SHA-pinned reproducible public DEV receipts.
"""
import json
import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from broad_auditor import audit, ALL_PROGRAMS
from fixture import sources, heldout_plan, canonical_digest
from fixture_auditor import audit_fixture


def main():
    start = time.perf_counter_ns()
    entries = []
    for fid in range(8):
        bundle = sources(fid)
        plan = heldout_plan(bundle)
        beginning = time.perf_counter_ns()
        wider = audit(bundle, plan)
        narrow = audit_fixture(bundle, plan)
        if wider["fraction"] > narrow["fraction"] + 1e-12:
            raise AssertionError("broader hypotheses deceptively increase certainty")
        entries.append({
            "fixture": fid, "source_sha256": bundle["source_sha256"],
            "plan_sha256": plan["plan_sha256"],
            "broad_survivors": wider["survivors"],
            "narrow_survivors": narrow["survivor_count"],
            "broad_identifiable": wider["identifiable"],
            "narrow_fraction": narrow["fraction"],
            "broad_fraction": wider["fraction"],
            "diagnostic_wall_ns": time.perf_counter_ns() - beginning,
        })
    summary = {
        "schema": "wsp100.wide-fixture-diagnostic.v1",
        "classification": "DEV_BROAD_CERTIFIER_ONLY",
        "catalogue_size": len(ALL_PROGRAMS),
        "original_worlds_consumed": False,
        "scientific_superiority": False,
        "entries": entries,
        "mean_broad_identifiability": sum(x["broad_fraction"] for x in entries) / 8,
        "mean_narrow_identifiability": sum(x["narrow_fraction"] for x in entries) / 8,
        "process_wall_ns": time.perf_counter_ns() - start,
    }
    summary["receipt_sha256"] = canonical_digest({
        k: summary[k] for k in ("schema", "classification", "catalogue_size",
                                "original_worlds_consumed", "scientific_superiority",
                                "entries")})
    print("WSP100_BROAD_DEV_DIAGNOSTIC=" + json.dumps(
        summary, sort_keys=True, separators=(",", ":"), allow_nan=False
    ), flush=True)


if __name__ == "__main__":
    main()
