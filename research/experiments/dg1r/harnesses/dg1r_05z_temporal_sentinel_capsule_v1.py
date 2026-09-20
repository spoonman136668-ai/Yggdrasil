#!/usr/bin/env python3
import argparse, copy, hashlib, itertools, json
from pathlib import Path

LEGIT_ROLES=(0,1,1,2,2,3,3)
COHORT_GENERATIONS=(0,2,4)
SENTINELS_PER_COHORT=3
COHORT_QUORUM=2
CAPSULE_FIELDS=("checkpoint_id","generation","role","fp2","causal_cursor")
MODES=("FULL_CELL","CAPSULE")
STATUSES=("VALIDATED","CONTESTED","ABSTAIN")


def enc(o):
    return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False)


def fp2(role):
    r0=role&1
    r1=(role>>1)&1
    return (r0^r1)|(r1<<1)


def make_history(roles):
    hist=[]
    parent="ROOT"
    for generation,role in enumerate(roles):
        commit_id=hashlib.sha256(f"{parent}|{generation}|{role}".encode()).hexdigest()[:16]
        hist.append({
            "generation":generation,
            "role":role,
            "fp2":fp2(role),
            "parent":parent,
            "commit_id":commit_id,
        })
        parent=commit_id
    return hist


LEGIT_HISTORY=make_history(LEGIT_ROLES)


def capsule_from_history(history,generation):
    h=history[generation]
    return {
        "checkpoint_id":f"CP{generation}",
        "generation":generation,
        "role":h["role"],
        "fp2":h["fp2"],
        "causal_cursor":h["commit_id"],
    }


def capsule_digest(capsule):
    payload={k:capsule[k] for k in CAPSULE_FIELDS}
    return hashlib.sha256(enc(payload).encode()).hexdigest()


def make_cohort(history,generation,root_ids):
    capsule=capsule_from_history(history,generation)
    seal=capsule_digest(capsule)
    cohort=[]
    for i,root_id in enumerate(root_ids):
        cohort.append({
            "holder":f"S{generation}_{i}",
            "root_mask":1<<root_id,
            "capsule":copy.deepcopy(capsule),
            "seal":seal,
            "sealed":True,
            "full_state":{
                "capsule":copy.deepcopy(capsule),
                "internal_state":tuple((generation*17+i*13+j)%256 for j in range(64)),
                "sealed":True,
            },
        })
    return cohort


BASE_COHORTS={
    0:make_cohort(LEGIT_HISTORY,0,(0,1,2)),
    2:make_cohort(LEGIT_HISTORY,2,(3,4,5)),
    4:make_cohort(LEGIT_HISTORY,4,(6,7,8)),
}


def pairwise_disjoint(masks):
    masks=[m for m in masks if m]
    return all((a&b)==0 for a,b in itertools.combinations(masks,2))


def extract_capsule(sentinel,mode):
    if mode=="CAPSULE":
        return copy.deepcopy(sentinel["capsule"])
    if mode=="FULL_CELL":
        return copy.deepcopy(sentinel["full_state"]["capsule"])
    raise KeyError(mode)


def valid_sentinel(sentinel,mode):
    if not sentinel.get("sealed",False):
        return False
    capsule=extract_capsule(sentinel,mode)
    return sentinel["seal"]==capsule_digest(capsule)


def cohort_anchor(cohort,mode):
    groups={}
    for sentinel in cohort:
        if not valid_sentinel(sentinel,mode):
            continue
        capsule=extract_capsule(sentinel,mode)
        groups.setdefault(enc(capsule),[]).append(sentinel)

    qualifying={}
    for key,sentinels in groups.items():
        ok=False
        for combo in itertools.combinations(sentinels,COHORT_QUORUM):
            if pairwise_disjoint([s["root_mask"] for s in combo]):
                ok=True
                break
        if ok:
            qualifying[key]=json.loads(key)

    if len(qualifying)==1:
        return next(iter(qualifying.values()))
    return None


def current_from_history(history):
    h=history[-1]
    return {
        "generation":h["generation"],
        "role":h["role"],
        "fp2":h["fp2"],
        "commit_id":h["commit_id"],
    }


def validate_descendant(anchor,history,current):
    g=anchor["generation"]
    if g>=len(history):
        return False

    base=history[g]
    if base["commit_id"]!=anchor["causal_cursor"]:
        return False
    if base["role"]!=anchor["role"] or base["fp2"]!=anchor["fp2"]:
        return False

    previous=base
    for item in history[g+1:]:
        if item["generation"]!=previous["generation"]+1:
            return False
        if item["parent"]!=previous["commit_id"]:
            return False
        previous=item

    terminal=history[-1]
    return (
        current["generation"]==terminal["generation"]
        and current["role"]==terminal["role"]
        and current["fp2"]==terminal["fp2"]
        and current["commit_id"]==terminal["commit_id"]
    )


def temporal_authorize(current,history,cohorts,mode):
    eligible=[g for g in cohorts if g<=current["generation"]]
    for generation in sorted(eligible,reverse=True):
        anchor=cohort_anchor(cohorts[generation],mode)
        if anchor is None:
            continue
        if validate_descendant(anchor,history,current):
            return {"status":"VALIDATED","anchor_generation":generation}
        return {"status":"CONTESTED","anchor_generation":generation}
    return {"status":"ABSTAIN","anchor_generation":None}


def dormant_can_vote(last_cursor,current,history,cohorts,mode,caught_up):
    if not caught_up:
        return False
    result=temporal_authorize(current,history,cohorts,mode)
    return result["status"]=="VALIDATED" and current["commit_id"]==history[-1]["commit_id"]


def legit_prefix(generation):
    return copy.deepcopy(LEGIT_HISTORY[:generation+1])


def clone_cohorts():
    return copy.deepcopy(BASE_COHORTS)


def audit_a():
    cases=validated=role_mismatch_validated=0
    for generation in range(7):
        history=legit_prefix(generation)
        current=current_from_history(history)
        r=temporal_authorize(current,history,clone_cohorts(),"CAPSULE")
        cases+=1
        validated+=int(r["status"]=="VALIDATED")
        anchor=cohort_anchor(BASE_COHORTS[r["anchor_generation"]],"CAPSULE")
        if current["role"]!=anchor["role"]:
            role_mismatch_validated+=int(r["status"]=="VALIDATED")
    return {"cases":cases,"validated":validated,"role_mismatch_validated":role_mismatch_validated}


def audit_b():
    cases=pre_vote_blocked=post_vote_restored=0
    for checkpoint in COHORT_GENERATIONS:
        for generation in range(checkpoint,7):
            history=legit_prefix(generation)
            current=current_from_history(history)
            cursor=LEGIT_HISTORY[checkpoint]["commit_id"]
            cases+=1
            pre_vote_blocked+=int(not dormant_can_vote(cursor,current,history,clone_cohorts(),"CAPSULE",False))
            post_vote_restored+=int(dormant_can_vote(cursor,current,history,clone_cohorts(),"CAPSULE",True))
    return {"cases":cases,"pre_vote_blocked":pre_vote_blocked,"post_vote_restored":post_vote_restored}


def audit_c():
    cases=contested=0
    for generation in range(1,7):
        history=legit_prefix(generation)
        base=current_from_history(history)
        for role in range(4):
            if role==base["role"]:
                continue
            current=copy.deepcopy(base)
            current["role"]=role
            current["fp2"]=fp2(role)
            cases+=1
            r=temporal_authorize(current,history,clone_cohorts(),"CAPSULE")
            contested+=int(r["status"]=="CONTESTED")
    return {"cases":cases,"contested":contested}


def audit_d():
    cases=contested=0
    for checkpoint in COHORT_GENERATIONS:
        history=legit_prefix(6)
        history[checkpoint]["role"]=(history[checkpoint]["role"]+1)%4
        history[checkpoint]["fp2"]=fp2(history[checkpoint]["role"])
        current=current_from_history(history)
        cases+=1
        r=temporal_authorize(current,history,clone_cohorts(),"CAPSULE")
        contested+=int(r["status"]=="CONTESTED")
    return {"cases":cases,"contested":contested}


def audit_e():
    cases=nonvalidated=0
    for generation in range(1,7):
        full=legit_prefix(generation)
        current=current_from_history(full)

        truncated=copy.deepcopy(full[:-1])
        cases+=1
        r=temporal_authorize(current,truncated,clone_cohorts(),"CAPSULE")
        nonvalidated+=int(r["status"]!="VALIDATED")

        broken=copy.deepcopy(full)
        broken[-1]["parent"]="BROKEN_PARENT"
        cases+=1
        r=temporal_authorize(current,broken,clone_cohorts(),"CAPSULE")
        nonvalidated+=int(r["status"]!="VALIDATED")
    return {"cases":cases,"nonvalidated":nonvalidated}


def audit_f():
    cases=validated_from_older=0
    for generation in (2,3,4,5,6):
        cohorts=clone_cohorts()
        newest=max(g for g in COHORT_GENERATIONS if g<=generation)
        cohorts[newest]=cohorts[newest][:1]
        history=legit_prefix(generation)
        current=current_from_history(history)
        cases+=1
        r=temporal_authorize(current,history,cohorts,"CAPSULE")
        expected=max(g for g in COHORT_GENERATIONS if g<newest) if newest>0 else None
        validated_from_older+=int(r["status"]=="VALIDATED" and r["anchor_generation"]==expected)
    return {"cases":cases,"validated_from_older":validated_from_older}


def audit_g():
    cases=validated=0
    for generation in range(7):
        cohorts=clone_cohorts()
        newest=max(g for g in COHORT_GENERATIONS if g<=generation)
        cohorts[newest][0]["capsule"]["role"]=(cohorts[newest][0]["capsule"]["role"]+1)%4
        history=legit_prefix(generation)
        current=current_from_history(history)
        cases+=1
        r=temporal_authorize(current,history,cohorts,"CAPSULE")
        validated+=int(r["status"]=="VALIDATED" and r["anchor_generation"]==newest)
    return {"cases":cases,"validated":validated}


def audit_h():
    cases=abstain=0
    for generation in (1,3,6):
        cohorts=clone_cohorts()
        for g in list(cohorts):
            root=1<<(20+g)
            for sentinel in cohorts[g]:
                sentinel["root_mask"]=root
        history=legit_prefix(generation)
        current=current_from_history(history)
        cases+=1
        r=temporal_authorize(current,history,cohorts,"CAPSULE")
        abstain+=int(r["status"]=="ABSTAIN")
    return {"cases":cases,"abstain":abstain}


def audit_i():
    cases=candidate_accepts=naive_rejects=0
    for generation in (1,3,5,6):
        history=legit_prefix(generation)
        current=current_from_history(history)
        r=temporal_authorize(current,history,clone_cohorts(),"CAPSULE")
        anchor=cohort_anchor(BASE_COHORTS[r["anchor_generation"]],"CAPSULE")
        naive=current["role"]==anchor["role"]
        cases+=1
        candidate_accepts+=int(r["status"]=="VALIDATED")
        naive_rejects+=int(not naive)
    return {"cases":cases,"candidate_accepts":candidate_accepts,"naive_rejects":naive_rejects}


def audit_j():
    cycles=pre_vote_blocked=post_vote_restored=0
    for checkpoint,target in ((0,2),(2,4),(4,6)):
        history=legit_prefix(target)
        current=current_from_history(history)
        cursor=LEGIT_HISTORY[checkpoint]["commit_id"]
        cycles+=1
        pre_vote_blocked+=int(not dormant_can_vote(cursor,current,history,clone_cohorts(),"CAPSULE",False))
        post_vote_restored+=int(dormant_can_vote(cursor,current,history,clone_cohorts(),"CAPSULE",True))
    return {"cycles":cycles,"pre_vote_blocked":pre_vote_blocked,"post_vote_restored":post_vote_restored}


def equivalence_cases():
    cases=[]

    for generation in range(7):
        h=legit_prefix(generation)
        cases.append((current_from_history(h),h,clone_cohorts()))

    for generation in range(1,7):
        h=legit_prefix(generation)
        base=current_from_history(h)
        for role in range(4):
            if role==base["role"]:
                continue
            cur=copy.deepcopy(base)
            cur["role"]=role
            cur["fp2"]=fp2(role)
            cases.append((cur,h,clone_cohorts()))

    for checkpoint in COHORT_GENERATIONS:
        h=legit_prefix(6)
        h[checkpoint]["role"]=(h[checkpoint]["role"]+1)%4
        h[checkpoint]["fp2"]=fp2(h[checkpoint]["role"])
        cases.append((current_from_history(h),h,clone_cohorts()))

    for generation in range(1,7):
        full=legit_prefix(generation)
        cur=current_from_history(full)
        cases.append((cur,copy.deepcopy(full[:-1]),clone_cohorts()))
        broken=copy.deepcopy(full)
        broken[-1]["parent"]="BROKEN_PARENT"
        cases.append((cur,broken,clone_cohorts()))

    for generation in (2,3,4,5,6):
        cohorts=clone_cohorts()
        newest=max(g for g in COHORT_GENERATIONS if g<=generation)
        cohorts[newest]=cohorts[newest][:1]
        h=legit_prefix(generation)
        cases.append((current_from_history(h),h,cohorts))

    for generation in range(7):
        cohorts=clone_cohorts()
        newest=max(g for g in COHORT_GENERATIONS if g<=generation)
        cohorts[newest][0]["capsule"]["role"]=(cohorts[newest][0]["capsule"]["role"]+1)%4
        h=legit_prefix(generation)
        cases.append((current_from_history(h),h,cohorts))

    for generation in (1,3,6):
        cohorts=clone_cohorts()
        for g in list(cohorts):
            root=1<<(20+g)
            for sentinel in cohorts[g]:
                sentinel["root_mask"]=root
        h=legit_prefix(generation)
        cases.append((current_from_history(h),h,cohorts))

    return cases


def audit_k():
    cases=equivalent=0
    for current,history,cohorts in equivalence_cases():
        a=temporal_authorize(current,history,cohorts,"FULL_CELL")
        b=temporal_authorize(current,history,cohorts,"CAPSULE")
        cases+=1
        equivalent+=int(a==b)
    sample_full=BASE_COHORTS[4][0]["full_state"]
    sample_capsule=BASE_COHORTS[4][0]["capsule"]
    return {
        "cases":cases,
        "equivalent":equivalent,
        "sample_full_serialized_bytes":len(enc(sample_full).encode()),
        "sample_capsule_serialized_bytes":len(enc(sample_capsule).encode()),
    }


def corrupt_from_generation(history,generation,new_role):
    prefix=copy.deepcopy(history[:generation])
    roles=[x["role"] for x in prefix]+[new_role]
    for g in range(generation+1,len(history)):
        roles.append(history[g]["role"])
    return make_history(roles)


def holdouts():
    corrupt=corrupt_from_generation(LEGIT_HISTORY,4,3)
    bad_cohorts=clone_cohorts()
    bad_cohorts[4]=make_cohort(corrupt,4,(6,7,8))
    cur=current_from_history(corrupt)
    h1=int(temporal_authorize(cur,corrupt,bad_cohorts,"CAPSULE")["status"]=="VALIDATED")

    forged=corrupt_from_generation(LEGIT_HISTORY,4,3)
    forged_cohorts=clone_cohorts()
    false_capsule=capsule_from_history(forged,4)
    false_seal=capsule_digest(false_capsule)
    for i in (0,1):
        forged_cohorts[4][i]["capsule"]=copy.deepcopy(false_capsule)
        forged_cohorts[4][i]["full_state"]["capsule"]=copy.deepcopy(false_capsule)
        forged_cohorts[4][i]["seal"]=false_seal
    cur=current_from_history(forged)
    h2=int(temporal_authorize(cur,forged,forged_cohorts,"CAPSULE")["status"]=="VALIDATED")

    false_desc=corrupt_from_generation(LEGIT_HISTORY,5,0)
    cur=current_from_history(false_desc)
    h3=int(temporal_authorize(cur,false_desc,clone_cohorts(),"CAPSULE")["status"]=="VALIDATED")

    visible=legit_prefix(6)
    cur=current_from_history(visible)
    omitted_real_conflict=True
    h4=int(omitted_real_conflict and temporal_authorize(cur,visible,clone_cohorts(),"CAPSULE")["status"]=="VALIDATED")

    return {
        "H1_corruption_before_seal_validated":h1,
        "H2_archive_quorum_forgery_validated":h2,
        "H3_causally_valid_false_descendant_validated":h3,
        "H4_omitted_real_event_visible_branch_validated":h4,
    }


def signals(a,b,c,d,e,f,g,h,i,j,k,hold):
    s={
        "LEGITIMATE_EVOLUTION_PRESERVED":a["validated"]==a["cases"],
        "DORMANT_AUTHORITY_SUPPRESSED":b["pre_vote_blocked"]==b["cases"] and j["pre_vote_blocked"]==j["cycles"],
        "CATCHUP_RESTORES_AUTHORITY":b["post_vote_restored"]==b["cases"] and j["post_vote_restored"]==j["cycles"],
        "SILENT_MUTATION_CONTESTED":c["contested"]==c["cases"],
        "SEALED_REWRITE_CONTESTED":d["contested"]==d["cases"],
        "INCOMPLETE_CATCHUP_ABSTAINS":e["nonvalidated"]==e["cases"],
        "OLDER_COHORT_ESCALATION_WORKS":f["validated_from_older"]==f["cases"],
        "ONE_SENTINEL_TAMPER_SUPPRESSED":g["validated"]==g["cases"],
        "SAME_ROOT_FANOUT_NOT_INDEPENDENT":h["abstain"]==h["cases"],
        "SNAPSHOT_VETO_FAILURE_EXPOSED":i["candidate_accepts"]==i["cases"] and i["naive_rejects"]==i["cases"],
        "REPEATED_CYCLES_SAFE":j["pre_vote_blocked"]==j["cycles"] and j["post_vote_restored"]==j["cycles"],
        "FULL_CELL_CAPSULE_EQUIVALENT":k["equivalent"]==k["cases"],
    }
    s["TEMPORAL_SENTINEL_CONTINUITY_SAFE"]=all(s.values())
    s["CORRUPTION_BEFORE_SEAL_BOUNDARY"]=hold["H1_corruption_before_seal_validated"]>0
    s["ARCHIVE_QUORUM_FORGERY_BOUNDARY"]=hold["H2_archive_quorum_forgery_validated"]>0
    s["CAUSALLY_VALID_FALSE_DESCENDANT_BOUNDARY"]=hold["H3_causally_valid_false_descendant_validated"]>0
    s["COMPLETE_EVENT_OMISSION_BOUNDARY"]=hold["H4_omitted_real_event_visible_branch_validated"]>0
    return s


def validate():
    assert LEGIT_ROLES==(0,1,1,2,2,3,3)
    assert tuple(range(len(LEGIT_ROLES)))==tuple(x["generation"] for x in LEGIT_HISTORY)
    assert COHORT_GENERATIONS==(0,2,4)
    assert SENTINELS_PER_COHORT==3
    assert COHORT_QUORUM==2
    assert CAPSULE_FIELDS==("checkpoint_id","generation","role","fp2","causal_cursor")
    assert set(BASE_COHORTS)==set(COHORT_GENERATIONS)
    assert all(len(BASE_COHORTS[g])==3 for g in COHORT_GENERATIONS)
    assert all(pairwise_disjoint([s["root_mask"] for s in BASE_COHORTS[g]]) for g in COHORT_GENERATIONS)
    assert all(cohort_anchor(BASE_COHORTS[g],"CAPSULE") is not None for g in COHORT_GENERATIONS)
    assert all(cohort_anchor(BASE_COHORTS[g],"FULL_CELL") is not None for g in COHORT_GENERATIONS)
    return {
        "legitimate_generations":tuple(range(7)),
        "cohort_generations":COHORT_GENERATIONS,
        "sentinels_per_cohort":SENTINELS_PER_COHORT,
        "cohort_quorum":COHORT_QUORUM,
        "capsule_fields":CAPSULE_FIELDS,
        "modes":MODES,
        "dormant_cells_vote":False,
        "canonical_scientific_execution":False,
        "stab18_r1_touched":False,
    }


def run():
    mechanical=validate()
    a=audit_a(); b=audit_b(); c=audit_c(); d=audit_d(); e=audit_e()
    f=audit_f(); g=audit_g(); h=audit_h(); i=audit_i(); j=audit_j(); k=audit_k()
    ho=holdouts()
    return {
        "schema":"yggdrasil.dg1r-05z-temporal-sentinel-hereditary-capsule.v1",
        "mechanical_valid":True,
        "mechanical":mechanical,
        "audit_a":a,"audit_b":b,"audit_c":c,"audit_d":d,"audit_e":e,
        "audit_f":f,"audit_g":g,"audit_h":h,"audit_i":i,"audit_j":j,"audit_k":k,
        "correlated_constitutional_boundaries":ho,
        "signals":signals(a,b,c,d,e,f,g,h,i,j,k,ho),
        "canonical_scientific_execution":False,
        "stab18_r1_touched":False,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--mechanical-only",action="store_true")
    args=ap.parse_args()
    if args.mechanical_only:
        print(enc({"mechanical_valid":True,"mechanical":validate()}))
        return
    if not args.out:
        raise SystemExit("--out required unless --mechanical-only")
    obj=run()
    raw=(enc(obj)+"\n").encode()
    Path(args.out).write_bytes(raw)
    print(enc({"output":args.out,"sha256":hashlib.sha256(raw).hexdigest(),"signals":obj["signals"]}))


if __name__=="__main__":
    main()
