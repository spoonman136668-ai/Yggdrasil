"""Y050: two hidden worlds with identical multi-channel feedback but different truth."""
import hashlib
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

prior=Path(__file__).resolve().parent.parent/"20261013-y040-hibernation"/"execute.py"
spec=importlib.util.spec_from_file_location("y040",prior)
y40=importlib.util.module_from_spec(spec)
spec.loader.exec_module(y40)
WORLDS=("PAIRED_BIASED_A","PAIRED_GENUINE_A_PLUS3")
ARMS=("AUDIT_BOTH","CONSERVATIVE_A_ABSTENTION")


def groups(seed):
    assert 224<=seed<=231
    core=y40.active(seed,10)
    assert len(core)==7
    return core[:4],core[4:]


def truth(seed,key,ep,world):
    base=y40.target(seed,key,0,"STABLE")
    if ep<6 or key not in y40.permutation(seed)[:7]:return base
    a,_=groups(seed)
    if key in a and world=="PAIRED_GENUINE_A_PLUS3":
        return (base+3)%4
    return (base+2)%4


def report(seed,key,ep,world):
    value=truth(seed,key,ep,world)
    a,_=groups(seed)
    if ep==10 and key in a and world=="PAIRED_BIASED_A":
        return (value+1)%4
    return value


def fingerprint(seed):
    raw={"cue_order":y40.permutation(seed),
         "initial":[truth(seed,k,0,"PAIRED_BIASED_A") for k in range(16)]}
    return hashlib.sha256(json.dumps(raw,sort_keys=True,
                                    separators=(",",":")).encode()).hexdigest()


def evaluate(seed,world,arm):
    a,b=groups(seed)
    live={};dormant=OrderedDict()
    pretrace=hashlib.sha256()
    rows=[]
    for ep in range(12):
        keys=y40.active(seed,ep)
        primary={};audits={}
        remaining=list(keys)
        if ep==10:
            sampled=a[:2]+b[:1]
            assert all(k in dormant for k in sampled)
            primary={k:report(seed,k,ep,world) for k in sampled}
            audits={"A":report(seed,a[0],ep,world),
                    "B":report(seed,b[0],ep,world)}
            remaining=[k for k in keys if k not in primary]
        da=[(primary[k]-dormant[k])%4 for k in a if k in primary]
        db=[(primary[k]-dormant[k])%4 for k in b if k in primary]
        if ep==10:
            assert len(da)==2 and len(db)==1
        conflicting=(ep==10 and
                     (len(set(da))>1 or audits["A"]!=primary[a[0]]
                      or audits["B"]!=primary[b[0]]))
        predictions={}
        for k in remaining:
            old=live[k] if k in live else dormant.get(k,0)
            if ep!=10:
                guess=old
            elif conflicting or (arm=="CONSERVATIVE_A_ABSTENTION" and k in a):
                guess=None
            else:
                delta=da[0] if k in a else db[0]
                guess=(old+delta)%4
            predictions[k]=guess
        assert len(remaining)+len(primary)==7
        assert not set(remaining).intersection(primary)
        early_hash=None
        if ep==10:
            early_hash=hashlib.sha256(bytes(
                [k for k in keys if k in primary for _ in (0,)]
                +[primary[k] for k in keys if k in primary]
                +[audits["A"],audits["B"]])).hexdigest()
        # True unsampled labels now exposed ONLY to evaluator after forecasts.
        authoritative={k:truth(seed,k,ep,world) for k in keys}
        correct=sum(predictions[k]==authoritative[k] for k in remaining)
        abstained=sum(predictions[k] is None for k in remaining)
        wrong=len(remaining)-correct-abstained
        if ep<=9:
            pretrace.update(bytes((ep,))+bytes(
                x for k in keys for x in (k,authoritative[k])))
        for k in keys:dormant.pop(k,None)
        writes=0
        for k in sorted(set(live)-set(keys)):
            dormant.pop(k,None)
            dormant[k]=live[k]
            writes+=1
            while len(dormant)>9:dormant.popitem(last=False)
        live=authoritative
        assert len(live)==7 and len(dormant)<=9
        assert not set(live).intersection(dormant)
        rows.append({"episode":ep,"scored":len(remaining),
                     "early_reports":len(primary)+len(audits),
                     "unique_reported_cues":len(primary),
                     "correct":correct,"wrong":wrong,"abstained":abstained,
                     "conflict":bool(conflicting),"early_hash":early_hash,
                     "predictions":[predictions[k] for k in remaining] if ep==10 else None,
                     "remaining_keys":remaining if ep==10 else None,
                     "targets":[authoritative[k] for k in remaining] if ep==10 else None,
                     "writes":writes,"occupancy":len(dormant)})
    return {"seed":seed,"cohort":"development" if seed<228 else "heldout",
            "world":world,"arm":arm,
            "pre_feedback_sha256":pretrace.hexdigest(),
            "first_return":rows[10],"relearn":rows[11],"episodes":rows}


def run():
    fingerprints={str(s):fingerprint(s) for s in range(224,232)}
    if len(set(fingerprints.values()))!=8:
        return {"classification":"NONUNIQUE_FINGERPRINT","fingerprints":fingerprints,
                "rows":[],"model_calls":0}
    rows=[evaluate(s,w,a) for s in range(224,232) for w in WORLDS for a in ARMS]
    by={(r["seed"],r["world"],r["arm"]):r for r in rows}
    equivalent=True
    target_delta=True
    for seed in range(224,232):
        weak=by[seed,"PAIRED_BIASED_A","AUDIT_BOTH"]
        strong=by[seed,"PAIRED_GENUINE_A_PLUS3","AUDIT_BOTH"]
        x,y=weak["first_return"],strong["first_return"]
        equivalent &= (weak["pre_feedback_sha256"]==strong["pre_feedback_sha256"]
                       and x["early_hash"]==y["early_hash"]
                       and x["predictions"]==y["predictions"])
        a,_=groups(seed)
        target_delta &= all((j-i)%4==1 for key,i,j in zip(
            x["remaining_keys"],x["targets"],y["targets"]) if key in a)
        for world in WORLDS:
            p=by[seed,world,"AUDIT_BOTH"];q=by[seed,world,"CONSERVATIVE_A_ABSTENTION"]
            for metric in ("writes","occupancy"):
                equivalent &= [z[metric] for z in p["episodes"]]==[
                    z[metric] for z in q["episodes"]]
            equivalent &= p["relearn"]["correct"]==q["relearn"]["correct"]==7
    held=[r for r in rows if r["seed"]>=228]
    totals={world:{arm:{
        metric:sum(r["first_return"][metric] for r in held
                    if r["world"]==world and r["arm"]==arm)
        for metric in ("scored","early_reports","correct","wrong","abstained","conflict")}
        for arm in ARMS} for world in WORLDS}
    p=totals["PAIRED_BIASED_A"];q=totals["PAIRED_GENUINE_A_PLUS3"]
    if not equivalent or not target_delta:
        classification="INVALID_PAIRED_HISTORY"
    elif (p["AUDIT_BOTH"]["correct"]==8 and p["AUDIT_BOTH"]["wrong"]==8
          and q["AUDIT_BOTH"]["correct"]==16 and q["AUDIT_BOTH"]["wrong"]==0
          and all(t["CONSERVATIVE_A_ABSTENTION"]["wrong"]==0
                  and t["CONSERVATIVE_A_ABSTENTION"]["abstained"]==8
                  for t in (p,q))):
        classification="CORRELATED_EVIDENCE_AMBIGUITY"
    else:
        classification="MIXED"
    return {"schema":"yggdrasil.y050-observational-equivalence.v1",
            "classification":classification,
            "parent":"33b29c90302fcc9f7302415039b998940d0c25a9",
            "fingerprints":fingerprints,"paired_history_equivalent":bool(equivalent),
            "group_a_target_delta_plus1":bool(target_delta),
            "heldout":totals,"rows":rows,"model_calls":0,
            "claim_limit":"Finite paired synthetic world counterexample: two agreeing biased channels may be indistinguishable from genuine target change."}


if __name__=="__main__":
    original=run()
    assert original==run()
    print(json.dumps(original,sort_keys=True,indent=2))
