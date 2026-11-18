"""Read-only independent CKAD31 pilot evidence sealer; does not score any model."""
import argparse
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).parent
PILOT=(9311,9322)
ARMS={"native_original","native_sparse","native_guarded",
      "gf2_conventional","logistic_conventional","smoothed_frequency",
      "bayes_2880","sham"}
COVERAGE={"native_original","native_sparse","native_guarded","gf2_conventional"}


def require(ok,msg):
    if not ok:
        raise ValueError("CKAD31_PILOT_AUDIT_"+msg)


def check(raw,seed,lock):
    doc=json.loads(raw)
    require(doc.get("schema")=="yggdrasil.ckad31.uncertainty-guard.v1" and
            doc.get("mode")=="pilot" and doc.get("B_scored") is False and
            doc.get("lock")==lock,"ENVELOPE")
    c=doc["case"]
    require(c["seed"]==seed and c["source_rows"]==144 and
            c["held_composite_cases"]==48,"CASE_BUDGET")
    require(set(c["metrics"])==ARMS and
            all(v["cases"]==48 and 0<=v["brier"]<=1 and 0<=v["accuracy"]<=1
                for v in c["metrics"].values()),"SCORES")
    require(set(c["coverage"])==COVERAGE and
            all(0<=v<=1 for v in c["coverage"].values()),"COVERAGE")
    require(set(c["confident_wrong"])==COVERAGE,"GUESS_COUNT")
    require(c["confident_wrong"]["native_guarded"]==0 and
            c["confident_wrong"]["gf2_conventional"]==0,"IDENTIFIABILITY_SAFETY")
    require(c["coverage"]["native_guarded"]<=c["coverage"]["native_sparse"]+1e-9 and
            c["coverage"]["native_guarded"]<=c["coverage"]["gf2_conventional"]+1e-9,
            "GUARD_SUBSET")
    require(c["cold_restore_exact"] is True and
            c["old_primitive_retention_exact"] is True and
            c["local_quarantine_exact"] is True,"MEMORY_CUSTODY")
    require(len(c["span_ranks"])==3 and all(0<=v<=16 for v in c["span_ranks"])
            and len(c["solver"])==3 and len(c["bayes_law_counts"])==3
            and all(1<=v<=2880 for v in c["bayes_law_counts"]),"CONTROLS")
    for k in ("source_checkpoint_sha256","cold_checkpoint_sha256"):
        require(set(c[k])=={"native_original","native_sparse"} and
                all(len(h)==64 and all(x in "0123456789abcdef" for x in h)
                    for h in c[k].values()),"SHA_CUSTODY")
    return c


def fixed_decision(cases):
    require(tuple(x["seed"] for x in cases)==PILOT,"ORDER")
    go=any(
        c["coverage"]["native_guarded"] >= 0.10 and
        c["metrics"]["native_guarded"]["brier"] <=
        min(c["metrics"]["native_original"]["brier"],
            c["metrics"]["native_sparse"]["brier"]) - 0.02
        for c in cases
    )
    return ("PILOT_GO" if go else "SCREEN_NO_GO"),go


def audit_sealed():
    lock_raw=(HERE/"source_lock.json").read_bytes()
    lock=json.loads(lock_raw)
    cases=[]
    digests={}
    for seed in PILOT:
        raw=(HERE/f"pilot-{seed}.json").read_bytes()
        cases.append(check(raw,seed,lock))
        digests[str(seed)]=hashlib.sha256(raw).hexdigest()
    decision,go=fixed_decision(cases)
    report=json.loads((HERE/"pilot_screen_report.json").read_bytes())
    require(report=={
        "schema":"yggdrasil.ckad31.pilot-screen.v1",
        "pilot_seeds":list(PILOT),
        "primary_seeds_untouched":[1311,1322,1333],
        "primary_scored":False,
        "classification":decision,"screen_go":go,
        "source_lock_sha256":hashlib.sha256(lock_raw).hexdigest(),
        "pilot_receipt_sha256":digests,
        "pilot_measures":{str(c["seed"]):{
            "native_brier":c["metrics"]["native_original"]["brier"],
            "sparse_brier":c["metrics"]["native_sparse"]["brier"],
            "guard_brier":c["metrics"]["native_guarded"]["brier"],
            "guard_coverage":c["coverage"]["native_guarded"],
            "guard_false_confident":c["confident_wrong"]["native_guarded"]}
                          for c in cases}
    },"SCREEN_REPORT")
    if go:
        certificate=json.loads((HERE/"pilot_certificate.json").read_bytes())
        require(certificate=={
            "schema":"yggdrasil.ckad31.pilot-certificate.v1",
            "screen_go":True,"primary_scored":False,
            "source_lock_sha256":hashlib.sha256(lock_raw).hexdigest(),
            "pilot_receipt_sha256":digests,
            "pilot_seeds":list(PILOT)
        },"CERTIFICATE")
    else:
        require(not (HERE/"pilot_certificate.json").exists(),"UNAUTHORIZED_CERT")
    return report


def seal(root):
    lock_raw=(HERE/"source_lock.json").read_bytes()
    lock=json.loads(lock_raw)
    found=[]
    for seed in PILOT:
        data=(root/f"ckad31-pilot-{seed}"/"result.json").read_bytes()
        found.append((seed,data,check(data,seed,lock)))
    decision,go=fixed_decision([c for _,_,c in found])
    receipts={str(seed):hashlib.sha256(raw).hexdigest() for seed,raw,_ in found}
    report={
        "schema":"yggdrasil.ckad31.pilot-screen.v1",
        "pilot_seeds":list(PILOT),"primary_seeds_untouched":[1311,1322,1333],
        "primary_scored":False,"classification":decision,"screen_go":go,
        "source_lock_sha256":hashlib.sha256(lock_raw).hexdigest(),
        "pilot_receipt_sha256":receipts,
        "pilot_measures":{str(seed):{
            "native_brier":c["metrics"]["native_original"]["brier"],
            "sparse_brier":c["metrics"]["native_sparse"]["brier"],
            "guard_brier":c["metrics"]["native_guarded"]["brier"],
            "guard_coverage":c["coverage"]["native_guarded"],
            "guard_false_confident":c["confident_wrong"]["native_guarded"]}
                          for seed,_,c in found}}
    for seed,data,_ in found:
        (HERE/f"pilot-{seed}.json").write_bytes(data)
    (HERE/"pilot_screen_report.json").write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    if go:
        (HERE/"pilot_certificate.json").write_text(json.dumps({
            "schema":"yggdrasil.ckad31.pilot-certificate.v1",
            "screen_go":True,"primary_scored":False,
            "source_lock_sha256":hashlib.sha256(lock_raw).hexdigest(),
            "pilot_receipt_sha256":receipts,
            "pilot_seeds":list(PILOT)},sort_keys=True,indent=2)+"\n")
    check_report=audit_sealed()
    require(check_report==report,"AUDIT_DRIFT")
    print(json.dumps(report,sort_keys=True))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",type=Path)
    args=ap.parse_args()
    if args.root is None:
        print(json.dumps(audit_sealed(),sort_keys=True))
    else:
        seal(args.root)


if __name__=="__main__":
    main()
