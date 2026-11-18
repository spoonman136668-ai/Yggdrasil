"""CKAD32 independent pilot evidence audit and original-byte sealer.

Reads JSON receipts only. Never imports the generator or rescores any held
consequence. Stop classification is independent of candidate implementation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEEDS = (9451, 9452)
POLICIES = ("bounded_committee24","uniform_random",
            "fixed_public_order","full_exact_information_gain")
READOUTS = ("native_original","native_sparse","bayes_2880",
            "polynomial_logistic","smoothed_frequency","sham")


def require(condition,code):
    if not condition:
        raise ValueError("CKAD32_PILOT_EVIDENCE_"+code)


def check_receipt(raw,seed,lock):
    d=json.loads(raw)
    require(d.get("schema")=="yggdrasil.ckad32.causal-tournaments.v1"
            and d.get("mode")=="pilot" and d.get("seed")==seed
            and d.get("primary_scored") is False and d.get("lock")==lock,
            "ENVELOPE")
    c=d["case"]
    require(c["seed"]==seed and c["primary_first_use"] is False
            and c["cpu_seconds"]>=0 and c["wall_seconds"]>=0,"SEED_OR_TIME")
    held=c["shared_held_inputs"]
    initial=c["shared_initial_inputs"]
    legal=c["legal_probe_inputs"]
    require(len(held)==12 and len(initial)==6 and len(legal)==14
            and len(set(held+initial+legal))==32
            and all(type(x) is int and 0<=x<32 for x in held+initial+legal),
            "HELD_LEAK_OR_PARTITION")
    arms=c["policy_results"]
    require(set(arms)==set(POLICIES),"POLICY_SET")
    for policy,p in arms.items():
        require(p["policy"]==policy and p["source_rows"]==144 and
                p["old_source_rows"]==48 and p["pressure_rows"]==96 and
                p["held_composite_cases"]==36,"ACTION_BUDGET")
        require(set(p["metrics"])==set(READOUTS) and
                all(m["cases"]==36 and 0<=m["brier"]<=1
                    for m in p["metrics"].values()),"METRIC_SET")
        require(set(p["primitive_coverage"])=={"native_original","native_sparse"}
                and set(p["primitive_wrong"])=={"native_original","native_sparse"} and
                all(0<=v<=1 for v in p["primitive_coverage"].values()) and
                all(0<=v<=36 for v in p["primitive_wrong"].values()),"READOUT_BUDGET")
        require(len(p["posterior_survivors"])==3 and
                all(type(x) is int and 1<=x<=2880 for x in p["posterior_survivors"]),
                "EXACT_GRAMMAR")
        require(len(p["streams"])==3 and len(p["observed_source"])==3,
                "PUBLIC_WITNESS_SHAPE")
        for slot in range(3):
            stream=p["streams"][slot]
            records=p["observed_source"][slot]
            require(stream["initial_survivors"]>=stream["final_survivors"]>=1
                    and stream["final_survivors"]==p["posterior_survivors"][slot],
                    "SURVIVOR_COUNT")
            probes=stream["probes"]
            require(len(probes)==10 and len(records)==16,"PROBE_NUMBER")
            source_x=[x[0]+16*x[1] for x in records]
            source_y=[x[2] for x in records]
            require(source_x[:6]==initial and
                    len(set(source_x))==16 and
                    all(x in legal for x in source_x[6:]) and
                    all(type(y) is int and y in (0,1) for y in source_y),
                    "PROBE_SOURCE_RECONCILIATION")
            available=set(legal)
            previous=stream["initial_survivors"]
            for step,rec in enumerate(probes):
                x,y=source_x[6+step],source_y[6+step]
                require(rec["step"]==step and rec["public_input"]==x and
                        rec["revealed_consequence"]==y and x in available and
                        rec["survivors_before"]==previous and
                        1<=rec["survivors_after"]<=previous,
                        "SURVIVOR_TRANSITION")
                if policy=="bounded_committee24":
                    require(1<=rec["committee_size"]<=24 and
                            rec["committee_size"]<=previous and
                            0<=rec["disagreement"]<=.25,"BOUNDED_COMMITTEE")
                elif policy=="full_exact_information_gain":
                    require(rec["committee_size"]==previous and
                            0<=rec["disagreement"]<=.25,"EXACT_POSTERIOR_CONTROL")
                else:
                    require(rec["committee_size"]==0 and
                            rec["disagreement"] is None,"SHAM_PROBE_METADATA")
                if policy=="fixed_public_order":
                    require(x==min(available),"FIXED_POLICY_DRIFT")
                available.remove(x)
                previous=rec["survivors_after"]
            require(previous==stream["final_survivors"],"FINAL_SURVIVOR_DRIFT")
        m=p["model"]
        require(m["cold_restore_exact"] is True and
                m["retention_exact"] is True and
                m["quarantine_exact"] is True and
                0<=m["solver_eligible"]<=m["solver_attempts"]<=3
                and len(m["solver"])==3,"COLD_MEMORY_OR_SOLVER")
        for key in ("before_sha256","cold_sha256"):
            require(set(m[key])=={"native_original","native_sparse"}
                    and all(type(h) is str and len(h)==64 and
                            all(d in "0123456789abcdef" for d in h)
                            for h in m[key].values()),"SHA_PIN")
    return c


def gate(cases):
    require(tuple(c["seed"] for c in cases)==SEEDS,"ORDER")
    candidate="bounded_committee24"
    trigger=any(
        c["policy_results"][candidate]["metrics"]["native_sparse"]["brier"]
        <= min(c["policy_results"][p]["metrics"]["native_sparse"]["brier"]
               for p in ("uniform_random","fixed_public_order"))-.025
        and sum(c["policy_results"][candidate]["posterior_survivors"])/3
        <= sum(c["policy_results"]["uniform_random"]["posterior_survivors"])/3
        for c in cases
    )
    return "PILOT_GO" if trigger else "SCREEN_NO_GO",trigger


def expected_report(pairs,lock_raw):
    cases=[p[2] for p in pairs]
    decision,go=gate(cases)
    return {
        "schema":"yggdrasil.ckad32.pilot-screen.v1",
        "decision":decision,"screen_go":go,
        "pilot_seeds":list(SEEDS),
        "primary_seeds_untouched":[1451,1452,1453],
        "primary_scored":False,
        "source_lock_sha256":hashlib.sha256(lock_raw).hexdigest(),
        "pilot_receipt_sha256":{str(seed):hashlib.sha256(raw).hexdigest()
                                for seed,raw,_ in pairs},
        "scores":{str(c["seed"]):{
            "committee_native_sparse_brier":c["policy_results"]["bounded_committee24"]["metrics"]["native_sparse"]["brier"],
            "random_native_sparse_brier":c["policy_results"]["uniform_random"]["metrics"]["native_sparse"]["brier"],
            "fixed_native_sparse_brier":c["policy_results"]["fixed_public_order"]["metrics"]["native_sparse"]["brier"],
            "exactIG_native_sparse_brier":c["policy_results"]["full_exact_information_gain"]["metrics"]["native_sparse"]["brier"],
            "committee_posterior_survivors":c["policy_results"]["bounded_committee24"]["posterior_survivors"],
            "random_posterior_survivors":c["policy_results"]["uniform_random"]["posterior_survivors"]
        } for c in cases},
    }


def audit():
    lock_raw=(HERE/"source_lock.json").read_bytes()
    lock=json.loads(lock_raw)
    pairs=[]
    for seed in SEEDS:
        raw=(HERE/f"pilot-{seed}.json").read_bytes()
        pairs.append((seed,raw,check_receipt(raw,seed,lock)))
    expected=expected_report(pairs,lock_raw)
    report=json.loads((HERE/"pilot_screen_report.json").read_bytes())
    require(report==expected,"REPORT_IDENTITY")
    cert=HERE/"pilot_certificate.json"
    if expected["screen_go"]:
        require(cert.is_file(),"PILOT_CERT_MISSING")
        d=json.loads(cert.read_bytes())
        require(d=={
            "schema":"yggdrasil.ckad32.pilot-certificate.v1",
            "screen_go":True,"primary_scored":False,
            "source_lock_sha256":expected["source_lock_sha256"],
            "pilot_receipt_sha256":expected["pilot_receipt_sha256"],
            "pilot_seeds":list(SEEDS)
        },"CERT_IDENTITY")
    else:
        require(not cert.exists(),"UNAUTHORIZED_PRIMARY_CERT")
    return report


def seal(root):
    lock_raw=(HERE/"source_lock.json").read_bytes()
    lock=json.loads(lock_raw)
    pairs=[]
    for seed in SEEDS:
        raw=(root/f"ckad32-pilot-{seed}"/"result.json").read_bytes()
        pairs.append((seed,raw,check_receipt(raw,seed,lock)))
    report=expected_report(pairs,lock_raw)
    for seed,raw,_ in pairs:
        (HERE/f"pilot-{seed}.json").write_bytes(raw)
    (HERE/"pilot_screen_report.json").write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    if report["screen_go"]:
        d={
            "schema":"yggdrasil.ckad32.pilot-certificate.v1",
            "screen_go":True,"primary_scored":False,
            "source_lock_sha256":report["source_lock_sha256"],
            "pilot_receipt_sha256":report["pilot_receipt_sha256"],
            "pilot_seeds":list(SEEDS)}
        (HERE/"pilot_certificate.json").write_text(json.dumps(d,sort_keys=True,indent=2)+"\n")
    require(audit()==report,"AUDIT_DISAGREEMENT")
    print(json.dumps(report,sort_keys=True))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",type=Path)
    args=ap.parse_args()
    if args.root is None:
        print(json.dumps(audit(),sort_keys=True))
    else:
        seal(args.root)


if __name__=="__main__":
    main()
