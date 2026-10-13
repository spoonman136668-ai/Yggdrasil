"""Y030: independent keyed structured geometry for bounded cache falsification."""
import hashlib
import json
from collections import OrderedDict

TEMPLATES=((6,10,14),(5,9,13),(7,10,13),(6,11,14),
           (7,11,15),(5,10,14),(6,9,15),(7,12,15))


def salt(seed):
    digest=hashlib.sha256(("Y030/"+str(seed)).encode("utf-8")).digest()
    return int.from_bytes(digest[:2],"big")%16


def geometry(seed,episode):
    s=salt(seed)
    active=[(s+2*episode+5*j)%16 for j in range(7)]
    assert len(set(active))==7
    center=(7*s+3*episode+11*(seed-40))%16
    pattern=TEMPLATES[(seed-40+episode)%8]
    homes={key:center for key in active[:4]}
    for j,key in enumerate(active[4:]):
        homes[key]=(center+pattern[j])%16
    neighbors={
        key:{(home+offset)%16 for offset in range(-2,3)}
        for key,home in homes.items()
    }
    return active,neighbors


def hall_cardinality(active,neighbors):
    max_deficiency=0
    for mask in range(1,1<<7):
        union=set()
        for j,key in enumerate(active):
            if mask&(1<<j):
                union.update(neighbors[key])
        max_deficiency=max(max_deficiency,mask.bit_count()-len(union))
    return 7-max_deficiency


def match(active,neighbors,preferred):
    owner={}
    calls=0
    for key in active:
        cell=preferred.get(key)
        if cell is not None and cell in neighbors[key] and cell not in owner:
            owner[cell]=key

    def augment(key,seen):
        nonlocal calls
        calls+=1
        for cell in sorted(neighbors[key],key=lambda c:(c!=preferred.get(key),c)):
            if cell in seen:continue
            seen.add(cell)
            old=owner.get(cell)
            if old is None or augment(old,seen):
                owner[cell]=key
                return True
        return False

    for key in active:
        if key not in owner.values():
            augment(key,set())
    assigned={key:cell for cell,key in owner.items()}
    assert len(assigned)==hall_cardinality(active,neighbors)
    assert all(cell in neighbors[key] for key,cell in assigned.items())
    return assigned,calls


def evaluate(seed,use_cache):
    cache=OrderedDict()
    prev_active=set()
    prev_assignments={}
    evaluator_history={}
    trace=[]
    for episode in range(8):
        active,neighbors=geometry(seed,episode)
        pref={k:cache[k] for k in active if k in cache} if use_cache else {}
        legal={k:v for k,v in pref.items() if v in neighbors[k]}
        assigned,calls=match(active,neighbors,pref)
        returning=[k for k in assigned if k in evaluator_history]
        churn=sum(assigned[k]!=evaluator_history[k] for k in returning)
        for k in assigned:
            evaluator_history[k]=assigned[k]
        for k in active:
            cache.pop(k,None)
        writes=0
        for k in sorted(prev_active.difference(active)):
            cache.pop(k,None)
            if k in prev_assignments:
                cache[k]=prev_assignments[k]
                writes+=1
                while len(cache)>9:
                    cache.popitem(last=False)
        assert len(cache)<=9 and len(cache)+len(active)<=16
        assert not set(cache).intersection(active)
        prev_active=set(active)
        prev_assignments=assigned
        trace.append({
            "episode":episode,"matching_cardinality":len(assigned),
            "returning_count":len(returning),"churn":churn,
            "search_calls":calls,"writes":writes,"cache_entries":len(cache),
            "legal_preferences":len(legal)
        })
    return {
        "seed":seed,"cohort":"development" if seed<44 else "heldout",
        "policy":"cache_read" if use_cache else "sham",
        "total_churn":sum(t["churn"] for t in trace),
        "writes":sum(t["writes"] for t in trace),
        "search_calls":sum(t["search_calls"] for t in trace),
        "legal_prefs":sum(t["legal_preferences"] for t in trace),
        "episodes":trace
    }


def signature(seed):
    canonical=[]
    for episode in range(8):
        active,neighbors=geometry(seed,episode)
        canonical.append({
            "active":active,
            "neighbors":[sorted(neighbors[k]) for k in active]
        })
    encoded=json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def run():
    rows=[evaluate(seed,read) for seed in range(40,48)
          for read in (False,True)]
    cohort_signatures={str(seed):signature(seed) for seed in range(40,48)}
    unique=len(set(cohort_signatures.values()))==8
    all_matched=all(all(ep["matching_cardinality"]==7 for ep in a["episodes"])
                    for a in rows)
    writes_equal=all(rows[j]["writes"]==rows[j+1]["writes"]
                     for j in range(0,len(rows),2))
    for j in range(0,len(rows),2):
        a,b=rows[j:j+2]
        if all_matched:
            assert a["writes"]==b["writes"]
            assert [t["cache_entries"] for t in a["episodes"]]==[
                t["cache_entries"] for t in b["episodes"]]
    pairs=[(rows[2*(s-40)],rows[2*(s-40)+1]) for s in range(44,48)]
    savings=[a["total_churn"]-b["total_churn"] for a,b in pairs]
    if not unique:
        classification="NONINDEPENDENT_INPUT"
    elif not all_matched:
        classification="GEOMETRY_DEFICIENCY"
    elif sum(savings)>0:
        classification="OUT_OF_FAMILY_BENEFIT"
    else:
        classification="OUT_OF_FAMILY_NO_BENEFIT"
    return {
        "schema":"yggdrasil.y030-keyed-geometry.v1",
        "predecessor_head":"3d169808b5996ee1d9ca7304574843d2152018a9",
        "classification":classification,
        "geometry_signatures":cohort_signatures,
        "unique_signatures":unique,
        "all_seven_matched":all_matched,
        "matched_cache_writes":writes_equal,
        "heldout_savings":savings,
        "heldout_sham_churn":sum(a["total_churn"] for a,b in pairs),
        "heldout_cache_churn":sum(b["total_churn"] for a,b in pairs),
        "rows":rows,"model_calls":0,
        "claim_limit":"Fresh keyed synthetic geometry; no real-life intelligence transfer"
    }


if __name__=="__main__":
    o=run()
    assert o==run()
    print(json.dumps(o,sort_keys=True,indent=2))
