"""Local feature sufficiency diagnostic, without invented success claims.

A four-bit public world can contain contradictory labels under a two-bit
receptive field. Compute a predeclared information ceiling from training
pairs only, then check held-out errors separately. Feature conflicts do not
confer access to future labels or hidden regime identity.
"""
import json
from specialization_scaling_audit import families, measure

def conflicts(cases):
    per_cell=[]
    for i in range(4):
        observed={}
        for bits,outcome in cases:
            key=(bits[i],bits[(i+1)%4])
            observed.setdefault(key,set()).add(outcome)
        per_cell.append({
            "distinct_features":len(observed),
            "ambiguous_features":sum(len(labels)>1 for labels in observed.values()),
            "conflicting_samples":sum(
                1 for bits,_ in cases
                if len(observed[(bits[i],bits[(i+1)%4])])>1),
        })
    return per_cell

def run():
    evidence=[]
    for seed in (3,17,41):
        cases=families(seed)
        for count in (2,4,8,12):
            trained=cases[:count]
            results=measure(seed,count,4)
            evidence.append({
                "seed":seed,
                "trained":count,
                "local_conflicts":conflicts(trained),
                "native_correct":results["native_trained"]["correct"],
                "native_wrong":results["native_trained"]["wrong"],
                "native_abstentions":results["native_trained"]["abstentions"],
                "tabular_correct":results["table_trained"]["correct"],
                "heldout_wrong":results["native_heldout"]["wrong"],
                "actions":results["actions"],
            })
    return {
        "experiments":evidence,
        "scope":"Observational information-sufficiency diagnosis of two-bit local receptive fields on generated public parity families",
        "limitation":"Conflict counts are a retrospective diagnostic of training data, not an action-selection oracle or proof that four-bit local learning cannot succeed.",
    }

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True))
