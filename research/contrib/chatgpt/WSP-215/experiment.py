"""WSP215: fresh frozen cohort on exact, untouched WSP214 mechanism implementation.

Read-only source loading, no previous cohort replay, no native Yggdrasil data.
WSP215 prereg freeze bbb386dec56f01002a16278c8375c7d71b2302a1.
"""
from __future__ import annotations
from collections import defaultdict
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "WSP-214" / "experiment.py"
EXPECTED_BLOB = "d56c3e842a6b42e3f9c85fc2660a17c055b3c129"
SCHEMA = "wsp215.gate-admission.source-free.v1"
PREREG = "bbb386dec56f01002a16278c8375c7d71b2302a1"
WORLDS = ((21503, "hub", 24), (21504, "complete", 12),
          (21505, "hub", 24), (21506, "complete", 12))
PREVIOUS_PRIMARY = frozenset((21401,21402,21403,21404,
                              21411,21412,21413,21414))


def _git_blob_sha(path):
    raw = path.read_bytes().replace(b"\r\n",b"\n")
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") +
                        b"\0" + raw).hexdigest()


if _git_blob_sha(SRC) != EXPECTED_BLOB:
    raise RuntimeError("WSP215 exact frozen predecessor code drift")

_spec = importlib.util.spec_from_file_location("wsp215_private_frozen_gate_implementation", SRC)
if _spec is None or _spec.loader is None:
    raise RuntimeError("WSP215 source-exact implementation unavailable")
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)

# This module is a private import. No WSP214 source file or canonical model is
# modified. Change only the independently frozen identity and source-world key.
_base.SCHEMA = SCHEMA
_base.PREREG = PREREG
_base.WORLDS = WORLDS
_base.FORBIDDEN = frozenset(set(_base.FORBIDDEN) | set(PREVIOUS_PRIMARY))
_base.POLICY_SCHEMA = "wsp215.policy-bound-gate.v1"
SYNTHETIC_DIGEST = _base.SYNTHETIC_DIGEST
MODELS = _base.MODELS
ConsensusGate = _base.ConsensusGate
SurpriseGate = _base.SurpriseGate
RandomGate = _base.RandomGate


def metadata(world):
    if world not in WORLDS or world[0] in _base.FORBIDDEN:
        raise ValueError("not a frozen WSP215 source-free world")
    seed, topology, n = world
    gene = f"FABRICATED_WSP215_{seed}"
    pairs = defaultdict(list)
    for i, j in _base._pairs(topology, n):
        group = _base.pair_group(gene, i, j)
        bucket = _base.group_bucket(group)
        if bucket == "FIT":
            pairs[(bucket, _base.fit_stage(group))].append((i,j,group))
        elif bucket == "PUBLIC_DEV":
            pairs[(bucket, None)].append((i,j,group))
    if any(not pairs[("FIT",s)] for s in range(4)) or not pairs[("PUBLIC_DEV",None)]:
        raise ValueError("noncompliant frozen FIT/held partition")
    return gene, pairs


def _factor(seed, alt, pos, k):
    if seed not in {w[0] for w in WORLDS} or alt not in ("C","D") or pos < 1 or k not in range(4):
        raise ValueError("nonfrozen synthetic WSP215 source")
    key = f"WSP215\0{seed}\0{alt}\0{pos}\0{k}".encode("utf-8")
    return hashlib.sha256(key).digest()[0] % 7 - 3


# The exact inherited gate algorithm/score/thresholds call these two names
# by module-global lookup. A *private* module is configured only once.
_base.metadata = metadata
_base._factor = _factor
run_world = _base.run_world
run_primary = _base.run_primary
classify = _base.classify


if __name__ == "__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",required=True)
    args=ap.parse_args()
    result=run_primary()
    Path(args.output).write_text(json.dumps(
        result,sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print("WSP215_CLASSIFICATION="+result["classification"])
    for w in result["worlds"]:
        print("WSP215_WORLD="+str(w["world"])+" STATUS="+w["status"]+
              " GAIN="+str(w.get("strong_gain",False))+
              " RECOVER="+str(w.get("consensus_better_strict",False))+
              " STRICT_WRITES="+str(sum(d["strict_selected"] for d in w["diagnostics"]))+
              " SOFT_BUDGET="+str(sum(d["k"] for d in w["diagnostics"])))
