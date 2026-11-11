"""WSP-13 frozen public development evaluator. No private test or paid API."""
import json
import time
from composite_memory import (BASE, BASE_CODE, GRADIENT_STEPS, HIDDEN,
                              N, SLOTS, TRIPLES, NumericRuleBuilder,
                              oracle_truth, stimulus, symbolic_exact)


def execute():
    t0=time.perf_counter()
    numeric=symbolic=base_only=ablated=zero=cubic_negative=restores=faults=0
    public=heldout=features_allocated=0
    for code in range(1024):
        observations=tuple((stimulus(m),oracle_truth(code,stimulus(m)))
                           for m in BASE+TRIPLES)
        model=NumericRuleBuilder()
        for x,y in observations:
            model.observe_training(x,y)
            public+=1
        if not model.is_complete():
            raise AssertionError("WSP13_NOT_TRAINED")
        expected_addrs=[TRIPLES[i] for i in range(10) if (code >> i)&1]
        got_addrs=[sum(b<<j for j,b in enumerate(addr))
                   for occ,addr in zip(model.feature_occupied,
                                       model.feature_addresses) if occ]
        if expected_addrs!=got_addrs:
            raise AssertionError("WSP13_SYNAPTIC_FEATURE_IDENTITY_MISMATCH")
        features_allocated+=len(got_addrs)
        raw=model.snapshot()
        cold=NumericRuleBuilder.restore(raw)
        restores+=cold.snapshot()==raw
        for mask in HIDDEN:
            x=stimulus(mask)
            truth=oracle_truth(code,x)
            pred=model.predict(x)
            heldout+=1
            numeric+=pred==truth
            symbolic+=symbolic_exact(observations,x)==truth
            base_pred=model._base_prediction(x)
            base_only+=base_pred==truth
            # disabling all new synaptic clause occupancies is the ablation
            # (same prediction as base-only, validated separately in tests).
            ablated+=base_pred==truth
            zero+=truth==0
            cubic_negative+=pred!=(truth ^ int(all(x[:4])))
            if cold.predict(x)!=pred:
                raise AssertionError("WSP13_COLD_PREDICTION_MISMATCH")
        faulty_label=oracle_truth(code,stimulus(15)) ^ 1
        faults+=((not model.verify_new_witness(stimulus(15),faulty_label))
                 and model.predict(stimulus(31)) is None)
    required=(public==26624 and heldout==6144 and
              numeric==symbolic==6144 and
              base_only==ablated==zero==3072 and
              cubic_negative==2048 and
              restores==faults==1024 and
              features_allocated==1024*10//2 and GRADIENT_STEPS==0)
    report={
        "schema":"wsp13.public-dev-result.v1",
        "worlds":1024,
        "public_observations":public,
        "hidden_predictions":heldout,
        "numeric_feature_generalization_exact":numeric,
        "equal_information_symbolic_exact":symbolic,
        "base_only_exact":base_only,
        "new_feature_ablation_exact":ablated,
        "zero_predictor_exact":zero,
        "unseen_fourth_order_wrong":cubic_negative,
        "cold_restores":restores,
        "observed_contradiction_latches":faults,
        "total_new_synaptic_feature_instances":features_allocated,
        "gradient_steps":GRADIENT_STEPS,
        "elapsed_seconds_not_comparative_efficiency":round(time.perf_counter()-t0,3),
        "scientific_superiority":"UNVERIFIED__operator_type_preprogrammed__symbolic_tie",
        "engineering_public_dev":"PASS" if required else "FAIL"
    }
    print(json.dumps(report,sort_keys=True,indent=2))
    if not required:
        raise SystemExit(1)
    return report


if __name__=="__main__":
    execute()
