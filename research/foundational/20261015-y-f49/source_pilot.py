"""Y-F49: conditional causal-identifiability of 12 public intervention pairs.

Fresh disjoint TRAIN cohort; coupled public intervention structure versus
decoupled causal-null condition. Truth and source mode are evaluation-only.
Not a primary original, accepted science, or live controller instruction.
"""
import importlib.util
import json
import sys
from pathlib import Path

P = Path(__file__).resolve().parent.parent / "20261015-y-f48" / "source_pilot.py"
spec = importlib.util.spec_from_file_location("y_f49_f48_controls", P)
base = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = base
spec.loader.exec_module(base)
FIT=range(441000,441008)
DIAG=range(441100,441108)
ORIGINAL=range(442000,442016)
OLD_ORIGINALS=(range(382000,382016),range(402000,402016),range(422000,422016))
FAMILIES=(660,661,662,663)
ORIGINAL_FAMILIES=(664,665,666,667)

# Move all F45-F48 source/corpus pointers to a new disjoint FIT/diagnostic
# registry. Predecessor source algorithms and previously learned controls
# remain the same. No prior diagnostic is reused as the new fit cohort.
for module in (base,base.parent,base.parent.prior):
    module.FIT=FIT
    module.DIAGNOSTIC=DIAG
    module.FAMILIES=FAMILIES
    module.RESERVED=ORIGINAL
    module.RESERVED_FAMILIES=ORIGINAL_FAMILIES
base.OLD_RESERVED=range(422000,422016)
base.parent.prior.task=lambda bits,f:base.parent.old_task(bits,480+(f-660))
base.parent.prior.task_probability=lambda probs,f:base.parent.old_probability(probs,480+(f-660))

PAIRED="learned_intervention_invariant"
SHUFFLED="count_matched_shuffled_intervention_pairs"
UNPAIRED="learned_unpaired_ablation"
FAIR=("fitted_Gaussian_latent","empirical_conditional_Brier","Gaussian_kernel",
      "public_global_static","source_variance",UNPAIRED,SHUFFLED)

def run():
    assert not (set(FIT)&set(DIAG) or set(DIAG)&set(ORIGINAL)
                or any(set(DIAG)&set(r) for r in OLD_ORIGINALS)
                or set(FAMILIES)&set(ORIGINAL_FAMILIES))
    # Preserves 12 paired public readings and two bought target channels
    # per role; uses only new diagnostic seeds for unseen mechanism shifts.
    report=base.parent.run()
    rows=report["rows"]
    assert len(rows)==128
    assert all(r["seed"] in DIAG and r["family"] in FAMILIES
               and r["public_pairs"]==12 and r["public_flat_anchors"]==24
               for r in rows)
    assert {r["condition"] for r in rows}=={"coupled","decoupled"}
    assert {r["mechanism"] for r in rows}==set(base.parent.prior.HELDOUT_MECHANISMS)
    arms=report["scores"]
    def count(part,arm):
        return sum(r["predictions"][arm]==r["truth"] for r in part)
    coupled=[r for r in rows if r["condition"]=="coupled"]
    decoupled=[r for r in rows if r["condition"]=="decoupled"]
    assert len(coupled)==len(decoupled)==64
    couple_correct={a:count(coupled,a) for a in arms}
    null_correct={a:count(decoupled,a) for a in arms}
    couple_shuffled=(couple_correct[PAIRED]-couple_correct[SHUFFLED])/len(coupled)
    null_shuffled=(null_correct[PAIRED]-null_correct[SHUFFLED])/len(decoupled)
    couple_unpaired=(couple_correct[PAIRED]-couple_correct[UNPAIRED])/len(coupled)
    strongest_coupled=max(couple_correct[a] for a in FAIR)
    coupled_gain=(couple_correct[PAIRED]-strongest_coupled)/len(coupled)
    mech={m:{a:count([r for r in rows if r["mechanism"]==m],a)
             for a in arms} for m in base.parent.prior.HELDOUT_MECHANISMS}
    no_mechanism_regression=all(mech[m][PAIRED]>=max(mech[m][a] for a in FAIR)
                                for m in mech)
    passed=(coupled_gain>=.02 and couple_shuffled>0 and couple_unpaired>0
            and abs(null_shuffled)<=.01
            and couple_shuffled-null_shuffled>=.02
            and no_mechanism_regression)
    report.update(
        schema="yggdrasil.f49.conditional-pair-causal-null.trainonly.v1",
        stage="NEW_CAUSAL_NULL_TRAIN_DIAGNOSTIC_NO_ORIGINAL",
        diagnostic_seeds=[DIAG.start,DIAG.stop],fit_seeds=[FIT.start,FIT.stop],
        families=list(FAMILIES),proposed_originals_not_consumed=[ORIGINAL.start,ORIGINAL.stop],
        original_families_not_consumed=list(ORIGINAL_FAMILIES),
        prior_originals_not_consumed=[[r.start,r.stop] for r in OLD_ORIGINALS],
        condition_correct={"coupled":couple_correct,"decoupled":null_correct},
        heldout_mechanism_correct=mech,
        coupled_gain_over_strongest_fair=coupled_gain,
        coupled_paired_vs_shuffled_gain=couple_shuffled,
        coupled_paired_vs_unpaired_gain=couple_unpaired,
        decoupled_null_paired_vs_shuffled_gain=null_shuffled,
        coupled_minus_null_ablation_difference=couple_shuffled-null_shuffled,
        heldout_mechanism_nondegradation=no_mechanism_regression,
        frozen_criterion_met=passed,
        verdict="TRAIN_ONLY_SUPPORTED_NOT_F3" if passed else "TRAIN_ONLY_NEGATIVE",
        evaluator_truth_never_selector_input=True, primary_original_not_executed=True,
        independent_F3_custody=False,native_576_byte_resident_qualified=False,
        accepted_ref_mutation=False,paid_api_calls=0)
    return report

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
