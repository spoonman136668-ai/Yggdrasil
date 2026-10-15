"""Independent F46 Yggdrasil review of previously generated TRAIN-only rows.

No new Yggdrasil source pilot.run call, no extra original. Rebuild the outcome
and numerical prediction from the already frozen public/diagnostic sources and
paid channel indices, then independently check FP/FN/Brier/logloss and gates.
"""
import importlib.util,json,math,pathlib,sys

ROOT=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("y_f46_existing_training_provenance",ROOT/"source_pilot.py")
model=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=model
spec.loader.exec_module(model)

ARMS=("learned_intervention_invariant","fitted_Gaussian_latent",
 "empirical_conditional_Brier","Gaussian_kernel","public_global_static",
 "learned_unpaired_ablation","source_variance",
 "count_matched_shuffled_intervention_pairs","evaluator_oracle_unfair")
FAIR=("fitted_Gaussian_latent","empirical_conditional_Brier","Gaussian_kernel",
      "public_global_static","source_variance","learned_unpaired_ablation",
      "count_matched_shuffled_intervention_pairs")
CAND="learned_intervention_invariant"

def metric(rows,arm):
    n=len(rows)
    correct=sum(r["predictions"][arm]==r["truth"] for r in rows)
    fp=sum(bool(r["predictions"][arm]) and not r["truth"] for r in rows)
    fn=sum((not bool(r["predictions"][arm])) and r["truth"] for r in rows)
    brier=sum((r["probabilities"][arm]-float(r["truth"]))**2 for r in rows)/n
    loss=-sum(math.log(r["probabilities"][arm] if r["truth"] else
                       1-r["probabilities"][arm]) for r in rows)/n
    return {"correct":correct,"total":n,"accuracy":correct/n,"fp":fp,"fn":fn,
            "Brier":brier,"logloss":loss}
def equal_scores(actual,expected):
    assert actual.keys()==expected.keys()
    for field,value in expected.items():
        if isinstance(value,float):
            assert math.isclose(actual[field],value,rel_tol=1e-10,abs_tol=1e-10),(field,actual[field],value)
        else:assert actual[field]==value,(field,actual[field],value)

def audit(path):
    doc=json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    assert doc["schema"]=="yggdrasil.f46.paired-vs-shuffled-anchor.trainonly.v1"
    assert doc["stage"]=="TRAIN_ONLY_CAUSAL_ABLATION_NOT_PRIMARY_ORIGINAL"
    assert doc["questions"]==128 and len(doc["rows"])==128
    assert doc["diagnostic_seeds"]==[401100,401108]
    assert doc["fit_seeds"]==[401000,401008]
    assert doc["reserved_seeds"]==[402000,402016]
    assert doc["old_original_reserved_not_touched"]==[382000,382016]
    assert doc["families"]==[520,521,522,523]
    assert doc["reserved_families"]==[524,525,526,527]
    assert doc["original_source_cohorts_not_reused"]
    assert doc["primary_original_not_executed"] and not doc["independent_F3_custody"]
    assert not doc["accepted_ref_mutation"] and not doc["native_576_byte_resident_qualified"]
    assert doc["paid_api_calls"]==0 and doc["diagnostic_labels_not_used_in_fit"]
    assert doc["private_modes_never_in_action_inputs"]
    assert doc["public_reference_pairs"]==12
    assert doc["packed_parameter_bytes"]==132 and doc["packed_bytes_not_native_residency"]
    assert doc["train_mechanisms"]==list(model.prior.TRAIN_MECHANISMS)
    assert doc["heldout_mechanisms"]==list(model.prior.HELDOUT_MECHANISMS)
    assert set(doc["train_mechanisms"]).isdisjoint(doc["heldout_mechanisms"])
    rows=doc["rows"]
    assert len({(r["seed"],r["family"],r["mechanism"],r["condition"]) for r in rows})==128
    for row in rows:
        seed,family=row["seed"],row["family"]
        assert seed in model.DIAGNOSTIC and family in model.FAMILIES
        assert row["mechanism"] in model.prior.HELDOUT_MECHANISMS
        assert row["condition"] in model.prior.CONDITIONS
        mech=2+model.prior.HELDOUT_MECHANISMS.index(row["mechanism"])
        cond=model.prior.CONDITIONS.index(row["condition"])
        pairs=model.prior.public_pairs(seed,family,mech,cond)
        assert len(pairs)==12
        assert all(p[0][0]==p[1][0] for p in pairs)
        ref=model.prior.flat(pairs)
        corr=model.prior.prior.reliabilities(ref)
        hidden=[model.prior.source(seed,family,role,mech,cond,97000+role,0)
                for role in range(3)]
        truth=model.prior.task([h[0] for h in hidden],family)
        assert row["truth"]==truth
        assert row["public_pairs"]==12 and row["public_flat_anchors"]==24
        assert set(row["predictions"])==set(ARMS)
        assert set(row["probabilities"])==set(ARMS)
        assert set(row["receipts"])==set(ARMS)-{"evaluator_oracle_unfair"}
        assert row["predictions"]["evaluator_oracle_unfair"]==truth
        for arm,traces in row["receipts"].items():
            assert len(traces)==3
            estimated=[]
            for role,channel_indices in enumerate(traces):
                assert len(channel_indices)==2 and channel_indices[0]==0
                j=channel_indices[1]
                assert isinstance(j,int) and j in (1,2,3)
                value=hidden[role][2][j]
                estimated.append(model.prior.prior.bit_prob(value,j,corr))
            expected_answer=model.prior.task([v>=.5 for v in estimated],family)
            expected_p=model.prior.task_probability(estimated,family)
            assert row["predictions"][arm]==expected_answer
            assert math.isclose(row["probabilities"][arm],expected_p,rel_tol=1e-11,abs_tol=1e-11)
        oracle=.999999 if truth else .000001
        assert math.isclose(row["probabilities"]["evaluator_oracle_unfair"],oracle,rel_tol=1e-11,abs_tol=1e-11)
    assert set(doc["scores"])==set(ARMS)
    for arm in ARMS:equal_scores(doc["scores"][arm],metric(rows,arm))
    assert doc["scores"]["evaluator_oracle_unfair"]["correct"]==128
    for field,key,values in (
      ("by_mechanism","mechanism",model.prior.HELDOUT_MECHANISMS),
      ("by_condition","condition",model.prior.CONDITIONS)):
        for v in values:
            subset=[row for row in rows if row[key]==v]
            assert len(subset)==64
            for arm in ARMS:equal_scores(doc[field][v][arm],metric(subset,arm))
    strongest=max(FAIR,key=lambda a:doc["scores"][a]["accuracy"])
    gain=doc["scores"][CAND]["accuracy"]-doc["scores"][strongest]["accuracy"]
    shuffled=doc["scores"][CAND]["accuracy"]-doc["scores"]["count_matched_shuffled_intervention_pairs"]["accuracy"]
    unpaired=doc["scores"][CAND]["accuracy"]-doc["scores"]["learned_unpaired_ablation"]["accuracy"]
    no_regress=all(doc["by_mechanism"][m][CAND]["correct"]>=max(
        doc["by_mechanism"][m][a]["correct"] for a in FAIR)
        for m in model.prior.HELDOUT_MECHANISMS)
    accepted=gain>=.02 and shuffled>0 and unpaired>0 and no_regress
    assert doc["strongest_fair_control"]==strongest
    assert math.isclose(doc["gain_over_strongest_fair"],gain,abs_tol=1e-11)
    assert math.isclose(doc["shuffled_pairs_ablation_gain"],shuffled,abs_tol=1e-11)
    assert math.isclose(doc["unpaired_ablation_gain"],unpaired,abs_tol=1e-11)
    assert doc["heldout_mechanism_nondegradation"]==no_regress
    assert doc["frozen_criterion_met"]==accepted
    verdict=("TRAIN_ONLY_CAUSAL_INTERVENTION_SUPPORTED_NOT_F3"
             if accepted else "TRAIN_ONLY_CAUSAL_INTERVENTION_NEGATIVE")
    assert doc["verdict"]==verdict
    out={"schema":"yggdrasil.f46.existing-train-audit.v1",
         "mode":"READ_ONLY_EXISTING_TRAIN_ARTIFACT_NOT_PRIMARY_ORIGINAL",
         "source_run":38803873408,
         "cases":128,
         "scores_correct":{arm:doc["scores"][arm]["correct"] for arm in ARMS},
         "brier":{arm:doc["scores"][arm]["Brier"] for arm in ARMS},
         "strongest_fair":strongest,"gain":gain,
         "shuffled_ablation_gain":shuffled,"unpaired_ablation_gain":unpaired,
         "no_heldout_mechanism_regression":no_regress,
         "frozen_gate_pass":accepted,"verdict":verdict,
         "independent_F3_custody":False,"original_executed":False,
         "accepted_ref_mutated":False}
    print(json.dumps(out,sort_keys=True,indent=2))
    return out

if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: independent_audit.py RESULT_JSON")
    audit(sys.argv[1])
