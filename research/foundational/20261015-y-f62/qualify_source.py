"""Y-F62 source-only qualification entrypoint for the EXISTING authorized runner.

One fail-closed invocation; no experimental FIT call, no dispatch, no
workflow/queue mutation, no scientific acceptance or new controller.
Usage: python3 -B research/foundational/20261015-y-f62/qualify_source.py --expect-head EXACT_40_CHARACTER_COMMIT
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib, subprocess, sys

HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[2]
FROZEN={
    "research/foundational/20261015-y-f62/prereg.json":"f0fffb43fc1f344261c4802d917696aaf4035ce0",
    "research/foundational/20261015-y-f62/source_pilot.py":"7ed72deca5584d7c0b6562d74456fa7d4bee6712",
    "research/foundational/20261015-y-f62/audit_public.py":"383fff0bdd8c8b48fde9538d4e4d768db1c1896f",
    "research/foundational/20261015-y-f62/test_precode.py":"3987efb6db00ad773fcc3c261499e39acd3beee5",
    "research/foundational/20261015-y-f62/test_engineering.py":"82b1a3ac3027f30175c893b76c9a9d7a4d9b4a39",
    "research/foundational/20261015-y-f61/prereg.json":"67de09eecedfb5285e90a634a3e55aafa3e4a369",
    "research/foundational/20261015-y-f61/source_pilot.py":"68827a45543639585da82d05e5d301782fbc79a6",
    "research/foundational/20261015-y-f60/source_feasibility.py":"123dd7e979485ae07664118f948cd651b0386526",
    "research/foundational/20261015-y-f59/source_feasibility.py":"232cf1bca7e2d1df5236ffa85c0a20f13a98a6ae",
    "research/foundational/20261015-y-f58/source_feasibility.py":"f275d28e3755e2c90ea482d076d7401d722d71b8",
    "research/foundational/20261015-y-f52/source_pilot.py":"ef06d80c127ca6dab1e496fb855eb36f0dce6d17"
}
def git_blob_sha(path):
    b=path.read_bytes()
    return hashlib.sha1(b"blob "+str(len(b)).encode()+bytes([0])+b).hexdigest()

def output(*args):
    return subprocess.check_output(args,cwd=ROOT,text=True).strip()

def execute(label,argv):
    print("Y_F62_SOURCE_GATE_START="+label,flush=True)
    subprocess.run(argv,cwd=ROOT,check=True)
    print("Y_F62_SOURCE_GATE_PASS="+label,flush=True)

def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument("--expect-head",required=True)
    args=parser.parse_args(argv)
    if len(args.expect_head)!=40 or any(c not in "0123456789abcdef" for c in args.expect_head):
        raise AssertionError("EXACT_40_HEX_HEAD_REQUIRED")
    assert output("git","rev-parse","HEAD")==args.expect_head,"SOURCE_IDENTITY_DRIFT"
    assert not output("git","status","--porcelain"),"DIRTY_WORKTREE"
    subprocess.run(["git","merge-base","--is-ancestor",
        "77adfbb7e7a0f6caebbe27461f8a57470d5d1736","HEAD"],
        cwd=ROOT,check=True)
    for name,expected in FROZEN.items():
        assert git_blob_sha(ROOT/name)==expected, "SOURCE_OR_CONTROL_BLOB_DRIFT: "+name
    prereg=json.loads((HERE/"prereg.json").read_text(encoding="utf-8"))
    assert prereg["stage"]=="PRECODE_FROZEN_NO_FIT_OR_SCIENCE_EXECUTED"
    assert prereg["fit"]["training"]==[761000,761008]
    assert prereg["fit"]["within_fit_validation"]==[761008,761016]
    assert prereg["diagnostic_UNAUTHORIZED"]["seeds"]==[761100,761116]
    assert prereg["original_UNRESERVED"]["seeds"]==[762000,762016]
    assert prereg["authority"]["source_independent_F3"] is False
    assert prereg["thresholds"]["learned_accuracy_gain_vs_strongest_equal_byte_fair_min"]==0.05
    # F60 provenance uses an original Git COMMIT SHA, whereas this harness
    # pins the immutable source Git BLOB SHA. They are different identities.
    provenance=prereg["frozen_control_provenance"]
    assert provenance["F60_exact_source_sha"]=="d20afb1dc0de789be5c8985c1a31ee75038da73b"
    assert provenance["F59_source_blob_sha"]==FROZEN["research/foundational/20261015-y-f59/source_feasibility.py"]
    assert provenance["F58_source_blob_sha"]==FROZEN["research/foundational/20261015-y-f58/source_feasibility.py"]
    assert provenance["F61_source_blob_sha"]==FROZEN["research/foundational/20261015-y-f61/source_pilot.py"]
    assert provenance["F61_historical_trained_int8_weights"]==[39,11,-10,35,17,18,18,28,-7,-83,12,1]
    assert provenance["exact_historical_methods_no_adaptive_refit"] is True
    assert prereg["learned_policy"]["max_serialized_retained_memory_bytes"]==144
    assert prereg["learned_policy"]["parameters_max"]==12
    assert prereg["thresholds"]["positive_composition_retrieval_ablation"] is True
    assert prereg["authority"]["protected_primary_original_executed"] is False
    execute("FROZEN_PRECODE",[
        sys.executable,"-B","-m","unittest","discover","-s",
        str(HERE),"-p","test_precode.py","-v"])
    execute("SOURCE_AND_INDEPENDENT_AUDIT",[
        sys.executable,"-B","-m","unittest","discover","-s",
        str(HERE),"-p","test_engineering.py","-v"])
    execute("SINGLE_FULL_REPOSITORY_REGRESSION",[
        sys.executable,"-B","-m","pytest","-q"])
    print("Y_F62_SOURCE_GATE=PASS",flush=True)
    print(json.dumps(dict(schema="yggdrasil.f62.source-qualification.v1",
        source_head=args.expect_head,stage="SOURCE_ONLY",
        pinned_blob_count=len(FROZEN),
        scientific_fit_train_executed=False,
        scientific_fit_validation_executed=False,
        scientific_diag_or_original_executed=False,
        independent_F3=False,science_eligible_without_owner_authorization=False,
        full_regression_runs=1),sort_keys=True))
if __name__=="__main__":
    try:
        main()
    except (AssertionError,subprocess.CalledProcessError,FileNotFoundError) as exc:
        print("Y_F62_SOURCE_GATE=FAIL",repr(exc),file=sys.stderr)
        sys.exit(1)
