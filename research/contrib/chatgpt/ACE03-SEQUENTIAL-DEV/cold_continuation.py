"""Bounded cold-process checkpoint/continuation probe; no data generator."""
import base64
import json
import subprocess
import sys
from pathlib import Path

# Embedded Windows Python may omit the script directory from sys.path.
# Resolve only the checked-out sibling modules, not ambient PYTHONPATH.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from transfer_study_eval import ARMS, make_arm, forecast, checkpoint

MAX_BYTES = 16384
MAX_PROBES = 512
MAX_EVENTS = 2816
MAX_REQUEST = 262144


def probe(request):
    arm = request["arm"]
    seed = request["seed"]
    if arm not in ARMS or type(seed) is not int or not 0<=seed<2**32:
        raise ValueError("probe identity")
    raw = base64.b64decode(request["checkpoint"],validate=True)
    if not 0<len(raw)<=MAX_BYTES:
        raise ValueError("checkpoint budget")
    model = type(make_arm(arm,seed)).restore(raw)
    # The serialized control mode/seed must match the caller's expected arm.
    expected = make_arm(arm,seed)
    if hasattr(expected,"mode") and (model.mode,model.seed)!=(expected.mode,expected.seed):
        raise ValueError("control identity mismatch")
    if checkpoint(model)!=raw:
        raise ValueError("initial checkpoint mismatch")
    probes,events = request["probes"],request["events"]
    if len(probes)>MAX_PROBES or len(events)>MAX_EVENTS:
        raise ValueError("probe budget")
    before = [forecast(model,k,p) for k,p in probes]
    seen = []
    for k,p,y in events:
        seen.append(forecast(model,k,p))
        model.observe(model.cursor,k,p,tuple(y))
    return {"before":before,"preupdate":seen,
            "after":[forecast(model,k,p) for k,p in probes],
            "checkpoint":base64.b64encode(checkpoint(model)).decode("ascii"),
            "cursor":model.cursor}


def cold_probe(arm,seed,raw,probes,events=(),timeout=60):
    if not 0<timeout<=60:
        raise ValueError("timeout budget")
    payload=json.dumps({"arm":arm,"seed":seed,"checkpoint":base64.b64encode(raw).decode("ascii"),
                        "probes":probes,"events":events},separators=(",",":"),allow_nan=False).encode("ascii")
    if len(payload)>MAX_REQUEST:
        raise ValueError("request budget")
    child=subprocess.run([sys.executable,"-B",*(['-O'] if sys.flags.optimize else []),str(Path(__file__).resolve())],
                         input=payload,capture_output=True,timeout=timeout,check=False)
    if child.returncode:
        raise RuntimeError('cold child failed: '+child.stderr[:4096].decode('utf-8',errors='replace'))
    return json.loads(child.stdout)


if __name__=="__main__":
    request=sys.stdin.buffer.read(MAX_REQUEST+1)
    if len(request)>MAX_REQUEST:
        raise ValueError("request budget")
    sys.stdout.write(json.dumps(probe(json.loads(request)),separators=(",",":"),allow_nan=False))
