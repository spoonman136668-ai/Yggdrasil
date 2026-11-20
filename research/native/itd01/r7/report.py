"""Emit original local DEV research evidence, no protected first use."""
from __future__ import annotations
import hashlib
import json
import sys
import time
import tracemalloc
from native_cells import study,gates


def main():
    tracemalloc.start()
    t0=time.process_time()
    results=[study(seed) for seed in (17,31,47)]
    passed=gates(results)
    raw=json.dumps(results,sort_keys=True,separators=(",",":")).encode()
    current,peak=tracemalloc.get_traced_memory()
    report={
        "schema":"itd01.r7.yggdrasil.local-cell.v1",
        "evidence_class":"SOURCE_FREE_PUBLIC_SENSORY_FEEDBACK_PILOT",
        "original_scientific_first_use":False,
        "protected_held_H1_H2_consumed":False,
        "native_architecture":"YGGDRASIL_INDEPENDENT_LOCAL_CELL_PLASTICITY",
        "results":results,"results_sha256":hashlib.sha256(raw).hexdigest(),
        "cpu_seconds_including_public_fixture":round(time.process_time()-t0,6),
        "peak_tracemalloc_bytes_not_whole_process_rss":peak,
        "disposition":"SOURCE_FREE_NATIVE_LEARNING_PASS" if passed
                      else "SOURCE_FREE_NATIVE_LEARNING_NO_GO",
        "full_ITD01_transfer":"NOT_TESTED",
    }
    print(json.dumps(report,sort_keys=True,indent=2))
    return 0 if passed else 2


if __name__=="__main__":
    sys.exit(main())
