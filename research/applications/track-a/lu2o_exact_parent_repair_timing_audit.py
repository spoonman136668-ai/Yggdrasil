#!/usr/bin/env python3
import hashlib, json, sys
from pathlib import Path

import lu2n_contiguous_16cell_lesion_robustness_v1 as n

LU2NF1="a4657c94a654d2b4f83b6af0c7844b65e6999593"
BOUND_BUNDLE_SHA256="a14a1f4dad871d196628f7e62218aad115ada1eb8e9fc98bfb8ca28081809f24"
BOUND_MANIFEST_SHA256=[
"f6ba25119e06212c096f8d2bcd8ba9a9bb50d3d31d9d5431fe95e38837b7632e",
"4ef388baed20466e8d87ba1941cd67524e3bf40b2169b6cf7177711d9f8930bc",
"e771f5c7b0406645246aa7a23b05cdb6e9fbcc149b3cfcf1c5553eddce13b6b6",
"8b5b737385df199055cd5ff9ebd13a8df4472917451c03915114f0cd9ac1ef06",
"4643c3371201a38f096566c2d4cee3a4aa3736c384ab4708a57cc6b4ede36cf5",
"a906e490770542fe36c1d77ff7a91aa62509252c3ba9f13087d44fc7888bec8e",
"547d666074df254bf567eedb27dab65967c6f689ee2354946cfd484c070151b1",
"1f540211c6ab447deb40e7233291743ecfcc6e5b94d6eee5de149f7e0a050a97",
"18a418649e8d040a2d737122cdf50355287d5aee399800c4d6fccb6cc1196fba",
"ced52c52d1268bc15a29dd05713cb90fb4a39d527f6c22fd852f7f4349da43e1"
]
EXPECTED_A0_PROJECTION_SHA256={
1:"c43c321144c94aff02eb81e42718f9f71d09037182e7e5fd3fe8b155b221d9c2",
2:"3757d08a4ca27dbbcc82bdd62b5c1210dd97e1601d4b63235ce645cca15aab87",
3:"af33079f542ea8729612887a15717e1a6df30fc5a60ef166c9312fe4cf976583",
4:"e3a8eeaa59d298013b14da66ab98d1e82a27e6a20bc532e26b934bfee409810d",
5:"8277e64c71174fad23399c810c0699755412d4001d5c379b3f716f038144f76d",
6:"084d00d25af550cb4de936a5016e273a631ef61e7434afd4a1c3ef18b3ab6dff",
7:"a67d984012e79d2f8f55794bcb01b36dbde18ee938f00ee2077ee984b24a8e82",
8:"41dda50c03cf4a6cb95366ba21e6a7e7d448647d6690dbe4ac7f299e3f643214",
9:"6c5cd07b003c21bc2eeace3a6396fae6cd85ef28798c8d3329c77ec55c770e3f",
10:"82e7043433416fde2c54d849030f804fa99a212185f5ce42e355c2c927223d1e"
}
PROJECTION_FIELDS=(
"correct_done","incorrect_done","expired","backlog","operations",
"operations_per_correct_completion","phase","stream_phase","stream_total",
"repair","events","state_sha256","trace_sha256",
"matching_duplicate_cell","matching_duplicate_request"
)

def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":")).encode()

def projection(result):
    return {k:result[k] for k in PROJECTION_FIELDS}

def replay_one(m):
    n.validate_manifest(m)
    g=n.g
    orig_req=g.Task2Request
    orig_do=g.do_operation
    registry={}
    detected_epoch={}

    def tracked_request(*args,**kwargs):
        r=orig_req(*args,**kwargs)
        registry[r.rid]=r
        return r

    def tracked_do(seed,t,cell,op,r,trace):
        before=r.stage
        orig_do(seed,t,cell,op,r,trace)
        if op=="VERIFY" and before=="AT_EGRESS" and r.stage=="REPAIR_PENDING":
            detected_epoch.setdefault(r.rid,t)

    g.Task2Request=tracked_request
    g.do_operation=tracked_do
    try:
        result,_,_=n._with_validation(g.run_world,m,"U_A0")
    finally:
        g.Task2Request=orig_req
        g.do_operation=orig_do

    rep=m["replicate"]
    raw=canonical(projection(result))
    replay_sha=hashlib.sha256(raw).hexdigest()
    if replay_sha!=EXPECTED_A0_PROJECTION_SHA256[rep]:
        raise SystemExit(f"LU2O replay mismatch replicate={rep} expected={EXPECTED_A0_PROJECTION_SHA256[rep]} actual={replay_sha}")

    timing=[]
    for rid in m["corrupt_ids"]:
        r=registry.get(rid)
        if r is None:
            raise SystemExit(f"LU2O missing request object replicate={rep} rid={rid}")
        det=detected_epoch.get(rid)
        repair=r.repair_epoch
        reverify=r.verified_epoch if r.verified_after_repair else None
        timing.append({
            "rid":rid,
            "arrival_epoch":r.created,
            "first_at_egress_epoch":r.first_egress_epoch,
            "first_verification_detection_epoch":det,
            "first_repair_epoch":repair,
            "first_successful_reverify_epoch":reverify,
            "done_epoch":r.done_epoch,
            "terminal_state_at_epoch_160":r.stage,
            "reached_egress_after_corrupt":bool(r.reached_egress_after_corrupt),
            "detected":bool(r.detected),
            "repaired":bool(r.repaired),
            "verified_after_repair":bool(r.verified_after_repair),
            "expired_epoch":r.expired_epoch,
            "request_age_at_first_detection":None if det is None else det-r.created,
            "request_age_at_first_repair":None if repair is None else repair-r.created,
            "request_age_at_successful_reverify":None if reverify is None else reverify-r.created,
            "epochs_remaining_after_first_detection":None if det is None else 159-det,
            "epochs_remaining_after_first_repair":None if repair is None else 159-repair,
        })

    return {
        "replicate":rep,
        "manifest_sha256":m["manifest_sha256"],
        "accepted_projection_sha256":EXPECTED_A0_PROJECTION_SHA256[rep],
        "replay_projection_sha256":replay_sha,
        "replay_integrity":True,
        "repair_summary":result["repair"],
        "correct_done":result["correct_done"],
        "incorrect_done":result["incorrect_done"],
        "expired":result["expired"],
        "timing":timing,
    }

def main():
    ms=n.primary_manifests(LU2NF1)
    bundle=canonical(ms)
    if hashlib.sha256(bundle).hexdigest()!=BOUND_BUNDLE_SHA256:
        raise SystemExit("LU2O bound manifest bundle mismatch")
    if [m["manifest_sha256"] for m in ms]!=BOUND_MANIFEST_SHA256:
        raise SystemExit("LU2O bound manifest identity mismatch")

    rows=[replay_one(m) for m in ms]
    failed=[]
    for row in rows:
        if row["replicate"] not in (5,8,10):
            continue
        pending=[
            x for x in row["timing"]
            if x["reached_egress_after_corrupt"] and x["detected"] and not x["repaired"]
        ]
        failed.append({"replicate":row["replicate"],"unrepaired_detected":pending})

    out={
        "schema":1,
        "lu2o_replay_integrity":all(r["replay_integrity"] for r in rows),
        "accepted_lu2n_primary_sha256":"a742491a9282e346d848850000c0f24a3f6ea7fdf4b8c62eefa35e7f31432d77",
        "lu2nf1":LU2NF1,
        "failed_world_timing":failed,
        "all_worlds":rows,
    }
    Path(sys.argv[1]).write_bytes(canonical(out))

if __name__=="__main__":
    main()
