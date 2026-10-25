"""Frozen Y022 circular-geometry out-of-cohort transfer."""
import json
def maxmatch(seed,radius):
    owner={}
    homes=[(7*k+seed)%16 for k in range(16)]
    assert len(set(homes))==16
    def augment(k,seen):
        h=homes[k]
        for offset in range(-radius,radius+1):
            cell=(h+offset)%16
            if cell in seen:continue
            seen.add(cell)
            prior=owner.get(cell)
            if prior is None or augment(prior,seen):
                owner[cell]=k
                return True
        return False
    for k in range(16):
        augment(k,set())
    return len(owner)
def run():
    rows=[{"seed":s,"cohort":"development" if s<4 else "heldout","radius_one_cardinality":maxmatch(s,1),"radius_two_cardinality":maxmatch(s,2)} for s in range(8)]
    valid=all(0<=r["radius_one_cardinality"]<=r["radius_two_cardinality"]<=16 for r in rows)
    return {"schema":"yggdrasil.y022-new-cohort.v1","rows":rows,"frozen_homes_bijective":True,"source_population":"new_generated_synthetic","model_calls":0,"classification":"INVALID" if not valid else "NEGATIVE_TRANSFER" if all(x["radius_one_cardinality"]==16 for x in rows[4:]) else "MIXED_TRANSFER","claim_limit":"Not R016 original-data validation or independent scientific acceptance"}
if __name__=="__main__":
    o=run();assert o==run()
    print(json.dumps(o,sort_keys=True,indent=2))
