"""NCI-MISMATCH-A3: contradiction audit of a fixed native causal-class model.

Source-free fabricated effects ONLY. Does not import real causal environments.
Every arm seals full held predictions before private held truth is unlocked.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from yggdrasil.native_context_basis import NativeContextBasis, canonical, digest, feature_row

A2 = ROOT / "research/contrib/chatgpt/NCI-ACTIVE-A2/experiment.py"
spec = importlib.util.spec_from_file_location("nci_active_a2_parent", A2)
a2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a2)

IN_SEEDS = tuple(range(300,332))
SHIFT_SEEDS = tuple(range(400,432))
CONDITIONS = (("IN_FAMILY", IN_SEEDS, False, False),
              ("SHIFT", SHIFT_SEEDS, True, False),
              ("CORRUPT", IN_SEEDS, False, True))
AUDIT = 8
FIT = 24
EFFECTS = 32
MIN_IDENTIFIED = 4

def require(ok, reason):
    if not ok:
        raise ValueError("NCI_MISMATCH_A3_" + reason)

def key(label, seed, mask):
    return a2.key("mismatch-a3:"+label, seed, mask)

def independent_rank_add(basis, mask):
    value = feature_row(mask,3)
    while value:
        pivot = value.bit_length()-1
        if pivot not in basis:
            basis[pivot] = value
            return True
        value ^= basis[pivot]
    return False

def audit_inputs(seed, fit_masks, remaining, fit_predictions, strategy):
    """Input-only candidate score uses frozen FIT predictions, never labels."""
    require(strategy in ("target","random"),"AUDIT_STRATEGY")
    require(len(fit_masks)==FIT and len(set(fit_masks))==FIT
            and len(remaining)==40 and not set(remaining)&set(fit_masks),
            "FIT_INPUT_BOUNDARY")
    if strategy=="random":
        return tuple(sorted(remaining, key=lambda m:key("random",seed,m))[:AUDIT])
    rank3 = {}
    for x in fit_masks:
        independent_rank_add(rank3,x)
    pending = set(remaining)
    selected = []
    while len(selected)<AUDIT:
        # Rank candidate by (identified under FIT, degree3 novelty, action
        # balancing, immutable SHA tie). This sees no private source outcome.
        observed_action1 = sum(m>>6 for m in fit_masks+tuple(selected))
        observed_action0 = len(fit_masks)+len(selected)-observed_action1
        def rank_key(m):
            identified = fit_predictions[m] is not None
            novel = independent_rank_add(dict(rank3),m)
            action = m>>6
            improves_balance = (action == 1 and observed_action1 < observed_action0) or (action == 0 and observed_action0 < observed_action1)
            return (0 if identified else 1, 0 if novel else 1,
                    0 if improves_balance else 1, key("target",seed,m))
        best = min(pending,key=rank_key)
        selected.append(best)
        pending.remove(best)
        independent_rank_add(rank3,best)
    return tuple(selected)

def prefit_and_audit(world, seed, fit_masks, fit_effects, audit_masks):
    """Record 8 genuinely new effects and a frozen pre-audit contradiction."""
    fit_vec,fit_checkpoint = a2.native_predictions(fit_masks,fit_effects)
    require(fit_vec==a2.independent_predictions(fit_masks,fit_effects),
            "PREFIT_PARITY")
    effects = tuple(world.observe(m) for m in audit_masks)
    compared = [(fit_vec[m], y) for m,y in zip(audit_masks,effects)
                if fit_vec[m] is not None]
    conflicts = sum(p!=y for p,y in compared)
    eligible = fit_checkpoint is not None and len(compared)>=MIN_IDENTIFIED and conflicts==0
    return {"fit_predictions":fit_vec, "fit_checkpoint":fit_checkpoint,
            "audit_effects":effects, "compared":len(compared),
            "conflicts":conflicts,"gate":eligible}

def compute_native(masks, outcomes):
    vec,raw = a2.native_predictions(masks,outcomes)
    require(vec==a2.independent_predictions(masks,outcomes),
            "FULL_EXACT_SYMBOLIC_PARITY")
    return vec, raw

def metric(pred,held,truth):
    return a2.metric(pred,held,truth)

def case(seed, shifted, corrupt, held, initial, available):
    # Two separately instantiated synthetic actors preserve exact action-call
    # budget (32 per targeted and 32 per random arm).
    pool = initial+available
    target = a2.FabricatedWorld(seed,shifted,held,pool)
    random = a2.FabricatedWorld(seed,shifted,held,pool)
    require(target.source_sha256==random.source_sha256,
            "ACTOR_WORLD_PARITY")
    active_full,_ = a2.choose_inputs("active",seed,initial,available)
    shared_fit = tuple(initial)+tuple(active_full[:16])
    require(len(shared_fit)==FIT and len(set(shared_fit))==FIT,
            "FIT_UNIQUE")
    rest = tuple(m for m in available if m not in shared_fit)
    require(len(rest)==40,"AUDIT_POOL_SIZE")
    original_fit = tuple(target.observe(m) for m in shared_fit)
    replicate_fit = tuple(random.observe(m) for m in shared_fit)
    require(replicate_fit==original_fit,"SHARED_FIT_EFFECTS")
    fit_effects = (tuple(a2.corrupt_labels(seed, shared_fit,original_fit))
                   if corrupt else original_fit)
    provisional,raw24 = compute_native(shared_fit,fit_effects)
    targeted_inputs = audit_inputs(seed,shared_fit,rest,provisional,"target")
    random_inputs = audit_inputs(seed,shared_fit,rest,provisional,"random")
    require(len(set(targeted_inputs))==len(set(random_inputs))==AUDIT,
            "AUDIT_INPUT_COUNT")
    def train_arm(world,audit_masks):
        effects = tuple(world.observe(m) for m in audit_masks)
        compared = [(provisional[m], y) for m,y in zip(audit_masks,effects)
                    if provisional[m] is not None]
        conflicts = sum(p!=y for p,y in compared)
        pass_gate = raw24 is not None and len(compared)>=MIN_IDENTIFIED and conflicts==0
        fit_start=time.perf_counter()
        unvalidated, full_raw = compute_native(
            shared_fit+audit_masks,fit_effects+effects)
        fit_seconds = time.perf_counter()-fit_start
        allowed = pass_gate and full_raw is not None
        gated = unvalidated if allowed else [None]*128
        # Every output is composed before the source reveals held truth.
        return {"audit_masks":audit_masks,"audit_outcomes":effects,
                "identified_audits":len(compared),"contradictions":conflicts,
                "gate_precheck":pass_gate,"admitted":allowed,
                "unvalidated":unvalidated,"gated":gated,"raw32":full_raw,
                "fit_seconds":fit_seconds}
    target_arm = train_arm(target,targeted_inputs)
    random_arm = train_arm(random,random_inputs)
    require(target.effect_calls==random.effect_calls==EFFECTS,
            "EFFECT_BUDGET")
    # Fully trained conventional baseline on same observed masks/effects.
    cart=a2.cart_predictions(seed,
        shared_fit+targeted_inputs,fit_effects+target_arm["audit_outcomes"])
    cart_random=a2.cart_predictions(seed,
        shared_fit+random_inputs,fit_effects+random_arm["audit_outcomes"])
    frozen = [(target_arm["unvalidated"],target_arm["gated"]),
              (random_arm["unvalidated"],random_arm["gated"])]
    require(not target._evaluation_unlocked and not random._evaluation_unlocked,
            "PREDICTION_BEFORE_HELD")
    target.unlock_evaluation()
    random.unlock_evaluation()
    truth=tuple(target.held_outcome(m) for m in held)
    require(truth==tuple(random.held_outcome(m) for m in held),
            "ACTOR_HELD_TRUTH")
    arms={}
    checkpoint_bundle=[]
    for name,arm,cart_pred in (("target",target_arm,cart),
                               ("random",random_arm,cart_random)):
        arms[name]={"observed_effects":EFFECTS,
                    "fit_effects":FIT,"audit_effects":AUDIT,
                    "input_sha256":digest(canonical(shared_fit+arm["audit_masks"])),
                    "fit_label_sha256":digest(canonical(fit_effects)),
                    "audit_input_sha256":digest(canonical(arm["audit_masks"])),
                    "audit_outcome_sha256":digest(canonical(arm["audit_outcomes"])),
                    "identified_audits":arm["identified_audits"],
                    "contradictions":arm["contradictions"],
                    "gate_precheck":arm["gate_precheck"],
                    "admitted":arm["admitted"],
                    "unvalidated":metric(arm["unvalidated"],held,truth),
                    "gated":metric(arm["gated"],held,truth),
                    "cart":metric(cart_pred,held,truth),
                    "native_full_fit_seconds":arm["fit_seconds"]}
        if arm["raw32"] is not None:
            raw=arm["raw32"]
            checkpoint_bundle.append({
               "key":f"{seed}:{int(shifted)}:{int(corrupt)}:{name}",
               "native_ascii":raw.decode("ascii"),
               "checkpoint_sha256":digest(raw),
               "full_predictions_sha256":digest(canonical(arm["unvalidated"]))})
        require(arm["admitted"] == (arm["gate_precheck"] and
                                    arm["raw32"] is not None),"ADMISSION")
        require(arm["gated"] == (arm["unvalidated"] if arm["admitted"]
                                else [None]*128),"GATE_READOUT")
    return {"seed":seed,"shifted":shifted,"corrupt":corrupt,
            "source_sha256":target.source_sha256,
            "held_inputs_sha256":digest(canonical(held)),
            "held_truth_sha256":digest(canonical(truth)),
            "shared_fit_inputs_sha256":digest(canonical(shared_fit)),
            "simulated_effect_calls":target.effect_calls+random.effect_calls,
            "prefit_checkpoint_sha256":digest(raw24) if raw24 else None,
            "arms":arms},checkpoint_bundle

def aggregation(cases):
    summary={}
    for condition in ("IN_FAMILY","SHIFT","CORRUPT"):
        chosen=[c for c in cases
                if (condition=="IN_FAMILY" and not c["shifted"] and not c["corrupt"])
                or (condition=="SHIFT" and c["shifted"])
                or (condition=="CORRUPT" and c["corrupt"])]
        arms={}
        for name in ("target","random"):
            arms[name]={"admitted_worlds":sum(c["arms"][name]["admitted"] for c in chosen),
                        "worlds_with_contradictions":sum(
                            c["arms"][name]["contradictions"]>0 for c in chosen),
                        "contradictions":sum(c["arms"][name]["contradictions"] for c in chosen),
                        "identified_audits":sum(c["arms"][name]["identified_audits"] for c in chosen),
                        "effects":sum(c["arms"][name]["observed_effects"] for c in chosen),
                        "gated":{metric:sum(c["arms"][name]["gated"][metric] for c in chosen)
                                 for metric in ("correct","wrong","abstained","questions")},
                        "unvalidated":{metric:sum(c["arms"][name]["unvalidated"][metric] for c in chosen)
                                 for metric in ("correct","wrong","abstained","questions")},
                        "cart":{metric:sum(c["arms"][name]["cart"][metric] for c in chosen)
                                 for metric in ("correct","wrong","abstained","questions")}}
        summary[condition]={"worlds":len(chosen),"arms":arms}
    return summary

def run(out):
    held,_,initial,available=a2.split_inputs()
    cases=[]
    bundle=[]
    start=time.perf_counter()
    for name,seeds,shifted,corrupt in CONDITIONS:
        for seed in seeds:
            row,models=case(seed,shifted,corrupt,held,initial,available)
            cases.append(row)
            bundle.extend(models)
    require(len(cases)==96 and all(c["simulated_effect_calls"]==64 for c in cases),
            "WORLD_EFFECT_ACCOUNTING")
    bundle_path=out/"native-bundle.json"
    bundle_path.write_bytes(canonical({"schema":"yggdrasil.nci-mismatch-a3.native-bundle.v1",
                                      "models":bundle}))
    script="""import json,sys
from pathlib import Path
from yggdrasil.native_context_basis import NativeContextBasis,canonical,digest
a=json.loads(Path(sys.argv[1]).read_bytes())
for m in a["models"]:
    raw=m["native_ascii"].encode("ascii")
    assert digest(raw)==m["checkpoint_sha256"]
    restored=NativeContextBasis.restore(raw,m["checkpoint_sha256"])
    answers=[restored.predict(0,x&63,x>>6) for x in range(128)]
    assert digest(canonical(answers))==m["full_predictions_sha256"]
print("NCI_MISMATCH_A3_COLD_MODELS="+str(len(a["models"])))"""
    proc=subprocess.run([sys.executable,"-B","-c",script,str(bundle_path)],
                        cwd=ROOT,check=True,capture_output=True,text=True,timeout=90,
                        env=dict(os.environ,PYTHONPATH=str(ROOT),PYTHONDONTWRITEBYTECODE="1"))
    require(proc.stdout.strip()==f"NCI_MISMATCH_A3_COLD_MODELS={len(bundle)}",
            "COLD_RESTORATION")
    summary=aggregation(cases)
    in_target=summary["IN_FAMILY"]["arms"]["target"]
    sh_target=summary["SHIFT"]["arms"]["target"]
    co_target=summary["CORRUPT"]["arms"]["target"]
    sh_base=sh_target["unvalidated"];sh_gated=sh_target["gated"]
    in_base=in_target["unvalidated"];in_gated=in_target["gated"]
    co_gated=co_target["gated"]
    def answered(x):return x["correct"]+x["wrong"]
    def wrong_rate(x):
        return x["wrong"]/answered(x) if answered(x) else 0.0
    gates={
      "shift_baseline_wrong_positive":sh_base["wrong"]>0,
      "shift_wrong_reduction_90pct":sh_base["wrong"]>0 and 10*sh_gated["wrong"]<=sh_base["wrong"],
      "shift_wrong_answered_le1pct":wrong_rate(sh_gated)<=0.01,
      "shift_wrong_total_le1pct":100*sh_gated["wrong"]<=sh_gated["questions"],
      "in_family_coverage_75pct":4*in_gated["correct"]>=3*in_gated["questions"],
      "in_family_zero_wrong":in_gated["wrong"]==0,
      "in_family_baseline_loss_le10pp":10*(in_base["correct"]-in_gated["correct"])<=in_gated["questions"],
      "target_no_worse_shift_wrong_than_random":
          sh_gated["wrong"]<=summary["SHIFT"]["arms"]["random"]["gated"]["wrong"],
      "corrupt_wrong_answered_le1pct":wrong_rate(co_gated)<=0.01,
      "matched_effects":all(q["effects"]==32*32 for s in summary.values() for q in s["arms"].values())
    }
    return {"schema":"yggdrasil.nci-mismatch-a3.result.v1",
      "classification":"CONTRADICTION_AUDIT_SOURCEFREE_DEVELOPMENT_SUPPORTED"
        if all(gates.values()) else "CONTRADICTION_AUDIT_SOURCEFREE_DEVELOPMENT_NO_GO",
      "gates":gates,"scientific_pass":False,"accepted_native":False,
      "source_first_use":False,"original_source_actions":0,
      "simulated_effect_calls":sum(c["simulated_effect_calls"] for c in cases),
      "source_actor_count":len(cases)*2,"case_count":len(cases),
      "cold_models":len(bundle),"summary":summary,"cases":cases,
      "whole_wall_seconds":time.perf_counter()-start}

def stable_view(x):
    if isinstance(x,dict):
        return {k:stable_view(v) for k,v in x.items()
                if k not in ("native_full_fit_seconds","whole_wall_seconds",
                             "environment","stable_sha256")}
    if isinstance(x,list):return [stable_view(a) for a in x]
    return x

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--verify")
    args=p.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    r=run(args.out)
    r["environment"]={"python":platform.python_version(),
                      "platform":platform.platform()}
    r["stable_sha256"]=digest(canonical(stable_view(r)))
    if args.verify:
        require(args.verify==r["stable_sha256"],"PLATFORM_PARITY")
    (args.out/"result.json").write_bytes(canonical(r))
    print("NCI_MISMATCH_A3_STABLE_SHA256="+r["stable_sha256"],flush=True)
    print("NCI_MISMATCH_A3_SCORE="+canonical(
        {"classification":r["classification"],"gates":r["gates"],
         "summary":r["summary"],"cold_models":r["cold_models"]}).decode("ascii"),flush=True)
    if os.getenv("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"],"a") as f:
            f.write("stable="+r["stable_sha256"]+"\n")
