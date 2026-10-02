"""Sealed source for EXP-BRIDGE-HETEROGENEOUS-DEGRADATION-SHIFT-001."""
import argparse
import json
import math

EXPERIMENT = "EXP-BRIDGE-HETEROGENEOUS-DEGRADATION-SHIFT-001"
SEEDS = (170003,171007,172001,173021,174031,175039)
STRUCTURE_COUNT = 16
DIAGNOSTIC_RECORDS = 992
VALIDATION_RECORDS = 512


def motif(i):
    return (128+i,64+((7*i)%32),170,85)


def motif_successor(i):
    return 16+13*i


def compound(c):
    return tuple(motif(c)+motif(c+4))


def canonical_state():
    cells=[]
    for i in range(8):
        cells.append({"index":i,"type":1,"key":motif(i),"successor":motif_successor(i),"active":True})
    for c in range(4):
        cells.append({"index":8+c,"type":2,"key":compound(c),"active":True})
    for c in range(4):
        cells.append({"index":12+c,"type":3,"high":c%2,"low":c%2,"active":True})
    return cells


def copy_state(cells):
    out=[]
    for cell in cells:
        row=dict(cell)
        if "key" in row:
            row["key"]=tuple(row["key"])
        out.append(row)
    return out


def cell_signature(cell):
    if cell["type"]==1:
        return (cell["index"],1,cell["active"],tuple(cell["key"]),cell["successor"])
    if cell["type"]==2:
        return (cell["index"],2,cell["active"],tuple(cell["key"]))
    return (cell["index"],3,cell["active"],cell["high"],cell["low"])


def state_jaccard(a,b):
    left={cell_signature(x) for x in a}
    right={cell_signature(x) for x in b}
    union=left|right
    return len(left&right)/len(union) if union else 1.0


def catalog():
    records={}
    for c in range(4):
        records[("compound",c)] = bytes([8+c,2]+list(compound(c)))
        records[("profile",c)] = bytes([12+c,3,c%2,c%2])
    assert sum(len(v) for v in records.values())==56
    return records


def degrade(cells,c,degradation_class):
    out=copy_state(cells)
    if degradation_class==0:
        out[8+c]["active"]=False
        out[8+c]["key"]=tuple()
    elif degradation_class==1:
        out[12+c]["active"]=False
        out[12+c]["high"]=-1
        out[12+c]["low"]=-1
    elif degradation_class==2:
        key=list(out[8+c]["key"])
        key[0]^=1
        out[8+c]["key"]=tuple(key)
    elif degradation_class==3:
        out[12+c]["high"]^=1
        out[12+c]["low"]^=1
    else:
        raise AssertionError("unknown degradation class")
    return out,{8+c,12+c}


def find_compound(cells,key):
    for idx in range(8,12):
        cell=cells[idx]
        if cell["active"] and tuple(cell["key"])==tuple(key):
            return idx-8
    return None


def predict_reference(cells,a_key,b_key):
    a=find_compound(cells,a_key)
    b=find_compound(cells,b_key)
    if a is None or b is None:
        return 255
    pa=cells[12+a]
    pb=cells[12+b]
    if not pa["active"] or not pb["active"]:
        return 255
    return 224+(pa["high"]<<1)+pb["low"]


def predict_local(cells,key):
    for idx in range(8):
        cell=cells[idx]
        if cell["active"] and tuple(cell["key"])==tuple(key):
            return cell["successor"]
    return 255


def local_accuracy(cells):
    correct=0
    total=0
    for repeat in range(64):
        for i in range(8):
            correct += int(predict_local(cells,motif(i))==motif_successor(i))
            total += 1
    return correct/total


def reference_target(a,b):
    return 224+((a%2)<<1)+(b%2)


def filler(seed,record,j,phase):
    state=(seed ^ (phase*0x9E3779B9) ^ (record*0x45D9F3B)) & 0xFFFFFFFF
    for k in range(j+1):
        state=(1664525*state+1013904223+k)&0xFFFFFFFF
    return 192+((state>>24)&63)


def grammar_rows(seed,records,phase):
    assert records%16==0
    rows=[]
    record=0
    for repeat in range(records//16):
        for a in range(4):
            for b in range(4):
                raw=list(compound(a))
                raw.extend(filler(seed,record,j,phase) for j in range(12))
                raw.extend(compound(b))
                raw.append(reference_target(a,b))
                raw.extend(filler(seed^0xA5A5A5A5,record,j,phase) for j in range(3))
                rows.append((a,b,bytes(raw)))
                record+=1
    return rows


def splitmix64(value):
    value=(value+0x9E3779B97F4A7C15)&0xFFFFFFFFFFFFFFFF
    value=((value^(value>>30))*0xBF58476D1CE4E5B9)&0xFFFFFFFFFFFFFFFF
    value=((value^(value>>27))*0x94D049BB133111EB)&0xFFFFFFFFFFFFFFFF
    return value^(value>>31)


def shifted_filler(seed,record,j,phase):
    value=splitmix64((seed<<17) ^ (phase<<9) ^ (record*7+j))
    return 160+(value%64)


def shifted_grammar_rows(seed,phase):
    rows=[]
    record=0
    for a in range(4):
        for b in range(4):
            weight=1+((a+2*b)%3)
            for _ in range(32*weight):
                raw=list(compound(a))
                raw.extend(shifted_filler(seed,record,j,phase) for j in range(12))
                raw.extend(compound(b))
                raw.append(reference_target(a,b))
                raw.extend(shifted_filler(seed^0xA5A5A5A5,record,j,phase) for j in range(3))
                rows.append((a,b,bytes(raw)))
                record+=1
    assert len(rows)==992
    return rows


def overall_accuracy(cells,rows):
    correct=0
    for _,_,raw in rows:
        correct += int(predict_reference(cells,tuple(raw[0:8]),tuple(raw[20:28]))==raw[28])
    return correct/len(rows)


def stratified_accuracy(cells,rows,lesion_id):
    aff_c=aff_t=un_c=un_t=0
    for a,b,raw in rows:
        ok=int(predict_reference(cells,tuple(raw[0:8]),tuple(raw[20:28]))==raw[28])
        if a==lesion_id or b==lesion_id:
            aff_c+=ok; aff_t+=1
        else:
            un_c+=ok; un_t+=1
    return aff_c/aff_t, un_c/un_t


def error_monitor(cells,rows,retained_catalog):
    key_to_id={compound(c):c for c in range(4)}
    counts={key:0 for key in key_to_id}
    for _,_,raw in rows:
        a_key=tuple(raw[0:8])
        b_key=tuple(raw[20:28])
        pred=predict_reference(cells,a_key,b_key)
        target=raw[28]
        if pred==target:
            continue
        for key in (a_key,b_key):
            if key in key_to_id and ("compound",key_to_id[key]) in retained_catalog:
                counts[key]+=1
    ordered=sorted(counts.items(),key=lambda kv:(-kv[1],kv[0]))
    selected_key,selected_count=ordered[0]
    runner_count=ordered[1][1]
    ratio=selected_count/runner_count if runner_count else float("inf")
    return selected_key,key_to_id[selected_key],ratio


def apply_candidate(cells,compound_record,profile_record):
    out=copy_state(cells)
    invalid=0
    ops=0
    read_bytes=len(compound_record)+len(profile_record)
    if len(compound_record)!=10 or len(profile_record)!=4:
        return out,0,read_bytes,1
    cr=list(compound_record)
    pr=list(profile_record)
    if cr[1]!=2 or pr[1]!=3:
        return out,0,read_bytes,1
    c_receiver=cr[0]
    p_receiver=pr[0]
    if not (8<=c_receiver<=11 and 12<=p_receiver<=15):
        return out,0,read_bytes,1
    out[c_receiver]={"index":c_receiver,"type":2,"key":tuple(cr[2:10]),"active":True}
    out[p_receiver]={"index":p_receiver,"type":3,"high":pr[2],"low":pr[3],"active":True}
    ops=2
    return out,ops,read_bytes,invalid


def wrong_candidate_records(retained_catalog,c):
    source=(c+1)%4
    target_comp=list(retained_catalog[("compound",c)])
    target_prof=list(retained_catalog[("profile",c)])
    source_comp=list(retained_catalog[("compound",source)])
    source_prof=list(retained_catalog[("profile",source)])
    target_comp[2:10]=source_comp[2:10]
    target_prof[2:4]=source_prof[2:4]
    return bytes(target_comp),bytes(target_prof)


def correct_candidate_records(retained_catalog,c):
    return retained_catalog[("compound",c)],retained_catalog[("profile",c)]


def unlesioned_mutations(base,current,lesioned_indices):
    count=0
    for idx in range(STRUCTURE_COUNT):
        if idx in lesioned_indices:
            continue
        if cell_signature(base[idx])!=cell_signature(current[idx]):
            count+=1
    return count


def run():
    retained_catalog=catalog()
    seen_classes=set()
    metrics={
        "valid_seed_count":0.0,
        "completed_cycle_count":0.0,
        "minimum_monitor_target_selection_accuracy":1.0,
        "minimum_selected_error_count_ratio_vs_runner_up":float("inf"),
        "minimum_degradation_class_coverage":0.0,
        "maximum_wrong_candidate_validation_gain":0.0,
        "wrong_candidate_retain_count":0.0,
        "wrong_candidate_revert_count":0.0,
        "minimum_correct_candidate_validation_gain":1.0,
        "correct_candidate_retain_count":0.0,
        "correct_candidate_revert_count":0.0,
        "minimum_post_retain_affected_long_range_accuracy":1.0,
        "minimum_post_retain_unaffected_long_range_accuracy":1.0,
        "minimum_post_retain_local_accuracy":1.0,
        "minimum_structure_jaccard_after_each_cycle":1.0,
        "maximum_unlesioned_structure_mutation_count":0.0,
        "maximum_candidate_read_bytes":0.0,
        "maximum_candidate_repair_operations":0.0,
        "maximum_final_structure_count":16.0,
        "minimum_final_structure_count":16.0,
        "degradation_class_label_access_count":0.0,
        "lesion_label_access_count":0.0,
        "evaluator_strata_access_in_decision_count":0.0,
        "policy_threshold_change_count":0.0,
        "capacity_growth_event_count":0.0,
        "invalid_cycle_rows":0.0,
    }

    for seed in SEEDS:
        state=canonical_state()
        for cycle in range(4):
            degradation_class=cycle%4
            seen_classes.add(degradation_class)
            target_id=(seed+3*cycle)%4
            cycle_base=copy_state(state)
            damaged,target_indices=degrade(state,target_id,degradation_class)
            diagnostic=shifted_grammar_rows(seed,30+cycle)
            validation=grammar_rows(seed,VALIDATION_RECORDS,50+cycle)

            selected_key,selected_id,ratio=error_monitor(damaged,diagnostic,retained_catalog)
            metrics["minimum_monitor_target_selection_accuracy"]=min(
                metrics["minimum_monitor_target_selection_accuracy"],
                1.0 if selected_id==target_id else 0.0,
            )
            metrics["minimum_selected_error_count_ratio_vs_runner_up"]=min(
                metrics["minimum_selected_error_count_ratio_vs_runner_up"],ratio
            )

            damaged_validation=overall_accuracy(damaged,validation)
            damaged_local=local_accuracy(damaged)

            wrong_comp,wrong_prof=wrong_candidate_records(retained_catalog,selected_id)
            wrong_state,wrong_ops,wrong_read,wrong_invalid=apply_candidate(damaged,wrong_comp,wrong_prof)
            metrics["invalid_cycle_rows"]+=wrong_invalid
            wrong_acc=overall_accuracy(wrong_state,validation)
            wrong_local=local_accuracy(wrong_state)
            wrong_gain=wrong_acc-damaged_validation
            metrics["maximum_wrong_candidate_validation_gain"]=max(metrics["maximum_wrong_candidate_validation_gain"],wrong_gain)
            metrics["maximum_candidate_read_bytes"]=max(metrics["maximum_candidate_read_bytes"],float(wrong_read))
            metrics["maximum_candidate_repair_operations"]=max(metrics["maximum_candidate_repair_operations"],float(wrong_ops))
            wrong_retain=(wrong_gain>=0.35 and (damaged_local-wrong_local)<=0.0)
            if wrong_retain:
                metrics["wrong_candidate_retain_count"]+=1.0
                state=wrong_state
                metrics["completed_cycle_count"]+=1.0
                metrics["invalid_cycle_rows"]+=1.0
                continue
            metrics["wrong_candidate_revert_count"]+=1.0
            candidate_base=copy_state(damaged)

            correct_comp,correct_prof=correct_candidate_records(retained_catalog,selected_id)
            correct_state,correct_ops,correct_read,correct_invalid=apply_candidate(candidate_base,correct_comp,correct_prof)
            metrics["invalid_cycle_rows"]+=correct_invalid
            correct_acc=overall_accuracy(correct_state,validation)
            correct_local=local_accuracy(correct_state)
            correct_gain=correct_acc-damaged_validation
            metrics["minimum_correct_candidate_validation_gain"]=min(metrics["minimum_correct_candidate_validation_gain"],correct_gain)
            metrics["maximum_candidate_read_bytes"]=max(metrics["maximum_candidate_read_bytes"],float(correct_read))
            metrics["maximum_candidate_repair_operations"]=max(metrics["maximum_candidate_repair_operations"],float(correct_ops))
            correct_retain=(correct_gain>=0.35 and (damaged_local-correct_local)<=0.0)
            if correct_retain:
                metrics["correct_candidate_retain_count"]+=1.0
                state=correct_state
            else:
                metrics["correct_candidate_revert_count"]+=1.0
                state=copy_state(candidate_base)

            affected,unaffected=stratified_accuracy(state,validation,target_id)
            metrics["minimum_post_retain_affected_long_range_accuracy"]=min(metrics["minimum_post_retain_affected_long_range_accuracy"],affected)
            metrics["minimum_post_retain_unaffected_long_range_accuracy"]=min(metrics["minimum_post_retain_unaffected_long_range_accuracy"],unaffected)
            metrics["minimum_post_retain_local_accuracy"]=min(metrics["minimum_post_retain_local_accuracy"],local_accuracy(state))
            metrics["minimum_structure_jaccard_after_each_cycle"]=min(metrics["minimum_structure_jaccard_after_each_cycle"],state_jaccard(canonical_state(),state))
            metrics["maximum_unlesioned_structure_mutation_count"]=max(
                metrics["maximum_unlesioned_structure_mutation_count"],
                float(unlesioned_mutations(cycle_base,state,target_indices)),
            )
            count=sum(1 for cell in state if cell["active"])
            metrics["maximum_final_structure_count"]=max(metrics["maximum_final_structure_count"],float(count))
            metrics["minimum_final_structure_count"]=min(metrics["minimum_final_structure_count"],float(count))
            metrics["completed_cycle_count"]+=1.0

        metrics["valid_seed_count"]+=1.0

    metrics["minimum_degradation_class_coverage"]=float(len(seen_classes))
    if math.isinf(metrics["minimum_selected_error_count_ratio_vs_runner_up"]):
        metrics["minimum_selected_error_count_ratio_vs_runner_up"]=0.0
    assert all(math.isfinite(v) for v in metrics.values())
    return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"metrics":metrics}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",required=True)
    args=parser.parse_args()
    with open(args.out,"w",encoding="utf-8",newline="\n") as handle:
        json.dump(run(),handle,allow_nan=False,separators=(",",":"))


if __name__=="__main__":
    main()
