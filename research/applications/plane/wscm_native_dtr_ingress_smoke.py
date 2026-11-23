#!/usr/bin/env python3
"""Source-free native ingress smoke using one previously recorded public DTR row."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, platform, sys
from pathlib import Path

# The qualification workflow invokes scripts by path, so Python initially sees
# this script directory, not the checkout root. Add the exact checked-out root.
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

EXPERIMENT="WSCM-NATIVE-DTR-INGRESS-SMOKE-01"
EXPECTED_NATIVE_BLOB="5a77232cdd4a0fda314e47278c9ba0ed109cfd50"
SOURCE_RESULT_SHA256="b8228c4fd94a2b8506d34e2cf7aa95a349b42f8069bc786ca83349479d5f3e7d"
PUBLIC_ROW={"s1":0,"x1":0,"s2":0,"x2":1,"y":1}
VIEWS=((0,0),(0,0))  # duplicate unprojected view pattern from existing native tests

def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii")+data).hexdigest()

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--out",required=True); args=parser.parse_args()
    source=Path("yggdrasil/native_episode_experience.py")
    raw=source.read_bytes()
    actual=git_blob_sha(raw)
    if actual!=EXPECTED_NATIVE_BLOB:
        status="NATIVE_SOURCE_BLOB_MISMATCH"
        metrics={"native_source_blob_expected":EXPECTED_NATIVE_BLOB,"native_source_blob_actual":actual}
        ok=False
    else:
        from yggdrasil.native_episode_experience import NativeEpisodeExperience
        from yggdrasil.native_context_basis import digest
        baseline=NativeEpisodeExperience()
        baseline_raw=baseline.checkpoint()
        identifier=hashlib.sha256(b"wscm-native-dtr-ingress-smoke-20261123/episode-0").hexdigest()
        candidate=baseline.observe(identifier,VIEWS,PUBLIC_ROW)
        candidate_raw=candidate.checkpoint()
        restored=NativeEpisodeExperience.restore(candidate_raw,digest(candidate_raw))
        transition=candidate.forecast((0,0),0)
        terminal=candidate.forecast((0,0),0,0,1)
        ok=(
            baseline.checkpoint()==baseline_raw and len(baseline._ledger)==0 and
            len(candidate._ledger)==1 and candidate._projection is None and
            candidate._mismatches==[0,0] and restored.checkpoint()==candidate_raw and
            transition.numerator==1 and transition.denominator==3 and
            terminal.numerator==2 and terminal.denominator==3 and
            restored._ledger==candidate._ledger
        )
        status="NATIVE_DTR_PUBLIC_ROW_INGRESS_PASS" if ok else "NATIVE_DTR_PUBLIC_ROW_INGRESS_ASSERTION_FAILED"
        metrics={
            "native_source_blob_expected":EXPECTED_NATIVE_BLOB,"native_source_blob_actual":actual,
            "source_public_result_sha256":SOURCE_RESULT_SHA256,"source_public_row":PUBLIC_ROW,
            "views":VIEWS,"views_are_duplicate_unprojected_padding":True,
            "native_scratch_rows_before":len(baseline._ledger),"native_scratch_rows_after":len(candidate._ledger),
            "native_projection":candidate._projection,"native_projection_mismatch_counts":candidate._mismatches,
            "transition_forecast":[transition.numerator,transition.denominator],
            "terminal_forecast":[terminal.numerator,terminal.denominator],
            "baseline_immutability_pass":baseline.checkpoint()==baseline_raw,
            "cold_restore_byte_identical":restored.checkpoint()==candidate_raw,
            "canonical_learner_updated":False,"persistent_checkpoint_written":False,
            "new_source_actions":0,"new_source_resets":0,"new_source_steps":0,
            "new_source_interventions":0,"model_fits":0,"python_version":platform.python_version()
        }
    result={
      "schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,
      "status":status,"metrics":metrics,"scientific_pass":False,
      "scientific_gain_verified":False,"source_first_use":False
    }
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
    return 0
if __name__=="__main__": raise SystemExit(main())
