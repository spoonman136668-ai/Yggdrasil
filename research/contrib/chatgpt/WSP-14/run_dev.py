"""WSP-14 frozen 256-world exhaustive DEV; information-bound negative."""
import hashlib
import json
import time
from nand_program import (MAX_NANDS, OBSERVED, HIDDEN, GRADIENT_STEPS_DIRECT,
                          NumericNand, catalog, synthesize, observed_world,
                          symbolic_eval, bits, fully_train_8hot, trained_predict)


def run():
    start=time.perf_counter()
    programs=catalog()
    codebook_digest=hashlib.sha256(json.dumps(
        sorted((m, cost,repr(p)) for m,(cost,p) in programs.items()),
        separators=(",",":")).encode("ascii")).hexdigest()
    obsfit=equal=numeric_correct=symbolic_correct=zero_correct=trained_correct=0
    swapped_correct=restores=ablation_changed=hidden_queries=0
    restricted_worlds=restricted_numeric=restricted_symbolic=restricted_trained=0
    signatures=set()
    total_gates=0
    for truth_mask in range(256):
        examples=observed_world(truth_mask)
        chosen_cost, chosen_mask, program=synthesize(examples)
        c=NumericNand.from_program(program)
        total_gates+=c.used
        canonical=c.snapshot()
        restored=NumericNand.restore(canonical)
        restores+=restored.snapshot()==canonical
        weights, steps, bce=fully_train_8hot(examples)
        if bce>0.02 or steps>2048:
            raise AssertionError("WSP14_TRAINED_CONTROL_NOT_CONVERGED")
        signatures.add(tuple(y for _,y in examples))
        restricted=programs[truth_mask][0] <= 4
        restricted_worlds+=restricted
        for idx in range(8):
            x=bits(idx)
            pred=c.predict(x)
            equal+=pred==symbolic_eval(program,x)
            if restored.predict(x)!=pred:
                raise AssertionError("WSP14_COLD_REPLAY_MISMATCH")
            if idx in OBSERVED:
                obsfit+=pred==((truth_mask>>idx)&1)
            else:
                target=(truth_mask>>idx)&1
                hidden_queries+=1
                numeric_correct+=pred==target
                symbolic_correct+=symbolic_eval(program,x)==target
                zero_correct+=target==0
                trained_correct+=trained_predict(weights,idx)==target
                swapped_correct+=pred!=(target ^ 1)
                if restricted:
                    restricted_numeric+=pred==target
                    restricted_symbolic+=symbolic_eval(program,x)==target
                    restricted_trained+=trained_predict(weights,idx)==target
        if c.used:
            # Direct gate perturbation, without accepting a noncanonical state.
            prior=c.predict(bits(0))
            last=c.used-1
            old=c.weights[last]
            c.weights[last]=[0,0]
            value=list(bits(0))
            for gate in range(c.used):
                a,b=c.sources[gate]
                w1,w2=c.weights[gate]
                value.append(int(w1*value[a]+w2*value[b]>=-1))
            ablation_changed+=int(value[c.output]!=prior)
            c.weights[last]=old
    required=(len(programs)==256 and obsfit==1280 and equal==2048 and
              hidden_queries==768 and numeric_correct==symbolic_correct==
              zero_correct==trained_correct==swapped_correct==384 and
              len(signatures)==32 and restores==256 and
              ablation_changed>=1 and GRADIENT_STEPS_DIRECT==0)
    report={
        "schema":"wsp14.public-dev-result.v1",
        "catalog_mask_count":len(programs),
        "catalog_sha256":codebook_digest,
        "maximum_minimal_nand_gate_count":max(g for g,_ in programs.values()),
        "total_programmed_nand_gates_across_worlds":total_gates,
        "observed_examples_fitted":obsfit,
        "numeric_vs_symbolic_program_agreement":equal,
        "full_program_queries":2048,
        "hidden_queries":hidden_queries,
        "hidden_numeric_correct":numeric_correct,
        "hidden_symbolic_correct":symbolic_correct,
        "hidden_zero_correct":zero_correct,
        "hidden_fully_trained_8hot_correct":trained_correct,
        "hidden_flip_alternative_wrong":swapped_correct,
        "training_signatures_converged":len(signatures),
        "cold_restores":restores,
        "gate_ablation_changed_outputs":ablation_changed,
        "restricted_cost4_worlds":restricted_worlds,
        "restricted_cost4_hidden_predictions":restricted_worlds*3,
        "restricted_cost4_numeric_correct":restricted_numeric,
        "restricted_cost4_symbolic_correct":restricted_symbolic,
        "restricted_cost4_trained8hot_correct":restricted_trained,
        "gradient_steps_direct_circuit":GRADIENT_STEPS_DIRECT,
        "elapsed_seconds_not_cost_superiority":round(time.perf_counter()-start,3),
        "scientific_status":"UNVERIFIED; exhaustive hidden labels information-theoretically ambiguous; NAND search is external",
        "dev_engineering":"PASS" if required else "FAIL"
    }
    print(json.dumps(report,sort_keys=True,indent=2))
    if not required:
        raise SystemExit(1)
    return report


if __name__=="__main__":
    run()
