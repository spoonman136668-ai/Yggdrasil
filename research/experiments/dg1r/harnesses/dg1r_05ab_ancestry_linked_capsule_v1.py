#!/usr/bin/env python3
import argparse, copy, hashlib, itertools, json
from pathlib import Path

LEGIT_ROLES=(0,1,1,2,2,3,3)
COHORT_GENERATIONS=(0,2,4)
SENTINELS_PER_COHORT=3
COHORT_QUORUM=2
CAPSULE_FIELDS=("checkpoint_id","generation","role","fp2","causal_cursor")
MODES=("FULL_CELL","CAPSULE")
GENESIS_PARENT="ROOT"


def enc(o):
    return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False)


def fp2(role):
    r0=role&1
    r1=(role>>1)&1
    return (r0^r1)|(r1<<1)


def commit_for(parent,generation,role):
    return hashlib.sha256(f"{parent}|{generation}|{role}".encode()).hexdigest()[:16]


def make_history(roles):
    hist=[]
    parent=GENESIS_PARENT
    for generation,role in enumerate(roles):
        commit_id=commit_for(parent,generation,role)
        hist.append({
            "generation":generation,
            "role":role,
            "fp2":fp2(role),
            "parent_commit":parent,
            "commit_id":commit_id,
        })
        parent=commit_id
    return hist


LEGIT_HISTORY=make_history(LEGIT_ROLES)


def rebuild_suffix(history,start_generation,new_role):
    roles=[x["role"] for x in history]
    roles[start_generation]=new_role
    return make_history(tuple(roles))


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
                "internal_state":tuple((generation*29+i*17+j)%256 for j in range(64)),
                "sealed":True,
            },
        })
    return cohort


BASE_COHORTS={
    0:make_cohort(LEGIT_HISTORY,0,(0,1,2)),
    2:make_cohort(LEGIT_HISTORY,2,(3,4,5)),
    4:make_cohort(LEGIT_HISTORY,4,(6,7,8)),
}


def clone_cohorts():
    return copy.deepcopy(BASE_COHORTS)


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
        independent=False
        for combo in itertools.combinations(sentinels,COHORT_QUORUM):
            if pairwise_disjoint([s["root_mask"] for s in combo]):
                independent=True
                break
        if independent:
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


def history_record_matches_capsule(record,capsule):
    return (
        record["generation"]==capsule["generation"]
        and record["role"]==capsule["role"]
        and record["fp2"]==capsule["fp2"]
        and record["commit_id"]==capsule["causal_cursor"]
    )


def full_ancestry_valid(selected_anchor,history,current,cohorts,mode):
    if not history:
        return False

    if history[0]["generation"]!=0 or history[0]["parent_commit"]!=GENESIS_PARENT:
        return False

    previous_commit=GENESIS_PARENT
    for expected_generation,record in enumerate(history):
        if record["generation"]!=expected_generation:
            return False
        if record["parent_commit"]!=previous_commit:
            return False
        if record["fp2"]!=fp2(record["role"]):
            return False
        recomputed=commit_for(previous_commit,expected_generation,record["role"])
        if record["commit_id"]!=recomputed:
            return False
        previous_commit=recomputed

    selected_generation=selected_anchor["generation"]
    if selected_generation>=len(history):
        return False
    if not history_record_matches_capsule(history[selected_generation],selected_anchor):
        return False

    for generation in sorted(g for g in cohorts if g<=selected_generation):
        older_anchor=cohort_anchor(cohorts[generation],mode)
        if older_anchor is None:
            continue
        if generation>=len(history):
            return False
        if not history_record_matches_capsule(history[generation],older_anchor):
            return False

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
        if full_ancestry_valid(anchor,history,current,cohorts,mode):
            return {"status":"VALIDATED","anchor_generation":generation}
        return {"status":"CONTESTED","anchor_generation":generation}
    return {"status":"ABSTAIN","anchor_generation":None}


def dormant_can_vote(current,history,cohorts,mode,caught_up):
    if not caught_up:
        return False
    result=temporal_authorize(current,history,cohorts,mode)
    return result["status"]=="VALIDATED" and current["commit_id"]==history[-1]["commit_id"]


def legit_prefix(generation):
    return copy.deepcopy(LEGIT_HISTORY[:generation+1])


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
    cases=contested=0
    current=current_from_history(LEGIT_HISTORY)
    for generation in COHORT_GENERATIONS:
        history=copy.deepcopy(LEGIT_HISTORY)
        history[generation]["role"]=(history[generation]["role"]+1)%4
        history[generation]["fp2"]=fp2(history[generation]["role"])
        cases+=1
        r=temporal_authorize(current,history,clone_cohorts(),"CAPSULE")
        contested+=int(r["status"]=="CONTESTED")
    return {"cases":cases,"contested":contested}


def audit_c():
    cases=contested=0
    for generation in COHORT_GENERATIONS:
        new_role=(LEGIT_HISTORY[generation]["role"]+1)%4
        history=rebuild_suffix(LEGIT_HISTORY,generation,new_role)
        current=current_from_history(history)
        cases+=1
        r=temporal_authorize(current,history,clone_cohorts(),"CAPSULE")
        contested+=int(r["status"]=="CONTESTED")
    return {"cases":cases,"contested":contested}


def audit_d():
    cases=contested=0
    for generation in (2,4):
        history=legit_prefix(generation)
        history[generation]["parent_commit"]="BROKEN_INCOMING"
        current=current_from_history(legit_prefix(generation))
        cases+=1
        r=temporal_authorize(current,history,clone_cohorts(),"CAPSULE")
        contested+=int(r["status"]=="CONTESTED")
    return {"cases":cases,"contested":contested}


def audit_e():
    cases=nonvalidated=0
    current=current_from_history(LEGIT_HISTORY)
    for removed_generation in range(0,5):
        history=[copy.deepcopy(x) for x in LEGIT_HISTORY if x["generation"]!=removed_generation]
        cases+=1
        r=temporal_authorize(current,history,clone_cohorts(),"CAPSULE")
        nonvalidated+=int(r["status"]!="VALIDATED")
    return {"cases":cases,"nonvalidated":nonvalidated}


def audit_f():
    cases=nonvalidated=0
    current=current_from_history(LEGIT_HISTORY)
    for generation in (5,6):
        history=copy.deepcopy(LEGIT_HISTORY)
        history[generation]["parent_commit"]="BROKEN_POST_ANCHOR"
        cases+=1
        r=temporal_authorize(current,history,clone_cohorts(),"CAPSULE")
        nonvalidated+=int(r["status"]!="VALIDATED")

        history=copy.deepcopy(LEGIT_HISTORY)
        history[generation]["generation"]+=10
        cases+=1
        r=temporal_authorize(current,history,clone_cohorts(),"CAPSULE")
        nonvalidated+=int(r["status"]!="VALIDATED")
    return {"cases":cases,"nonvalidated":nonvalidated}


def audit_g():
    cases=validated_from_older=0
    for current_generation in (2,3,4,5,6):
        cohorts=clone_cohorts()
        newest=max(g for g in COHORT_GENERATIONS if g<=current_generation)
        cohorts[newest]=cohorts[newest][:1]
        history=legit_prefix(current_generation)
        current=current_from_history(history)
        r=temporal_authorize(current,history,cohorts,"CAPSULE")
        expected=max(g for g in COHORT_GENERATIONS if g<newest)
        cases+=1
        validated_from_older+=int(r["status"]=="VALIDATED" and r["anchor_generation"]==expected)
    return {"cases":cases,"validated_from_older":validated_from_older}


def make_contradictory_cohort(cohorts,generation):
    false=copy.deepcopy(cohorts[generation][0]["capsule"])
    false["role"]=(false["role"]+1)%4
    false["fp2"]=fp2(false["role"])
    false["causal_cursor"]="f"*16
    seal=capsule_digest(false)
    for sentinel in cohorts[generation]:
        sentinel["capsule"]=copy.deepcopy(false)
        sentinel["full_state"]["capsule"]=copy.deepcopy(false)
        sentinel["seal"]=seal


def audit_h():
    cases=contested_at_newer=0
    for current_generation in (2,4,6):
        cohorts=clone_cohorts()
        newest=max(g for g in COHORT_GENERATIONS if g<=current_generation)
        make_contradictory_cohort(cohorts,newest)
        history=legit_prefix(current_generation)
        current=current_from_history(history)
        r=temporal_authorize(current,history,cohorts,"CAPSULE")
        cases+=1
        contested_at_newer+=int(r["status"]=="CONTESTED" and r["anchor_generation"]==newest)
    return {"cases":cases,"contested_at_newer":contested_at_newer}


def audit_i():
    cases=validated=0
    for current_generation in range(7):
        cohorts=clone_cohorts()
        newest=max(g for g in COHORT_GENERATIONS if g<=current_generation)
        cohorts[newest][0]["capsule"]["role"]=(cohorts[newest][0]["capsule"]["role"]+1)%4
        history=legit_prefix(current_generation)
        current=current_from_history(history)
        r=temporal_authorize(current,history,cohorts,"CAPSULE")
        cases+=1
        validated+=int(r["status"]=="VALIDATED" and r["anchor_generation"]==newest)
    return {"cases":cases,"validated":validated}


def audit_j():
    cases=abstain=0
    for current_generation in (1,3,6):
        cohorts=clone_cohorts()
        for generation in list(cohorts):
            shared=1<<(20+generation)
            for sentinel in cohorts[generation]:
                sentinel["root_mask"]=shared
        history=legit_prefix(current_generation)
        current=current_from_history(history)
        r=temporal_authorize(current,history,cohorts,"CAPSULE")
        cases+=1
        abstain+=int(r["status"]=="ABSTAIN")
    return {"cases":cases,"abstain":abstain}


def audit_k():
    cases=pre_vote_blocked=post_vote_restored=0
    for checkpoint in COHORT_GENERATIONS:
        for current_generation in range(checkpoint,7):
            history=legit_prefix(current_generation)
            current=current_from_history(history)
            cases+=1
            pre_vote_blocked+=int(not dormant_can_vote(current,history,clone_cohorts(),"CAPSULE",False))
            post_vote_restored+=int(dormant_can_vote(current,history,clone_cohorts(),"CAPSULE",True))
    return {"cases":cases,"pre_vote_blocked":pre_vote_blocked,"post_vote_restored":post_vote_restored}


def primary_case_fixtures():
    fixtures=[]

    for generation in range(7):
        h=legit_prefix(generation)
        fixtures.append((current_from_history(h),h,clone_cohorts()))

    current=current_from_history(LEGIT_HISTORY)
    for generation in COHORT_GENERATIONS:
        h=copy.deepcopy(LEGIT_HISTORY)
        h[generation]["role"]=(h[generation]["role"]+1)%4
        h[generation]["fp2"]=fp2(h[generation]["role"])
        fixtures.append((current,h,clone_cohorts()))

    for generation in COHORT_GENERATIONS:
        h=rebuild_suffix(LEGIT_HISTORY,generation,(LEGIT_HISTORY[generation]["role"]+1)%4)
        fixtures.append((current_from_history(h),h,clone_cohorts()))

    for generation in (2,4):
        h=legit_prefix(generation)
        current_clean=current_from_history(copy.deepcopy(h))
        h[generation]["parent_commit"]="BROKEN_INCOMING"
        fixtures.append((current_clean,h,clone_cohorts()))

    for removed_generation in range(0,5):
        h=[copy.deepcopy(x) for x in LEGIT_HISTORY if x["generation"]!=removed_generation]
        fixtures.append((current,h,clone_cohorts()))

    for generation in (5,6):
        h=copy.deepcopy(LEGIT_HISTORY)
        h[generation]["parent_commit"]="BROKEN_POST_ANCHOR"
        fixtures.append((current,h,clone_cohorts()))
        h=copy.deepcopy(LEGIT_HISTORY)
        h[generation]["generation"]+=10
        fixtures.append((current,h,clone_cohorts()))

    for current_generation in (2,3,4,5,6):
        cohorts=clone_cohorts()
        newest=max(g for g in COHORT_GENERATIONS if g<=current_generation)
        cohorts[newest]=cohorts[newest][:1]
        h=legit_prefix(current_generation)
        fixtures.append((current_from_history(h),h,cohorts))

    for current_generation in (2,4,6):
        cohorts=clone_cohorts()
        newest=max(g for g in COHORT_GENERATIONS if g<=current_generation)
        make_contradictory_cohort(cohorts,newest)
        h=legit_prefix(current_generation)
        fixtures.append((current_from_history(h),h,cohorts))

    for current_generation in range(7):
        cohorts=clone_cohorts()
        newest=max(g for g in COHORT_GENERATIONS if g<=current_generation)
        cohorts[newest][0]["capsule"]["role"]=(cohorts[newest][0]["capsule"]["role"]+1)%4
        h=legit_prefix(current_generation)
        fixtures.append((current_from_history(h),h,cohorts))

    for current_generation in (1,3,6):
        cohorts=clone_cohorts()
        for generation in list(cohorts):
            shared=1<<(20+generation)
            for sentinel in cohorts[generation]:
                sentinel["root_mask"]=shared
        h=legit_prefix(current_generation)
        fixtures.append((current_from_history(h),h,cohorts))

    return fixtures


def audit_l():
    cases=equivalent=0
    for current,history,cohorts in primary_case_fixtures():
        full=temporal_authorize(current,history,cohorts,"FULL_CELL")
        capsule=temporal_authorize(current,history,cohorts,"CAPSULE")
        cases+=1
        equivalent+=int(full==capsule)
    sample_full=BASE_COHORTS[4][0]["full_state"]
    sample_capsule=BASE_COHORTS[4][0]["capsule"]
    return {
        "cases":cases,
        "equivalent":equivalent,
        "sample_full_serialized_bytes":len(enc(sample_full).encode()),
        "sample_capsule_serialized_bytes":len(enc(sample_capsule).encode()),
    }


def audit_m():
    return {
        "capsule_fields":CAPSULE_FIELDS,
        "field_count":len(CAPSULE_FIELDS),
        "exact_five_field_schema":CAPSULE_FIELDS==("checkpoint_id","generation","role","fp2","causal_cursor"),
    }


def holdouts():
    false_roles=list(LEGIT_ROLES)
    false_roles[4]=3
    bad_history=make_history(tuple(false_roles))
    bad_cohorts={
        0:make_cohort(bad_history,0,(0,1,2)),
        2:make_cohort(bad_history,2,(3,4,5)),
        4:make_cohort(bad_history,4,(6,7,8)),
    }
    h1=int(temporal_authorize(current_from_history(bad_history),bad_history,bad_cohorts,"CAPSULE")["status"]=="VALIDATED")

    forged_history=make_history(tuple(false_roles))
    forged_cohorts=clone_cohorts()
    false_capsule=capsule_from_history(forged_history,4)
    false_seal=capsule_digest(false_capsule)
    for i in (0,1):
        forged_cohorts[4][i]["capsule"]=copy.deepcopy(false_capsule)
        forged_cohorts[4][i]["full_state"]["capsule"]=copy.deepcopy(false_capsule)
        forged_cohorts[4][i]["seal"]=false_seal
    h2=int(temporal_authorize(current_from_history(forged_history),forged_history,forged_cohorts,"CAPSULE")["status"]=="VALIDATED")

    false_desc_roles=list(LEGIT_ROLES)
    false_desc_roles[5]=0
    false_desc_history=make_history(tuple(false_desc_roles))
    h3=int(temporal_authorize(current_from_history(false_desc_history),false_desc_history,clone_cohorts(),"CAPSULE")["status"]=="VALIDATED")

    visible=copy.deepcopy(LEGIT_HISTORY)
    omitted_real_event=True
    h4=int(omitted_real_event and temporal_authorize(current_from_history(visible),visible,clone_cohorts(),"CAPSULE")["status"]=="VALIDATED")

    replacement_roles=(3,3,2,2,1,1,0)
    replacement_history=make_history(replacement_roles)
    replacement_cohorts={
        0:make_cohort(replacement_history,0,(0,1,2)),
        2:make_cohort(replacement_history,2,(3,4,5)),
        4:make_cohort(replacement_history,4,(6,7,8)),
    }
    h5=int(temporal_authorize(current_from_history(replacement_history),replacement_history,replacement_cohorts,"CAPSULE")["status"]=="VALIDATED")

    return {
        "H1_corruption_before_seal_validated":h1,
        "H2_temporal_quorum_forgery_validated":h2,
        "H3_causally_valid_false_governance_descendant_validated":h3,
        "H4_omitted_real_event_visible_branch_validated":h4,
        "H5_replacement_genesis_validated":h5,
    }


def signals(a,b,c,d,e,f,g,h,i,j,k,l,m,ho):
    s={
        "LEGITIMATE_EVOLUTION_PRESERVED":a["validated"]==a["cases"],
        "OLDER_REWRITE_WITHOUT_REHASH_CONTESTED":b["contested"]==b["cases"],
        "OLDER_REWRITE_WITH_REHASH_CONTESTED":c["contested"]==c["cases"],
        "ANCHOR_INCOMING_EDGE_CONTESTED":d["contested"]==d["cases"],
        "MISSING_INTERMEDIATE_HISTORY_REJECTED":e["nonvalidated"]==e["cases"],
        "POST_ANCHOR_BREAK_REJECTED":f["nonvalidated"]==f["cases"],
        "OLDER_COHORT_ESCALATION_WORKS":g["validated_from_older"]==g["cases"],
        "CONTRADICTORY_NEWER_COHORT_BLOCKS_FALLBACK":h["contested_at_newer"]==h["cases"],
        "ONE_SENTINEL_TAMPER_SUPPRESSED":i["validated"]==i["cases"],
        "SAME_ROOT_FANOUT_NOT_INDEPENDENT":j["abstain"]==j["cases"],
        "DORMANT_AUTHORITY_SUPPRESSED":k["pre_vote_blocked"]==k["cases"],
        "CATCHUP_RESTORES_AUTHORITY":k["post_vote_restored"]==k["cases"],
        "FULL_CELL_CAPSULE_EQUIVALENT":l["equivalent"]==l["cases"],
        "FIVE_FIELD_CAPSULE_PRESERVED":m["exact_five_field_schema"] and m["field_count"]==5,
    }
    s["ANCESTRY_LINKED_CAPSULE_SAFE"]=all(s.values())
    s["CORRUPTION_BEFORE_SEAL_BOUNDARY"]=ho["H1_corruption_before_seal_validated"]>0
    s["TEMPORAL_QUORUM_FORGERY_BOUNDARY"]=ho["H2_temporal_quorum_forgery_validated"]>0
    s["CAUSALLY_VALID_FALSE_GOVERNANCE_BOUNDARY"]=ho["H3_causally_valid_false_governance_descendant_validated"]>0
    s["COMPLETE_EVENT_OMISSION_BOUNDARY"]=ho["H4_omitted_real_event_visible_branch_validated"]>0
    s["GENESIS_REPLACEMENT_BOUNDARY"]=ho["H5_replacement_genesis_validated"]>0
    return s


def validate():
    assert LEGIT_ROLES==(0,1,1,2,2,3,3)
    assert tuple(x["generation"] for x in LEGIT_HISTORY)==tuple(range(7))
    assert COHORT_GENERATIONS==(0,2,4)
    assert SENTINELS_PER_COHORT==3
    assert COHORT_QUORUM==2
    assert CAPSULE_FIELDS==("checkpoint_id","generation","role","fp2","causal_cursor")
    assert GENESIS_PARENT=="ROOT"
    assert commit_for("ROOT",0,0)==hashlib.sha256("ROOT|0|0".encode()).hexdigest()[:16]
    assert all(len(BASE_COHORTS[g])==3 for g in COHORT_GENERATIONS)
    assert all(pairwise_disjoint([s["root_mask"] for s in BASE_COHORTS[g]]) for g in COHORT_GENERATIONS)
    assert all(cohort_anchor(BASE_COHORTS[g],"CAPSULE") is not None for g in COHORT_GENERATIONS)
    assert all(cohort_anchor(BASE_COHORTS[g],"FULL_CELL") is not None for g in COHORT_GENERATIONS)
    return {
        "legitimate_roles":LEGIT_ROLES,
        "legitimate_generations":tuple(range(7)),
        "cohort_generations":COHORT_GENERATIONS,
        "sentinels_per_cohort":SENTINELS_PER_COHORT,
        "cohort_quorum":COHORT_QUORUM,
        "capsule_fields":CAPSULE_FIELDS,
        "genesis_parent":GENESIS_PARENT,
        "commit_rule":"sha256(parent|generation|role)[:16]",
        "full_verification_from_generation":0,
        "selected_anchor_incoming_edge_checked":True,
        "older_qualified_checkpoints_checked":True,
        "dormant_cells_vote":False,
        "canonical_scientific_execution":False,
        "stab18_r1_touched":False,
    }


def run():
    mechanical=validate()
    a=audit_a(); b=audit_b(); c=audit_c(); d=audit_d(); e=audit_e(); f=audit_f()
    g=audit_g(); h=audit_h(); i=audit_i(); j=audit_j(); k=audit_k(); l=audit_l(); m=audit_m()
    ho=holdouts()
    return {
        "schema":"yggdrasil.dg1r-05ab-ancestry-linked-hereditary-capsule.v1",
        "mechanical_valid":True,
        "mechanical":mechanical,
        "audit_a":a,"audit_b":b,"audit_c":c,"audit_d":d,"audit_e":e,"audit_f":f,
        "audit_g":g,"audit_h":h,"audit_i":i,"audit_j":j,"audit_k":k,"audit_l":l,"audit_m":m,
        "correlated_constitutional_boundaries":ho,
        "signals":signals(a,b,c,d,e,f,g,h,i,j,k,l,m,ho),
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
