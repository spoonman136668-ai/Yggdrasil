"""NKR-15: replay locked NKR-14 failure under two explicit readouts.

The already-frozen NKR-14 result at its *original SHA* is unchanged. Here a
new isolated source candidate retains observed action-zero parity when its
action-effect grammar is unsupported. Family-agnostic action-1 prediction
abstains on every unobserved effect bit, rather than inventing an operator.

No hidden mechanism, authentic real-world data or original accepted owner
can be accessed by the learner.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from yggdrasil.native_operator_discovery import NativeOperatorDiscovery
from yggdrasil.native_intervention_repair import digest
from yggdrasil.public_causal_cells import PublicCausalCells


def load(name, filename):
    spec=importlib.util.spec_from_file_location(name,filename)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


nkr14=load("nkr15_source_frozen_nkr14",
           Path(__file__).resolve().parents[1]/"NKR-14/experiment.py")
nkr13=load("nkr15_source_frozen_nkr13",
           Path(__file__).resolve().parents[1]/"NKR-13/experiment.py")


def score(pred, truth):
    return int(pred is not None and pred==truth)


def run_frozen():
    start=time.monotonic()
    legacy=PublicCausalCells().snapshot()
    metrics={
        "worlds":12,"cold_queries":192,
        "source_interventions_per_world":16,
        "qualified_new_world_models":0,
        "identified_conjunction_operators":0,
        "baseline_only_models":0,
        "insufficient_evidence_refusals":0,
        "conditional_cold_correct":0,
        "conditional_cold_coverage":0,
        "conditional_cold_confident_wrong":0,
        "conditional_cold_abstentions":0,
        "unrestricted_cold_correct":0,
        "unrestricted_cold_coverage":0,
        "unrestricted_cold_confident_wrong":0,
        "unrestricted_cold_abstentions":0,
        "independent_conservative_correct":0,
        "independent_conservative_confident_wrong":0,
        "old_retention":0,
        "exact_cold_checkpoint":0,
        "single_sensor_noise_false_repairs":0,
        "single_sensor_noise_refusals":0,
    }
    per=[]
    for world in range(12):
        env=nkr14.HiddenWorld(world)
        old=nkr14.warmup(env)
        raw=nkr14.freeze_bundle(
            "nkr15-warm-"+digest(nkr14.canonical(old))[:16],old)
        candidate=NativeOperatorDiscovery.from_warmup(raw,digest(raw))
        old_raw=candidate.checkpoint()
        new=nkr14.source_visible_actions(env)
        new_raw=nkr14.freeze_bundle(
            "nkr15-source-"+digest(nkr14.canonical(new))[:16],new)
        staged,receipt=candidate.stage_public_interventions(
            new_raw,digest(new_raw))
        if candidate.checkpoint()!=old_raw:
            raise AssertionError("NKR15_ORIGINAL_MEMORY_MUTATED")
        if staged.operator_discovered:
            metrics["qualified_new_world_models"]+=1
            if staged.operator_supported:
                metrics["identified_conjunction_operators"]+=1
            else:
                metrics["baseline_only_models"]+=1
            cold=NativeOperatorDiscovery(
                staged.checkpoint(),staged.checkpoint_sha256)
            if cold.checkpoint()!=staged.checkpoint():
                raise AssertionError("NKR15_COLD_SOURCE_RESTORE_DRIFT")
            metrics["exact_cold_checkpoint"]+=1
        else:
            metrics["insufficient_evidence_refusals"]+=1
            cold=staged
        prior_benchmark=nkr14.UnrestrictedBooleanEffectControl(new)
        before={
            k:metrics[k] for k in (
                "conditional_cold_correct","conditional_cold_coverage",
                "conditional_cold_confident_wrong","unrestricted_cold_correct",
                "unrestricted_cold_coverage","unrestricted_cold_confident_wrong")
        }
        for context in nkr14.COLD:
            for action in (0,1):
                truth=env.intervene(context,action)
                # Preserve NKR13's *conditional* operator-grammar readout
                # only if source evidence created a new candidate.
                cond=cold.predict(context,action)["public_outcome"] if (
                    cold.operator_discovered) else None
                safe=cold.predict_unrestricted(context,action)
                if (safe["native_accepted"] or safe["can_write_causal_owner"]
                        or safe["can_write_historical_facts"]
                        or safe["scientific_pass"]):
                    raise AssertionError("NKR15_EPISTEMIC_SAFETY_BREACH")
                protected=safe["public_outcome"]
                independent=prior_benchmark.predict(context,action)
                metrics["conditional_cold_correct"]+=score(cond,truth)
                metrics["conditional_cold_coverage"]+=int(cond is not None)
                metrics["conditional_cold_confident_wrong"]+=int(
                    cond is not None and cond!=truth)
                metrics["conditional_cold_abstentions"]+=int(cond is None)
                metrics["unrestricted_cold_correct"]+=score(protected,truth)
                metrics["unrestricted_cold_coverage"]+=int(protected is not None)
                metrics["unrestricted_cold_confident_wrong"]+=int(
                    protected is not None and protected!=truth)
                metrics["unrestricted_cold_abstentions"]+=int(protected is None)
                metrics["independent_conservative_correct"]+=score(
                    independent,truth)
                metrics["independent_conservative_confident_wrong"]+=int(
                    independent is not None and independent!=truth)
        for context in range(16):
            for action in (0,1):
                value=env.intervene(context,action,old=True)
                metrics["old_retention"]+=score(cold.prior(context,action),value)
        per.append({
            "world":world,"source_classification":receipt["classification"],
            "baseline_only":staged.operator_discovered and
                            not staged.operator_supported,
            "conjunction_supported":staged.operator_supported,
            "conditional_correct":metrics["conditional_cold_correct"]-
                                  before["conditional_cold_correct"],
            "conditional_coverage":metrics["conditional_cold_coverage"]-
                                   before["conditional_cold_coverage"],
            "conditional_wrong":metrics["conditional_cold_confident_wrong"]-
                                before["conditional_cold_confident_wrong"],
            "unrestricted_correct":metrics["unrestricted_cold_correct"]-
                                   before["unrestricted_cold_correct"],
            "unrestricted_coverage":metrics["unrestricted_cold_coverage"]-
                                    before["unrestricted_cold_coverage"],
            "unrestricted_wrong":metrics["unrestricted_cold_confident_wrong"]-
                                 before["unrestricted_cold_confident_wrong"],
        })
    # One source-visible noisy anomaly in each of four *unchanged* worlds
    # must never be elevated into a permanent baseline or operator repair.
    for world in range(4):
        env=nkr14.HiddenWorld(world)
        warm=nkr14.warmup(env)
        raw=nkr14.freeze_bundle("nkr15-noise-warm-"+str(world),warm)
        prior=NativeOperatorDiscovery.from_warmup(raw,digest(raw))
        original=prior.checkpoint()
        noise=[(f"sensor-nkr15-{i:02d}",x,a,
                env.intervene(x,a,old=True)^int(i==0))
               for i,(x,a) in enumerate(nkr14.ACTION_SEQUENCE)]
        if sum(prior.prior(x,a)!=outcome
               for _,x,a,outcome in noise)!=1:
            raise AssertionError("NKR15_NOISE_CONTROL_CHANGED")
        source=nkr14.freeze_bundle(
            "nkr15-noise-public-"+str(world),noise)
        staged,receipt=prior.stage_public_interventions(
            source,digest(source))
        if staged.operator_discovered:
            metrics["single_sensor_noise_false_repairs"]+=1
        if receipt["classification"]=="INSUFFICIENT_CHANGE_EVIDENCE":
            metrics["single_sensor_noise_refusals"]+=1
        if prior.checkpoint()!=original:
            raise AssertionError("NKR15_ONE_BIT_ERROR_DESTROYED_PRIOR")
    old_conj=nkr13.run_frozen()
    old_totals=old_conj["totals"]
    if (old_totals["native_correct"]!=129
            or old_totals["native_confident_wrong"]!=0):
        raise AssertionError("NKR15_REGRESSED_EARLIER_CONJUNCTION_SCIENCE")
    if PublicCausalCells().snapshot()!=legacy:
        raise AssertionError("NKR15_ACCEPTED_NATIVE_STATE_CHANGED")
    success=(
        metrics["qualified_new_world_models"]==11
        and metrics["identified_conjunction_operators"]==2
        and metrics["baseline_only_models"]==9
        and metrics["insufficient_evidence_refusals"]==1
        and metrics["conditional_cold_correct"]==98
        and metrics["conditional_cold_coverage"]==104
        and metrics["conditional_cold_confident_wrong"]==6
        and metrics["unrestricted_cold_correct"]==88
        and metrics["unrestricted_cold_coverage"]==88
        and metrics["unrestricted_cold_confident_wrong"]==0
        and metrics["independent_conservative_correct"]==96
        and metrics["independent_conservative_confident_wrong"]==0
        and metrics["old_retention"]==384
        and metrics["exact_cold_checkpoint"]==11
        and metrics["single_sensor_noise_false_repairs"]==0
        and metrics["single_sensor_noise_refusals"]==4)
    return {
        "schema":"yggdrasil.nkr15.factorized-causal-uncertainty-dev.v1",
        "classification":"SOURCE_BOUND_SAFE_PARTIAL_REPAIR_DEV_PASS"
        if success else "SOURCE_BOUND_SAFE_PARTIAL_REPAIR_DEV_NO_GO",
        "nkr14_original_frozen_result_preserved_at_original_sha":True,
        "changed_candidate_branch_new_protocol":True,
        "source_mode":"engineering_fixture_only",
        "unrestricted_mode_assumes_action_zero_parity":True,
        "frozen_dev_threshold_met":success,
        "old_conjunction_conditional_correct":old_totals["native_correct"],
        "old_conjunction_conditional_confident_wrong":old_totals["native_confident_wrong"],
        "independent_strong_control_superiority":False,
        "scientific_pass":False,
        "native_accepted":False,
        "authentic_external_world_source":False,
        "per_world":per,"totals":metrics,
        "wall_seconds":time.monotonic()-start,
    }


if __name__=="__main__":
    print("NKR15_FROZEN_FACTOR_READOUT="+json.dumps(
        run_frozen(),sort_keys=True,separators=(",",":")),flush=True)
