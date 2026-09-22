#!/usr/bin/env python3
"""Small deterministic research harness for Yggdrasil Application-A experiments.

Scientific mechanisms stay in experiment modules. This file only handles
artifact integrity, stage bookkeeping, duplicate-run comparison, and
portable parent materialization.
"""
from __future__ import annotations
import argparse, base64, gzip, hashlib, json, re, subprocess, sys
from pathlib import Path

SCHEMA = 1
ALLOWED = {
    "PREREGISTERED": {"PARENT_VERIFIED"},
    "PARENT_VERIFIED": {"IMPLEMENTED"},
    "IMPLEMENTED": {"MECHANICAL_VERIFIED"},
    "MECHANICAL_VERIFIED": {"FROZEN"},
    "FROZEN": {"MANIFEST_BOUND"},
    "MANIFEST_BOUND": {"PRIMARY_VERIFIED"},
    "PRIMARY_VERIFIED": {"CLOSED"},
    "CLOSED": set(),
}

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def save_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, sort_keys=True, indent=2) + "\n", encoding="utf-8")

def expected_from_loader(loader: Path) -> str:
    txt=loader.read_text(encoding="utf-8")
    m=re.search(r"EXPECTED=['\"]([0-9a-f]{64})['\"]", txt)
    if not m:
        raise SystemExit(f"no EXPECTED sha256 in loader: {loader}")
    return m.group(1)

def materialize(loader: Path, payload: Path, out: Path):
    expected=expected_from_loader(loader)
    raw=base64.b64decode(payload.read_text(encoding="utf-8").strip(), validate=True)
    src=gzip.decompress(raw)
    got=sha256_bytes(src)
    if got != expected:
        raise SystemExit(f"source hash mismatch expected={expected} got={got}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(src)
    print(json.dumps({"materialized":str(out),"bytes":len(src),"sha256":got},sort_keys=True))
    return got, len(src)

def transition(state_path: Path, target: str, updates: dict | None=None):
    s=load_json(state_path)
    if s.get("schema") != SCHEMA:
        raise SystemExit("unsupported state schema")
    cur=s["status"]
    if target != cur and target not in ALLOWED.get(cur,set()):
        raise SystemExit(f"illegal transition {cur} -> {target}")
    s["status"]=target
    if updates:
        for k,v in updates.items():
            s[k]=v
    save_json(state_path,s)
    return s

def run_pair(command, out1: Path, out2: Path, evidence: Path):
    def one(out):
        argv=[str(out) if x=="{out}" else x for x in command]
        cp=subprocess.run(argv, text=True, capture_output=True)
        if cp.returncode:
            sys.stdout.write(cp.stdout)
            sys.stderr.write(cp.stderr)
            raise SystemExit(cp.returncode)
        return cp
    out1.parent.mkdir(parents=True,exist_ok=True)
    one(out1); one(out2)
    b1,b2=out1.read_bytes(),out2.read_bytes()
    same=b1==b2
    ev={
        "byte_identical":same,
        "run1_sha256":sha256_bytes(b1),
        "run2_sha256":sha256_bytes(b2),
        "run1_bytes":len(b1),
        "run2_bytes":len(b2),
        "command":command,
    }
    save_json(evidence,ev)
    print(json.dumps(ev,sort_keys=True))
    if not same:
        raise SystemExit("duplicate runs are not byte-identical")

def apply_request(request_path: Path, state_path: Path):
    req=load_json(request_path)
    state=load_json(state_path)
    if req.get("experiment") != state.get("experiment"):
        raise SystemExit("request/state experiment mismatch")
    action=req["action"]
    if action=="materialize_parent":
        p=state["parent"]
        got,n=materialize(Path(p["loader"]),Path(p["payload"]),Path(p["materialized_source"]))
        if got != p["expected_source_sha256"]:
            raise SystemExit("state expected parent hash differs from loader")
        p["verified"]=True
        p["verified_bytes"]=n
        p["verified_source_sha256"]=got
        state["parent"]=p
        state["status"]="PARENT_VERIFIED"
        state["last_request"]=req
        save_json(state_path,state)
        return
    if action=="run_pair":
        run_pair(req["command"],Path(req["out1"]),Path(req["out2"]),Path(req["evidence"]))
        state["last_request"]=req
        save_json(state_path,state)
        return
    raise SystemExit(f"unknown action: {action}")

def main():
    ap=argparse.ArgumentParser()
    sp=ap.add_subparsers(dest="cmd",required=True)
    p=sp.add_parser("materialize")
    p.add_argument("--loader",required=True); p.add_argument("--payload",required=True); p.add_argument("--out",required=True)
    p=sp.add_parser("transition")
    p.add_argument("--state",required=True); p.add_argument("--to",required=True)
    p=sp.add_parser("apply-request")
    p.add_argument("--request",required=True); p.add_argument("--state",required=True)
    a=ap.parse_args()
    if a.cmd=="materialize":
        materialize(Path(a.loader),Path(a.payload),Path(a.out))
    elif a.cmd=="transition":
        transition(Path(a.state),a.to)
    elif a.cmd=="apply-request":
        apply_request(Path(a.request),Path(a.state))

if __name__=="__main__":
    main()
