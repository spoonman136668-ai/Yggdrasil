"""Y052: online audit routing from recent true feedback, with one-step failure delay."""
import hashlib, importlib.util, json
from collections import OrderedDict
from pathlib import Path

p=Path(__file__).resolve().parent.parent/"20261013-y040-hibernation"/"execute.py"
spec=importlib.util.spec_from_file_location("y040_pinned",p)
y40=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y40)

WORLD=("PERSISTENT","FLIPPED_AT_RETURN","SECOND_SHIFT")
ARMS=("FROZEN_HISTORY","LATEST_FEEDBACK","DUAL_AUDIT")


def groups(seed):
    assert 248<=seed<=255
    core=y40.active(seed,10)
    return core[:4],core[4:]


def historic_group(seed):
    return "A" if seed%2==0 else "B"


def wrong_group(seed,condition,ep):
    first=historic_group(seed)
    other="B" if first=="A" else "A"
    if ep in (0,1):return first
    if ep==10:
        return other if condition=="FLIPPED_AT_RETURN" else first
    if ep==11:
        return first if condition=="PERSISTENT" else other
    return None


def true_value(seed,key,ep):
    orig=y40.target(seed,key,0,"STABLE")
    if ep<6 or key not in y40.permutation(seed)[:7]:
        return orig
    return (orig+2)%4


def source_fingerprint(seed):
    raw={"order":y40.permutation(seed),
         "labels":[true_value(seed,key,0) for key in range(16)]}
    return hashlib.sha256(json.dumps(raw,sort_keys=True,
                                    separators=(",",":")).encode()).hexdigest()


def evaluate(seed,condition,arm):
    aa,bb=groups(seed)
    cache=OrderedDict()
    live={}
    historic={"A":0,"B":0}
    latest={"A":0,"B":0}
    pretrace=hashlib.sha256()
    episodes=[]
    for ep in range(12):
        current=y40.active(seed,ep)
        assert len(current)==7
        sampled={}
        audit={}
        remaining=list(current)
        chosen=[]
        if ep in (10,11):
            keys=aa[:2]+bb[:1]
            assert len(keys)==3
            sampled={k:true_value(seed,k,ep) for k in keys}
            fault=wrong_group(seed,condition,ep)
            if fault:
                for k in keys:
                    if (fault=="A" and k in aa) or (fault=="B" and k in bb):
                        sampled[k]=(sampled[k]+1)%4
            if arm=="DUAL_AUDIT":
                chosen=["A","B"]
            else:
                evidence=(historic if arm=="FROZEN_HISTORY" or ep==10 else latest)
                chosen=["A" if evidence["A"]>=evidence["B"] else "B"]
            for group in chosen:
                k=aa[0] if group=="A" else bb[0]
                audit[group]=true_value(seed,k,ep)
            remaining=[k for k in current if k not in sampled]
        da=[(sampled[k]-(live[k] if k in live else cache[k]))%4
            for k in aa if k in sampled]
        db=[(sampled[k]-(live[k] if k in live else cache[k]))%4
            for k in bb if k in sampled]
        if ep in (10,11):
            assert len(da)==2 and len(db)==1
        conflict_a=(len(set(da))>1 or
                    ("A" in audit and sampled[aa[0]]!=audit["A"]))
        conflict_b=("B" in audit and sampled[bb[0]]!=audit["B"])
        guesses={}
        for k in remaining:
            old=live[k] if k in live else cache.get(k,0)
            if ep not in (10,11):
                pred=old
            elif (k in aa and conflict_a) or (k in bb and conflict_b):
                pred=None
            else:
                pred=(old+(da[0] if k in aa else db[0]))%4
            guesses[k]=pred
        assert len(remaining)+len(sampled)==7
        # NOW evaluator supplies entire true feedback for this completed episode.
        truth={k:true_value(seed,k,ep) for k in current}
        if ep in (0,1):
            keys=aa[:2]+bb[:1]
            reports={k:truth[k] for k in keys}
            old_fault=wrong_group(seed,condition,ep)
            for k in keys:
                if (old_fault=="A" and k in aa) or (old_fault=="B" and k in bb):
                    reports[k]=(reports[k]+1)%4
                if reports[k]!=truth[k]:
                    historic["A" if k in aa else "B"]+=1
            pretrace.update(bytes((ep,))+bytes(
                item for k in current for item in (k,truth[k])))
            pretrace.update(bytes(
                item for k in keys for item in (k,reports[k])))
        elif ep<=9:
            pretrace.update(bytes((ep,))+bytes(
                item for k in current for item in (k,truth[k])))
        if ep==10:
            latest={"A":0,"B":0}
            for k,report in sampled.items():
                if report!=truth[k]:
                    latest["A" if k in aa else "B"]+=1
        correct=sum(guesses[k]==truth[k] for k in remaining)
        abstained=sum(guesses[k] is None for k in remaining)
        wrong=len(remaining)-correct-abstained
        for k in current:cache.pop(k,None)
        writes=0
        for k in sorted(set(live)-set(current)):
            cache.pop(k,None)
            cache[k]=live[k]
            writes+=1
            while len(cache)>9:cache.popitem(last=False)
        live=truth
        assert len(live)==7 and len(cache)<=9 and not set(live).intersection(cache)
        episodes.append({
            "episode":ep,"early_reports":len(sampled)+len(audit),
            "distinct_samples":len(sampled),
            "scored":len(remaining),
            "correct":correct,"wrong":wrong,"abstained":abstained,
            "audit":chosen,"writes":writes,"occupancy":len(cache),
            "conflict_a":bool(conflict_a),"conflict_b":bool(conflict_b),
        })
    return {"seed":seed,"cohort":"development" if seed<252 else "heldout",
            "condition":condition,"arm":arm,"old_errors":historic,
            "latest_e10_errors":latest,
            "pre_feedback_sha256":pretrace.hexdigest(),
            "e10":episodes[10],"e11":episodes[11],"episodes":episodes}


def run():
    signatures={str(s):source_fingerprint(s) for s in range(248,256)}
    if len(set(signatures.values()))!=8:
        return {"schema":"yggdrasil.y052-feedback-update.v1",
                "classification":"NONUNIQUE_FINGERPRINT",
                "fingerprints":signatures,"rows":[],"model_calls":0}
    records=[evaluate(seed,c,a) for seed in range(248,256)
             for c in WORLD for a in ARMS]
    lookup={(r["seed"],r["condition"],r["arm"]):r for r in records}
    valid=True
    for seed in range(248,256):
        hashes={lookup[seed,c,"FROZEN_HISTORY"]["pre_feedback_sha256"]
                for c in WORLD}
        valid &= len(hashes)==1
        start={tuple(lookup[seed,c,"LATEST_FEEDBACK"]["e10"]["audit"])
               for c in WORLD}
        valid &= len(start)==1
        for c in WORLD:
            same=[lookup[seed,c,a] for a in ARMS]
            for key in ("writes","occupancy"):
                histories=[[row[key] for row in r["episodes"]] for r in same]
                valid &= histories[0]==histories[1]==histories[2]
            valid &= all(r[e]["scored"]==4 and r[e]["distinct_samples"]==3
                         for r in same for e in ("e10","e11"))
    held=[r for r in records if r["seed"]>=252]
    result={c:{a:{e:{
        k:sum(r[e][k] for r in held if r["condition"]==c and r["arm"]==a)
        for k in ("scored","early_reports","correct","wrong","abstained")}
        for e in ("e10","e11")} for a in ARMS} for c in WORLD}
    flipped=result["FLIPPED_AT_RETURN"]
    second=result["SECOND_SHIFT"]
    stable=result["PERSISTENT"]
    if not valid:classification="INVALID_PAIRED_HISTORY"
    elif (flipped["LATEST_FEEDBACK"]["e11"]["wrong"]==0
          and flipped["LATEST_FEEDBACK"]["e11"]["wrong"]<
              flipped["FROZEN_HISTORY"]["e11"]["wrong"]
          and second["LATEST_FEEDBACK"]["e11"]["wrong"]>=1
          and all(result[c]["DUAL_AUDIT"][e]["wrong"]==0
                  for c in ("FLIPPED_AT_RETURN","SECOND_SHIFT")
                  for e in ("e10","e11"))
          and all(stable["LATEST_FEEDBACK"][e]["wrong"]==0
                  for e in ("e10","e11"))):
        classification="FEEDBACK_RECOVERY_WITH_RENEWED_DRIFT_LIMIT"
    else:classification="MIXED"
    return {"schema":"yggdrasil.y052-feedback-update.v1",
            "classification":classification,
            "parent":"9e903211b791ef427e6fde9c7598cfeb22ffb0ae",
            "fingerprints":signatures,"paired_history_valid":bool(valid),
            "heldout":result,"rows":records,"model_calls":0,
            "claim_limit":"One-step historical feedback reliability update, finite two-group sensor shift and full previous-episode labels."}


if __name__=="__main__":
    original=run()
    assert original==run()
    print(json.dumps(original,sort_keys=True,indent=2))
