"""Independent read-only reconstruction of frozen original CKAD25-AE result.

No import or execution of native cumulative learner or its original scorer.
Verifies actual witnessed edge/vertex source hashes, source/held separation,
the constant-F2 K4 rank and its independent cycle signatures, every repair
and Bayesian score, and the exact two failed preregistered gates.
"""
import argparse
import hashlib
import itertools
import json
import random
from pathlib import Path

SEEDS=(81503,81517,81533,81551,81569,81587,81607,81623,
       81643,81659,81677,81697,81713,81731,81749,81769,
       81787,81803,81817,81839,81853,81869,81883,81901,
       81919,81937,81953,81971,81989,82003,82021,82037)
STRATA=("CLEAN","SINGLE","DOUBLE","EDGE5","DOUBLE_ANCHOR5")
ARMS=("native_k4_scdr","independent_exact_k4_cohomology_repair",
      "fixed_edge_validation","seeded_random_edge_validation",
      "full_16vertex_64mask_mixture_bayes_same_anchors")
EDGES=((0,1),(0,2),(0,3),(1,2),(1,3),(2,3))
CYCLES=((0,1,3),(0,2,4),(1,2,5))
SINGLE={tuple(int(j in cycle) for cycle in CYCLES):j for j in range(6)}


def check(ok,claim):
    if not ok:raise ValueError("CKAD25AE_INDEPENDENT_"+claim)


def encode(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True,
                      allow_nan=False).encode("ascii")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def new_rng(tag,*values):
    return random.Random(int(sha(encode(["CKAD25-AE-SCDR-K4",tag,*values]))[:16],16))


def prior_rng(tag,*values):
    return random.Random(int(sha(encode(["CKAD25-AB",tag,*values]))[:16],16))


def graph(values):
    return [values[u]^values[v] for u,v in EDGES]


def cycle(bits):
    return tuple(sum(bits[i] for i in row)%2 for row in CYCLES)


def score(prob,correct):
    p=[float(v) for v in prob]
    return {"brier":round(sum((v-y)**2 for v,y in zip(p,correct))/6,9),
            "confident_wrong":sum(v in (0.,1.) and int(v)!=y for v,y in zip(p,correct)),
            "confident":sum(v in (0.,1.) for v in p),
            "predictions":[round(v,12) for v in p]}


def conventional_bayes(observed,anchor):
    masses=[0.]*6
    total=0.
    for verts in itertools.product((0,1),repeat=4):
        true=graph(verts)
        errors=sum((int(a!=b)<<i) for i,(a,b) in enumerate(zip(observed,true)))
        n=errors.bit_count()
        exact=all(verts[v]==y for v,y in anchor.items())
        p=0.
        if exact:
            p+=(0.2 if n==0 else 0.)
            p+=(0.2/6 if n==1 else 0.)
            p+=(0.2/15 if n==2 else 0.)
            p+=0.2*(0.05**n)*(0.95**(6-n))
        if n==2:
            witness=1.
            for vertex,y in anchor.items():
                witness*=0.95 if verts[vertex]==y else 0.05
            p+=(0.2/15)*witness
        total+=p
        for j,b in enumerate(true): masses[j]+=p*b
    check(total>0,"EXACT_BAYES_DENOM")
    return [x/total for x in masses]


def independent_conventional(measured,anchors,edge):
    sigma=cycle(measured)
    matches=[i for i in range(6)
             if tuple(int(i in row) for row in CYCLES)==sigma]
    if sigma==(0,0,0):return measured[:],"NO_DEFECT",False
    if len(matches)!=1:return measured[:],"NONLOCALIZABLE",False
    index=matches[0]
    if edge!=index:return measured[:],"UNVALIDATED_DEFECT",False
    u,v=EDGES[index]
    check(set(anchors)=={u,v},"CONVENTIONAL_ANCHOR_SCOPE")
    truth=anchors[u]^anchors[v]
    if truth==measured[index]:
        return measured[:],"REJECTED_BY_ANCHORS",False
    corrected=measured[:]
    corrected[index]=truth
    check(cycle(corrected)==(0,0,0),"BAD_REPAIRED_GLOBAL_SECTION")
    return corrected,"SOURCE_WITNESSED_CORRECTION",True


def reconstruct(raw,source_path,parent_path):
    d=json.loads(raw)
    check(encode(d)==raw,"ORIGINAL_CANONICAL_BYTES")
    check(d["schema"]=="yggdrasil.ckad25ae.source-backed-K4-H1-repair.v1",
          "SCHEMA")
    check(d["fresh_seeds"]==list(SEEDS)
          and d["scored_original_primary"] is True,"ORIGINAL_SEEDS")
    check(d["executed_source_sha256"]==sha(source_path.read_bytes())
          and d["parent_AB_source_sha256"]==sha(parent_path.read_bytes())
          and d["parent_AB_source_sha256"]=="00d17c1f0b5b74084484d359d1abea41f2ecd4fc1f7ed1b9a65e4919556dbeca"
          and d["original_native_checkpoint_sha256"]==
              "c52681bf26f08817b3747647472913fa792da2de33f74b8fa7c0f2b0e78c119f",
          "ORIGINAL_SOURCE_PIN")
    check(d["independent_source_actions"]==7552
          and d["policy_world_episodes"]==800
          and d["distinct_true_edge_labels"]==960
          and d["conditional_held_edge_predictions"]==4800,
          "ACTION_ACCOUNTING")
    check(d["no_latent_vertex_labels_passed_to_native"] is True
          and d["original_observed_negative_edges_immutable"] is True
          and d["inferred_native_sheaf_restriction_maps"] is False
          and d["source_free_synthetic_only"] is True,
          "NO_FALSE_WORLD_TRANSFER")
    check(d["scientific_pass"] is False
          and d["algorithmic_superiority"] is False
          and d["universal_safety"] is False
          and d["owner_science_first_use"] is False
          and d["accepted_main_changed"] is False
          and d["forge_dispatch"] is False
          and d["merge"] is False and d["deployment"] is False,
          "SCIENCE_OR_AUTHORITY_CLAIM")
    # Rank d0: image contains exactly 2^3=8 distinguishable edge patterns;
    # global gauge bit simultaneous inversion is its one-dimensional kernel.
    image={tuple(graph(x)) for x in itertools.product((0,1),repeat=4)}
    check(len(image)==8 and all(cycle(v)==(0,0,0) for v in image)
          and len(SINGLE)==6 and (1,1,1) not in SINGLE,
          "MATHEMATICAL_K4_TRUE_SHEAF")
    observations=d["world_cases"]
    check(len(observations)==160 and len(d["per_seed_provenance"])==32,
          "FROZEN_WORLD_SET")
    derived={arm:[] for arm in ARMS}
    raw_errors=[]
    double_noise_false=0
    for seed in SEEDS:
        record=d["per_seed_provenance"][str(seed)]
        source=list(range(16))
        prior_rng("public-roster",seed).shuffle(source)
        source=source[:12]
        check(record["source_masks_sha256"]==sha(encode(source))
              and len(record["native_compiled_source_shas"])==3
              and all(len(x)==64 for x in record["native_compiled_source_shas"])
              and len(record["native_initial_cold_sha256"])==64,
              "NATIVE_CUMULATIVE_OLD_SOURCE_CUSTODY")
        weights=record["evaluator_only_source_weights"]
        check(set(weights)=={"A","B","C"}
              and all(type(w) is int and w.bit_count()==3 for w in weights.values())
              and len(set(weights.values()))==3,"SOURCE_FIT_LAWS")
        def sourcey(w,m):
            row=sum(1<<i for i in range(16) if (m&i)==i)
            return (w&row).bit_count()%2
        fit_packets=[[k,[[mask&7,mask>>3,sourcey(weights[k],mask)]
                         for mask in source]]
                     for k in ("A","B","C")]
        check(record["new_A_B_C_source_fit_36_do_sha256"]==sha(encode(fit_packets)),
              "TRAINED_SOURCE_36_REAL_ACTIONS")
        for name in ("A","B","C"):
            forms=[sum(1<<i for i in range(16) if (m&i)==i)
                   for m in source]
            surviving=0
            for terms in itertools.combinations(range(16),3):
                w=sum(1<<i for i in terms)
                if all(((w&f).bit_count()%2)==sourcey(weights[name],m)
                       for f,m in zip(forms,source)):
                    surviving+=1
            check(surviving==1,"NATIVE_SOURCE_LAW_UNIQUE")
        sub=[x for x in observations if x["seed"]==seed]
        check(len(sub)==5 and {x["stratum_evaluator_only"] for x in sub}
              ==set(STRATA),"FIVE_FROZEN_STRATA")
        for stratum in STRATA:
            x=next(z for z in sub if z["stratum_evaluator_only"]==stratum)
            r=new_rng("evaluator-world",seed,stratum)
            vertices=[r.randrange(2) for _ in range(4)]
            true=graph(vertices)
            if stratum=="CLEAN":bad=[]
            elif stratum=="SINGLE":bad=r.sample(range(6),1)
            elif stratum in ("DOUBLE","DOUBLE_ANCHOR5"):bad=r.sample(range(6),2)
            else:bad=[i for i in range(6) if r.random()<.05]
            vnoise=[int(r.random()<.05) if stratum=="DOUBLE_ANCHOR5"
                    else 0 for _ in range(4)]
            measured=[true[i]^int(i in bad) for i in range(6)]
            sigma=cycle(measured)
            pre=("NO_DEFECT" if sigma==(0,0,0) else
                 "UNVALIDATED_DEFECT" if sigma in SINGLE
                 else "NONLOCALIZABLE")
            check(x["evaluator_only_latent_vertex_bits"]==vertices
                  and x["evaluator_only_wrong_edge_ids"]==sorted(bad)
                  and x["evaluator_only_anchor_sensor_noise"]==vnoise
                  and x["observed_edge_values"]==measured
                  and x["true_cycle_H1_syndrome"]==list(sigma)
                  and x["native_pre_anchor_status"]==pre
                  and x["true_edge_sha256"]==sha(encode(true))
                  and x["six_true_edge_witness_sha256"]==
                      sha(encode([[i,1,measured[i]] for i in range(6)])),
                  "EVALUATOR_GROUND_TRUTH_AND_OBSERVED_SOURCE")
            raw_errors.append(score(measured,true)["brier"])
            check(set(x["arms"])==set(ARMS),"ALL_EQUAL_INFO_ARMS")
            for arm in ARMS:
                datum=x["arms"][arm]
                if arm in ("native_k4_scdr",
                           "independent_exact_k4_cohomology_repair",
                           "full_16vertex_64mask_mixture_bayes_same_anchors"):
                    chosen=SINGLE.get(sigma,0)
                elif arm=="fixed_edge_validation":
                    chosen=0
                else:
                    chosen=new_rng("independent-random-edge",seed,stratum).randrange(6)
                u,v=EDGES[chosen]
                anchors={u:vertices[u]^vnoise[u],v:vertices[v]^vnoise[v]}
                packet=[[u,0,anchors[u]],[v,0,anchors[v]]]
                check(datum["selected_edge"]==chosen
                      and datum["two_vertex_anchor_source_sha256"]==sha(encode(packet))
                      and datum["source_retained"] is True
                      and datum["actual_edge_actions"]==6
                      and datum["actual_vertex_anchor_actions"]==2
                      and len(datum["cold_sha256"])==64,
                      "ACTUAL_NEW_ANCHOR_WITNESS_AND_COLD")
                if arm in ("native_k4_scdr","independent_exact_k4_cohomology_repair"):
                    pred,status,repaired=independent_conventional(measured,anchors,chosen)
                elif arm in ("fixed_edge_validation","seeded_random_edge_validation"):
                    pred=measured[:]
                    fixed_true=anchors[u]^anchors[v]
                    repaired=fixed_true!=measured[chosen]
                    if repaired:pred[chosen]=fixed_true
                    status=("DIRECT_ANCHOR_CORRECTION" if repaired
                            else "DIRECT_ANCHOR_CONSISTENT")
                else:
                    pred=conventional_bayes(measured,anchors)
                    repaired=False
                    status="EXACT_GENERATIVE_BAYES"
                exact_score=score(pred,true)
                false=bool(repaired and any(pred[i]!=true[i] and
                          pred[i]!=measured[i] for i in range(6)))
                still=(None if arm=="full_16vertex_64mask_mixture_bayes_same_anchors"
                       else sum(round(float(p))!=y for p,y in zip(pred,true)))
                check(datum["status"]==status
                      and datum["repair_certified"] is repaired
                      and datum["false_repair"] is false
                      and datum["true_wrong_edges_before"]==len(bad)
                      and datum["remaining_wrong_edges"]==still
                      and datum["metric"]==exact_score,
                      "INDEPENDENT_EACH_PREDICTION_AND_REPAIR")
                derived[arm].append((stratum,datum))
    stat={}
    for arm in ARMS:
        rows=[x for _,x in derived[arm]]
        stat[arm]={
            "mean_brier":round(sum(v["metric"]["brier"] for v in rows)/160,9),
            "false_repairs_total":sum(v["false_repair"] for v in rows),
            "confident_wrong_total":sum(v["metric"]["confident_wrong"] for v in rows),
            "genuine_do_actions":sum(v["actual_edge_actions"]+
                                     v["actual_vertex_anchor_actions"] for v in rows)}
        for stratum in STRATA:
            sub=[x for s,x in derived[arm] if s==stratum]
            stat[arm][stratum]={
                "mean_brier":round(sum(x["metric"]["brier"] for x in sub)/32,9),
                "confirmed":sum(x["repair_certified"] for x in sub),
                "false_repairs":sum(x["false_repair"] for x in sub),
                "confident_wrong":sum(x["metric"]["confident_wrong"] for x in sub)}
        check(stat[arm]==d["arm_statistics"][arm],
              "ORIGINAL_ARM_SUMMARY_"+arm)
    no_repair=round(sum(raw_errors)/len(raw_errors),9)
    check(no_repair==d["no_repair_brier"],"ORIGINAL_NO_REPAIR_ERROR")
    c=stat["native_k4_scdr"]
    gates={
        "native_source_cold_and_old_causal_knowledge_retained":
            all(v["source_retained"] for a in ARMS for _,v in derived[a]),
        "real_charged_source_and_anchor_actions":
            sum(v["genuine_do_actions"] for v in stat.values())==6400,
        "genuine_k4_h1_rank_and_unique_single_fault_localization":
            len(SINGLE)==6 and
            all(v["remaining_wrong_edges"]==0 for s,v in derived["native_k4_scdr"]
                if s=="SINGLE"),
        "no_overwriting_or_false_correction_on_clean_and_exact_double":
            all(not v["repair_certified"] for s,v in derived["native_k4_scdr"]
                if s in ("CLEAN","DOUBLE")),
        "preregistered_brier_gain_vs_no_repair":
            c["mean_brier"]<=no_repair-.03+1e-12,
        "noisy_anchor_false_repair_at_most_5_percent":
            c["DOUBLE_ANCHOR5"]["false_repairs"]<=int(32*.05),
        "full_independent_conventional_k4_repair_parity":
            all(x["metric"]==y["metric"] and x["status"]==y["status"]
                for (_,x),(_,y) in zip(derived["native_k4_scdr"],
                                      derived["independent_exact_k4_cohomology_repair"])),
        "within_0_05_of_strong_full_mixture_bayes":
            c["mean_brier"]<=stat["full_16vertex_64mask_mixture_bayes_same_anchors"]["mean_brier"]+.05+1e-12
    }
    check(gates==d["frozen_gates"] and sum(gates.values())==6
          and d["development_disposition"]=="DEVELOPMENT_MIXED_OR_NO_GO"
          and gates["noisy_anchor_false_repair_at_most_5_percent"] is False
          and gates["within_0_05_of_strong_full_mixture_bayes"] is False,
          "FROZEN_TWO_FAILURES_MUST_NOT_BE_HIDDEN")
    return {"raw_sha256":sha(raw),"worlds":160,"policy_episodes":800,
            "source_do_outcomes":7552,"strong_original_brier":no_repair,
            "candidate_brier":c["mean_brier"],
            "exact_bayes_brier":stat["full_16vertex_64mask_mixture_bayes_same_anchors"]["mean_brier"],
            "noisy_anchor_false_repair":c["DOUBLE_ANCHOR5"]["false_repairs"],
            "frozen_gate_pass":6,"frozen_gate_total":8,
            "disposition":"DEVELOPMENT_MIXED_OR_NO_GO","scientific_pass":False}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("original_file",type=Path)
    p.add_argument("--scorer",type=Path,default=Path(
        "research/contrib/chatgpt/CKAD25-AE/run.py"))
    p.add_argument("--parent",type=Path,default=Path(
        "research/contrib/chatgpt/CKAD25-AB/run.py"))
    a=p.parse_args()
    evidence=reconstruct(a.original_file.read_bytes(),a.scorer,a.parent)
    print("CKAD25AE_INDEPENDENT_800_REAL_SOURCE_AND_4800_TRUE_EDGE_AUDIT_PASS")
    print(json.dumps(evidence,sort_keys=True))


if __name__=="__main__":
    main()
