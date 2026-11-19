"""CKAD25-AE: native source-grounded K4 sheaf defect *witnessed repair*.

The 3-cycle SCDR predecessor showed a genuine H1 but no edge localization.
Here K4 H1 has dimension3 and singles have unique syndromes. However a
syndrome alone is not permission to overwrite actual source evidence: paid
vertex-action anchor observations must verify the correction. Raw source
edge values remain durable. Exact conventional cohomology is required to
TIE native; a full 16-vertex/64-mask generative Bayes is a stronger control.
"""
from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
import random
import time
from fractions import Fraction
from pathlib import Path

from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner

HERE=Path(__file__).resolve().parent
AB=HERE.parent/"CKAD25-AB"/"run.py"
AB_SHA256="00d17c1f0b5b74084484d359d1abea41f2ecd4fc1f7ed1b9a65e4919556dbeca"
PRIMARY=(81503,81517,81533,81551,81569,81587,81607,81623,
         81643,81659,81677,81697,81713,81731,81749,81769,
         81787,81803,81817,81839,81853,81869,81883,81901,
         81919,81937,81953,81971,81989,82003,82021,82037)
DEV=(82999,)
STRATA=("CLEAN","SINGLE","DOUBLE","EDGE5","DOUBLE_ANCHOR5")
ARMS=("native_k4_scdr","independent_exact_k4_cohomology_repair",
      "fixed_edge_validation","seeded_random_edge_validation",
      "full_16vertex_64mask_mixture_bayes_same_anchors")
EDGES=((0,1),(0,2),(0,3),(1,2),(1,3),(2,3))
CYCLES=((0,1,3),(0,2,4),(1,2,5))
H1_SIGNATURE={tuple(int(k in cycle) for cycle in CYCLES):k for k in range(6)}


def must(ok,why):
    if not ok:raise ValueError("CKAD25AE_"+why)


def ab_parent():
    must(digest(AB.read_bytes())==AB_SHA256,"PARENT_SOURCE_UNVERIFIED")
    spec=importlib.util.spec_from_file_location("scdr_k4_frozen_native_parent",AB)
    must(spec is not None and spec.loader is not None,"PARENT_MODULE")
    x=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(x)
    must(x.SOURCE_SHA=="c52681bf26f08817b3747647472913fa792da2de33f74b8fa7c0f2b0e78c119f",
         "ORIGINAL_NATIVE_SOURCE_DRIFT")
    return x


def rng(tag,*args):
    key=digest(canonical(["CKAD25-AE-SCDR-K4",tag,*args]))
    return random.Random(int(key[:16],16))


def edge_truth(vertices):
    return [vertices[i]^vertices[j] for i,j in EDGES]


def edge_evidence(y):
    must(len(y)==6 and all(x in (0,1) for x in y),"EDGE_DOMAIN")
    return [[i,1,y[i]] for i in range(6)]


def anchor_evidence(vertices,indices,noisy):
    must(len(indices)==2 and len(set(indices))==2,"ANCHOR_DOMAIN")
    return [[k,0,vertices[k]^noisy[k]] for k in indices]


def witness(m,slot,rows,seed,episode,arm):
    name=digest(canonical(["CKAD25-AE",seed,episode,arm,slot]))
    return m.observe(slot,rows,digest(canonical(rows)),source_ref=name)


def independent_h1_syndrome(measured):
    # Explicit constant-F2 cellular coboundary constraints on K4:
    # d0(x)_ij=x_i+x_j. Every fundamental triangle evaluates 0 for d0.
    return tuple(sum(measured[i] for i in cycle)%2 for cycle in CYCLES)


def conventional_repair(measured,anchors,edge_index):
    """Exact independent minimal coboundary repair with paid validation."""
    sigma=independent_h1_syndrome(measured)
    candidates=[k for k in range(6)
                if tuple(int(k in cycle) for cycle in CYCLES)==sigma]
    if sigma==(0,0,0):
        return measured[:],"NO_DEFECT",False,None
    if len(candidates)!=1:
        return measured[:],"NONLOCALIZABLE",False,None
    suspect=candidates[0]
    if edge_index != suspect:
        return measured[:],"UNVALIDATED_DEFECT",False,suspect
    a,b=EDGES[edge_index]
    if set(anchors)!={a,b}:
        return measured[:],"BAD_ANCHOR_SCOPE",False,suspect
    true_pair=anchors[a]^anchors[b]
    if true_pair==measured[suspect]:
        return measured[:],"REJECTED_BY_ANCHORS",False,suspect
    corrected=measured[:]
    corrected[suspect]=true_pair
    must(independent_h1_syndrome(corrected)==(0,0,0),
         "INDEPENDENT_GLOBAL_SECTION_REPAIR_NOT_VALID")
    return corrected,"SOURCE_WITNESSED_CORRECTION",True,suspect


def exact_mixture_posterior(observed,anchor_obs):
    """Strong fully enumerated conventional Bayesian mixture without mode labels.

    5 equiprobable prospective regimes: clean, one corrupted edge,
    two corrupted edges, independent 5%-noisy edges, and two corrupted
    edges with 5%-noisy independently witnessed vertex anchor sensors.
    Uniform prior over 16 latent vertex assignments. Hidden mode and
    vertex bits are never supplied; this computes their posterior.
    """
    sums=[0.]*6
    denom=0.
    for bits in itertools.product((0,1),repeat=4):
        true=edge_truth(bits)
        mask=sum((observed[i]!=true[i])<<i for i in range(6))
        n=mask.bit_count()
        # In exact-channel modes, witnessed anchors must match true values.
        exact=all(bits[k]==v for k,v in anchor_obs.items())
        mass=0.
        if exact:
            mass+=(.2 if n==0 else 0.)
            mass+=(.2/6 if n==1 else 0.)
            mass+=(.2/15 if n==2 else 0.)
            mass+=.2*(.05**n)*(.95**(6-n))
        if n==2:
            anchor_likelihood=1.
            for k,v in anchor_obs.items():
                anchor_likelihood*=.95 if v==bits[k] else .05
            mass+=(.2/15)*anchor_likelihood
        denom+=mass
        for i,value in enumerate(true):
            sums[i]+=mass*value
    must(denom>0.,"FULL_EXACT_BAYES_ZERO_EVIDENCE")
    return [x/denom for x in sums]


def metrics(probs,truth):
    must(len(probs)==len(truth)==6,"SIX_TRUE_HELD_EDGES")
    f=[float(x) for x in probs]
    return {"brier":round(sum((p-y)**2 for p,y in zip(f,truth))/6,9),
            "confident_wrong":sum(p in (0.,1.) and int(p)!=y for p,y in zip(f,truth)),
            "confident":sum(p in (0.,1.) for p in f),
            "predictions":[round(p,12) for p in f]}


def run(seeds=PRIMARY):
    parent=ab_parent()
    original_raw=parent.CHECKPOINT.read_bytes()
    must(digest(original_raw)==parent.SOURCE_SHA,"ORIGINAL_NATIVE_BYTES")
    old=NativeCumulativeLearner.restore(original_raw,parent.SOURCE_SHA)
    per_seed={}
    results=[]
    for seed in seeds:
        source,_=parent.roster(seed)
        laws=parent.generator(seed,source)
        native=NativeCumulativeLearner.restore(original_raw,parent.SOURCE_SHA)
        for i,name in enumerate(("A","B","C"),1):
            rows=parent.public_records(laws[name],source)
            native,slot,status=native.incorporate_causal_world(
                rows,digest(canonical(rows)),source_ref=parent.ref(seed,"fit",i))
            must((slot,status)==(i,"ACQUIRED"),"ACTUAL_NATIVE_SOURCE_LEARNING")
            checkpoint=native.checkpoint()
            native=NativeCumulativeLearner.restore(checkpoint,digest(checkpoint))
        initial=native.checkpoint()
        fitted=[native._compiled[k].checkpoint() for k in (1,2,3)]
        per_seed[str(seed)]={
            "new_A_B_C_source_fit_36_do_sha256":digest(canonical(
                [[name,parent.public_records(laws[name],source)] for name in ("A","B","C")])),
            "native_compiled_source_shas":[digest(x) for x in fitted],
            "native_initial_cold_sha256":digest(initial),
            "source_masks_sha256":digest(canonical(source)),
            "evaluator_only_source_weights":laws
        }
        for episode in STRATA:
            r=rng("evaluator-world",seed,episode)
            vertices=[r.randrange(2) for _ in range(4)]
            true=edge_truth(vertices)
            if episode=="CLEAN":
                faulty=[]
            elif episode=="SINGLE":
                faulty=r.sample(range(6),1)
            elif episode in ("DOUBLE","DOUBLE_ANCHOR5"):
                faulty=r.sample(range(6),2)
            else:
                faulty=[k for k in range(6) if r.random()<.05]
            # Calibrator/vertex sensors are exact except for the separately
            # frozen negative Double+5%-anchor condition. No model gets mode.
            vertex_noise=[int(r.random()<.05) if episode=="DOUBLE_ANCHOR5"
                          else 0 for _ in range(4)]
            observed=[t^(i in faulty) for i,t in enumerate(true)]
            edge_rows=edge_evidence(observed)
            seed_native=NativeCumulativeLearner.restore(initial,digest(initial))
            edge_native=witness(seed_native,12,edge_rows,seed,episode,"shared")
            candidate=edge_native.scdr_k4_defect_repair()
            sigma=independent_h1_syndrome(observed)
            must(tuple(candidate["syndrome"])==sigma
                 and candidate["h1_dimension"]==3 and candidate["d0_rank"]==3,
                 "TRUE_K4_SOURCE_SHEAF_MISMATCH")
            sig_index=H1_SIGNATURE.get(sigma)
            must(candidate["suspect_edge"]==
                 (list(EDGES[sig_index]) if sig_index is not None else None),
                 "SOURCE_GROUNDED_OBSTRUCTION_DIFFERENCE")
            outcome={}
            for arm in ARMS:
                source_model=NativeCumulativeLearner.restore(initial,digest(initial))
                observed_model=witness(source_model,12,edge_rows,seed,episode,arm)
                if arm in ("native_k4_scdr",
                           "independent_exact_k4_cohomology_repair",
                           "full_16vertex_64mask_mixture_bayes_same_anchors"):
                    selected=sig_index if sig_index is not None else 0
                elif arm=="fixed_edge_validation":
                    selected=0
                else:
                    selected=rng("independent-random-edge",seed,episode).randrange(6)
                u,v=EDGES[selected]
                anchors=anchor_evidence(vertices,(u,v),vertex_noise)
                anchored_model=witness(observed_model,13,anchors,seed,episode,arm)
                anchor_seen={c:y for c,a,y in anchors}
                old_relation=(anchored_model._source._seen[0]==old._source._seen[0]
                              and anchored_model._properties.checkpoint()==old._properties.checkpoint()
                              and anchored_model._events[:len(old._events)]==old._events
                              and [anchored_model._compiled[k].checkpoint()
                                   for k in (1,2,3)]==fitted)
                must(old_relation,"OLD_SOURCE_OR_LEARNED_COMMITTEE_CORRUPTED")
                if arm=="native_k4_scdr":
                    got=anchored_model.scdr_k4_defect_repair()
                    predictions=got["repaired_edge_bits"]
                    status=got["status"]
                    repaired=got["repair_certified"]
                elif arm=="independent_exact_k4_cohomology_repair":
                    predictions,status,repaired,_=conventional_repair(
                        observed,anchor_seen,selected)
                elif arm in ("fixed_edge_validation","seeded_random_edge_validation"):
                    predictions=observed[:]
                    if anchors[0][2]^anchors[1][2]!=observed[selected]:
                        predictions[selected]=anchors[0][2]^anchors[1][2]
                        repaired=True
                        status="DIRECT_ANCHOR_CORRECTION"
                    else:
                        repaired=False
                        status="DIRECT_ANCHOR_CONSISTENT"
                else:
                    predictions=exact_mixture_posterior(observed,anchor_seen)
                    repaired=False
                    status="EXACT_GENERATIVE_BAYES"
                before_cold=anchored_model.checkpoint()
                cold=NativeCumulativeLearner.restore(before_cold,digest(before_cold))
                must(cold.checkpoint()==before_cold
                     and cold._source._seen[12].bit_count()==6
                     and cold._source._seen[13].bit_count()==2
                     and [cold._compiled[k].checkpoint() for k in (1,2,3)]==fitted,
                     "SOURCE_ANCHOR_COLD_RESTORATION")
                if arm=="native_k4_scdr":
                    must(cold.scdr_k4_defect_repair()==got,
                         "SOURCE_REPAIR_NOT_COLD_DETERMINISTIC")
                errbefore=sum(x!=y for x,y in zip(observed,true))
                errafter=sum(round(float(x))!=y for x,y in zip(predictions,true))
                vals=metrics(predictions,true)
                outcome[arm]={
                    "selected_edge":selected,
                    "two_vertex_anchor_source_sha256":digest(canonical(anchors)),
                    "status":status,
                    "repair_certified":repaired,
                    "source_retained":old_relation,
                    "cold_sha256":digest(before_cold),
                    "actual_edge_actions":6,"actual_vertex_anchor_actions":2,
                    "true_wrong_edges_before":errbefore,
                    "remaining_wrong_edges":errafter if arm!="full_16vertex_64mask_mixture_bayes_same_anchors" else None,
                    "false_repair":bool(repaired and
                        any(predictions[k]!=true[k] and predictions[k]!=observed[k]
                            for k in range(6))),
                    "metric":vals
                }
            must(outcome["native_k4_scdr"]["selected_edge"]==
                 outcome["independent_exact_k4_cohomology_repair"]["selected_edge"]
                 and outcome["native_k4_scdr"]["status"]==
                     outcome["independent_exact_k4_cohomology_repair"]["status"]
                 and outcome["native_k4_scdr"]["metric"]==
                     outcome["independent_exact_k4_cohomology_repair"]["metric"],
                 "FULL_INDEPENDENT_K4_COHOMOLOGY_PARITY")
            results.append({
                "seed":seed,"stratum_evaluator_only":episode,
                "evaluator_only_latent_vertex_bits":vertices,
                "evaluator_only_wrong_edge_ids":sorted(faulty),
                "evaluator_only_anchor_sensor_noise":vertex_noise,
                "true_edge_sha256":digest(canonical(true)),
                "six_true_edge_witness_sha256":digest(canonical(edge_rows)),
                "observed_edge_values":observed,
                "true_cycle_H1_syndrome":list(sigma),
                "native_pre_anchor_status":candidate["status"],
                "arms":outcome
            })
    must(len(results)==len(seeds)*5,"ALL_FROZEN_NEW_WORLD_STRATA")
    stats={}
    for arm in ARMS:
        rows=[w["arms"][arm] for w in results]
        stats[arm]={
            "mean_brier":round(sum(r["metric"]["brier"] for r in rows)/len(rows),9),
            "false_repairs_total":sum(r["false_repair"] for r in rows),
            "confident_wrong_total":sum(r["metric"]["confident_wrong"] for r in rows),
            "genuine_do_actions":sum(r["actual_edge_actions"]+
                                     r["actual_vertex_anchor_actions"] for r in rows)}
        for episode in STRATA:
            sub=[w["arms"][arm] for w in results
                 if w["stratum_evaluator_only"]==episode]
            stats[arm][episode]={
                "mean_brier":round(sum(r["metric"]["brier"] for r in sub)/len(sub),9),
                "confirmed":sum(r["repair_certified"] for r in sub),
                "false_repairs":sum(r["false_repair"] for r in sub),
                "confident_wrong":sum(r["metric"]["confident_wrong"] for r in sub)}
    no_repair=round(sum(metrics(w["observed_edge_values"],
                                  [w["evaluator_only_latent_vertex_bits"][u] ^
                                   w["evaluator_only_latent_vertex_bits"][v]
                                   for u,v in EDGES])["brier"]
                        for w in results)/len(results),9)
    cand=stats["native_k4_scdr"]
    noised=stats["native_k4_scdr"]["DOUBLE_ANCHOR5"]
    gates={
        "native_source_cold_and_old_causal_knowledge_retained":
            all(r["source_retained"] for w in results for r in w["arms"].values()),
        "real_charged_source_and_anchor_actions":
            len(seeds)==32 and
            sum(v["genuine_do_actions"] for v in stats.values())==6400,
        "genuine_k4_h1_rank_and_unique_single_fault_localization":
            len(H1_SIGNATURE)==6 and
            all(w["arms"]["native_k4_scdr"]["remaining_wrong_edges"]==0
                for w in results if w["stratum_evaluator_only"]=="SINGLE"),
        "no_overwriting_or_false_correction_on_clean_and_exact_double":
            all(not w["arms"]["native_k4_scdr"]["repair_certified"]
                for w in results if w["stratum_evaluator_only"] in ("CLEAN","DOUBLE")),
        "preregistered_brier_gain_vs_no_repair":
            cand["mean_brier"]<=no_repair-.03+1e-12,
        "noisy_anchor_false_repair_at_most_5_percent":
            noised["false_repairs"]<=int(len(seeds)*.05),
        "full_independent_conventional_k4_repair_parity":
            all(w["arms"]["native_k4_scdr"]["metric"]==
                w["arms"]["independent_exact_k4_cohomology_repair"]["metric"] and
                w["arms"]["native_k4_scdr"]["status"]==
                w["arms"]["independent_exact_k4_cohomology_repair"]["status"]
                for w in results),
        "within_0_05_of_strong_full_mixture_bayes":
            cand["mean_brier"]<=stats["full_16vertex_64mask_mixture_bayes_same_anchors"]["mean_brier"]+.05+1e-12
    }
    return {
        "schema":"yggdrasil.ckad25ae.source-backed-K4-H1-repair.v1",
        "executed_source_sha256":digest(Path(__file__).read_bytes()),
        "parent_AB_source_sha256":digest(AB.read_bytes()),
        "original_native_checkpoint_sha256":digest(original_raw),
        "scored_original_primary":tuple(seeds)==PRIMARY,
        "fresh_seeds":list(seeds),
        "independent_source_actions":len(seeds)*(36+5*5*8),
        "policy_world_episodes":len(results)*5,
        "distinct_true_edge_labels":len(results)*6,
        "conditional_held_edge_predictions":len(results)*5*6,
        "no_latent_vertex_labels_passed_to_native":True,
        "original_observed_negative_edges_immutable":True,
        "inferred_native_sheaf_restriction_maps":False,
        "source_free_synthetic_only":True,
        "owner_science_first_use":False,"accepted_main_changed":False,
        "forge_dispatch":False,"merge":False,"deployment":False,
        "scientific_pass":False,"algorithmic_superiority":False,
        "universal_safety":False,
        "per_seed_provenance":per_seed,
        "world_cases":results,
        "no_repair_brier":no_repair,
        "arm_statistics":stats,
        "frozen_gates":gates,
        "development_disposition":"BOUNDED_NATIVE_SCDR_SIGNAL" if all(gates.values())
                    else "DEVELOPMENT_MIXED_OR_NO_GO"
    }


def main():
    a=argparse.ArgumentParser()
    a.add_argument("--preflight",action="store_true")
    a.add_argument("--output",type=Path)
    args=a.parse_args()
    if args.preflight:
        must(args.output is None,"DEV_CANNOT_WRITE_PRIMARY")
        r=run(DEV)
        must(not r["scored_original_primary"]
             and r["independent_source_actions"]==236
             and r["policy_world_episodes"]==25
             and r["conditional_held_edge_predictions"]==150,
             "DISJOINT_DEV_WIRING")
        print("CKAD25AE_DISJOINT_NATIVE_SOURCE_PREFLIGHT_PASS")
        return
    must(args.output is not None,"EXPLICIT_FROZEN_OUTPUT_REQUIRED")
    begin=time.monotonic()
    r=run()
    raw=canonical(r)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_bytes(raw)
    print("CKAD25AE_FROZEN_DISPOSITION="+r["development_disposition"])
    print("CKAD25AE_NO_REPAIR_BRIER="+str(r["no_repair_brier"]))
    print("CKAD25AE_ARMS="+json.dumps(r["arm_statistics"],sort_keys=True))
    print("CKAD25AE_GATES="+json.dumps(r["frozen_gates"],sort_keys=True))
    print("CKAD25AE_RESULT_SHA256="+digest(raw))
    print("CKAD25AE_SCORER_WALL_SECONDS="+str(round(time.monotonic()-begin,3)))


if __name__=="__main__":main()
